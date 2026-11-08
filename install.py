#!/usr/bin/env python3
"""install.sh から呼ばれる。installer パッケージの CLI を実行する。"""

import sys

from installer.cli import main

if __name__ == "__main__":
    sys.exit(main())
