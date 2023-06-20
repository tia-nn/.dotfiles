def _xonshrc_vox():
    from xontrib.voxapi import Vox


    v = Vox()
    if 'misc' not in v:
        v.create('misc')
    v.activate('misc')


_xonshrc_vox()
