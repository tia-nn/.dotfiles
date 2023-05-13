
xontrib load vox

if not ![xontrib load vox_tabcomplete]:
    xpip install xonsh-vox-tabcomplete
    xontrib load vox_tabcomplete
