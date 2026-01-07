# Copyright 2021 Pants project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

import os
import sys
from pathlib import PurePath

from core.discovery import get_dev_port


class Service:
    def __init__(self, name_or_file: str):
        if os.path.sep in name_or_file:
            # This is the __file__ of the caller, so compute the service name.
            rparts = list(reversed(PurePath(name_or_file).parts))
            self._name = ".".join(reversed(rparts))
            print(f"{rparts=}\n{self._name=}")
        else:
            self._name = name_or_file

    def hello(self, settings):
        from pyfiglet import Figlet
        from termcolor import colored

        service_path = self._name.split(".")
        print(f"{service_path=}")
        service = "quiz"
        f = Figlet(font="standard")
        print(colored(f.renderText(f"{service}"), "green"))

        version = settings.__VERSION__
        mode = settings.__APP_MODE__
        print(colored(f"{mode}-{version}", "yellow"))

    def run_daphne(self):
        # from phoenix.asgi import GunicornApplication
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{self._name}.settings")
        print(f"==> {self._name}.settings")
        from daphne.cli import CommandLineInterface
        from django.conf import settings

        # self.hello(settings)
        args = ["-p", "8070", "-b", "0.0.0.0", "core.asgi:app"]

        # Run the Daphne server
        sys.exit(CommandLineInterface().run(args))

    def run_server(self):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{self._name}.settings")
        args = sys.argv

        print(f"{sys.argv=} || {sys.argv}")

        if len(sys.argv) > 1:
            from django.core.management import execute_from_command_line

            execute_from_command_line(args)
        else:
            self.run_daphne()
