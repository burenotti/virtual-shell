from typing import Protocol


class Shell(Protocol):

    def run(self) -> None:
        ...


def from_file(file_path: str) -> Shell:
    return