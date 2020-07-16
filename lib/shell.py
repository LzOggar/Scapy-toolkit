import os
import re
import sys
import json
import logging
import ipaddress 

try:
    import tabulate
    from lib import env
    from lib import net
except ImportError as err:
    print(err)
 
class Shell(object):
    """
    """

    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter(fmt="%(asctime)s :: %(message)s", datefmt="%H:%M:%S")

        try:
            handler = logging.FileHandler(env.shell_logs_path, mode="a", encoding="utf-8")
            handler.setLevel(logging.INFO)
            handler.setFormatter(formatter)
            handler.suffix = "%Y-%m-%d"
        except IOError as err:
            print(err)
            sys.exit()

        self.logger.addHandler(handler)

        try:
            with open(env.shell_settings_path, "r") as fs:
                self.settings = json.loads(fs.read())
        except (IOError, json.JSONDecodeError) as err:
            self.logger.error(err)
            sys.exit()

        self.ifs = " "
        self.status = False
        self.result = {}

    def run(self):
        """
        """

        regex = re.compile(self.ifs)
        self.status = True

        while self.status:
            try:
                commands = input(self.settings["prompt"])
                if len(commands) > 0:
                    parsed_commands = regex.split(commands)
                    if parsed_commands[0] == "set":
                        if len(parsed_commands[1:]) == 2:
                            self.set(parsed_commands[1], parsed_commands[2])
                        else:
                            print("Invalid command. Please, find following \"help\".")
                            self.help(["set"])
                    elif parsed_commands[0] == "scan":
                        self.result = {}
                        if len(parsed_commands[1:]) == 1:
                            if net.is_valid_target(parsed_commands[1]):
                                target = list(ipaddress.ip_network(parsed_commands[1]).hosts())

                                if len(target) == 0:
                                    self.scan([parsed_commands[1]])
                                else:
                                    self.scan([str(v) for v in target])
                            else:
                                print("Invalid command. Please, find following \"help\".")
                                self.help(["scan"])
                        elif len(parsed_commands[1:]) == 2:
                            self.set("scan_type", parsed_commands[1])
                            if net.is_valid_target(parsed_commands[2]):
                                target = list(ipaddress.ip_network(parsed_commands[2]).hosts())

                                if len(target) == 0:
                                    self.scan([parsed_commands[2]])
                                else:
                                    self.scan([str(v) for v in target])
                            else:
                                print("Invalid command. Please, find following \"help\".")
                                self.help(["scan"])
                        else:
                            print("Invalid command. Please, find following \"help\".")
                            self.help(["scan"])
                    elif parsed_commands[0] == "get":
                        self.get(parsed_commands[1:])
                    elif parsed_commands[0] == "help":
                        self.help(parsed_commands[1:])
                    elif parsed_commands[0] == "version":
                        self.version()
                    elif parsed_commands[0] == "clear":
                        self.clear()
                    elif parsed_commands[0] == "exit":
                        self.exit()
                    elif parsed_commands[0] == "history":
                        print("Command under development.")
                    else:
                        print("Invalid command. Type \"help\" for more informations.")
            except KeyboardInterrupt:
                self.exit()

    def set(self, key, value):
        """
        """

        try:
            env.var_sets[key]["default"] = env.var_sets[key][value] if value != "default" else env.var_sets[key]["default"]
            print("{}.default={}".format(key, env.var_sets[key]["default"]))
        except KeyError:
            print("Invalid command. Please, find following \"help\".")
            self.help(["set"])

    def get(self, keys):
        """
        """

        if len(keys) > 0:
            headers = ["Vars","Values","Defaults"]
            table = [ [_,
                       "\n".join([k for k in env.var_sets[_].keys() if k != "default"]),
                       env.var_sets[_]["default"]]
                       for _ in keys if _ in env.var_sets.keys() ]
        else:
            headers = ["Vars","Values","Defaults"]
            table = [ [_,
                       "\n".join([k for k in env.var_sets[_].keys() if k != "default"]),
                       env.var_sets[_]["default"]]
                       for _ in env.var_sets.keys() ]

        print(tabulate.tabulate(table, headers=headers))

    def scan(self, target):
        """
        """

        threads = []
        if env.var_sets["scan_type"]["default"] == "icmp":
            start = time.process_time()

            print("Scanning ...")
            for _ in target:
                thread = net.ICMPThread(_, self.result)
                thread.start()
                threads.append(thread)

            while any([ _.is_alive() for _ in threads]):
                pass
            print("Scan done.")

            elapsed_time = time.process_time() - start
            up,down = 0,0  

            for v in self.result.values():
                if v == "up": 
                    up += 1
                else:
                    down += 1 

            output = "Targets: {0}/{2} (up) {1}/{2} (down) Elapsed time: {3} (s)".format(str(up),str(down),str(len(target)),str(elapsed_time))
            self.print_result()

            print("")
            print("-"*len(output))
            print(output)
        elif env.var_sets["scan_type"]["default"] == "tcp-syn":
            pass
        else:
            pass

    def print_result(self):
        """
        """

        i = 0
        headers = [ "Targets", "States"]
        table = [ [ k,v ] for k,v in self.result.items() ]

        print(tabulate.tabulate(table, headers=headers))

    def help(self, commands):
        """
        """

        if len(commands) > 0:
            headers = ["Names","Descriptions","Usages","Examples"]
            table = [ [self.settings["commands"][_]["name"],
                       self.settings["commands"][_]["description"],
                       self.settings["commands"][_]["usage"],
                       "\n".join([ v for v in self.settings["commands"][_]["examples"].values()])]
                       for _ in commands if _ in self.settings["commands"].keys() ]
        else:
            headers = ["Names","Descriptions","Usages","Examples"]
            table = [ [self.settings["commands"][_]["name"],
                       self.settings["commands"][_]["description"],
                       self.settings["commands"][_]["usage"],
                       "\n".join([ v for v in self.settings["commands"][_]["examples"].values()])]
                       for _ in self.settings["commands"].keys() ]

        print(tabulate.tabulate(table, headers=headers))

    def clear(self):
        """
        """

        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")

    def version(self):
        """
        """

        print("Version: {}".format(self.settings["version"]))

    def exit(self):
        """
        """

        self.status = False