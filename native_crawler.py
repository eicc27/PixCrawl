from crawler import Crawler
import urllib.request as req
from time import sleep
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
        driver = Crawler.init_webdriver(self.config, self.headless)
        driver.maximize_window()
        i = 1
        total = 0
        while True:
            print(f"Getting {name}'s pictures. Page {i}...")
            driver.get(f"{self.illust_url_base}{id}?p={i}")
            sleep(1)
            Crawler.scroll(driver)
            pic_elems = driver.find_elements("xpath", "//li//img")
            if pic_elems == []:
                break
            series = driver.find_elements("xpath", "//li//a//span")
            for pic, num in zip(pic_elems, series):
                pic = pic.get_attribute("src")
                if pic.find("img-error") >= 0:
                    continue
                start = pic.find("regular/") + 8
                end=pic.rfind("_p")
                pic = pic[start:end]
                num = num.get_attribute("innerHTML")
                num = int(num)
                self.expand(f"{id} {name}", pic, num)
                total += 1
                if self.cap and total > self.cap:
                    break
            if self.cap and total > self.cap:
                    break        
            i += 1
        driver.close()
        StrFormat.info(f"Crawling completed for {StrFormat.cstr(name, style='BOLD', fcolor='CYAN')}.")