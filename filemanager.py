import json
import config as cfg
import getpass

def loador():
    try:
        with open(f"./{cfg.or_file}", 'r') as f:
            cfg.or_data = json.load(f)
    except:
        pass

def saveor():
    with open(f"./{cfg.or_file}", 'w') as f:
        json.dump(cfg.or_data, f, indent=4)


def loadsteps():
    try:
        with open(f"./{cfg.steps_file}", 'r') as f:
            cfg.steps_data = json.load(f)
    except:
        pass

def loadtestcases():
    try:
        with open(f"./{cfg.testcase_file}", 'r') as f:
            cfg.testcase_data = json.load(f)
    except:
        pass

def loadrunfile():
    try:
        with open(f"./{cfg.run_file}", 'r') as f:
            cfg.run_data = json.load(f)
    except:
        pass

def loaddatafile():
    try:
        with open(f"./{cfg.datadict_file}", 'r') as f:
            cfg.data_dict = json.load(f)
    except:
        pass


def loadfiles():
    loador()
    loadsteps()
    loadtestcases()
    loadrunfile()
    loaddatafile()

    cfg.tc_name=cfg.testcase_data.get("project", "Unknown")
    cfg.tc_author = cfg.testcase_data.get("author", getpass.getuser())
    cfg.tc_env = cfg.testcase_data.get("env", "Unknown")