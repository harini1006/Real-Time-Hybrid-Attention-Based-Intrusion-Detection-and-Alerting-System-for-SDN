"""
FastAPI backend for the Hybrid Attention-Based IDS.
Provides REST endpoints and WebSocket for real-time monitoring.
"""
import os
import sys
import io
import json
import asyncio
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import MODEL_DIR, SAMPLE_SIZE, REALTIME_DELAY
from auth import authenticate_user, create_access_token, verify_token, register_user
from predict import PredictionEngine
from preprocessing import preprocess_dataframe
from alerts import record_alert, get_alerts, get_alert_stats, send_upload_summary_email_async

# ──────────────────────────── App Init ────────────────────────────
app = FastAPI(title="NetGuard AI — Intrusion Detection System", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
engine = PredictionEngine()
prediction_store = []  # Store predictions for download
dashboard_stats = {
    "total_traffic": 0,
    "total_attacks": 0,
    "total_benign": 0,
    "attack_distribution": {},
}


def _try_load_engine():
    try:
        if not engine.is_loaded:
            engine.load()
    except FileNotFoundError:
        pass


@app.on_event("startup")
async def startup():
    _try_load_engine()


# ──────────────────────────── Auth ────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    full_name: str = ""


@app.post("/api/auth/login")
async def login(req: LoginRequest):
    if not authenticate_user(req.username, req.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": req.username})
    return {"access_token": token, "token_type": "bearer", "username": req.username}


@app.post("/api/auth/register")
async def register(req: RegisterRequest):
    if len(req.username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    if not register_user(req.username, req.password, req.full_name):
        raise HTTPException(status_code=409, detail="Username already exists")
    return {"message": "Account created successfully. Please sign in."}


# ──────────────────────────── CSV Upload ────────────────────────────
@app.post("/api/upload")
async def upload_csv(file: UploadFile = File(...)):
    global prediction_store, dashboard_stats
    _try_load_engine()
    if not engine.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded. Train model first.")

    # Read CSV
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents), low_memory=False)
    df.columns = df.columns.str.strip()

    original_len = len(df)

    # Preprocess for prediction
    try:
        X, y_true, _, _, _ = preprocess_dataframe(
            df.copy(), fit_new=False,
            scaler=engine.scaler,
            label_encoder=engine.label_encoder,
            sample_size=SAMPLE_SIZE
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Preprocessing error: {str(e)}")

    # Predict
    results = engine.predict_batch(X)

    # Build response & update stats
    predictions = []
    attack_count = 0
    upload_attack_distribution = {}
    for i, r in enumerate(results):
        pred = {
            "id": i + 1,
            **r,
        }
        predictions.append(pred)

        if r["is_attack"]:
            attack_count += 1
            at = r["attack_type"]
            dashboard_stats["attack_distribution"][at] = dashboard_stats["attack_distribution"].get(at, 0) + 1
            upload_attack_distribution[at] = upload_attack_distribution.get(at, 0) + 1
            # Record alert (only for first 50 to avoid spam)
            if attack_count <= 50:
                record_alert(r, {"row_index": i + 1, "source": file.filename})

    benign_count = len(results) - attack_count
    dashboard_stats["total_traffic"] += len(results)
    dashboard_stats["total_attacks"] += attack_count
    dashboard_stats["total_benign"] += benign_count

    prediction_store = predictions

    if attack_count > 0:
        send_upload_summary_email_async(
            filename=file.filename,
            total_rows=original_len,
            processed_rows=len(results),
            attack_count=attack_count,
            benign_count=benign_count,
            attack_breakdown=upload_attack_distribution,
        )

    return {
        "filename": file.filename,
        "total_rows": original_len,
        "processed_rows": len(results),
        "attacks_found": attack_count,
        "benign_count": benign_count,
        "predictions": predictions[:500],  # Return first 500 for UI
        "total_predictions": len(predictions),
    }


# ──────────────────────────── Real-Time WebSocket ────────────────────────────
@app.websocket("/api/ws/realtime")
async def realtime_monitor(websocket: WebSocket):
    await websocket.accept()
    _try_load_engine()

    if not engine.is_loaded:
        await websocket.send_json({"error": "Model not loaded"})
        await websocket.close()
        return

    try:
        # Receive the CSV data
        data = await websocket.receive_text()
        msg = json.loads(data)

        if msg.get("type") == "start" and msg.get("csv_data"):
            csv_data = msg["csv_data"]
            df = pd.read_csv(io.StringIO(csv_data), low_memory=False)
            df.columns = df.columns.str.strip()

            # Preprocess
            try:
                X, _, _, _, _ = preprocess_dataframe(
                    df.copy(), fit_new=False,
                    scaler=engine.scaler,
                    label_encoder=engine.label_encoder,
                    sample_size=min(5000, len(df))
                )
            except Exception as e:
                await websocket.send_json({"error": str(e)})
                await websocket.close()
                return

            # Stream predictions row by row
            for i in range(len(X)):
                try:
                    # Check for stop signal
                    try:
                        stop_msg = await asyncio.wait_for(websocket.receive_text(), timeout=0.01)
                        if json.loads(stop_msg).get("type") == "stop":
                            await websocket.send_json({"type": "stopped", "processed": i})
                            break
                    except asyncio.TimeoutError:
                        pass

                    single_X = X[i:i+1]
                    result = engine.predict_batch(single_X)[0]
                    result["row_index"] = i + 1
                    result["timestamp"] = datetime.now(timezone.utc).isoformat()
                    result["type"] = "prediction"

                    # Track stats
                    dashboard_stats["total_traffic"] += 1
                    if result["is_attack"]:
                        dashboard_stats["total_attacks"] += 1
                        at = result["attack_type"]
                        dashboard_stats["attack_distribution"][at] = dashboard_stats["attack_distribution"].get(at, 0) + 1
                        record_alert(result, {"row_index": i + 1, "source": "realtime"}, send_email=True)
                    else:
                        dashboard_stats["total_benign"] += 1

                    await websocket.send_json(result)
                    await asyncio.sleep(REALTIME_DELAY)

                except WebSocketDisconnect:
                    break

            await websocket.send_json({"type": "complete", "total_processed": len(X)})
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass


# ──────────────────────────── Model Metrics ────────────────────────────
@app.get("/api/metrics")
async def get_metrics():
    metrics_path = os.path.join(MODEL_DIR, "metrics.json")
    if not os.path.exists(metrics_path):
        raise HTTPException(status_code=404, detail="No metrics found. Train model first.")
    with open(metrics_path) as f:
        return json.load(f)


# ──────────────────────────── Dashboard ────────────────────────────
@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    alert_stats = get_alert_stats()
    return {
        **dashboard_stats,
        "attack_ratio": round(
            dashboard_stats["total_attacks"] / max(1, dashboard_stats["total_traffic"]) * 100, 2
        ),
        "alert_stats": alert_stats,
    }


# ──────────────────────────── Alerts ────────────────────────────
@app.get("/api/alerts")
async def list_alerts(limit: int = Query(100), attack_type: str = Query(None)):
    return {"alerts": get_alerts(limit=limit, attack_type=attack_type)}


# ──────────────────────────── Download Predictions ────────────────────────────
@app.get("/api/predictions/download")
async def download_predictions():
    if not prediction_store:
        raise HTTPException(status_code=404, detail="No predictions available")
    df = pd.DataFrame(prediction_store)
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=predictions.csv"},
    )


# ──────────────────────────── Health ────────────────────────────
@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "model_loaded": engine.is_loaded,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
