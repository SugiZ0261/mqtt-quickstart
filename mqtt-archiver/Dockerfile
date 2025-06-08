# ベースイメージ
FROM python:3.11-slim

# ワークディレクトリ
WORKDIR /app

# 依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アーカイバースクリプトをコピー
COPY archiver.py .

# 実行時ユーザーを root のままでもいいですが、
# セキュリティ面で制限したい場合は下記を uncomment して
# ユーザーを作成＆切り替えてください。
# RUN useradd --create-home appuser
# USER appuser

# JSONL を出力するディレクトリを作成
RUN mkdir -p /data

# デフォルトの環境変数（Composeで上書き予定）
ENV MQTT_BROKER=mqtt-broker
ENV MQTT_PORT=1883
ENV MQTT_TOPIC=#
ENV OUTPUT_FILE=/data/messages.jsonl

# コンテナ起動時にスクリプトを実行
ENTRYPOINT ["python", "./archiver.py"]
