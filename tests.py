import unittest

from rmpy.rmpy import *


trash_path = "/home/pride/Workspace/univ/python/lab2/trash/files/"
info_path = "/home/pride/Workspace/univ/python/lab2/trash/info/"
log_path = "/home/pride/Workspace/univ/python/lab2/mylog.log"

dry = False
silent = False


def invoker(func, path):
    return func(path, trash_path, info_path, dry, silent)


logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s', level=logging.DEBUG, filename=log_path)


class TestRMPY(unittest.TestCase):

    def setUp(self):
        os.mkdir("test_dir")

        files = ["a", "b", "c"]
        for file in files:
            with open("test_dir/%s.txt" % file, "w"):
                pass

    def tearDown(self):
        empty_trash(trash_path, info_path, silent)
        if os.path.exists("test_dir"):
            shutil.rmtree("test_dir")

    def test_remove_relative(self):
        self.assertEqual(invoker(remove, "test_dir"), 4)

    def test_remove_absolute(self):
        abs_path = os.path.join(os.getcwd(), "test_dir/a.txt")
        self.assertEqual(invoker(remove, abs_path), 1)

    def test_no_file_to_remove(self):
        self.assertEqual(invoker(remove, "test_dir/f.txt"), 0)

    def test_remove_by_regex(self):
        self.assertEqual(invoker(remove_by_regex, "test_dir/*.txt"), 3)

    def test_remove_by_regex_dry(self):
        self.assertEqual(remove_by_regex("test_dir/*.txt", trash_path, info_path, dry=True, silent=False), 0)

    def test_no_regex_matches(self):
        self.assertEqual(invoker(remove_by_regex, "test_dir/*.cfg"), 0)

    def test_recover_folder(self):
        invoker(remove, "test_dir")
        self.assertRaises(Exception, invoker(recover, "test_dir"))

    def test_recover_child_and_parent(self):
        remove("test_dir/a.txt", trash_path, info_path, dry, silent)
        remove("test_dir", trash_path, info_path, dry, silent)
        recover("a.txt", trash_path, info_path, dry, silent)
        recover("test_dir", trash_path, info_path, dry, silent)


if __name__ == '__main__':
    unittest.main()
