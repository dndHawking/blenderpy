"""
Zero Dependecy Abstraction Layer to run Python scripts in Blender.
"""
from __future__ import annotations
from argparse import ArgumentParser
from sys import argv
from subprocess import Popen, PIPE, STDOUT
from tempfile import TemporaryDirectory
from typing import Any, Dict, Iterable, String, List
from urllib import request
from json import loads

# ToDo; provide option to use the official Blender Module instead of the Blender Binary.
# https://github.com/TylerGubala/blenderpy


class Blender:

    """
    Run Blender specific Python scripts.

    ```py
    B = Blender()
    B.run("generate")  # Construct will add '.py'
    ```

    ```bash
    python -m blender path/to/generate(.py)
    ```
    """

    def __init__(self, app: String = "blender") -> Blender:
        """
        Set the `path` parameter to the executable if you have not
        set the PATH variable on your machine. Otherwise the default
        will suffice.

        Args:
            path (str): The path to the Blender executable.
            allow_gist (bool): Allow the programmatic access of gists.

        Returns:
            Blender Object
        """
        self.app = app

    def terminal(self, cmd: String, **kwargs) -> String:
        """Run a Terminal command using popen.

        Args:
            cmd (str): The command to run.
            kwargs (dict): Keyword arguments to pass to the `Popen` object.

        Returns:
            The terminal output.
        """
        return (
            Popen(
                cmd,
                shell=kwargs.get("shell", True),
                stdin=kwargs.get("stdin", PIPE),
                close_fds=kwargs.get("close_fds", True),
                stdout=kwargs.get("stdout", PIPE),
                stderr=kwargs.get("stderr", STDOUT),
            )
            .stdout.read()
            .decode("utf8")
        )

    def speak(self, text: String | Iterable) -> None:
        """Print/Logging wrapper. Allowing quick and easy
        customizations.

        Args:
            text (str): The information to print/log
        """
        if isinstance(text, Iterable):
            if not any((isinstance(word, str) for word in text)):
                raise ValueError("I only use strings.")
            shout = " ".join(text)
        else:
            shout = text

        print(shout)

    def get_gist(self, gid: String) -> Dict[str, str]:
        """Download a Gist from GitHub.

        Args:
            gid (str): The UUID for your Gist.

        Returns:
            Dict[str, str]: The retrieved JSON from GitHub.
        """
        base_url = "https://api.github.com/gists/"

        with request.urlopen(base_url + str(gid)) as client:
            return loads(client.read().decode("utf-8"))

    def extract_dict_value(
        self, data: Dict[str, Any], keys: String | List[String]
    ) -> String | None:
        """Recursively get the dictionary values from an arbitrarily long keys list."""
        if data is None:
            return None

        elif isinstance(keys, str):
            return data.get(keys, None)

        return self.extract_dict_value(data.get(keys[0]), keys[1:])

    def run(
        self,
        script: String | None = None,
        binary: String | None = None,
        *args,
        **kwargs,
    ) -> String:
        """
        Run a Python script in Blender.

        Args:
            script (str): The location of your script. Either path or gist id.
            gist (str): Gist UUID to apply.
            binary (str): The Blender binary. Allocated during Object construction.
            args (iterable): All Python arguments to pass into the script.
                        Should contain one command per string,
                        formatted like: '-a myfile.txt'
            kwargs (dict): Optional Blender settings

        Returns:
            String: Terminal output after running the blender command.
        """
        if binary is not None:
            self.app = binary

        if script is not None:
            if ".py" not in script:
                script += ".py"
        else:
            raise ValueError("Provide either a local or external (gist) script source.")

        gui = "-b" if kwargs.get("headless", True) else ""
        runtime = "-P" if kwargs.get("python", True) else ""
        audio = "-noaudio" if not kwargs.get("audio", False) else ""
        python_args = " ".join(args)

        return self.terminal(
            f"{self.app} {audio} {gui} {runtime} {script} -- {python_args}"
        )

    def run_gist(
        self, gid: String, content: String | Iterable | None = None, **kwargs
    ) -> str:
        """Run a Python Blender script directly from a GitHub gist source.

        Args:
            gid (str): UUID of the desired Gist from GitHub.
            content (...): The target content to use in Blender.
            kwargs (dict): Any kwargs you wish to pass into TempDir.

        Returns:
            String: the terminal output after Blender closed.
        """
        with TemporaryDirectory(**kwargs) as temp:

            gist = self.get_gist(gid)
            fp = f"{temp}/{gid}"

            if content is None:
                text = gist
            elif isinstance(content, str):
                text = gist.get(content, None)
            elif isinstance(content, Iterable):
                text = self.extract_dict_value(gist, content)

            if text is None:
                raise ValueError(f"Could not find any content under {content}.")

            with open(fp, "r") as opened:
                opened.writelines(text)

            return self.run(fp)


class BlenderParser(ArgumentParser):

    """
    Created by: fr-andres
    ---------------------

    Example Usage:

    ```bash
    >>> blender --python my_script.py -- -a 1 -b 2
    >>> blender --python my_script.py --
    ```
    """

    def _get_argv_after_doubledash(self):
        """Return the sublist after `--`"""
        try:
            idx = argv.index("--")
            return argv[idx + 1 :]
        except ValueError:
            return []

    # overrides superclass
    def parse_args(self):
        """Override the superclass to take arguments after the `--` element"""
        return super().parse_args(args=self._get_argv_after_doubledash())
