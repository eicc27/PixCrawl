from strformat import StrFormat
import os
import platform
import subprocess

SYSTEM = platform.system()
CWD = os.getcwd()


if not os.path.isdir("./venv"):
    StrFormat.warning("No virtual environment for Python 3.10 detected.")
    StrFormat.warning("Trying to create one...")
    if SYSTEM == "Windows":
        os.system("py -3.10 -m venv ./venv")
    else:
        os.system("python3.10 -m venv ./venv")
    StrFormat.ok("Creation succeeded.")
if SYSTEM == "Windows":
    if not os.path.exists(f"{CWD}/venv/Scripts"):
        StrFormat.severe_warning(
            "Directory scripts for activating Windows virtual environment not found. Delete the venv directory and rerun this program.")
        exit(1)
    venv = f"cd {CWD}/venv/Scripts && activate && cd {CWD}"
elif SYSTEM == "Linux":
    if not os.path.exists(f"{CWD}/venv/bin"):
        StrFormat.severe_warning(
            "Directory bin for activating Linux virtual environment not found. Delete the venv directory and rerun this program.")
        exit(1)
    venv = f"source {CWD}/venv/bin/activate"


def check_installation(packages: list[tuple]):
    for package, name in packages:
        if SYSTEM == 'Linux':
            if not os.path.isdir(f"./venv/lib/python3.10/site-packages/{name}"):
                StrFormat.warning(
                    f"Module {name} not found. Trying to install...")
                subprocess.call(f"{venv} && pip install {package}", shell=True)
                StrFormat.ok(f"Installation of {name} suceeded.")
        else:
            if not os.path.isdir(f"./venv/lib/site-packages/{name}"):
                StrFormat.warning(
                    f"Module {name} not found. Trying to install...")
                subprocess.call(f"{venv} && pip install {package}", shell=True)
                StrFormat.ok(f"Installation of {name} suceeded.")


check_installation([("selenium", "selenium"),
                    ("fake_useragent", "fake_useragent"),
                    ("tqdm", "tqdm"),
                    ("lxml", "lxml"),
                    # ("msedge-selenium-tools", "msedge")
                    ])

subprocess.call(f"{venv} && python check_browser.py",
                cwd=".", shell=True)

StrFormat.ok("Pre-initialization checking passed. You can now run start_pc with --nocheck.")
