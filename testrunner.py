import time
import config as cfg
import filemanager as fm
import webapp as wa
import threading
from datetime import datetime
import getpass
import htmlreport as htmlreport
import datetime as dt

fm.loadfiles()

def starttest(name, testcasedef):
    step_fail_count=0
    test_start_time=datetime.now()#.strftime("%Y-%m-%d %H:%M:%S")
    drv=wa.webui()
    teststeps=testcasedef["steps"]
    report={}

    report["id"]=name
    report["name"]=testcasedef["name"]
    report["author"] = testcasedef.get("author", getpass.getuser())
    report["suite"] = testcasedef["suite"]
    report["start"] = test_start_time.strftime("%Y-%m-%d %H:%M:%S")
    report["status"]=""
    report["steps"] = []
    for stepname in teststeps:
        report_steps = {}
        stepdef=cfg.steps_data[stepname]

        if isinstance(stepdef, dict):
            test_step_start_time = datetime.now()#.strftime("%Y-%m-%d %H:%M:%S")
            report_steps["step_name"] = stepdef["description"]
            report_steps["author"] = report["author"]
            report_steps["status"] = ""
            report_steps["start"] = test_step_start_time.strftime("%H:%M:%S")
            status,err=drv.runstep(name, stepname, stepdef)
            test_step_end_time = datetime.now()#.strftime("%Y-%m-%d %H:%M:%S")
            diff_seconds = int((test_step_end_time - test_step_start_time).total_seconds())
            formatted = str(dt.timedelta(seconds=diff_seconds)).rjust(8, "0").split(".")[0]
            report_steps["end"]=test_step_end_time.strftime("%H:%M:%S")
            report_steps["duration"] = formatted
            report_steps["status"] = "PASS" if status else "FAIL"
            step_fail_count += 0 if status else 1
            report_steps["message"] =""
            report_steps["trace"] = err
        elif isinstance(stepdef, list):
            for steps in stepdef:
                test_step_start_time = datetime.now()#.strftime("%Y-%m-%d %H:%M:%S")
                report_steps["step_name"] = stepdef["description"]
                report_steps["author"] = report["author"]
                report_steps["status"] = ""
                report_steps["start"] = test_step_start_time.strftime("%H:%M:%S")
                status, err = drv.runstep(name, stepname, steps)
                test_step_end_time = datetime.now()#.strftime("%Y-%m-%d %H:%M:%S")
                diff_seconds = int((test_step_end_time - test_step_start_time).total_seconds())
                formatted = str(dt.timedelta(seconds=diff_seconds)).rjust(8, "0").split(".")[0]
                report_steps["end"] = test_step_end_time.strftime("%H:%M:%S")
                report_steps["duration"] = formatted
                report_steps["status"] = "PASS" if status else "FAIL"
                step_fail_count += 0 if status else 1
                report_steps["message"] = ""
                report_steps["trace"] = err

        else:
            test_step_start_time = datetime.now()#.strftime("%Y-%m-%d %H:%M:%S")
            report_steps["step_name"] = stepdef["description"]
            report_steps["author"] = report["author"]
            report_steps["status"] = ""
            report_steps["start"] = test_step_start_time.strftime("%H:%M:%S")
            report_steps["end"] = report_steps["start"]
            report_steps["duration"] = f"00:00:00"
            report_steps["status"] = "FAIL"
            report_steps["message"] ="incorrect step def format"
            report_steps["trace"] = f"step is defined as {type(stepdef)}, only dist or list is valid"
            print("incorrect step def format")
            step_fail_count += 1

        report["steps"].append(report_steps)

    report["status"]= "PASS" if step_fail_count==0 else "FAIL"
    test_end_time = datetime.now()
    diff_seconds = int((test_end_time - test_start_time).total_seconds())
    formatted = str(dt.timedelta(seconds=diff_seconds)).rjust(8, "0").split(".")[0]
    report["end"]=test_end_time.strftime("%Y-%m-%d %H:%M:%S")
    cfg.tc_duration+=diff_seconds
    report["duration"] = formatted

    cfg.test_report.append(report)



def runtest():
    threads=[]
    thread_name=""
    i=1
    for testcase_grp in cfg.run_data['testcases'].keys():
        testcases=cfg.run_data['testcases'][testcase_grp]
        for testcasename in testcases:
            testcasedef = cfg.testcase_data[testcasename]
            skiptc=testcasedef.get("skip", False)
            if not skiptc:
                thread_name=testcasedef.get("name", f"testcase_{i}")
                i+=1
                t=threading.Thread(target=starttest, args=(thread_name, testcasedef,))
                threads.append(t)
                t.start()

        for t in threads:
            t.join()

def runtest1():
    threads=[]
    thread_name=""
    i=1
    for testcase_grp in cfg.run_data['testcases'].keys():
        testcases=cfg.run_data['testcases'][testcase_grp]
        for testcasename in testcases:
            testcasedef = cfg.testcase_data[testcasename]
            skiptc=testcasedef.get("skip", False)
            if not skiptc:
                thread_name=testcasedef.get("name", f"testcase_{i}")
                i+=1
                starttest(thread_name, testcasedef)
                exit(1)

runtest1()
#htmlreport.htmlreport(cfg.test_report)