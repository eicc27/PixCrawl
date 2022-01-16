from concurrent.futures import ThreadPoolExecutor
import os
from time import perf_counter
from crawler import Crawler
from strformat import StrFormat
from urllib import request as req
from urllib import error, parse
from tqdm import tqdm
from fake_useragent import UserAgent
from lxml import etree
import socket

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
        socket.setdefaulttimeout(10)
        Doujin.check()
        self.headless = "headless" in runtime.keys()
        self.config = config
        self.base_site, self.alt_site = self.config['doujin']
        self.keywd: list[str] = runtime['doujin']
        self.cap = Crawler.get_cap(runtime)
        self.targets = {}
        self.total = 0
        self.make_dirs()
    
    @staticmethod
    def encode_filename(fname: str):
        return fname.replace('?', '')
    
    @staticmethod
    def fake():
        headers = [('User-Agent', UserAgent(path="fake_headers.json").random),
                    ('Referer', 'http://ddd-smart.net')]
        opener = req.build_opener()
        opener.addheaders = headers
        req.install_opener(opener)

    def search(self, kwd: str, type=2):
        Doujin.fake()
        page_index = 1
        pages = 1
        num = 0
        self.targets[kwd] = []
        while page_index <= pages:
            print(f"Getting {kwd}'s targets. Page{page_index}...")
            webp = req.urlopen(f"http://ddd-smart.net/list.php?type={type}&keyword={parse.quote(kwd)}&sort_key=2&page={page_index}")
            webp = webp.read().decode('utf-8')
            webp = etree.HTML(webp)
            urls = webp.xpath('//ul[3]/li/div[1]//@src')
            titles = []
            for i, _ in enumerate(urls):
                titles.append(webp.xpath(f'string(//ul[3]/li[{i+1}]/div[2]/h2)'))
            # http://cdn.ddd-smart.net/20220102/002/thumbnail.jpg
            # http://cdn.ddd-smart.net/20220102/002/all.pdf
            for url, title in zip(urls, titles):
                self.targets[kwd].append(
                    (url.replace('thumbnail.jpg', 'all.pdf'), title)
                )
                num += 1
                self.total += 1
                if self.cap and num >= self.cap:
                    break
            if self.cap and num >= self.cap:
                    break
            if page_index == 1:
                total = int(webp.xpath('string(//div[1]/div[1]/p/span[1])'))
                pages = int(total / 30) + 1
            page_index += 1
        print(f"Crawling completed for {StrFormat.cstr(kwd, style='BOLD', fcolor='CYAN')}.")
        
    def searches(self):
        start = perf_counter()
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

    def download(self, kwd: str, src: tuple, pbar: tqdm, retry=0):
        if retry > 2:
            StrFormat.severe_warning(f"\nMax retries({retry}) reached for {src[0]}. Aborted.")
            return
        url, title = src
        Doujin.fake()
        try:
            req.urlretrieve(url, f"./True_LSP/{kwd}/{Doujin.encode_filename(title)}.pdf")
            pbar.update(1)
        except OSError:
            self.download(kwd, src, pbar, retry + 1)
        
    
    def downloads(self):
        pbar = tqdm(total=self.total)
        start = perf_counter()
        with ThreadPoolExecutor(max_workers=8) as pool:
            for kwd, srcs in self.targets.items():
                for src in srcs:
                    pool.submit(self.download, kwd, src, pbar)
        pbar.close()
        end = perf_counter()
        print(f"{StrFormat.functional('Downloading')} completed for {StrFormat.time_str(end-start)}.")