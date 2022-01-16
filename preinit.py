from sys import argv, version_info
from strformat import StrFormat
import os
import platform
import subprocess


MAJOR = version_info.major
MINOR = version_info.minor
SYSTEM = platform.system()


if not (MAJOR == 3 and MINOR == 10):
    StrFormat.severe_warning("This program uses Python 3.10 for match...case "
                             f"but your current version is {MAJOR}.{MINOR}.")
    StrFormat.severe_warning(
        "The program will not run without correct Python version.")
    StrFormat.info(
        "Get Python from: https://www.python.org/downloads/ or via your corresponding package manager.")
    StrFormat.info(
        "Or you have python >=3.10 downloaded then you need to specify the version of python used like following:")
    if SYSTEM == "Windows":
        print(">>py -3.10 preinit.py")
    else:
        print(">>python3.10 preinit.py")
    exit(1)
cwd = os.getcwd()
StrFormat.ok("Python version correct.")


def check_integrity(fnames: list[str]):
    for fname in fnames:
        if not os.path.isfile(f"{cwd}/{fname}"):
            StrFormat.severe_warning("Working directory not correct. Please change your directory"
                                     f" to the folder that contains {fname}.")
            exit(1)


check_integrity(["cli.py", "crawler.py",
                 "database.py", "downloader.py",
                 "native_crawler.py", "pixiv_crawler.py",
                 "pixcrawl.py", "strformat.py",
                 "args.json", "startups.json"
                 ])
StrFormat.ok("Integrity check passed.")


if not os.path.isdir("./venv"):
    StrFormat.warning("No virtual environment for Python 3.10 detected.")
    StrFormat.warning("Trying to create one...")
    if SYSTEM == "Windows":
        os.system("py -3.10 -m venv ./venv")
    else:
        os.system("python3.10 -m venv ./venv")
    StrFormat.ok("Creation succeeded.")
if SYSTEM == "Windows":
    if not os.path.exists(f"{cwd}/venv/Scripts"):
        StrFormat.severe_warning(
            "Directory scripts for activating Windows virtual environment not found. Delete the venv directory and rerun this program.")
        exit(1)
    venv = f"cd {cwd}/venv/Scripts && activate && cd {cwd}"
elif SYSTEM == "Linux":
    if not os.path.exists(f"{cwd}/venv/bin"):
        StrFormat.severe_warning(
            "Directory bin for activating Linux virtual environment not found. Delete the venv directory and rerun this program.")
        exit(1)
    venv = f"source {cwd}/venv/bin/activate"


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

StrFormat.ok("Pre-initialization checking passed.")
# argv_str = " ".join(argv[1:])
# subprocess.call(f"{venv} && python pixcrawl.py {argv_str}",
#                 cwd=".", shell=True)
