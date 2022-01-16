from json import loads
from crawler import Crawler
import urllib.request as req
from time import perf_counter, sleep
from strformat import StrFormat

class NativeCrawler(Crawler):
    def __init__(self, runtime: dict) -> None:
        super().__init__(runtime)
        self.illust_url_base = self.config["format"]["mirror"]["illustrator"]
        self.pic_url_base = self.config["format"]["mirror"]["origin"]

    def map(self, id: str):
        response = req.urlopen(self.illust_url_base + id)
        page = bytes.decode(response.read())
        start = page.find("<title>") + 7
        end = page.find(" - p站")
        if page[start: start + 2] == "p站":
            StrFormat.severe_warning(f"Illustrator ID {id} not found.")
            return
        self.illusts[id] = page[start:end]
    
    def expand(self, key: str, value: str, num: int):
        res = []
        for i in range(num):
            res.append((f"{self.pic_url_base}{value}_p{i}.jpg", False))
            res.append((f"{self.pic_url_base}{value}_p{i}.png", False))
        if key not in self.pictures:
            self.pictures[key] = res
        else:
            self.pictures[key].extend(res)
        
    def get(self, id: str, name: str):
        limit = 30
        offset = 0
        total = 0
        while True:
            webp = req.urlopen(f"https://www.vilipix.com/api/illust?user_id={id}&limit={limit}&offset={offset}")
            webp_json = loads(webp.read().decode('utf-8'))['rows']
            if webp_json == []:
                break
            for row in webp_json:
                num = row['page_count']
                regular_url = row['regular_url']
                start = regular_url.find("regular/") + 8
                end = regular_url.rfind("_p") 
                self.expand(f"{id} {name}", regular_url[start:end], num)
                if self.cap and total >= self.cap:
                    break
                total += 1
            if self.cap and total >= self.cap:
                break
            offset += 30
    
    def gets(self):
        start = perf_counter()
        for id, name in self.illusts.items():
            print(f"Getting {name}'s pictures...")
            self.get(id, name)
        end = perf_counter()
        print(f"{StrFormat.functional('Crawling')} completed in {StrFormat.time_str(end-start)}.")
    