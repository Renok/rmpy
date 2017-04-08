import os
import json

base_config = "config.json"


def load_config(config_file=base_config):
    booleans = ["1", "0"]
    config = {}
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
        print("Error")

    return config
