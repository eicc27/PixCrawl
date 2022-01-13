from os import stat


STYLE = {
    "DEFAULT": 0,
    "BOLD": 1,
    "UNDERLINE": 4,
    "REVERSE": 7
}
FCOLOR = {
    "BLACK": 30,
    "RED": 31,
    "GREEN": 32,
    "YELLOW": 33,
    "BLUE": 34,
    "MAGENTA": 35,
    "CYAN": 36,
    "WHITE": 37
}
BCOLOR = {
    "BLACK": 40,
    "RED": 41,
    "GREEN": 42,
    "YELLOW": 43,
    "BLUE": 44,
    "MAGENTA": 45,
    "CYAN": 46,
    "WHITE": 47
}


class StrFormat:
    @staticmethod
    def cstr(s: str, style="", fcolor="", bcolor=""):
        if style != '':
            style = STYLE[style]
        if fcolor != '':
            fcolor = FCOLOR[fcolor]
        if bcolor != '':
            bcolor = BCOLOR[bcolor]
            return f"\033[{style};{fcolor};{bcolor}m{s}\033[0m"
        else:
            return f"\033[{style};{fcolor}m{s}\033[0m"

    @staticmethod
    def ok(s: str):
        msg = StrFormat.cstr("√", style="UNDERLINE", fcolor="GREEN")
        return print(StrFormat.cstr(f"{s}\t", style="DEFAULT", fcolor="GREEN") + msg)

    @staticmethod
    def info(s: str):
        return print(StrFormat.cstr(s, style="DEFAULT", fcolor="BLUE"))

    @staticmethod
    def warning(s: str):
        msg = StrFormat.cstr("!", style="UNDERLINE", fcolor="YELLOW")
        return print(StrFormat.cstr(f"{s}\t", style="DEFAULT", fcolor="YELLOW") + msg)

    @staticmethod
    def severe_warning(s: str):
        msg = StrFormat.cstr("×", style="UNDERLINE", fcolor="MAGENTA")
        return print(StrFormat.cstr(f"{s}\t", style="DEFAULT", fcolor="MAGENTA") + msg)

    @staticmethod
    def mapping(l1: list[str], l2: list[str]):
        for s1, s2 in zip(l1, l2):
            s1 = StrFormat.cstr(s1, fcolor="CYAN")
            s2 = StrFormat.cstr(s2, fcolor="RED")
            print(f"{s1} ====> {s2}")

    @staticmethod
    def time_str(time: float):
        if time > 60:
            time = int(time)
            secs = time % 60
            mins = int((time - secs) / 60)
            if secs == 0:
                res = f"{mins} minutes" if mins != 1 else f"{mins} minute"
            else:
                res = f"{mins} minutes {secs} seconds" if mins != 1 else f"{mins} minute {secs} seconds"
        else:
            res = f"{'%.1f' % time} seconds"
        return StrFormat.cstr(res, style="BOLD", fcolor="BLUE")
    
    @staticmethod
    def functional(s: str):
        return StrFormat.cstr(s, style="UNDERLINE", fcolor="CYAN")

    @staticmethod
    def query(s: str):
        print(s, end=StrFormat.cstr("\t>?", style="BOLD", fcolor="BLUE"))
        return input("\b")
