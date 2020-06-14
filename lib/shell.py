import os, sys, json, logging, tabulate
from lib import env

class Shell(object):
    """
    """

    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter(fmt="%(asctime)s :: %(message)s", datefmt="%H:%M:%S")

        try:
            handler = logging.FileHandler(env.logs_path, mode="a", encoding="utf-8")
            handler.setLevel(logging.INFO)
            handler.setFormatter(formatter)
            handler.suffix = "%Y-%m-%d"
        except IOError as err:
            print(err)
            sys.exit()

        self.logger.addHandler(handler)

        try:
            with open(env.settings_path, "r") as fs:
                self.settings = json.loads(fs.read())
        except (IOError, json.JSONDecodeError) as err:
            self.logger.error(err)
            sys.exit()

    def help(self, commands):
        """
        """

        if len(commands) > 0:
            headers = ["Name","Description","Usage"]
            table = [ [self.settings["commands"][_]["name"],
                       self.settings["commands"][_]["description"],
                       self.settings["commands"][_]["usage"]]
                       for _ in commands[1:] if _ in self.settings["commands"].keys() ]
            print(tabulate.tabulate(table, headers=headers))
        else:
            output = "Following commands are available: \n" + ", ".join([_ for _ in self.settings["commands"].keys()])
            print(output)

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

        try:
            print("Version: " + self.settings["version"])
        except KeyError as err:
            output = "KeyError: " + str(err) + " not found in " + env.settings_path
            self.logger.error(output)
            print(output)
