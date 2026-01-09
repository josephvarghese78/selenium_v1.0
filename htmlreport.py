import os, json, platform, datetime
from jinja2 import Environment, FileSystemLoader
import datetime as dt
import config as cfg
# -- sample data (replace with your real test run)
#tests = ""


def htmlreport(report):

    # summary calculations
    passed = sum(1 for t in report if t["status"]=="PASS")
    failed = sum(1 for t in report if t["status"]=="FAIL")
    skipped = sum(1 for t in report if t["status"]=="SKIP")
    total = len(report)
    formatted = str(dt.timedelta(seconds=cfg.tc_duration)).rjust(8, "0").split(".")[0]

    summary = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "pass_percent": round((passed/total*100) if total else 0,2),
        "duration": formatted,
        "author": cfg.tc_author,
        "project": cfg.tc_name,
        "env": cfg.tc_env,
        "system": platform.system() + " " + platform.release(),
        "os": platform.platform(),
        "python": platform.python_version(),
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # ensure output folder
    out_dir = os.path.join("output")
    os.makedirs(out_dir, exist_ok=True)

    # load template and render
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("report.html")

    # tests as dict keyed by id (makes client code simpler)
    tests_dict = {t["id"]: t for t in report}

    html = template.render(
        title = f"{summary['project']} - Test Report",
        tests_json = json.dumps(tests_dict),
        summary_json = json.dumps(summary),
        summary = summary,
        tests = report,  # kept for server-side listings if desired
        generated_at = summary['generated_at']
    )

    path = "./output"
    count = sum(1 for f in os.listdir(path) if f.startswith(f"{cfg.tc_name}") and f.endswith("html"))
    report_filename = f"{cfg.tc_name}.html" if count == 0 else f"{cfg.tc_name} {count}.html"

    out_path = os.path.join(out_dir, report_filename)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print("Report generated:", out_path)
    print("Open it in your browser (file://...)")
