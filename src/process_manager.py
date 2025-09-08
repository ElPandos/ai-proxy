import logging
import os
import stat
import subprocess
from pathlib import Path
from typing import List

from packaging.version import Version


class ProcessManager:
    __procs: List[subprocess.Popen] = []

    def __init__(self) -> None:
        pass

    def run(self, folder_path: str, output_file: str) -> None:
        commands = []
        commands.append(self.__eric_proxy())
        commands.append(self.__litellm(folder_path, output_file))
        commands.append(self.__lmstudio())

        # Start processes
        self.__procs = [subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for cmd in commands]

        # Wait for them to finish (blocking)
        # for proc in self.__procs:
        #    proc.wait()

    def __eric_proxy(self) -> List:
        return ["uv", "run", "ericai", "ericaiproxy"]

    def __litellm(self, folder_path: str, output_file: str) -> List:
        return ["uv", "run", "litellm", "--port", "4000", "--config", f"{folder_path}/{output_file}"]

    def __lmstudio(self) -> List:
        folder = Path.home() / "Downloads"
        latest_app_image = self.__find_latest_appimage(folder)
        appimage_and_path = Path(f"{folder}/{latest_app_image}")
        appimage_and_path.chmod(appimage_and_path.stat().st_mode | stat.S_IEXEC)
        return [str(appimage_and_path), "--no-sandbox"]

    def __find_latest_appimage(self, directory: str) -> str | None:
        try:
            candidates = [f for f in os.listdir(directory) if f.startswith("LM-Studio-") and f.endswith(".AppImage")]

            if not candidates:
                return None

            # Parse versions (extract the part between LM-Studio- and -x64.AppImage)
            def extract_version(fname: str) -> Version:
                version_str = fname.removeprefix("LM-Studio-").removesuffix("-x64.AppImage")
                return Version(version_str)

            return max(candidates, key=extract_version)
        except Exception as e:
            logging.error(f"Error: {e}")

    def terminate_all(self) -> None:
        for proc in self.__procs:
            self.terminate(proc.pid)
        self.__procs = []

    def terminate(self, pid: int) -> None:
        for proc in self.__procs:
            if proc.poll() is None and pid == proc.pid:
                logging.info(f"Killing process: {proc.pid}")
                proc.kill()
                proc.wait()
