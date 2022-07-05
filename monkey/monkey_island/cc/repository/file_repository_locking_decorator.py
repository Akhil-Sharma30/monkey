from typing import BinaryIO

from readerwriterlock import rwlock

from . import IFileRepository


class FileRepositoryLockingDecorator(IFileRepository):
    def __init__(self, file_repository: IFileRepository):
        self._file_repository = file_repository
        self._rwlock = rwlock.RWLockFair()

    def save_file(self, unsafe_file_name: str, file_contents: BinaryIO):
        with self._rwlock.gen_wlock():
            return self._file_repository.save_file(unsafe_file_name, file_contents)

    def open_file(self, unsafe_file_name: str) -> BinaryIO:
        with self._rwlock.gen_rlock():
            return self._file_repository.open_file(unsafe_file_name)

    def delete_file(self, unsafe_file_name: str):
        with self._rwlock.gen_wlock():
            return self._file_repository.delete_file(unsafe_file_name)

    def delete_all_files(self):
        with self._rwlock.gen_wlock():
            return self._file_repository.delete_all_files()
