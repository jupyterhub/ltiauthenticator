"""illumidesk version info"""

# for now, update the version so that its the same as the one reflected
# within the repo's root package.json
version_info = (
    1,
    0,
    1,
    "dev",
)
__version__ = ".".join(map(str, version_info[:4]))

if len(version_info) > 4:
    __version__ = "%s%s" % (__version__, version_info[4])
