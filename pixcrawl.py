import json
from cli import CLI
from sys import argv
import os
from database import Database
from doujin import Doujin
from downloader import Downloader
from native_crawler import NativeCrawler
from time import perf_counter
from pixiv_crawler import PixivCrawler
from strformat import StrFormat
import warnings


class PixCrawl:
    def __init__(self, cli: CLI, startup: str) -> None:
        self.startup = startup
        self.config = json.load(open(startup))
        self.runtime = cli.runtime
        if "profile" in self.runtime.keys():
            self.set_profile()
        elif "browser" in self.runtime.keys():
            self.set_browser()
        elif "r18" in self.runtime.keys():
            self.set_r18()
        elif "mode" in self.runtime.keys():
            if "mirror" in self.runtime.keys():
                self.get_mirror()
            else:
                self.get_pixiv()
        elif "doujin" in self.runtime.keys():
            self.get_doujin()
    
    def set_profile(self):
        browser, profile = self.runtime["profile"]
        if browser not in ['chrome', 'edge', 'firefox']:
            StrFormat.severe_warning(f"Specified browser {browser} is not supported.")
            StrFormat.info(f"Supported browser: chrome, edge and firefox.")
            exit(1)
        if not os.path.isdir(profile):
            StrFormat.severe_warning(f"Specified path {profile} does not exist.")
            exit(1)
        if browser not in self.config.keys():
            StrFormat.severe_warning(f"Specified browser {browser} is not supported.")
            exit(1)
        self.config[browser]["profile"] = profile
        json.dump(self.config, open(self.startup, 'w'), indent=4)

    def set_browser(self):
        browser = self.runtime["browser"][0]
        if browser not in ['edge', 'chrome', 'firefox']:
            StrFormat.severe_warning(f"Specified browser {browser} is not supported.")
            StrFormat.info(f"Supported browser: chrome, edge and firefox.")
            exit(1)
        self.config["browser"] = browser
        json.dump(self.config, open(self.startup, 'w', encoding='utf-8'), indent=4)
    
    def set_r18(self):
        r18 = self.runtime["r18"][0]
        match r18:
            case "true":
                r18 = True
            case "false":
                r18 = False
            case _:
                StrFormat.severe_warning(f"Specified r18 config {r18} is not supported.")
                StrFormat.info(f"Argument --r18 can only accept 'true' or 'false'.")
                exit(1)
        self.config["r18"] = r18
        json.dump(self.config, open(self.startup, 'w'), indent=4)
    
    def get_mirror(self):
        if self.runtime["mode"] in ['g', 'd']:
            crawler = NativeCrawler(self.runtime)
            crawler.maps()
            crawler.gets()
            downloader = Downloader(crawler.pictures, self.runtime, True)
            downloader.recover()
            avail_pictures = downloader.downloads(downloader.pictures)
            if self.runtime["mode"] == 'd':
                dtb = Database(avail_pictures, True)
                dtb.write_map()
                dtb.write_url()
    
    def get_pixiv(self):
        if self.runtime["mode"] in ['g', 'd']:
            crawler = PixivCrawler(self.runtime)
            crawler.maps()
            crawler.gets()
            downloader = Downloader(crawler.pictures, self.runtime, False)
            downloader.recover()
            avail_pictures = downloader.downloads(downloader.pictures)
            if self.runtime["mode"] == 'd':
                dtb = Database(avail_pictures, False)
                dtb.write_map()
                dtb.write_url()

    def get_doujin(self):
        dj = Doujin(self.config, self.runtime)
        dj.searches()
        dj.downloads()


if __name__ == "__main__":
    warnings.filterwarnings("ignore",category=DeprecationWarning)
    start = perf_counter()
    PixCrawl(CLI(argv, "args.json"), "startups.json")
    end = perf_counter()
    StrFormat.ok(f"Program successfully finished in {StrFormat.time_str(end - start)}.")
    exit(0)