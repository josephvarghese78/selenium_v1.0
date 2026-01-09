from selenium.webdriver.common.keys import Keys
import os

KEY_MAP = {
    "ctrl": Keys.CONTROL,
    "cmd": Keys.COMMAND,
    "control": Keys.CONTROL,
    "shift": Keys.SHIFT,
    "alt": Keys.ALT,
    "enter": Keys.ENTER,
    "return": Keys.RETURN,
    "tab": Keys.TAB,
    "space": Keys.SPACE,
    "backspace": Keys.BACKSPACE,
    "delete": Keys.DELETE,
    "del": Keys.DELETE,
    "esc": Keys.ESCAPE,
    "escape": Keys.ESCAPE,
    "home": Keys.HOME,
    "end": Keys.END,
    "insert": Keys.INSERT,
    "ins": Keys.INSERT,
    "page_up": Keys.PAGE_UP,
    "pgup": Keys.PAGE_UP,
    "page_down": Keys.PAGE_DOWN,
    "pgdn": Keys.PAGE_DOWN,
    "arrow_up": Keys.ARROW_UP,
    "up": Keys.ARROW_UP,
    "arrow_down": Keys.ARROW_DOWN,
    "down": Keys.ARROW_DOWN,
    "arrow_left": Keys.ARROW_LEFT,
    "left": Keys.ARROW_LEFT,
    "arrow_right": Keys.ARROW_RIGHT,
    "right": Keys.ARROW_RIGHT,
    "f1": Keys.F1,
    "f2": Keys.F2,
    "f3": Keys.F3,
    "f4": Keys.F4,
    "f5": Keys.F5,
    "f6": Keys.F6,
    "f7": Keys.F7,
    "f8": Keys.F8,
    "f9": Keys.F9,
    "f10": Keys.F10,
    "f11": Keys.F11,
    "f12": Keys.F12,
    # Add more special keys if needed
}

#constants
ELEMENT_HEALING_THRESHOLD=['MATCH', 'HIGH_MATCH']  # Options: "NO_MATCH", "LOW_MATCH", "MATCH", "HIGH_MATCH"
ELEMENTS_FUZZY_METHOD="SELENIUM"  # Options: "BS4", "SELENIUM", selenium is slower use BS4
UPDATE_OR_ON_HEAL=True
UPDATE_OR_ON_NEW_DESC_FOUND=True
ELEMENT_HIGHLIGHT=True
ELEMENT_HIGHLIGHT_COLOR="blue"
ELEMENT_HIGHLIGHT_SIZE=2
ELEMENT_HIGHLIGHT_BLINK=1

#shared variables
osName=None
or_data=None
steps_data=None
run_data=None
data_dict=None
testScript=None
run_file="./testsuite/run.json"
or_file="./testsuite/objects_definition.json"
steps_file="./testsuite/steps_definition.json"
testcase_file="./testsuite/testcase_definition.json"
datadict_file="./testsuite/data_dictonary.json"
testcase_data=None
tc_name=""
tc_author=""
tc_duration=0
tc_env=""

test_report=[]

if os.name=="nt":
    osName="WIN"
elif os.name=="posix":
    osName="MAC"
else:
    osName=""

def get_element_confidence_score(score):
    if score < .30:
        return "NO_MATCH"
    elif .30 <= score < .65:
        return "LOW_MATCH"
    elif .65 <= score <= 1.0:
        return "MATCH"
    else: # score > 1.0
        return "HIGH_MATCH"