from enum import Enum

class OutputFormat(str, Enum):
    jpg = "JPG"
    png = "PNG"
    webp = "WEBP"

class OutputType(str, Enum):
    url = "URL"
    base64 = "base64Data"
    data_uri = "dataURI"