import os
import urllib.request
from pathlib import Path
from subprocess import PIPE, CalledProcessError, Popen
from typing import Optional

from covalent._file_transfer import File
from covalent._file_transfer.strategies.transfer_strategy_base import FileTransferStrategy

import boto3
from furl import furl

class S3(FileTransferStrategy):

    """
    Implements Base FileTransferStrategy class to use HTTP to download files from public URLs.
    """

    def __init__(self,
                 aws_access_key_id : str = os.getenv('AWS_ACCESS_KEY_ID') or None,
                 aws_secret_access_key : str = os.getenv('AWS_SECRET_ACCESS_KEY') or None,
                 aws_session_token : str = os.getenv('AWS_SESSION_TOKEN') or None,
                 region_name : str = os.getenv('AWS_REGION') or None
    ):

        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_session_token = aws_session_token
        self.region_name = region_name
        
        
    # return callable to download here implies 'from' is a remote source
    def download(self, from_file: File, to_file: File = File()) -> File:
        from_filepath = from_file.filepath
        to_filepath = to_file.filepath
        bucket_name = furl(from_file.uri).origin[5:] 

        def callable():
            s3 = boto3.client("s3",
                              aws_access_key_id = self.aws_access_key_id,
                              aws_secret_access_key = self.aws_secret_access_key,
                              aws_session_token = self.aws_session_token,
                              region_name = self.region_name,
            )
            s3.download_file(bucket_name, from_filepath, to_filepath)

        return callable

    # return callable to download here implies 'to' is a remote source
    def upload(self, from_file: File, to_file: File = File()) -> File:

        from_filepath = from_file.filepath
        to_filepath = to_file.filepath
        bucket_name = furl(to_file.uri).origin[5:] 

        def callable():
            s3 = boto3.client("s3",
                              aws_access_key_id = self.aws_access_key_id,
                              aws_secret_access_key = self.aws_secret_access_key,
                              aws_session_token = self.aws_session_token,
                              region_name = self.region_name,
            )
            s3.upload_file(from_filepath,bucket_name, to_filepath)

        return callable
    
    # No S3 Strategy for copy
    def cp(self, from_file: File, to_file: File = File()) -> File:
        raise NotImplementedError
