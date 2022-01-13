from selenium.webdriver import Chrome, ChromeOptions, Firefox, FirefoxOptions
from selenium.common.exceptions import WebDriverException
from msedge.selenium_tools import Edge, EdgeOptions
from strformat import StrFormat
has_browser = False
try:
    options = ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.headless = True
    driver = Chrome(options=options)
    driver.close()
    StrFormat.ok("Chrome is ready.")
    has_browser = True
except WebDriverException:
    StrFormat.warning("No Chrome or no chromedriver.")
    StrFormat.info(
        "Get Chrome from https://www.google.cn/chrome/index.html with latest version recommended.")
    StrFormat.info(
        "Get chromedriver from https://chromedriver.chromium.org/downloads with corresponding version, and put it to PATH.")
try:
    options = EdgeOptions()
    options.use_chromium = True
    options.headless = True
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = Edge(options=options)
    driver.close()
    StrFormat.ok("Edge is ready.")
    has_browser = True
except WebDriverException:
    StrFormat.warning("No Edge or no edgedriver.")
    StrFormat.info(
        "Get Edge from https://www.microsoft.com/zh-cn/edge with the guide it gives.")
    StrFormat.info(
        "Get edgedriver from https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/ with corresponding version, and put it to PATH.")
try:
    options = FirefoxOptions()
    options.headless = True
    driver = Firefox(options=options)
    driver.close()
    StrFormat.ok("Firefox is ready.")
    has_browser = True
except WebDriverException:
    StrFormat.warning("No Firefox or no geckodriver.")
    StrFormat.info(
        "Get Firefox from https://www.firefox.com.cn/ with latest version suggested.")
    StrFormat.info(
        "Get geckodriver from https://github.com/mozilla/geckodriver/releases with latest version recommended, and put it to PATH.")
if not has_browser:
    StrFormat.severe_warning("No supported browser available. Aborting...")
    exit(1)