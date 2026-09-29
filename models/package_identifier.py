from sqlmodel import Enum

class PackageIdentifier(str, Enum):
    avatars_120 = "avatars-120"