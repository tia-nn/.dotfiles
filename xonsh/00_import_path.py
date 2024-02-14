def _xonshrc_import_path():
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent))


_xonshrc_import_path()
