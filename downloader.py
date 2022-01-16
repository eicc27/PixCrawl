from time import perf_counter
from crawler import Crawler
from tqdm import tqdm
from os.path import exists
from os import mkdir
from fake_useragent import UserAgent
import urllib.request as req
from urllib.error import HTTPError
from concurrent.futures import ThreadPoolExecutor
from strformat import StrFormat
from json import load, dump
import socket
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def copy(obj: dict[str, list]) -> dict[str, list]:
    res = {}
    for key, values in obj.items():
        res[key] = []
        for value in values:
            res[key].append(value)
    return res


def encode_filename(fname: str):
    return fname.replace('/', '_')


class Downloader:
    '''
    Functional interfaces: downloads, recover
    '''
    def __init__(self, pictures: dict[str, list[str]], runtime: dict,
                mirror: bool) -> None:
        socket.setdefaulttimeout(10)
        self.mirror = mirror
        self.headless = "headless" in runtime.keys()
        self.config = load(open("startups.json", 'r'))
        self.picture_base_url = self.config["format"]["mirror"]["picture"
            ] if self.mirror else self.config["format"]["pixiv"]["picture"]
        self.recovery_path = "recovery.json"
        self.pictures = pictures

    def recover(self):
        print(
            StrFormat.cstr("====>Reading recovery file<====",
                           style="BOLD",
                           fcolor="RED"))
        try:
            self.remain_pics: dict[str, list[list]] = load(open(self.recovery_path, 'r+', encoding='utf-8'))
            for key, values in self.remain_pics.items():
                for i, value in enumerate(values):
                    self.remain_pics[key][i] = tuple(value)
            has_history = False
            for value in self.remain_pics.values():
                if len(value):
                    has_history = True
            if has_history:
                self.downloads(self.remain_pics)
            else:
                StrFormat.warning("No history has been recorded.")
        except FileNotFoundError:
            StrFormat.warning("No history has beed recorded.")

    @staticmethod
    def total(target) -> int:
        res = 0
        for key in target.keys():
            res += len(target[key])
        return int(res / 2)

    def mkdir_lsp(self):
        if not exists("./LSP"):
            mkdir("./LSP")
        for key in self.pictures.keys():
            key = encode_filename(key)
            if not exists(f"./LSP/{key}"):
                mkdir(f"./LSP/{key}")
                mkdir(f"./LSP/{key}/R")
                mkdir(f"./LSP/{key}/NR")

    @staticmethod
    def fake(mirror=False):
        if not mirror:
            headers = [('User-Agent', UserAgent(path="fake_headers.json").random),
                    ('Referer', 'https://www.pixiv.net')]
        else:
            headers = [('User-Agent', UserAgent(path="fake_headers.json").random),
                    ('Referer', 'https://www.vilipix.com')]
        opener = req.build_opener()
        opener.addheaders = headers
        req.install_opener(opener)

    def download(self, key: str, url: str, r18: bool,
                 avail: dict[str, list], rest: dict[str, list],
                 pbar: tqdm, retry=0):
        if retry == 3:
            StrFormat.severe_warning(f"Max retries({retry}) reached for {url}. Aborted.")
        filename = url[url.rfind('/') + 1:]
        Downloader.fake()
        try:
            req.urlretrieve(url,
                f"./LSP/{encode_filename(key)}/R/{filename}" if r18 else f"./LSP/{encode_filename(key)}/NR/{filename}"
            )
            pbar.update(1)
            self.err_pictures[key].remove((url, r18))
            rest[key].remove((url, r18))
        except HTTPError:
            avail[key].remove((url, r18))
            rest[key].remove((url, r18))
        except OSError:
            self.download(key, url, r18, avail, rest, pbar, retry + 1)
        finally:
            dump(rest, open(self.recovery_path, 'w+', encoding='utf-8'), indent=4, ensure_ascii=False)

    def downloads(self, target: dict):
        print(
            StrFormat.cstr("====>Starting full Pixcrawl downloading<====",
                           style="BOLD",
                           fcolor="RED"))
        self.mkdir_lsp()
        start = perf_counter()
        dump(target, open('target.json', 'w+', encoding='utf-8'), indent=4, ensure_ascii=False)
        avail_pictures = copy(target)
        rest_pictures = copy(target)
        self.err_pictures = copy(target)
        dump(rest_pictures,
             open(self.recovery_path, 'w+', encoding='utf-8'),
             indent=4,
             ensure_ascii=False)
        progress_bar = tqdm(total=Downloader.total(target))
        with ThreadPoolExecutor() as pool:
            for key in target.keys():
                for url, r18 in target[key]:
                    pool.submit(self.download, key, url, r18,
                                  avail_pictures, rest_pictures, progress_bar)
        end = perf_counter()
        dump(self.err_pictures, open('error.json', 'w+', encoding='utf-8'), indent=4, ensure_ascii=False)
        print(
            f"\n{StrFormat.functional('Naive downloading')} completed in {StrFormat.time_str(end - start)}."
        )
        self.rematches(progress_bar, avail_pictures)
        return avail_pictures
        
    
    def find_unavail(self):
        res = {}
        for key, value in self.err_pictures.items():
            urls = []
            for url, r18 in value:
                alt = (url.replace("jpg",
                                  "png") if url[-3:] == "jpg" else url.replace(
                                      "png", "jpg"), r18)
                target = (url[url.rfind('/') + 1:url.rfind("_")], r18)
                if alt in value and target not in urls:
                    urls.append(target)
            res[key] = urls
        return res

    def rematch_native(self, key: str, value: tuple[str, bool], pbar: tqdm, target: dict):
        url, _ = value
        driver = Crawler.init_webdriver(self.config, self.headless)
        driver.maximize_window()
        driver.get(self.picture_base_url + url)
        Crawler.scroll(driver)
        picture_elems = driver.find_elements("xpath", "//main//li//img")
        source = []
        for picture in picture_elems:
            picture.click()
            source.append(
                driver.find_element("xpath",
                                    "//div/div[2]/img").get_attribute("src"))
            sleep(.5)
            driver.find_element("xpath", "//div[3]//button/i").click()
            sleep(.5)
        driver.close()
        for picture in source:
            i = picture.rfind("original/") + 9
            target[key].append((picture[i:], False))
            fname = picture[picture.rfind('/') + 1:]
            req.urlretrieve(picture, f"./LSP/{encode_filename(key)}/NR/{fname}")
            pbar.update(1)

    def rematch_pixiv(self, key: str, value: tuple[str, bool], pbar: tqdm, target: dict):
        pic_id, r18 = value
        driver = Crawler.init_webdriver(self.config, self.headless, True)
        driver.maximize_window()
        driver.get(self.picture_base_url + pic_id)
        WebDriverWait(driver, 10).until(ec.presence_of_all_elements_located(("xpath", "//figure//img")))
        expand_btn = driver.find_elements("xpath", "//div[4]//button/div[2]")
        if expand_btn != []:
            expand_btn[0].click()
            sleep(.5)
        Crawler.scroll(driver)
        pic_elems = driver.find_elements("xpath", "//figure//img")
        source = []
        for elem in pic_elems:
            elem.click()
            WebDriverWait(driver, 10).until(ec.presence_of_element_located(("xpath", "//div/div[1]/div/img")))
            picture_elem = driver.find_element("xpath", "//div/div[1]/div/img")
            source.append(picture_elem.get_attribute("src"))
            picture_elem.click()
            sleep(.5)
        driver.close()
        for picture in source:
            i = picture.rfind("img/") + 4
            target[key].append((picture[i:], r18))
            fname = picture[picture.rfind('/') + 1:]
            req.urlretrieve(picture, 
                f"./LSP/{encode_filename(key)}/NR/{fname}" if not r18 else f"./LSP/{encode_filename(key)}/R/{fname}"
            )
            pbar.update(1)
            
    def rematches(self, pbar: tqdm, target: dict):
        rematch = self.rematch_native if self.mirror else self.rematch_pixiv
        StrFormat.info("Fixing downloads with WebDriver...")
        self.unavail = self.find_unavail()
        start = perf_counter()
        with ThreadPoolExecutor(max_workers=4) as pool:
            for key, values in self.unavail.items():
                for value in values:
                    if self.config['browser'] == 'firefox':
                        pool.submit(rematch, key, value, pbar, target)
                    else:
                        rematch(key, value, pbar, target)
            pool.shutdown()
        end = perf_counter()
        pbar.close()
        print(
            f"{StrFormat.functional('Fixing')} completed in {StrFormat.time_str(end - start)}."
        )
