def _xonshrc_tools():
    from typing import List, Dict, Optional, Deque, Any
    from pprint import pprint
    from collections import deque
    from copy import copy
    import sys
    import os
    from xonsh.built_ins import XSH
    from xontrib.abbrevs import abbrevs

    aliases = XSH.aliases

    def load_envfile(args: List[str]):
        if args == []:
            args = ['.env']

        envs = []
        for file_name in args:
            try:
                f = open(file_name)
            except Exception as e:
                print(f'ignore file: {file_name}; {e}', file=sys.stderr)
                continue
            envs.append(f.read())
            f.close()

        XSH.aliases['source-bash']([f'''
            set -a
            {os.sep.join(envs)}
            set +a
        '''])

    # def env_with_dotenv(args: List[str], stdin=None, stdout=None, stderr=None):
    #     try:
    #         f = open('.dotenv')
    #     except Exception as e:
    #         print(f"can't open .env file; {e}", file=sys.stderr)
    #         env = []
    #     else:
    #         env = f.read().split()
    #         f.close()

    #     env @(env) @(args)

    class EnvStack():
        stack: Deque[Dict[str, Any]]

        def __init__(self):
            self.stack = deque()

        def pope(self, args: List[str]):
            verbose = '-v' in args
            ldenv = self.stack.pop()
            denv = XSH.env.detype()

            for k, v in ldenv.items():
                if k in ['__ALIAS_NAME', '__ALIAS_STACK']:
                    continue
                if k in denv and v == denv[k]:
                    continue
                if verbose:
                    print('${0} = {1}  # before ${0} value is {2}'.format(
                        k, repr(v), repr(XSH.env[k])))
                XSH.env[k] = v
            for k in denv:
                if k not in ldenv:
                    if k in ['__ALIAS_NAME', '__ALIAS_STACK']:
                        continue
                    if verbose:
                        print('del ${0}  # before ${0} value is {1}'.format(
                            k, repr(XSH.env[k])))
                    del XSH.env[k]

        def pushe(self):
            self.stack.append(copy(XSH.env.detype()))

    def push_and_loadenv(args):
        __envstack__.pushe()
        load_envfile(args)

    global __envstack__
    try:
        __envstack__ = __envstack__ if __envstack__ is not None else EnvStack()
    except NameError:
        __envstack__ = EnvStack()

    aliases['pushe'] = __envstack__.pushe
    aliases['pope'] = __envstack__.pope

    aliases['loadenv'] = load_envfile
    # aliases['envd'] = env_with_dotenv
    abbrevs['envd'] = "env @(open('.env').read().split())"
    aliases['push-and-loadenv'] = push_and_loadenv


_xonshrc_tools()
