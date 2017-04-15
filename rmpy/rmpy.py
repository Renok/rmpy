"""
All pretty pieces of this program is a result of Ballmer peak.
Unfortunately the remaining 90% is the result of falling into the Ballmer tail.
"""

import os
import glob
import shutil
import logging
import argparse
import datetime

from rmpy.config_tools import load_config
from rmpy.auxiliary_tools import Codes, ask_confirmation, get_size, output, print_progress_bar


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("remove", nargs="*", help="Delete files")
    parser.add_argument("-rec", dest="recover", help="Recover file")
    parser.add_argument("-re", dest="regex", help="Use regex")
    parser.add_argument("-e", dest="empty", action="store_true", help="Empty trash")
    parser.add_argument("-f", dest="force", action="store_true", help="Ignore nonexistent files")
    parser.add_argument("-c", dest="confirm", action="store_true", help="Confirmation mode")
    parser.add_argument("-s", dest="silent", action="store_true", help="Silent mode")
    parser.add_argument("--dry", action="store_true", help="Dry run")
    parser.add_argument("--log", help="Log path")
    parser.add_argument("--show", nargs="?", const=10, help="Show trash")
    parser.add_argument("--trash", help="Trash path")
    parser.add_argument("--config", help="Upload config")
    parser.add_argument("--policy", help="Recycle policy")
    parser.add_argument("--size", help="Policy size")
    parser.add_argument("--day", help="Policy day")
    args = parser.parse_args()

    config = load_config()
    if args.config:
        new_config = args.config
        config.update(load_config(new_config))

    dry = config["dry"]
    day = config["day"]
    size = config["size"]
    force = config["force"]
    trash = config["trash"]
    silent = config["silent"]
    policy = config["policy"]
    confirm = config["confirm"]
    log_path = config["log_path"]

    if args.dry:
        dry = True
    if args.force:
        force = True
    if args.silent:
        silent = True
    if args.confirm:
        confirm = True
    if args.size:
        size = int(args.size)
    if args.day:
        day = int(args.day)
    if args.trash:
        trash = args.trash
    if args.log:
        log_path = args.log
    if args.policy:
        policy = args.policy

    trash_path, info_path = os.path.join(trash, "files"), os.path.join(trash, "info")
    if not os.path.exists(trash_path):
        os.makedirs(trash_path)
        os.makedirs(info_path)

    logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s', level=logging.DEBUG, filename=log_path)

    if confirm:
        ask_confirmation()

    if args.remove:
        files_num = 0
        for target in args.remove:
            code, files = remove(target, trash_path, info_path, dry, silent, force)
            if code != Codes.GOOD.value:
                output(silent, code, files, " File(s) were removed")
            files_num += files
        output(silent, Codes.GOOD.value, files_num, " File(s) were removed")

    if args.recover:
        code = recover(args.recover, trash_path, info_path, dry, silent)
        output(silent, code, "File recovered")

    if args.regex:
        code, files_num = remove_by_regex(args.regex, trash_path, info_path, dry, silent, force)
        output(silent, code, files_num, " File(s) were removed")

    if args.empty:
        code = empty_trash(trash_path, info_path, dry, silent)
        output(silent, code, "Trash is empty now")

    if args.show:
        num = int(args.show)
        trash_list = show_trash(trash_path, num)
        output(silent, Codes.GOOD.value, "Last elements in trash: ", trash_list)
        if not trash_list:
            print("Trash is empty")

    recycle_policy(policy, trash_path, info_path, day, size)


def remove(target, trash_path, info_path, dry=False, silent=False, force=False):
    files_num = 0
    code = Codes.GOOD.value
    target_path = os.path.abspath(target)

    try:
        # New path for target and its info
        info = os.path.join(info_path, os.path.basename(target_path))
        trash = os.path.join(trash_path, os.path.basename(target_path))

        # Looking for exception for dry-run case
        os.rename(target_path, target_path)

        if dry:
            if not silent:
                print(target_path, " would be replaced to trash")

        else:
            # If target is a directory, then count the number of files inside
            if os.path.isdir(target_path):
                files_num += sum([len(files) + len(dirs) for _, dirs, files in os.walk(target_path)])

            # Name conflict solution
            if os.path.exists(trash):
                count = 1
                while True:
                    if os.path.exists("{}_nfm_{}".format(trash, count)):
                        count += 1
                    else:
                        break
                trash += "_nfm_{}".format(count)
                info += "_nfm_{}".format(count)

            # Replace target to trash and create info file
            os.replace(target_path, trash)
            with open(info, 'w') as file:
                file.write(target_path)

            files_num += 1
            logging.info(target_path + " File removed")

    except FileNotFoundError:
        # Ignore exception for force mode case
        if not force:
            logging.error(target_path + " No such file to remove")
            code = Codes.NO_FILE.value

    except Exception:
        logging.error("Unknown error")
        code = Codes.BAD.value

    return code, files_num


def remove_by_regex(regex, trash_path, info_path, dry=False, silent=False, force=False):
    files_removed = 0
    code = Codes.GOOD.value

    # List of files names by regex
    files = glob.glob(regex)

    if files:
        iteration = 0
        total_files = len(files)

        # Remove files and count their number
        for file in files:
            _, files_num = remove(file, trash_path, info_path, dry, silent, force)
            files_removed += files_num

            # Draw progress bar by current iteration
            iteration += 1
            if not dry and not silent:
                print_progress_bar(iteration, total_files, prefix='Progress:', suffix='Complete', length=50)

    else:
        logging.info(regex + " No regex matches")
        code = Codes.NO_FILE.value

    return code, files_removed


def recover_recursive(trash, path):
    """Recursive function for solving conflicts, some code can be redundant"""
    if os.path.isdir(trash):
        if os.path.exists(path):
            if os.path.isdir(path):
                for obj in os.listdir(trash):

                    trash_child = os.path.join(trash, obj)
                    path_child = os.path.join(path, obj)

                    if not os.path.isdir(trash_child):
                        os.replace(trash_child, path_child)

                    elif os.path.isdir(trash_child):
                        if os.path.exists(path_child):
                            recover_recursive(trash_child, path_child)
                        else:
                            shutil.move(trash_child, path_child)
            else:
                os.remove(path)
                shutil.move(trash, path)
    else:
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
            os.replace(trash, path)


def recover(target, trash_path, info_path, dry=False, silent=False):
    code = Codes.GOOD.value

    try:
        # Paths to target and its info
        info = os.path.join(info_path, target)
        trash = os.path.join(trash_path, target)

        # Reading previous file location
        with open(info, 'r') as file:
            path = file.read()

        if dry:
            if not silent:
                print(path, " would be recovered")

        else:
            # Non-existent path conflict solution
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))

            # Recover target and remove its info
            os.replace(trash, path)
            os.remove(info)

            logging.info(target + " File recovered")

    except FileNotFoundError:
        logging.error(target + " No such file to recover")
        code = Codes.NO_FILE.value

    except OSError:
        # Name conflict solution
        recover_recursive(trash, path)
        os.remove(info)

        logging.info(target + " Recovery conflict")
        code = Codes.CONFLICT.value

    except Exception:
        logging.error("Unknown error")
        code = Codes.BAD.value

    return code


def empty_trash(trash_path, info_path, dry=False, silent=False):
    code = Codes.GOOD.value

    try:
        if dry:
            if not silent:
                print("Trash gonna be empty")

        else:
            # Remove all files from trash
            for file in os.listdir(trash_path):
                trash = os.path.join(trash_path, file)

                if os.path.isdir(trash):
                    shutil.rmtree(trash)
                else:
                    os.remove(trash)

            # Remove all info files
            for info in os.listdir(info_path):
                os.remove(os.path.join(info_path, info))

            logging.info("Trash cleared")

    except Exception:
        logging.error("Unknown error")
        code = Codes.BAD.value

    return code


def show_trash(trash_path, num):
    trash_list = os.listdir(trash_path)[-num:]

    return trash_list


def recycle_policy(policy, trash_path, info_path, day=6, size=100000):
    if policy == "time":
        if datetime.datetime.today().isoweekday() == day:
            empty_trash(trash_path, info_path, dry=False, silent=True)
    if policy == "size":
        if get_size(trash_path) + get_size(info_path) >= size:
            empty_trash(trash_path, info_path, dry=False, silent=True)

    return policy


if __name__ == '__main__':
    main()
