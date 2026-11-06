#!/bin/bash

# 1. 現在の「分」を2桁（00, 10, 20...）で取得
current_minute=$(date +%M)

# 2. 0分、10分、20分、30分、40分、50分のときは何もせず終了（スルー）する
case "$current_minute" in
    00|10|20|30|40|50)
        exit 0
        ;;
esac

read -r TEMP HUMI <<< $(mysql -N -u ledpro_writer -pledpro_writer -e "SELECT temperature, humidity FROM climate_log ORDER BY recorded_at DESC LIMIT 1;" ledpro)
TEMP_ZEN=$(echo "$TEMP" | sed 'y/0123456789./０１２３４５６７８９．/')
HUMI_ZEN=$(echo "$HUMI" | sed 'y/0123456789./０１２３４５６７８９．/')
/home/akko2777/myenv/bin/python3 /home/akko2777/dev/mqtt/mqtt_led_publisher.py --char-spacing -4 --scroll-speed 65 --repeat 2 "温度$TEMP_ZEN℃湿度$HUMI_ZEN％"
