def command(v: str) -> bool:
    return !(which @(v)).rtn == 0
