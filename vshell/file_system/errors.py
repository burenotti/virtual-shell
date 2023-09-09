class FileNotFound(Exception):

    def __init__(self, message: str, file_path: str, *args) -> None:
        super().__init__(message, file_path, *args)
        self.file_path = file_path


class FileTypeError(Exception):

    def __init__(self, message: str, file_path: str, *args) -> None:
        super().__init__(message, file_path, *args)
        self.file_path = file_path
