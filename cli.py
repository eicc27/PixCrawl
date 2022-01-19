import json

from strformat import StrFormat


class CLI:
    '''
    If a new function is specified, change the code in the match...case block of map_runtime.
    '''

    def __init__(self, args: list[str], config: str) -> None:
        self.runtime = {}
        self.args = args[1:]
        self.avail_args: dict[str, dict] = json.load(open(config, 'r'))
        self.keys = self.avail_args_keys()
        self.alias = {}
        self.map_alias()
        self.parsed_args: list[list] = self.parse()
        self.map_runtime()

    def avail_args_keys(self):
        res = []
        for key in self.avail_args.keys():
            res.append(key)
            if "alias" in self.avail_args[key].keys():
                res.append(self.avail_args[key]["alias"])
        return res

    def map_alias(self):
        for key in self.avail_args.keys():
            if "alias" in self.avail_args[key]:
                self.alias[self.avail_args[key]["alias"]] = key

    def parse(self):
        functional = []
        for key in self.avail_args.keys():
            if "father" not in self.avail_args[key].keys():
                functional.append(key)
        is_functional = []
        ind = 0
        parsed_args = []
        args_len = len(self.args)
        while(ind < args_len):
            origin = self.args[ind]
            if origin in self.alias.keys():
                origin = self.alias[origin]
            if "n" not in self.avail_args[origin].keys():
                ind += 1
                continue
            elif origin not in self.avail_args.keys():
                print(
                    f"Command {origin} could not be found. Type -h for help.")
                exit(1)
            if "father" not in self.avail_args[origin].keys():
                is_functional.append(True)
            if "father" in self.avail_args[origin].keys():
                f = False
                for father in self.avail_args[origin]["father"]:
                    if "alias" in self.avail_args[father]:
                        father_alias = self.avail_args[father]["alias"]
                        if father_alias in self.args:
                            f = True
                            break
                    if father in self.args:
                        f = True
                        break
                if not f:
                    print(
                        f"Command {origin} does not have an available dependent. Type -h for help.")
                    print(
                        f"It must be coupled with one of the following functional arguments: {self.avail_args[origin]['father']}")
                    exit(1)
            bias = 1
            while ind + bias < args_len and self.args[ind + bias] not in self.keys:
                bias += 1
            parsed_args.append(self.args[ind: ind + bias])
            ind += bias
        if len(is_functional) > 1:
            print("Multiple commands are specified. Run them one by one.")
            exit(1)
        if not len(is_functional):
            print("No functional commands specified. Type -h for help.")
            exit(1)
        return parsed_args

    def print_help(self):
        for key in self.avail_args.keys():
            print(f"{key}:")
            if "alias" in self.avail_args[key]:
                print(f"\talias: {self.avail_args[key]['alias']}")
            if "father" in self.avail_args[key]:
                print(f"\tdependencies:{self.avail_args[key]['father']}")
            print(f"\t{self.avail_args[key]['desc']}")
            req_args = self.avail_args[key]['n']
            if req_args < 0:
                req_args = "at least 1, no cap"
            elif req_args == 0:
                req_args = "no arguments"
            print(f"\trequired number of arguments: {req_args}")
            if "type" in self.avail_args[key]:
                print(
                    f"\taccepted argument type: {self.avail_args[key]['type']}")

    def map_runtime(self):
        for parsed_arg in self.parsed_args:
            arg_name = parsed_arg.pop(0)
            if arg_name in self.alias.keys():
                arg_name = self.alias[arg_name]
            if arg_name not in self.keys:
                print(f"Invalid argument {arg_name}.")
                exit(1)
            if self.avail_args[arg_name]['n'] >= 0 and len(parsed_arg) != self.avail_args[arg_name]['n']:
                print(f"Invalid parameter number for {arg_name}.")
                print(f"Given number is {len(parsed_arg)}.")
                print(
                    f"It requires {self.avail_args[arg_name]['n']} param(s).")
                exit(1)
            elif self.avail_args[arg_name]['n'] < 0 and len(parsed_arg) < 1:
                print(f"At least one parameter for {arg_name} is needed.")
                exit(1)
            match arg_name:
                case "-g" | "--get":
                    self.runtime["mode"] = "g"
                    self.runtime["illusts"] = parsed_arg
                case "-d" | "--database":
                    self.runtime["mode"] = "d"
                    self.runtime["illusts"] = parsed_arg
                case "-m" | "--mirror":
                    self.runtime["mirror"] = True
                case "--headless":
                    self.runtime["headless"] = True
                case "--profile":
                    self.runtime["profile"] = parsed_arg
                case "--browser":
                    self.runtime["browser"] = parsed_arg
                case "--r18":
                    self.runtime["r18"] = parsed_arg
                case "--doujin":
                    self.runtime["doujin"] = parsed_arg
                case "--cap":
                    self.runtime["cap"] = parsed_arg
                case "-h" | "--help":
                    self.print_help()
                    exit(0)

    def debug(self):
        print(self.runtime)
