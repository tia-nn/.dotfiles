def _xonshrc_tools():
    from typing import List, Dict, Optional
    from pprint import pprint


    class EnvLoader:
        old_env: Dict[str, Dict[str, Optional[str]]]

        def load_dotenv(args: List):
            pass

    def load_dotenv(args: List[str]):
        var_strs = [ll for ll in [l.strip() for l in $(cat @(args)).splitlines()] if ll and ll[0] != '#']

        # _

        pprint(var_strs)


    aliases['loadenv'] = load_dotenv


_xonshrc_tools()
