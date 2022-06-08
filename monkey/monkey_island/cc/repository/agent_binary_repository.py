from typing import BinaryIO

from . import AgentRetrivalError, FileRetrivalError, IAgentBinaryRepository, IFileRepository

LINUX_AGENT_FILE_NAME = "monkey-linux-64"
WINDOWS_AGENT_FILE_NAME = "monkey-windows-64.exe"


class AgentBinaryRepository(IAgentBinaryRepository):
    def __init__(self, file_repository: IFileRepository):
        self._file_repository = file_repository

    def __get_binary(self, filename) -> BinaryIO:
        try:
            agent_binary = self._file_repository.open_file(filename)
            return agent_binary
        except FileRetrivalError as err:
            raise AgentRetrivalError(
                f"An error occurred while retrieving the {filename}"
                f" agent binary from {self._file_repository}: {err}"
            )

    def get_linux_binary(self) -> BinaryIO:
        self.__get_binary(LINUX_AGENT_FILE_NAME)

    def get_windows_binary(self) -> BinaryIO:
        self.__get_binary(WINDOWS_AGENT_FILE_NAME)
