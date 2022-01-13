from concurrent.futures import ThreadPoolExecutor
import os
from time import perf_counter
from crawler import Crawler
from strformat import StrFormat
from urllib import request as req
from urllib import error, parse
from tqdm import tqdm
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

class Doujin:
    @staticmethod
    def check():
        conf = input(StrFormat.cstr(
            "You are going to explicitly 18-restricted site.\n A comfirmation must be specified.[y/N]", fcolor="RED"))
        if conf not in ['y', 'Y']:
            StrFormat.warning("User denial for proceeding.")
            exit(1)
        try:
            StrFormat.info("Checking proxy...")
            req.urlopen("https://www.google.com", timeout=10)
            StrFormat.ok("Proxy available.")
        except error.URLError:
            StrFormat.severe_warning("Foreign website not reachable. Configure your proxy first.")
            exit(1)

    def __init__(self, config: dict, runtime: dict) -> None:
        Doujin.check()
        self.headless = "headless" in runtime.keys()
        self.config = config
        self.base_site, self.alt_site = self.config['doujin']
        self.keywd: list[str] = runtime['doujin']
        self.cap = Crawler.get_cap(runtime)
        self.targets = {}
        self.make_dirs()
        self.total = 0
    
    def search(self, kwd: str, type=2):
        driver = Crawler.init_webdriver(self.config, self.headless, True)
        # type=2: search by character tag
        # sort_key=2: sort by recommendation
        srcs = []
        i = 0
        ind = 1
        total = 1
        while ind <= total:
            print(f"Getting keyword {kwd}'s targets. Page {ind}...")
            driver.get(f"http://ddd-smart.net/list.php?type={type}&keyword={parse.quote(kwd)}&sort_key=2&page={ind}")
            WebDriverWait(driver, 60).until(ec.presence_of_element_located(("xpath", "//ul[3]/li[1]/a")))
            Crawler.scroll(driver)
            elems = driver.find_elements("xpath", "//ul[3]/li/a")
            title_elems = driver.find_elements("xpath", "//ul[3]/li/div/h2")
            for title, elem in zip(title_elems, elems):
                url: str = elem.get_attribute("href")
                g_start = url.find("g=") + 2
                g_end = url.find("&dir=")
                g = url[g_start:g_end]
                dir_start = g_end + 5
                dir_end = url.find("&page=")
                dir = url[dir_start:dir_end]
                srcs.append((f"http://cdn.ddd-smart.net/{g}/{dir}/all.pdf", title.text))
                i += 1
                if self.cap and i > self.cap:
                    break
            if self.cap and i > self.cap:
                    break
            if ind == 1:
                total: str = driver.find_element("xpath", "//div[1]/div[1]/p/span[1]").text
                self.total += int(total)
                total = int(int(total) / 30) + 1
            ind += 1
        self.targets[kwd] = srcs
        driver.close()
        print(f"Crawling completed for {StrFormat.cstr(kwd, style='BOLD', fcolor='CYAN')}.")

    def searches(self):
        start = perf_counter()
        with ThreadPoolExecutor(max_workers=4) as pool:
            for kwd in self.keywd:
                self.search(kwd)
        end = perf_counter()
        print(f"{StrFormat.functional('Crawling')} completed in {StrFormat.time_str(end-start)}.")
        

    def make_dirs(self):
        if not os.path.exists("./True_LSP"):
            os.mkdir("./True_LSP")
        for kwd in self.keywd:
            if not os.path.exists(f"./True_LSP/{kwd}"):
                os.mkdir(f"./True_LSP/{kwd}")

    def download(self, kwd: str, src: tuple, pbar: tqdm):
        url, title = src
        headers = [('User-Agent', UserAgent(path="fake_headers.json").random),
                    ('Referer', 'http://ddd-smart.net')]
        opener = req.build_opener()
        opener.addheaders = headers
        req.install_opener(opener)
        req.urlretrieve(f"{url}", f"./True_LSP/{kwd}/{title}.pdf")
        pbar.update(1)
        
    
    def downloads(self):
        pbar = tqdm(total=self.total)
        start = perf_counter()
        with ThreadPoolExecutor(max_workers=8) as pool:
            for kwd, srcs in self.targets.items():
                for src in srcs:
                    self.download(kwd, src, pbar)
        pbar.close()
        end = perf_counter()
        print(f"{StrFormat.functional('Downloading')} completed for {StrFormat.time_str(end-start)}.")