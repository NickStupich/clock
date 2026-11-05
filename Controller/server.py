import asyncio
import datetime
import json
import os
import subprocess
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlsplit

os.environ.setdefault("MPLBACKEND", "Agg")  # calibration runs off the main thread

import numpy as np
import uvicorn
from fastapi import FastAPI, File, HTTPException, Request, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from clock_controller import ClockController

HERE = Path(__file__).resolve().parent
CAL_DIR = HERE.parent / "Simulator" / "calibration_images"
MAX_UPLOAD = 25 * 1024 * 1024


class Client:
    """Per-connection outbox: events are queued in order, frames are coalesced to the latest."""

    def __init__(self):
        self.events = asyncio.Queue()
        self.frame = None
        self.wake = asyncio.Event()

    async def pump(self, ws):
        while True:
            await self.wake.wait()
            self.wake.clear()
            while not self.events.empty():
                await ws.send_text(self.events.get_nowait())
            if self.frame is not None:
                frame, self.frame = self.frame, None
                await ws.send_bytes(frame)


class Hub:
    def __init__(self):
        self.clients = set()

    def event(self, message):
        text = json.dumps(message)
        for c in self.clients:
            c.events.put_nowait(text)
            c.wake.set()

    def frame(self, data):
        for c in self.clients:
            c.frame = data
            c.wake.set()


def git_commit():
    try:
        out = subprocess.run(["git", "rev-parse", "--short=8", "HEAD"], cwd=HERE,
                             capture_output=True, text=True, timeout=5)
        return out.stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def same_origin(headers):
    origin = headers.get("origin")
    return origin is None or urlsplit(origin).netloc == headers.get("host")


@asynccontextmanager
async def lifespan(app):
    app.state.hub = Hub()
    app.state.controller = ClockController(app.state.hub.frame, app.state.hub.event, git_commit())
    app.state.controller.start()
    yield
    await app.state.controller.stop()


app = FastAPI(lifespan=lifespan)


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    if not same_origin(ws.headers):
        await ws.close(code=1008)
        return

    await ws.accept()
    hub, controller = ws.app.state.hub, ws.app.state.controller
    client = Client()
    await ws.send_text(json.dumps(controller.snapshot()))
    await ws.send_bytes(controller.frame())
    hub.clients.add(client)
    pump = asyncio.create_task(client.pump(ws))

    try:
        while True:
            try:
                msg = json.loads(await ws.receive_text())
            except ValueError:
                continue
            if not isinstance(msg, dict):
                continue
            if msg.get("type") == "algorithm":
                controller.enable_algo(msg.get("value"))
            elif msg.get("type") == "overnightMode":
                controller.set_overnight_mode(msg.get("value"))
    except (WebSocketDisconnect, RuntimeError):
        pass
    finally:
        hub.clients.discard(client)
        pump.cancel()


def process_calibration_image(data):
    import cv2
    import HandOffsetCalculator

    img = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), flags=cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("upload is not a decodable image")

    CAL_DIR.mkdir(exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%S.%f")
    cv2.imwrite(str(CAL_DIR / f"{stamp}.jpg"), img)
    return HandOffsetCalculator.get_hand_offsets_from_image(img)


@app.post("/calibration")
async def upload_calibration(request: Request, file: UploadFile = File(...)):
    if not same_origin(request.headers):
        raise HTTPException(403, "cross-origin request rejected")

    controller = request.app.state.controller
    data = await file.read(MAX_UPLOAD + 1)
    if len(data) > MAX_UPLOAD:
        raise HTTPException(413, "image too large")

    controller.set_log("got image")
    try:
        offsets, log_msg = await asyncio.to_thread(process_calibration_image, data)
    except Exception as e:
        controller.set_log(f"calibration failed: {e}")
        raise HTTPException(400, "calibration failed")

    applied = await controller.set_calibration(offsets)
    if not applied:
        log_msg += f"\n\nIgnored: algorithm is {controller.algorithm_name}, not Calibration or Backlash"
    controller.set_log(log_msg)
    return {"applied": applied}


app.mount("/", StaticFiles(directory=HERE / "static", html=True), name="static")


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8080)
