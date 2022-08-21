#!/bin/sh

# reconnect trackpad for thinkpad x1 carbon 6th gen
# see https://wiki.archlinux.jp/index.php/Lenovo_ThinkPad_X1_Carbon_(Gen_6) for details

logger "reconnect drvctl"
echo -n "none" | tee /sys/bus/serio/devices/serio1/drvctl
echo -n "reconnect" | tee /sys/bus/serio/devices/serio1/drvctl
