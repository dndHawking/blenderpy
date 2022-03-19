"""
Abstraction to run Python scripts in Blender.
"""
from subprocess import Popen, PIPE, STDOUT
from typing import Callable, Iterable, Optional, Union


class Blender:
    
    """
    Run Blender specific Python scripts.
    
    ```py
    B = Blender()
    B.run("generate")  # Construct will add '.py'
    ```
    """
    
    def __init__(self, path: str = "blender", **kwargs) -> None:
        """Set the `path` parameter to the executable if you have not
        set the PATH variable on your machine. Otherwise the default
        will suffice.
        
        Parameters
        ----------
        path : str
            The path to the Blender executable.
        kwargs : dict
            Keyword arguments to pass to the `run` method.
            For example, `headless:False` and/or `audio:True`.
        """
        self.app = path
        self.kwargs = kwargs
    
    def call(self, cmd: str, **kwargs) -> str:
        """Run a Terminal command.
        
        Parameters
        ----------
        cmd : str
            The command to run.
        kwargs : dict
            Keyword arguments to pass to the `Popen` object.
        """
        p = Popen(
            cmd,
            shell=kwargs.get("shell", True),
            stdin=kwargs.get("stdin", PIPE),
            close_fds=kwargs.get("close_fds", True),
            stdout=kwargs.get("stdout", PIPE),
            stderr=kwargs.get("stderr", STDOUT),
        )
        
        return p.stdout.read().decode("utf8")
    
    def speak(self, text: Union[str, Iterable]) -> None:
        """Print/Logging wrapper. Allowing quick and easy
        customizations.
        """
        if isinstance(text, Iterable):
            if not any((isinstance(word, str) for word in text)):
                raise ValueError("I only use strings.")
            shout = ' '.join(text)
        else:
            shout = text
            
        print(shout)
    
    def _dry_run(self, python_args: Optional[Iterable] = None, **kwargs) -> str:
        """Validate the `run` arguments."""
        for arg in python_args:
            if not isinstance(arg, str):
                return "All Python arguments should be a string."
        
        for arg in kwargs:
            if not isinstance(kwargs[arg], bool):
                return f"{arg}; should be a boolean."
            
        return ""
        
    def run(self, script: str, python_args: Iterable, **kwargs) -> str:
        """Run a script in Blender. You only need to
        place a script path in the method to use blender.
        """
        if (error := self._dry_run(**kwargs, python_args=python_args)):
            raise ValueError(error)
        
        if ".py" not in script:
            script = script + ".py"
        
        gui = "-b" if kwargs.get("headless", True) else ""
        runtime = "-P" if kwargs.get("python", True) else ""
        audio = "-noaudio" if not kwargs.get("audio", False) else ""
        python_args = ' '.join(python_args)
        
        prod = self.call(
            f"{self.app} {audio} {gui} {runtime} {script} -- {python_args}"
        )
        
        return prod
