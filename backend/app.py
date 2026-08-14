"""
Flask API - Urban Parking Availability Prediction
"""

import os
import sys
import traceback
import numpy as np
from datetime import datetime, timedelta
from flask      import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

BACKEND_DIR  = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR     = os.path.dirname(BACKEND_DIR)
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
MODEL_FILE   = os.path.join(BACKEND_DIR, "saved_model", "parking_model.pkl")
DATA_FILE    = os.path.join(BACKEND_DIR, "data", "parking.csv")

sys.path.insert(0, BACKEND_DIR)

from data  import load_data, generate_data
from model import ParkingModel, ZONES, _get_status

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)

if not os.path.exists(DATA_FILE):
    print("Generating parking data...")
    generate_data(days=365)

df = load_data()

pm = ParkingModel()
pm.build()
MODEL_READY = pm.load(MODEL_FILE)

if not MODEL_READY:
    print("Auto training...")
    try:
        metrics     = pm.train(df)
        pm.save(MODEL_FILE)
        MODEL_READY = True
        print(f"Auto trained: MAE={metrics['mae']}")
    except Exception as e:
        print(f"Auto train failed: {e}")
        MODEL_READY = False


# ── Static ─────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:fn>")
def static_files(fn):
    return send_from_directory(FRONTEND_DIR, fn)


# ── Helpers ────────────────────────────────
def mock_prediction():
    hour   = datetime.now().hour
    result = {}

    capacities = {
        "mall": 500, "hospital": 300, "office": 400,
        "station": 250, "market": 200, "airport": 600
    }

    for zone, cap in capacities.items():
        if   0  <= hour <  6:  occ = 0.10
        elif 9  <= hour < 12:  occ = 0.75
        elif 12 <= hour < 14:  occ = 0.85
        elif 17 <= hour < 20:  occ = 0.90
        else:                   occ = 0.50

        occ       = float(np.clip(occ + np.random.normal(0, 0.05), 0.05, 0.99))
        occupied  = int(cap * occ)
        available = cap - occupied

        result[zone] = {
            "occupancy" : round(occ, 3),
            "occupied"  : occupied,
            "available" : available,
            "capacity"  : cap,
            "status"    : _get_status(occ),
        }
    return result


# ── API Routes ─────────────────────────────

@app.route("/api/status")
def api_status():
    return jsonify({
        "status"     : "ok",
        "model_ready": MODEL_READY,
        "data_rows"  : len(df),
        "python"     : sys.version.split()[0],
        "time"       : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })


@app.route("/api/train")
def api_train():
    global MODEL_READY, df
    try:
        print("Training started...")
        df      = load_data()
        metrics = pm.train(df)
        pm.save(MODEL_FILE)
        MODEL_READY = True
        return jsonify({
            "success": True,
            "message": "Model trained! MAE=" + str(metrics["mae"]),
            "metrics": metrics,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/predict")
def api_predict():
    global MODEL_READY
    try:
        if MODEL_READY:
            try:
                pred = pm.predict(df)
            except Exception as e:
                print(f"Model predict failed: {e}")
                pred = mock_prediction()
        else:
            pred = mock_prediction()

        # Calculate totals
        total_cap  = sum(v["capacity"]  for v in pred.values())
        total_occ  = sum(v["occupied"]  for v in pred.values())
        total_avail= sum(v["available"] for v in pred.values())
        total_pct  = round(total_occ / total_cap, 3)

        return jsonify({
            "success"    : True,
            "model_used" : MODEL_READY,
            "zones"      : pred,
            "summary"    : {
                "total_capacity" : total_cap,
                "total_occupied" : total_occ,
                "total_available": total_avail,
                "total_occupancy": total_pct,
                "status"         : _get_status(total_pct),
            },
        })
    except Exception as e:
        print("PREDICT ERROR:", traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/forecast")
def api_forecast():
    try:
        now    = datetime.now()
        result = []

        for i in range(24):
            ft   = now + timedelta(hours=i + 1)
            hour = ft.hour
            wd   = ft.weekday()

            if   0  <= hour <  6:  base = 0.10
            elif 9  <= hour < 12:  base = 0.75
            elif 12 <= hour < 14:  base = 0.85
            elif 17 <= hour < 20:  base = 0.90
            else:                   base = 0.50

            weekend = 1.15 if wd >= 5 else 1.0
            occ     = float(np.clip(
                base * weekend + np.random.normal(0, 0.05),
                0.05, 0.99
            ))

            total_cap   = 2250
            total_avail = int(total_cap * (1 - occ))

            result.append({
                "hour"           : hour,
                "label"          : ft.strftime("%H:00"),
                "occupancy"      : round(occ, 3),
                "available_spots": total_avail,
                "occupied_spots" : total_cap - total_avail,
                "status"         : _get_status(occ),
            })

        return jsonify({"success": True, "forecast": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/history")
def api_history():
    try:
        hours  = int(request.args.get("hours", 48))
        recent = df.tail(hours)

        records = []
        for _, row in recent.iterrows():
            records.append({
                "timestamp"      : str(row["timestamp"]),
                "hour"           : int(row["hour"]),
                "total_occupancy": float(row["total_occupancy"]),
                "total_available": int(row["total_available"]),
                "total_occupied" : int(row["total_occupied"]),
                "weather"        : str(row["weather"]),
                "event"          : int(row["event"]),
                "mall_occupancy" : float(row["mall_occupancy"]),
                "office_occupancy": float(row["office_occupancy"]),
                "hospital_occupancy": float(row["hospital_occupancy"]),
            })

        return jsonify({"success": True, "data": records})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/stats")
def api_stats():
    try:
        days   = int(request.args.get("days", 30))
        recent = df.tail(days * 24)
        grp    = recent.groupby("hour")["total_occupancy"].mean()

        zone_stats = {}
        for zone in ZONES:
            zone_stats[zone] = {
                "avg_occupancy" : round(float(recent[f"{zone}_occupancy"].mean()), 3),
                "avg_available" : round(float(recent[f"{zone}_available"].mean()), 0),
                "capacity"      : int(recent[f"{zone}_capacity"].iloc[0]),
            }

        return jsonify({
            "success": True,
            "stats": {
                "avg_occupancy"  : round(float(recent["total_occupancy"].mean()), 3),
                "avg_available"  : round(float(recent["total_available"].mean()), 0),
                "peak_hour"      : int(grp.idxmax()),
                "low_hour"       : int(grp.idxmin()),
                "event_count"    : int(recent["event"].sum()),
                "total_capacity" : int(recent["total_capacity"].iloc[0]),
                "hourly_pattern" : {
                    int(k): round(float(v), 3)
                    for k, v in grp.items()
                },
                "zone_stats"     : zone_stats,
                "weather_breakdown": {
                    "clear"     : int((recent["weather"] == "clear").sum()),
                    "rain"      : int((recent["weather"] == "rain").sum()),
                    "heavy_rain": int((recent["weather"] == "heavy_rain").sum()),
                },
            },
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/zones")
def api_zones():
    """Get current status of all parking zones."""
    try:
        latest = df.iloc[-1]
        zones  = {}

        for zone in ZONES:
            occ       = float(latest[f"{zone}_occupancy"])
            cap       = int(latest[f"{zone}_capacity"])
            occupied  = int(latest[f"{zone}_occupied"])
            available = int(latest[f"{zone}_available"])

            zones[zone] = {
                "capacity" : cap,
                "occupied" : occupied,
                "available": available,
                "occupancy": round(occ, 3),
                "status"   : _get_status(occ),
            }

        return jsonify({"success": True, "zones": zones})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ── Main ───────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("\n============================")
    print("  Parking Prediction API")
    print("============================")
    print(f"Model ready : {MODEL_READY}")
    print(f"Data rows   : {len(df)}")
    print(f"URL         : http://localhost:{port}")
    print("============================\n")
    app.run(debug=True, host="0.0.0.0", port=port)