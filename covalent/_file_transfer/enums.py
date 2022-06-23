import enum


class FileSchemes(str, enum.Enum):
    File = "file"
    S3 = "s3"
    Globus = "globus"


class FileTransferStrategyTypes(str, enum.Enum):
    Rsync = "rsync"
    HTTPS = "https"
    S3 = "s3"
    FTP = "ftp"
    GLOBUS = "globus"
