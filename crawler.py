from concurrent.futures.thread import ThreadPoolExecutor
from json import load
from selenium.webdriver.remote.webdriver import WebDriver
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from time import perf_counter, sleep
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from strformat import StrFormat
from platform import system
SYSTEM = system()

class Crawler:
    def __init__(self, runtime: dict) -> None:
        self.config = load(open("startups.json", 'r'))
        self.ids = runtime["illusts"]
        self.mode = runtime["mode"]
        self.headless = "headless" in runtime.keys()
        self.illusts: dict[str, str] = {}
        self.pictures: dict[str, list[str]] = {}
        self.illust_url_base = ""
        self.pic_url_base = ""
        self.cap = Crawler.get_cap(runtime)
    
    @staticmethod
    def get_cap(runtime: dict):
        if "cap" in runtime.keys():
            cap = runtime["cap"][0]
            if cap.isnumeric():
                cap = int(cap)
                if not cap or not isinstance(cap, int):
                    StrFormat.severe_warning("the argument for --cap must be a positive integer.")
                    exit(1)
            elif cap == 'none':
                cap = None
            else:
                StrFormat.severe_warning("the argument for --cap must be numeric or 'none'.")
                exit(1)
            return cap
    
    def map(self, id: str):
        raise NotImplementedError

    def maps(self):
        StrFormat.info("Mapping ID...")
        start = perf_counter()
        with ThreadPoolExecutor() as pool:
            for id in self.ids:
                self.map(id)
        end = perf_counter()
        if len(self.illusts) != len(self.ids):
            exit(1)
        StrFormat.mapping(self.illusts.keys(), self.illusts.values())
        print(f"{StrFormat.functional('Mapping')} finished successfully in {StrFormat.time_str(end - start)}.")

    def get(self, id: str, name: str):
        raise NotImplementedError

    def gets(self):
        start = perf_counter()
        with ThreadPoolExecutor(max_workers=4) as pool:
            for id, name in self.illusts.items():
                if self.config["browser"] == 'firefox':
                    pool.submit(self.get, id, name)
                else:
                    self.get(id, name)
        end = perf_counter()
        # dump(self.pictures, open("test.json", 'w'), indent=4)
        print(f"{StrFormat.functional('Crawling')} finished successfully in {StrFormat.time_str(end - start)}.")

    @staticmethod
    def scroll(driver: WebDriver):
        for i in range(1, 5):
            driver.execute_script(
                f'''
                    var i = {i} * document.body.scrollHeight/4;
                    window.scrollTo(0,i);
                '''
            )
            sleep(2)

    @staticmethod
    def init_webdriver(config: dict, headless: bool, is_async=False):
        cap = None
        match config["browser"]:
            case "firefox":
                options = webdriver.FirefoxOptions()
                options.headless = headless
                options.profile = config["firefox"]["profile"]
                if is_async:
                    cap = DesiredCapabilities.FIREFOX
                    cap["pageLoadStrategy"] = "none"
                return webdriver.Firefox(options=options, desired_capabilities=cap)
            case "chrome":
                options = webdriver.ChromeOptions()
                if SYSTEM == "Linux":
                    options.headless = headless
                if headless:
                    options.add_argument("window-size=1920,1080")
                options.add_experimental_option('excludeSwitches', ['enable-logging'])
                sep = config["chrome"]["profile"].rfind('/')
                usr_data_dir, prof_dir = config["chrome"]["profile"][:sep], config["chrome"]["profile"][sep+1:]
                options.add_argument(f"user-data-dir={usr_data_dir}")
                options.add_argument(f'profile-directory={prof_dir}')
                if is_async:
                    cap = DesiredCapabilities.CHROME
                    cap["pageLoadStrategy"] = "none"
                return webdriver.Chrome(options=options, desired_capabilities=cap)
            case "edge":
                options = EdgeOptions()
                options.use_chromium = True
                options.headless = headless
                if headless:
                    options.add_argument("window-size=1920,1080")
                options.add_experimental_option('excludeSwitches', ['enable-logging'])
                sep = config["edge"]["profile"].rfind('/')
                usr_data_dir, prof_dir = config["edge"]["profile"][:sep], config["edge"]["profile"][sep+1:]
                options.add_argument(f"user-data-dir={usr_data_dir}")
                options.add_argument(f'profile-directory={prof_dir}')
                if SYSTEM == 'Linux':
                    options.binary_location = config["edge"]["linux_bin_path"]
                if is_async:
                    cap = DesiredCapabilities.EDGE
                    cap["pageLoadStrategy"] = "none"
                return webdriver.Edge(options=options, capabilities=cap)