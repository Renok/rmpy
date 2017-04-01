import os
import sys
import time
import glob
import shutil
import logging
import argparse

from enum import Enum

from rmpy.trash_config import load_config


class Codes(Enum):
    GOOD = 0
    ALMOST_GOOD = 1
    BAD = 2


def main():
    parser = argparse.ArgumentParser(description="Mine rm")
    parser.add_argument("d", nargs="?", help="File to delete")
    parser.add_argument("-r", help="Recover file")
    parser.add_argument("-re", help="Use regex")
    parser.add_argument("-e", action="store_true", help="Empty trash")
    parser.add_argument("-s", nargs="?", const=10, help="Show trash")
    parser.add_argument("--dry", action="store_true", help="Dry run")
    parser.add_argument("--confirm", action="store_true", help="Confirm mode")
    parser.add_argument("--silent", action="store_true", help="Silent mode")
    parser.add_argument("--info", help="Info path")
    parser.add_argument("--trash", help="Trash path")
    parser.add_argument("--log", help="Log path")
    parser.add_argument("--config", help="Upload config")
    parser.add_argument("--politic", help="Recycle politic")
    args = parser.parse_args()

    config = load_config()
    if args.config:
        config.update(load_config(args.config))

    dry = config["dry"]
    silent = config["silent"]
    confirm = config["confirm"]
    politic = config["politic"]
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
    if args.politic:
        politic = args.politic

    logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s', level=logging.DEBUG, filename=log_path)

    if confirm:
        answer = input("Are you sure? [y/n]\n")
        if answer != 'y':
            print("Operation canceled")
            return

    if args.d:
        remove(args.d, trash_path, info_path, dry, silent)
    if args.r:
        recover(args.r, trash_path, info_path, dry, silent)
    if args.re:
        remove_by_regex(args.re, trash_path, info_path, dry, silent)
    if args.e:
        empty_trash(trash_path, info_path, silent)
    if args.s:
        show_trash(trash_path, num=int(args.s))

    recycle_politic(politic, trash_path, info_path)


def get_size(path):
    total_size = 0
    for dir_path, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(dir_path, f)
            total_size += os.path.getsize(fp)
    return total_size


def recycle_politic(politic, trash_path, info_path):
    if politic == "time":
        if time.asctime().split(' ')[0] == "Mon":
            empty_trash(trash_path, info_path, True)
    if politic == "size":
        if get_size(trash_path) + get_size(info_path) >= 100000:
            empty_trash(trash_path, info_path, True)


def output(silent, code, *args):
    if not silent:
        print(''.join(map(str, args)))
    else:
        sys.exit(code)


def remove(target, trash_path, info_path, dry, silent, by_re=False):
    files_num = 0
    target_path = os.path.abspath(target)

    try:
        info = os.path.join(info_path, os.path.basename(target_path))
        trash = os.path.join(trash_path, os.path.basename(target_path))

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
            if not by_re:
                output(silent, Codes.GOOD.value, files_num, " file(s) were removed")

        else:
            if os.path.exists(target_path):
                print(target_path, " would be replaced to trash")
            else:
                print("No such file")

    except FileNotFoundError:
        logging.error(target_path + " No such file to remove")
        output(silent, Codes.BAD.value, "No such file")

    except Exception:
        logging.error("Unknown error")
        output(silent, Codes.BAD.value, "Some $hit happened")

    return files_num


def remove_by_regex(regex, trash_path, info_path, dry, silent):
    files_num = 0

    if not glob.glob(regex):
        logging.info(regex + " No regex matches")
        output(silent, Codes.BAD.value, "No matches")

    else:
        for obj in glob.glob(regex):
            files_num += remove(obj, trash_path, info_path, dry=dry, silent=silent, by_re=True)

    output(silent, Codes.GOOD.value)
    return files_num


def recover(target, trash_path, info_path, dry, silent):
    try:
        info = os.path.join(info_path + target)
        trash = os.path.join(trash_path + target)

        with open(info, 'r') as file:
            path = file.read()

        if not dry:
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            os.replace(trash, path)
            os.remove(info)
            logging.info(target + " File recovered")
            output(silent, Codes.GOOD.value, "File was recovered")

        else:
            print(path, " would be recovered")

    except FileNotFoundError:
        logging.error(target + " No such file to recover")
        output(silent, Codes.BAD.value, "No such file")

    except OSError:
        for obj in os.listdir(trash):
            shutil.move(os.path.join(trash, obj), os.path.join(path, obj))
        shutil.rmtree(trash)
        os.remove(info)

        logging.info(target + " Recovery conflict")
        output(silent, Codes.ALMOST_GOOD.value, "Directory already exists but conflict solved")

    except Exception:
        logging.error("Unknown error")
        output(silent, Codes.BAD.value, "Some $hit happened")

    return 0


def empty_trash(trash_path, info_path, silent):
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
        output(silent, Codes.GOOD.value, "Trash is empty now")

    except Exception:
        logging.error("Unknown error")
        output(silent, Codes.BAD.value, "Some $hit happened")

    return 0


def show_trash(trash_path, num):
    trash_list = os.listdir(trash_path)[-num:]
    for x in trash_list:
        print(x)
    if len(trash_list):
        print("Last %d elements in trash" % len(trash_list))
    else:
        print("Trash is empty")

    return 0


if __name__ == '__main__':
    main()
