import logging
import platform
import stat
import subprocess
from pathlib import Path
from shutil import copyfileobj

from monkey_island.cc.repository import IAgentBinaryRepository, RetrievalError
from monkey_island.cc.server_utils.consts import ISLAND_PORT
from monkey_island.cc.services.utils.network_utils import get_local_ip_addresses

logger = logging.getLogger(__name__)

AGENT_NAMES = {"linux": "monkey-linux-64", "windows": "monkey-windows-64.exe"}


class LocalMonkeyRunService:
    def __init__(self, data_dir: Path, agent_binary_repository: IAgentBinaryRepository):
        self._data_dir = data_dir
        self._agent_binary_repository = agent_binary_repository

    def run_local_monkey(self):
        # get the monkey executable suitable to run on the server
        operating_system = platform.system().lower()
        try:
            agents = {
                "linux": self._agent_binary_repository.get_linux_binary,
                "windows": self._agent_binary_repository.get_windows_binary,
            }

            agent_binary = agents[platform.system().lower()]()
        except RetrievalError as err:
            logger.error(
                f"No Agent can be retrieved for the specified operating system"
                f'"{operating_system}"'
            )
            return False, str(err)
        except KeyError as err:
            logger.error(
                f"No Agents are available for unsupported operating system" f'"{operating_system}"'
            )
            return False, str(err)
        except Exception as err:
            logger.error(f"Error running agent from island: {err}")
            return False, str(err)

        dest_path = self._data_dir / AGENT_NAMES[operating_system]

        # copy the executable to temp path (don't run the monkey from its current location as it may
        # delete itself)
        try:
            with open(dest_path, "wb") as dest_agent:
                copyfileobj(agent_binary, dest_agent)

            dest_path.chmod(stat.S_IRWXU | stat.S_IRWXG)
        except Exception as exc:
            logger.error("Copy file failed", exc_info=True)
            return False, "Copy file failed: %s" % exc

        # run the monkey
        try:
            ip = get_local_ip_addresses()[0]
            port = ISLAND_PORT

            args = [str(dest_path), "m0nk3y", "-s", f"{ip}:{port}"]
            subprocess.Popen(args, cwd=self._data_dir)
        except Exception as exc:
            logger.error("popen failed", exc_info=True)
            return False, "popen failed: %s" % exc

        return True, ""
