import os
import json

base_config = "/home/pride/Workspace/univ/python/lab2/config.json"


def load_config(config_file=base_config):
    booleans = ["1", "0"]
    config = {"trash": "/home/pride/Workspace/univ/python/lab2/trash/",
              "log_path": "/home/pride/Workspace/univ/python/lab2/mylog.log",
              "dry": False,
              "silent": False,
              "confirm": False,
              "policy": "size",
              "force": False,
              "size": 100000,
              "day": 6
              }
    try:
        ext = os.path.splitext(config_file)[1]

        if ext == ".json":
            with open(config_file, 'r') as json_config:
                config = json.load(json_config)

        elif ext == ".txt":
            with open(config_file, 'r') as txt_config:
                content = txt_config.readlines()
                content = [x.strip() for x in content]
                for x in content:
                    line = (x.split(" = "))
                    if line[1] in booleans:
                        config[line[0]] = bool(int(line[1]))
                    else:
                        config[line[0]] = (line[1])

    except Exception:
        print("Config Error")

    return config
