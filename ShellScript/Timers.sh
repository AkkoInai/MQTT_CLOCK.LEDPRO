#!/bin/bash

# 現在の「秒」を取得
current_second=$(date +%-S)

# 55秒になるまでの残り秒数を計算して待つ（すでに55秒を過ぎていたら即実行）
if [ $current_second -lt 55 ]; then
    sleep_time=$((55 - current_second))
    sleep $sleep_time
fi

# 次の時間の「時」を取得（59分55秒なので、1時間足した数字にする）
# ※ 23分の時は +1 して 24（あるいは0）にする処理
next_hour=$(date -d "+1 hour" +%-H)

# 24時を0時と表現したい場合は以下の3行のコメントアウト（#）を外してください
if [ "$next_hour" -eq 24 ]; then
    next_hour=0
fi

# メッセージの表示（またはMQTT送信コマンドなどをここに書く）
/home/akko2777/myenv/bin/python3 /home/akko2777/dev/mqtt/mqtt_led_publisher.py --char-spacing -4 --scroll-speed 65 --repeat 2 "${next_hour}時です"

