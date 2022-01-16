from urllib import error, request
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver import Edge, Chrome, Firefox
from selenium.common.exceptions import WebDriverException
from strformat import StrFormat
from platform import system
from os import getenv, listdir
from json import load, dump
SYSTEM = system()
if SYSTEM == "Windows":
    HOME = getenv("APPDATA")[:-8].replace('\\', '/')
else:
    HOME = getenv("HOME")
config = load(open("./startups.json", 'r', encoding='utf-8'))
has_browser = False


# chrome://version/
try:
    options = ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.headless = True
    driver = Chrome(options=options)
    driver.close()
    StrFormat.ok("Chrome is ready.")
    has_browser = True
    if SYSTEM == "Windows":
        base_path = f"{HOME}/Local/Google/Chrome/User Data/"
    else:
        base_path =f"{HOME}/.config/chromium/"
    dirs = listdir(base_path)
    avail_dirs = []
    for dir in dirs:
        if "Default" in dir or "Profile" in dir:
            avail_dirs.append(dir)
    for i, dir in enumerate(avail_dirs):
        if "Default" in dir:
            print(f"[{i+1}]: {dir}", end='\t')
            StrFormat.warning("This is your default browsing profile. Try to avoid using it.")
        else:
            print(f"[{i+1}]: {dir}")
    while True:
        num = StrFormat.query("Select one profile from above:")
        if not num.isnumeric():
            StrFormat.warning("Input not correct.")
            continue
        num = int(num)
        if num <= 0 or num > len(avail_dirs):
            StrFormat.warning("Selecion out of range.")
            continue
        break
    config["chrome"]["profile"] = base_path + avail_dirs[num - 1]
    StrFormat.ok("Chrome profile directory successfully set.")
    login = StrFormat.query("Redirect to Pixiv login? [y/N]:")
    if login in ['y', 'Y']:
        try:
            request.urlopen("https://www.google.com", timeout=10)
            options.headless = False
            sep = config["chrome"]["profile"].rfind('/')
            usr_data_dir, prof_dir = config["chrome"]["profile"][:sep], config["chrome"]["profile"][sep+1:]
            options.add_argument(f"user-data-dir={usr_data_dir}")
            options.add_argument(f"profile-directory={prof_dir}")
            options.add_experimental_option("detach", True)
            driver = Chrome(options=options)
            driver.get("https://www.pixiv.net")
        except error.URLError:
            StrFormat.warning("Proxy unavailable. Skipping...")
except WebDriverException:
    StrFormat.warning("No Chrome or no chromedriver.")
    StrFormat.info(
        "Get Chrome from https://www.google.cn/chrome/index.html with latest version recommended.")
    StrFormat.info(
        "Get chromedriver from https://chromedriver.chromium.org/downloads with corresponding version, and put it to PATH.")

# edge://version
try:
    options = EdgeOptions()
    options.use_chromium = True
    options.headless = True
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    if SYSTEM == "Linux":
        path = StrFormat.query("Specify your Edge binary path:")
        options.binary_location = path
    driver = Edge(options=options)
    driver.close()
    if SYSTEM == 'Linux':
        config["edge"]["linux_bin_path"] = path
    StrFormat.ok("Edge is ready.")
    has_browser = True
    if SYSTEM == "Windows":
        base_path = f"{HOME}/Local/Microsoft/Edge/User Data/"
    else:
        base_path = f"{HOME}/.config/microsoft-edge/"
    dirs = listdir(base_path)
    avail_dirs = []
    for dir in dirs:
        if "Default" in dir or "Profile" in dir:
            avail_dirs.append(dir)
    for i, avail_dir in enumerate(avail_dirs):
        if "Default" in avail_dir:
            print(f"[{i+1}]: {avail_dir}", end='\t')
            StrFormat.warning("This is your default browsing profile, try to avoid using it.")
        else:
            print(f"[{i+1}]: {avail_dir}")
    while True:
        num = StrFormat.query("Select one profile from above:")
        if not num.isnumeric():
            StrFormat.warning("Input not correct.")
            continue
        num = int(num)
        if num <= 0 or num > len(avail_dirs):
            StrFormat.warning("Input out of range.")
            continue
        break
    config["edge"]["profile"] = base_path + avail_dirs[num - 1]
    StrFormat.ok("Edge profile directory successfully set.")
    login = StrFormat.query("Redirect to Pixiv login? [y/N]:")
    if login in ['y', 'Y']:
        try:
            request.urlopen("https://www.google.com", timeout=10)
            options.headless = False
            sep = config["chrome"]["profile"].rfind('/')
            usr_data_dir, prof_dir = config["chrome"]["profile"][:sep], config["chrome"]["profile"][sep+1:]
            options.add_argument(f"user-data-dir={usr_data_dir}")
            options.add_argument(f"profile-directory={prof_dir}")
            options.add_experimental_option("detach", True)
            driver = Edge(options=options)
            driver.get("https://www.pixiv.net")
            driver.implicitly_wait(300)
        except error.URLError:
            StrFormat.warning("Proxy not available. Skipping...")        
except WebDriverException:
    StrFormat.warning("No Edge or no edgedriver.")
    if SYSTEM == "Linux":
        StrFormat.warning("On linux, you should ensure a correct path to Edge browser.")
        StrFormat.info("Try whereis <edge-name> command if you wish.")
    StrFormat.info(
        "Get Edge from https://www.microsoft.com/zh-cn/edge with the guide it gives.")
    StrFormat.info(
        "Get edgedriver from https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/ with corresponding version, and put it to PATH.")

# about:profiles
try:
    options = FirefoxOptions()
    options.headless = True
    driver = Firefox(options=options)
    driver.close()
    StrFormat.ok("Firefox is ready.")
    has_browser = True
    if SYSTEM == "Windows":
        base_path = f"{HOME}/Roaming/Mozilla/Firefox/Profiles/"
    else:
        base_path = f"{HOME}/.mozilla/firefox/"
    dirs = listdir(base_path)
    avail_dirs = []
    for dir in dirs:
        if '.' in dir and '.ini' not in dir:
            avail_dirs.append(dir)
    for i, avail_dir in enumerate(avail_dirs):
        if "default-release" in avail_dir:
            print(f"[{i+1}]: {avail_dir}", end='\t')
            StrFormat.warning("This is your default browsing profile. Try to avoid using it.")
        else:
            print(f"[{i+1}]: {avail_dir}")
    while True:
        num = StrFormat.query("Select one profile from above:")
        if not num.isnumeric():
            StrFormat.warning("Input not correct.")
            continue
        num = int(num)
        if num <= 0 or num > len(avail_dirs):
            StrFormat.warning("Input out of range.")
            continue
        break
    config["firefox"]["profile"] = base_path + avail_dirs[num - 1]
    StrFormat.ok("Firefox profile directory successfully set.")
    login = StrFormat.query("Redirect to Pixiv login? [y/N]:")
    if login in ['y', 'Y']:
        try:
            request.urlopen("https://www.google.com", timeout=10)
            options.headless = False
            options.profile = config["firefox"]["profile"]
            options.set_preference("detach", True)
            driver = Firefox(options=options)
            driver.get("https://www.pixiv.net")
        except error.URLError:
            StrFormat.warning("Proxy not available. Skipping...")
except WebDriverException:
    StrFormat.warning("No Firefox or no geckodriver.")
    StrFormat.info(
        "Get Firefox from https://www.firefox.com.cn/ with latest version suggested.")
    StrFormat.info(
        "Get geckodriver from https://github.com/mozilla/geckodriver/releases with latest version recommended, and put it to PATH.")
if not has_browser:
    StrFormat.severe_warning("No supported browser available. Aborting...")
    exit(1)
dump(config, open("startups.json", 'w', encoding='utf-8'), indent=4)