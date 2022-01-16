from selenium.common.exceptions import TimeoutException
from crawler import Crawler
from downloader import Downloader
from urllib import request as req
from urllib import error
from strformat import StrFormat
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
class PixivCrawler(Crawler):
    def check_status(self):
        try:
            StrFormat.info("Checking proxy...")
            req.urlopen("https://www.google.com", timeout=10)
            StrFormat.ok("Proxy available.")
        except error.URLError:
            StrFormat.severe_warning("Foreign website not reachable. Configure your proxy first.")
            exit(1)
        StrFormat.info("Checking login status...")
        driver = Crawler.init_webdriver(self.config, True)
        driver.set_page_load_timeout(10)
        try:
            driver.get("https://www.pixiv.net/")
        except TimeoutException:
            pass
        elems = driver.find_elements("xpath", "//div[3]/div[2]/a[2]")
        if elems != []:
            StrFormat.severe_warning("Pixiv not signed in. Sign in with your configured profile once first.")
            driver.close()
            exit(1)
        driver.close()
        StrFormat.ok("Profile available for auto-login in Pixiv.")

    def __init__(self, runtime: dict) -> None:
        super().__init__(runtime)
        self.check_status()
        self.illust_url_base = self.config["format"]["pixiv"]["illustrator"]
        self.pic_url_base = self.config["format"]["pixiv"]["origin"]

    def map(self, id: str):
        Downloader.fake()
        try:
            response = req.urlopen(self.illust_url_base + id)
            page = bytes.decode(response.read())
            start = page.find("<title>") + 7
            end = page.find(" - pixiv")
            self.illusts[id] = page[start:end]
        except error.HTTPError:
            StrFormat.severe_warning(f"Illustrator ID {id} not found.")
    
    def expand(self, key: str, value: str, num: int, r18: bool):
        res = []
        for i in range(num):
            res.append((f"{self.pic_url_base}{value}_p{i}.jpg", r18))
            res.append((f"{self.pic_url_base}{value}_p{i}.png", r18))
        if key not in self.pictures:
            self.pictures[key] = res
        else:
            self.pictures[key].extend(res)
    
    def get(self, id: str, name: str):
        driver = Crawler.init_webdriver(self.config, self.headless, True)
        driver.maximize_window()
        ind = 1
        total = 0
        while True:
            print(f"Getting {name}'s pictures. Page {ind}...")
            driver.get(f"{self.illust_url_base}{id}/artworks?p={ind}")
            try:
                WebDriverWait(driver, 15).until(ec.presence_of_all_elements_located(("xpath", "//div[3]/div[1]//li[1]//a//img")))
                driver.save_screenshot("./test.png")
            except TimeoutException:
                break
            Crawler.scroll(driver)
            pic_elems = driver.find_elements("xpath",  "//div[3]/div[1]//a//img")
            # "string(//li[x]//div/span[2])"
            series = []
            isr18 = []
            for i, _ in enumerate(pic_elems):
                s = driver.find_elements("xpath", f"//li[{i+1}]//div/span[2]")
                if s == []:
                    series.append(1)
                else:
                    series.append(int(s[0].text))
                r = driver.find_elements("xpath", f"//li[{i+1}]//div[1]/div//div/div/div/div")
                if r != []:
                    isr18.append(True)
                else:
                    isr18.append(False)
            for pic, num, r18 in zip(pic_elems, series, isr18):
                pic = pic.get_attribute("src")
                start = pic.find("img/") + 4
                end = pic.rfind("_p")
                pic = pic[start:end]
                self.expand(f"{id} {name}", pic, num, r18)
                if self.cap and total > self.cap:
                    break
                total += 1
            if self.cap and total > self.cap:
                break
            ind += 1
        driver.close()
        StrFormat.info(f"Crawling completed for {StrFormat.cstr(name, style='BOLD', fcolor='CYAN')}.")
