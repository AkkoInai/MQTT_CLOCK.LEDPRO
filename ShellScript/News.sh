#!/bin/bash

# ニュースの抽出（上位5件を / で繋ぐ）
NEWS=$(curl -s "https://news.yahoo.co.jp/rss/topics/top-picks.xml" | grep -o '<title>[^<]*' | sed 's/<title>//' | tail -n +2 | head -n 5 | sed -e ':a' -e 'N' -e '$!ba' -e 's/\n/／/g')

# 現在の「秒」を取得
current_second=$(date +%-S)

# 25秒になるまでの残り秒数を計算して待つ（すでに25秒を過ぎていたら即実行）
if [ $current_second -lt 25 ]; then
    sleep_time=$((25 - current_second))
    sleep $sleep_time
fi

/home/akko2777/myenv/bin/python3 /home/akko2777/dev/mqtt/mqtt_led_publisher.py  --char-spacing -4 --scroll-speed 65 --repeat 1 "ニュースです【$NEWS】以上。" 
