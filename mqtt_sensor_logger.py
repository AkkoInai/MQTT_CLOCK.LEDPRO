#!/usr/bin/env python3
"""
mqtt_sensor_logger.py
---------------------
ESP32-LEDPRO から届く温湿度(climate)・振動(quake)・明るさ(light)を
MQTT で受信し、MariaDB に記録し続ける常駐ロガー。

事前準備:
  1. setup_ledpro_db.sql を MariaDB に流す(light_log テーブルも必要)
  2. paho-mqtt と pymysql を入れる
       Debian/Ubuntu: sudo apt install python3-paho-mqtt python3-pymysql
       pip の場合   : pip install paho-mqtt pymysql

起動例:
  LEDPRO_DB_PASSWORD=xxxx python3 mqtt_sensor_logger.py
  (または --db-password xxxx)
"""
import argparse
import fcntl
import json
import os
import signal
import sys
import time

import paho.mqtt.client as mqtt
import pymysql


def log(msg, err=False):
    stream = sys.stderr if err else sys.stdout
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}", file=stream, flush=True)


class Db:
    """書き込みに失敗したら接続を捨て、次の書き込みで再接続する。"""

    def __init__(self, args):
        self.args = args
        self.conn = None

    def _connect(self):
        self.conn = pymysql.connect(
            host=self.args.db_host,
            user=self.args.db_user,
            password=self.args.db_password,
            database=self.args.db_name,
            charset="utf8mb4",
            autocommit=True,
        )
        log(f"MariaDB接続: {self.args.db_host}/{self.args.db_name}")

    def insert(self, sql, params):
        for attempt in (1, 2):
            try:
                if self.conn is None:
                    self._connect()
                with self.conn.cursor() as cur:
                    cur.execute(sql, params)
                return True
            except pymysql.MySQLError as e:
                log(f"DB書き込み失敗(試行{attempt}): {e}", err=True)
                self.conn = None
        return False

    def close(self):
        if self.conn is not None:
            try:
                self.conn.close()
            except pymysql.MySQLError:
                pass
            self.conn = None


def num(body, key):
    """JSONの値を数値として取り出す。無い・数値でない場合は ValueError を投げる。"""
    if key not in body:
        raise ValueError(f"{key} がありません")
    v = body[key]
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise ValueError(f"{key} が数値ではありません: {v!r}")
    return float(v)


def make_handlers(db):
    def climate(body):
        return db.insert(
            "INSERT INTO climate_log (temperature, humidity) VALUES (%s, %s)",
            (num(body, "temperature"), num(body, "humidity")),
        )

    def quake(body):
        return db.insert(
            "INSERT INTO quake_log (magnitude, accel_x, accel_y, accel_z) VALUES (%s, %s, %s, %s)",
            (num(body, "magnitude"), num(body, "x"), num(body, "y"), num(body, "z")),
        )

    def light(body):
        return db.insert(
            "INSERT INTO light_log (raw, voltage) VALUES (%s, %s)",
            (int(num(body, "raw")), num(body, "voltage")),
        )

    return climate, quake, light


def acquire_lock(path):
    """同じロガーの二重起動を防ぐ。返り値のファイルを開いたままにしておくこと。"""
    f = open(path, "w")
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        log(f"別のロガーが動作中のため終了します(ロック: {path})", err=True)
        sys.exit(1)
    f.write(str(os.getpid()))
    f.flush()
    return f


def main():
    parser = argparse.ArgumentParser(description="センサー値をMQTTで受信してMariaDBに記録する")
    parser.add_argument("--mqtt-host", default="192.168.0.252")
    parser.add_argument("--mqtt-port", type=int, default=1883)
    parser.add_argument("--climate-topic", default="ledmatrix/sensor/climate")
    parser.add_argument("--quake-topic", default="ledmatrix/sensor/quake")
    parser.add_argument("--light-topic", default="ledmatrix/sensor/light")
    parser.add_argument("--db-host", default="localhost")
    parser.add_argument("--db-user", default="ledpro_writer")
    parser.add_argument("--db-password", default=os.environ.get("LEDPRO_DB_PASSWORD"),
                        help="省略時は環境変数 LEDPRO_DB_PASSWORD を使う")
    parser.add_argument("--db-name", default="ledpro")
    parser.add_argument("--lock-file", default="/tmp/ledpro_sensor_logger.lock")
    args = parser.parse_args()

    if not args.db_password:
        parser.error("--db-password か環境変数 LEDPRO_DB_PASSWORD を指定してください")

    _lock = acquire_lock(args.lock_file)  # プロセス終了までファイルを保持する

    db = Db(args)
    climate_h, quake_h, light_h = make_handlers(db)
    topic_map = {
        args.climate_topic: climate_h,
        args.quake_topic: quake_h,
        args.light_topic: light_h,
    }

    # paho-mqtt 2.x と 1.x の両方で動くようにする
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    except AttributeError:
        client = mqtt.Client()

    def on_connect(client, userdata, flags, rc, *_):
        log(f"MQTT接続: {rc}")
        for topic in topic_map:
            client.subscribe(topic)  # 再接続のたびに購読し直す
        log(f"購読: {', '.join(topic_map)}")

    def on_disconnect(client, userdata, *_):
        log("MQTT切断。自動再接続を待ちます", err=True)

    def on_message(client, userdata, msg):
        handler = topic_map.get(msg.topic)
        if handler is None:
            return
        try:
            body = json.loads(msg.payload.decode("utf-8"))
            ok = handler(body)
        except (ValueError, UnicodeDecodeError) as e:
            log(f"不正なデータ({msg.topic}): {e} payload={msg.payload[:120]!r}", err=True)
            return
        if ok:
            log(f"{handler.__name__} 記録: {body}")

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.reconnect_delay_set(min_delay=1, max_delay=30)

    def on_term(signum, frame):
        raise KeyboardInterrupt  # systemctl stop(SIGTERM)も通常終了として扱う

    signal.signal(signal.SIGTERM, on_term)

    client.connect_async(args.mqtt_host, args.mqtt_port, keepalive=30)
    log("記録を開始します。Ctrl+C / SIGTERMで終了")
    try:
        client.loop_forever(retry_first_connection=True)
    except KeyboardInterrupt:
        log("終了します")
    finally:
        client.disconnect()
        db.close()


if __name__ == "__main__":
    main()
