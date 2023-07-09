def _xonshrc_import_path():
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path.home() / '.dotfiles' / 'xonsh'))


_xonshrc_import_path()
