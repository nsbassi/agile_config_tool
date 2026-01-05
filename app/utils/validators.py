import re

_filename_re = re.compile(r'[^A-Za-z0-9_.-]')


def sanitize_filename(name: str) -> str:
    return _filename_re.sub('_', name)
