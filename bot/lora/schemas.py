from runware import ILora
from dataclasses import dataclass

@dataclass
class ILoraExtended(ILora):
    shortname: str
    link: str