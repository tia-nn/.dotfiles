from typing import List
from pprint import pprint


def load_dotenv(args: List[str]):
    var_strs = [ll for ll in [l.strip() for l in $(cat @(args)).splitlines()] if ll and ll[0] != '#']

    pprint(var_strs)


aliases['loadenv'] = load_dotenv
