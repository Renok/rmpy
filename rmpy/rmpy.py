"""
All pretty pieces of this program is a result of Ballmer peak.
Unfortunately the remaining 90% is the result of falling into the Ballmer tail.
"""

import glob
import shutil
import logging
import argparse
import datetime

from rmpy.secondary import *
from rmpy.config_tools import load_config


def main():
    parser = argparse.ArgumentParser(description="Mine rm")
    parser.add_argument("remove", nargs="?", help="File to delete")
    parser.add_argument("-rec", dest="recover", help="Recover file")
    parser.add_argument("-re", dest="regex", help="Use regex")
    parser.add_argument("-e", dest="empty", action="store_true", help="Empty trash")
    parser.add_argument("-s", dest="show", nargs="?", const=10, help="Show trash")
    parser.add_argument("-f", dest="force", action="store_true", help="Ignore nonexistent files")
    parser.add_argument("--dry", action="store_true", help="Dry run")
    parser.add_argument("--confirm", action="store_true", help="Confirm mode")
    parser.add_argument("--silent", action="store_true", help="Silent mode")
    parser.add_argument("--info", help="Info path")
    parser.add_argument("--trash", help="Trash path")
    parser.add_argument("--log", help="Log path")
    parser.add_argument("--config", help="Upload config")
    parser.add_argument("--policy", help="Recycle policy")
    args = parser.parse_args()

    config = load_config()
    if args.config:
        new_config = args.config
        config.update(load_config(new_config))

    dry = config["dry"]
    silent = config["silent"]
    confirm = config["confirm"]
    policy = config["policy"]
    force = config["force"]
    log_path = config["log_path"]
    info_path = config["info_path"]
    trash_path = config["trash_path"]

    if args.dry:
        dry = True
    if args.silent:
        silent = True
    if args.confirm:
        confirm = True
    if args.info:
        info_path = args.info
    if args.trash:
        trash_path = args.trash
    if args.log:
        log_path = args.log
    if args.policy:
        policy = args.policy
    if args.force:
        force = True

    logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s', level=logging.DEBUG, filename=log_path)

    if confirm:
        confirmation()
    if args.remove:
        answer = remove(args.remove, trash_path, info_path, dry, silent, force)
        output(silent, answer[0], answer[1], " File(s) were removed")
    if args.recover:
        code = recover(args.recover, trash_path, info_path, dry, silent)
        output(silent, code, "File recovered")
    if args.regex:
        answer = remove_by_regex(args.regex, trash_path, info_path, dry, silent, force)
        output(silent, answer[0], answer[1], " File(s) were removed")
    if args.empty:
        code = empty_trash(trash_path, info_path)
        output(silent, code, "Trash is empty now")
    if args.show:
        show_trash(trash_path, num=int(args.show))

    recycle_policy(policy, trash_path, info_path)


def remove(target, trash_path, info_path, dry, silent, force=False):
    files_num = 0
    code = Codes.GOOD.value
    target_path = os.path.abspath(target)

    try:
        info = os.path.join(info_path, os.path.basename(target_path))
        trash = os.path.join(trash_path, os.path.basename(target_path))
        os.rename(target_path, target_path)

        if not dry:
            if os.path.isdir(target_path):
                files_num += sum([len(files) + len(dirs) for _, dirs, files in os.walk(target_path)])

            # name conflict solution
            if os.path.exists(trash):
                count = 1
                while True:
                    if os.path.exists(trash + "_nfm_" + str(count)):
                        count += 1
                    else:
                        break
                trash += "_nfm_" + str(count)
                info += "_nfm_" + str(count)

            os.replace(target_path, trash)
            with open(info, 'w') as file:
                file.write(target_path)

            files_num += 1
            logging.info(target_path + " File removed")

        else:
            if not silent:
                print(target_path, " would be replaced to trash")

    except FileNotFoundError:
        if not force:
            logging.error(target_path + " No such file to remove")
            code = Codes.NO_FILE.value

    except Exception:
        logging.error("Unknown error")
        code = Codes.BAD.value

    return code, files_num


def remove_by_regex(regex, trash_path, info_path, dry, silent, force=False):
    files_num = 0
    code = Codes.GOOD.value
    files = glob.glob(regex)

    if files:
        # i = 0
        # l = len(files)
        # print_progress_bar(i, l, prefix='Progress:', suffix='Complete', length=50)
        for obj in glob.glob(regex):
            files_num += remove(obj, trash_path, info_path, dry, silent, force)[1]
            # i += 1
            # print_progress_bar(i, l, prefix='Progress:', suffix='Complete', length=50)

    else:
        logging.info(regex + " No regex matches")
        code = Codes.NO_FILE.value

    return code, files_num


# :*(
def recover_recursive(path1, path2):
    if os.path.isdir(path1):
        if os.path.exists(path2):
            for obj in path1:
                p1_obj = os.path.join(path1, obj)
                p2_obj = os.path.join(path2, obj)
                if not os.path.isdir(p1_obj):
                    os.replace(p1_obj, p2_obj)
                elif os.path.isdir(p1_obj):
                    if os.path.exists(p2_obj):
                        recover_recursive(p1_obj, p2_obj)
                    else:
                        shutil.move(p1_obj, p2_obj)
        shutil.rmtree(path1)
    else:
        shutil.rmtree(path2)
        os.replace(path1, path2)


def recover(target, trash_path, info_path, dry, silent):
    code = Codes.GOOD.value
    try:
        info = os.path.join(info_path, target)
        trash = os.path.join(trash_path, target)

        with open(info, 'r') as file:
            path = file.read()

        if not dry:
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            os.replace(trash, path)
            os.remove(info)
            logging.info(target + " File recovered")

        else:
            if not silent:
                print(path, " would be recovered")

    except FileNotFoundError:
        logging.error(target + " No such file to recover")
        return Codes.NO_FILE.value

    except OSError:
        if os.path.isdir(trash):
            if os.path.isdir(path):
                shutil.rmtree(path)
                shutil.move(trash, path)
            else:
                os.replace(path)
                shutil.move(trash, path)

        os.remove(info)

        logging.info(target + " Recovery conflict")

    except Exception:
        logging.error("Unknown error")

    return code


def empty_trash(trash_path, info_path):
    try:
        for obj in os.listdir(trash_path):
            trash = os.path.join(trash_path, obj)

            if os.path.isfile(trash):
                os.remove(trash)
            elif os.path.isdir(trash):
                shutil.rmtree(trash)
            else:
                os.unlink(trash)

        for obj in os.listdir(info_path):
            os.remove(os.path.join(info_path, obj))

        logging.info("Trash cleared")
        return Codes.GOOD.value

    except Exception:
        logging.error("Unknown error")
        return Codes.BAD.value


def show_trash(trash_path, num):
    trash_list = os.listdir(trash_path)[-num:]
    for file in trash_list:
        print(file)
    if trash_list:
        print("Last %d elements in trash" % len(trash_list))
    else:
        print("Trash is empty")

    return len(trash_list)


def recycle_policy(policy, trash_path, info_path, day=6, size=100000):
    if policy == "time":
        if datetime.datetime.today().isoweekday() == day:
            empty_trash(trash_path, info_path)
    if policy == "size":
        if get_size(trash_path) + get_size(info_path) >= size:
            empty_trash(trash_path, info_path)
    return policy


if __name__ == '__main__':
    main()
