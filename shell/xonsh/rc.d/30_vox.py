def _xonshrc_vox():
    from xonsh.built_ins import XSH

    # 対話シェルだけで使う（xonsh -c やスクリプトの実行では読まない）
    if not XSH.env.get('XONSH_INTERACTIVE'):
        return

    from xontrib.voxapi import Vox


    v = Vox()
    if 'misc' not in v:
        v.create('misc')
    v.activate('misc')


_xonshrc_vox()
