"""ltiauthenticator version info"""

version_info = (
    1,
    0,
    1,
    "dev",
)
__version__ = ".".join(map(str, version_info[:4]))

if len(version_info) > 4:
    __version__ = f"{__version__}{version_info[4]}"
