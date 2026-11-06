#!/bin/bash

# 今日の「月」と「日」を取得
M=$(date +%-m)
D=$(date +%-d)

# 日本の記念日データをインターネットから取得
DATA=$(curl -s "https://toshiki.dev{M}&d=${D}")

# 記念日の名前を1つだけ綺麗に抜き出す
TODAY_NJ=$(echo "$DATA" | grep -oP '"title":"\K[^"]+' | head -n 1)

# 結果を表示
if [ ! -z "$TODAY_NJ" ] && [ "$TODAY_NJ" != "null" ]; then
    echo "今日は「${TODAY_NJ}」です。"
else
    echo "今日の記念日が見つかりませんでした。"
fi

