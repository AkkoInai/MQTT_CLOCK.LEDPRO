#!/bin/bash

# 天気の抽出(横浜市東部)
WEATHER=$(python3 -c "
import json, urllib.request
data = json.load(urllib.request.urlopen('https://www.jma.go.jp/bosai/forecast/data/forecast/140000.json'))
areas = data[0]['timeSeries'][0]['areas']
w = next(a['weathers'][0] for a in areas if a['area']['name'] == '東部')
print(w)
")
# 1行で空白をすべて削除
WEATHER=$(echo "$WEATHER" | sed 's/[[:space:]　]//g')

# ニュースの抽出（上位5件を / で繋ぐ）
NEWS=$(curl -s "https://news.yahoo.co.jp/rss/topics/top-picks.xml" | grep -o '<title>[^<]*' | sed 's/<title>//' | tail -n +2 | head -n 5 | sed -e ':a' -e 'N' -e '$!ba' -e 's/\n/／/g')
# 結果を表示
echo "【今日の天気】$WEATHER 【ニュース】$NEWS"

python3 mqtt_led_publisher.py "$WEATHER" 
sleep 10
python3 mqtt_led_publisher.py "$NEWS" 
