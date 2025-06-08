#!/usr/bin/env python3
import os
import json
import time
import signal
import sys
from paho.mqtt import client as mqtt

# 環境変数からブローカー情報と出力先を取得
BROKER_HOST = os.getenv("MQTT_BROKER", "mqtt-broker")
BROKER_PORT = int(os.getenv("MQTT_PORT", "1883"))
TOPIC       = os.getenv("MQTT_TOPIC", "#")
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "/data/messages.jsonl")

# graceful shutdown 用
running = True
def _signal_handler(sig, frame):
    global running
    running = False
signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)

def on_connect(client, userdata, flags, rc):
    print(f"[archiver] Connected to {BROKER_HOST}:{BROKER_PORT} (rc={rc}), subscribing to '{TOPIC}'")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "topic": msg.topic,
        # バイナリ payload は UTF-8 と見なして文字列化。必要なら base64 encode などに変更可
        "payload": msg.payload.decode("utf-8", errors="replace")
    }
    line = json.dumps(entry, ensure_ascii=False)
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_start()

    # シグナル待ち or 接続維持
    try:
        while running:
            time.sleep(1)
    finally:
        print("[archiver] Shutting down...")
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
