import os
from downloader import encode_filename


class Database:
    def __init__(self, pictures: dict, mirror: bool) -> None:
        self.pictures = pictures
        self.mirror = mirror
        self.mk_dtbdir()
    
    def mk_dtbdir(self):
        if not os.path.exists("./data"):
            os.mkdir("./data")
        for key in self.pictures.keys():
            fname = f"./data/{encode_filename(key)}"
            if not os.path.exists(fname):
                os.mkdir(fname)
                os.mkdir(f"{fname}/pixiv")
                os.mkdir(f"{fname}/mirror")
    
    def write_map(self):
        f = open("./data/illust.csv", 'a+')
        current = Database.get_key("./data/illust.csv")
        if "id" not in f.readline():
            f.write("id, name\n")
        for key in self.pictures.keys():
            sep_loc = key.find(' ')
            id = key[:sep_loc]
            if id in current:
                continue
            name = key[sep_loc + 1:]
            f.write(f"{id}, {name}\n")
        f.close()
    
    def write_url(self):
        for key, values in self.pictures.items():
            fname = f"./data/{encode_filename(key)}/mirror/url.csv"  if self.mirror else f"./data/{encode_filename(key)}/pixiv/url.csv"
            f = open(fname, 'a+')
            current = Database.get_key(fname)
            if "url" not in f.readline():
                f.write("url, r18, fmt\n")
            for value in values:
                url, r18 = value
                if url in current:
                    continue
                fmt = url[-3:]
                start = url.find('original/') + 9 if self.mirror else url.find('img/') + 4
                end = url.rfind('.')
                url = url[start:end]
                f.write(f"{url}, {r18}, {fmt}\n")
            f.close()

    @staticmethod
    def get_key(fname):
        f = open(fname, 'r')
        res = f.readlines()[1:]
        for i, r in enumerate(res):
            res[i] = r[:r.find(',')]
        f.close()
        return res
