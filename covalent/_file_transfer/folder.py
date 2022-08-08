from typing import Optional

from covalent._file_transfer.file import File


class Folder(File):
    """
    Folder class to store components of provided URI including scheme (s3://, file://, ect.), determine if the file is remote,
    and act as facade to facilitate filesystem operations. Folder is a child of the File class which sets `is_dir` flag to True.

    Attributes:
        include_folder: Flag that determines if the folder should be included in the file transfer, if False only contents of folder are transfered.
    """

    def __init__(
        self,
        filepath: Optional[str] = None,
        is_remote: bool = False,
        is_dir: bool = True,
        include_folder: bool = False,
    ):
        super().__init__(filepath, is_remote, is_dir, include_folder)
