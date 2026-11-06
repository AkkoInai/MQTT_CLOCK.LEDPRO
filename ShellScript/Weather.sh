#!/bin/bash

# 天気の抽出(横浜市東部)
WEATHER=$(/home/akko2777/myenv/bin/python3 -c "
import json, urllib.request
data = json.load(urllib.request.urlopen('https://www.jma.go.jp/bosai/forecast/data/forecast/140000.json'))
areas = data[0]['timeSeries'][0]['areas']
w = next(a['weathers'][0] for a in areas if a['area']['name'] == '東部')
print(w)
")
# 1行で空白をすべて削除
WEATHER=$(echo "$WEATHER" | sed 's/[[:space:]　]//g')

# 現在の「秒」を取得
current_second=$(date +%-S)

# 18秒になるまでの残り秒数を計算して待つ（すでに18秒を過ぎていたら即実行）
if [ $current_second -lt 18 ]; then
    sleep_time=$((18 - current_second))
    sleep $sleep_time
fi
/home/akko2777/myenv/bin/python3 /home/akko2777/dev/mqtt/mqtt_led_publisher.py "$WEATHER" 
