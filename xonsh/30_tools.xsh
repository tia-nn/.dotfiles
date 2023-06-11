def _xonshrc_tools():
    from typing import List, Dict, Optional, Deque, Any
    from pprint import pprint
    from collections import deque
    from copy import copy

    class EnvLoader:
        old_env: Dict[str, Dict[str, Optional[str]]]

        def load_dotenv(args: List):
            pass

    def load_dotenv(args: List[str]):
        var_strs = [ll for ll in [l.strip() for l in $(cat @(args)).splitlines()] if ll and ll[0] != '#']

        # _

        pprint(var_strs)



    class EnvStack():
        stack: Deque[Dict[str, Any]]

        def __init__(self):
            self.stack = deque()

        def pope(self, args: List[str]):
            verbose = '-v' in args
            ldenv = self.stack.pop()
            denv = ${...}.detype()

            for k, v in ldenv.items():
                if k in ['__ALIAS_NAME', '__ALIAS_STACK']:
                    continue
                if k in denv and v == denv[k]:
                    continue
                if verbose:
                    print('${0} = {1}  # before ${0} value is {2}'.format(k, repr(v), repr(${k})))
                ${k} = v
            for k in denv:
                if k not in ldenv:
                    if k in ['__ALIAS_NAME', '__ALIAS_STACK']:
                        continue
                    if verbose:
                        print('del ${0}  # before ${0} value is {1}'.format(k, repr(${k})))
                    del ${k}

        def pushe(self):
            self.stack.append(copy(${...}.detype()))


    global __envstack__
    try:
        __envstack__ = __envstack__ if __envstack__ is not None else EnvStack()
    except NameError:
        __envstack__ = EnvStack()

    aliases['pushe'] = __envstack__.pushe
    aliases['pope'] = __envstack__.pope

    aliases['loadenv'] = load_dotenv


_xonshrc_tools()
