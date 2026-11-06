#!/bin/bash

# キャッシュファイルと日付の保存先（一時フォルダ）
CACHE_FILE="/tmp/zatsuneta_day_cache.txt"
CACHE_DATE_FILE="/tmp/zatsuneta_day_date.txt"

# 現在の「秒」を取得
current_second=$(date +%-S)
# 今日の一時的な日付文字列 (例: 0910)
TODAY_STR=$(date +%m%d)

# キャッシュファイルが存在し、かつ中に書き込まれた日付が今日と一致するか確認
if [ -f "$CACHE_FILE" ] && [ -f "$CACHE_DATE_FILE" ] && [ "$(cat $CACHE_DATE_FILE)" = "$TODAY_STR" ]; then
    # 条件クリア：WEBにはアクセスせず、保存したファイルからリストを読み込む
    list=$(cat "$CACHE_FILE")
else
    # 初回または日替わり時：手ほどき通りのURLを叩いて最新リストを取得
    list=$(curl -s "https://zatsuneta.com/archives/a`(date +%m%d)`.html" | grep -oP '(?<=title=")[^"]+(?=（[^）]+記念日）)')
    
    # 取得に成功した場合のみ、ファイルに今日のリストと日付をキャッシュする
    if [ -n "$list" ]; then
        echo "$list" > "$CACHE_FILE"
        echo "$TODAY_STR" > "$CACHE_DATE_FILE"
    fi
fi

# 25秒になるまでの残り秒数を計算して待つ（すでに25秒を過ぎていたら即実行）
if [ $current_second -lt 25 ]; then
    sleep_time=$((25 - current_second))
    sleep $sleep_time
fi

# 取得したリストから無作為に1つだけ抽出して表示（ここは毎回動く）
if [ -n "$list" ]; then
    # echo "$list" | shuf -n 1
    list_one=$(echo "$list" | shuf -n 1)
    # メッセージの表示（またはMQTT送信コマンドなどをここに書く）
    /home/akko2777/myenv/bin/python3 /home/akko2777/dev/mqtt/mqtt_led_publisher.py --repeat 2 "今日は$list_oneです"
else
    echo "取得に失敗しました。"
fi

