import unittest

from rmpy.rmpy import *


trash_path = "/home/pride/Workspace/univ/python/lab2/trash/files/"
info_path = "/home/pride/Workspace/univ/python/lab2/trash/info/"
log_path = "/home/pride/Workspace/univ/python/lab2/mylog.log"

dry = False
silent = False


logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s', level=logging.DEBUG, filename=log_path)


class TestRMPY(unittest.TestCase):

    def setUp(self):
        os.mkdir("test_dir")

        files = ["a", "b", "c"]
        for file in files:
            with open("test_dir/%s.txt" % file, "w"):
                pass

    def tearDown(self):
        empty_trash(trash_path, info_path, dry, silent)
        if os.path.exists("test_dir"):
            shutil.rmtree("test_dir")

    def test_remove_file_relative(self):
        file = "test_dir/a.txt"
        remove(file, trash_path, info_path)
        self.assertFalse(os.path.exists(file))
        self.assertTrue(os.path.exists(os.path.join(trash_path, "a.txt")))

    def test_remove_file_absolute(self):
        file = os.path.abspath("test_dir/a.txt")
        remove(file, trash_path, info_path)
        self.assertFalse(os.path.exists(file))
        self.assertTrue(os.path.exists(os.path.join(trash_path, "a.txt")))

    def test_remove_dir_relative(self):
        dir = "test_dir"
        remove(dir, trash_path, info_path)
        self.assertFalse(os.path.exists(dir))
        self.assertTrue(os.path.exists(os.path.join(trash_path, dir)))

    def test_remove_dir_absolute(self):
        dir = "test_dir"
        dir_path = os.path.abspath(dir)
        remove(dir_path, trash_path, info_path)
        self.assertFalse(os.path.exists(dir_path))
        self.assertTrue(os.path.exists(os.path.join(trash_path, dir)))

    def test_recover_file(self):
        remove("test_dir/a.txt", trash_path, info_path)
        self.assertFalse(os.path.exists("test_dir/a.txt"))
        recover("a.txt", trash_path, info_path)
        self.assertTrue(os.path.exists("test_dir/a.txt"))

    def test_recover_dir(self):
        dir = "test_dir"
        remove(dir, trash_path, info_path)
        self.assertFalse(os.path.exists(dir))
        recover(dir, trash_path, info_path)
        self.assertTrue(os.path.exists(dir))

    def test_remove_by_regex(self):
        remove_by_regex("test_dir/*.txt", trash_path, info_path, silent=True)
        self.assertFalse(os.path.exists("test_dir/b.txt"))
        self.assertTrue(os.path.exists(os.path.join(trash_path, "b.txt")))

    def test_recover_conflict_file_and_dir(self):
        remove("test_dir", trash_path, info_path)
        with open("test_dir", "w"):
            pass
        recover("test_dir", trash_path, info_path)
        self.assertTrue(os.path.isdir("test_dir"))

    def test_recover_hard_conflict(self):
        os.makedirs("test_dir/a/b/c")
        with open("test_dir/a/b/b.txt", "w"): pass
        with open("test_dir/a/b/c/c.txt", "w"): pass
        remove("test_dir/a/b/b.txt", trash_path, info_path)
        remove("test_dir", trash_path, info_path)
        recover("b.txt", trash_path, info_path)
        recover("test_dir", trash_path, info_path)
        self.assertTrue(os.path.exists("test_dir/a/b/c/c.txt"))
        self.assertTrue(os.path.exists("test_dir/a/b/b.txt"))

    def test_deleted_files_num(self):
        _, files_num = remove("test_dir", trash_path, info_path)
        self.assertEqual(files_num, 4)

    def test_deleted_files_dry_num(self):
        _, files_num = remove("test_dir", trash_path, info_path, dry=True)
        self.assertEqual(files_num, 0)

if __name__ == '__main__':
    unittest.main()
