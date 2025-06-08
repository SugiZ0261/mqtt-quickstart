import os
import json
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="MQTT Log API")

LOG_FILE = os.getenv("LOG_FILE", "/data/messages.jsonl")

class LogEntry(BaseModel):
    timestamp: str
    topic: str
    payload: str

def parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))

@app.get("/logs", response_model=List[LogEntry])
def get_logs(
    topic: Optional[str] = Query(None, description="フィルタするトピック（部分一致）"),
    start: Optional[str] = Query(None, description="開始時刻（ISO8601, inclusive）"),
    end:   Optional[str] = Query(None, description="終了時刻（ISO8601, inclusive）"),
    offset: int = Query(0, ge=0, description="スキップ件数"),
    limit:  int = Query(100, gt=0, le=1000, description="取得件数上限")
):
    """
    JSONL ファイルを逐行読み込み、各ログをオプションでフィルタして返却します。
    """
    if not os.path.exists(LOG_FILE):
        raise HTTPException(status_code=404, detail="Log file not found")

    entries = []
    start_dt = parse_iso(start) if start else None
    end_dt   = parse_iso(end)   if end else None

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = parse_iso(obj["timestamp"])
            if start_dt and ts < start_dt:  continue
            if end_dt   and ts > end_dt:    continue
            if topic    and topic not in obj["topic"]: continue
            entries.append(obj)
    # offset/limit
    return entries[offset : offset + limit]

@app.get("/logs/download")
def download_logs():
    """
    元の JSONL ファイルをそのままダウンロード用にストリーミング返却します。
    """
    if not os.path.exists(LOG_FILE):
        raise HTTPException(status_code=404, detail="Log file not found")
    def iterfile():
        with open(LOG_FILE, mode="rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                yield chunk
    return StreamingResponse(iterfile(), media_type="application/octet-stream")

@app.get("/health")
def health():
    return {"status": "ok"}
