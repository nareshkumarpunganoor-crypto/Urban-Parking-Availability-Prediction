"""
Parking Availability Prediction Model.
Predicts next 24h parking availability
for 6 zones using Gradient Boosting.
"""

import os
import numpy as np
import pandas as pd
import joblib

from sklearn.ensemble      import GradientBoostingRegressor
from sklearn.multioutput   import MultiOutputRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline      import Pipeline
from sklearn.metrics       import mean_absolute_error, mean_squared_error

PRED_LEN = 24
HISTORY  = 24

ZONES = ["mall", "hospital", "office", "station", "market", "airport"]


def _make_features(df):
    rows = []
    occ  = df["total_occupancy"].values

    for i in range(HISTORY, len(df) - PRED_LEN):
        r = df.iloc[i]

        h_sin = np.sin(2 * np.pi * r["hour"]        / 24)
        h_cos = np.cos(2 * np.pi * r["hour"]        / 24)
        d_sin = np.sin(2 * np.pi * r["day_of_week"] / 7)
        d_cos = np.cos(2 * np.pi * r["day_of_week"] / 7)
        m_sin = np.sin(2 * np.pi * r["month"]       / 12)
        m_cos = np.cos(2 * np.pi * r["month"]       / 12)

        lags = occ[i - HISTORY : i]

        zone_occs = [r[f"{z}_occupancy"] for z in ZONES]

        row = np.concatenate([
            [h_sin, h_cos, d_sin, d_cos, m_sin, m_cos,
             r["is_weekend"], r["weather_code"], r["event"]],
            zone_occs,
            lags
        ])
        rows.append(row)

    return np.array(rows, dtype=np.float32)


def _make_targets(df):
    tgts = []
    for i in range(HISTORY, len(df) - PRED_LEN):
        future = df.iloc[i : i + PRED_LEN]
        tgts.append([
            future[f"{z}_occupancy"].mean()
            for z in ZONES
        ])
    return np.array(tgts, dtype=np.float32)


class ParkingModel:

    def __init__(self):
        self.pipeline   = None
        self.is_trained = False

    def build(self):
        base = GradientBoostingRegressor(
            n_estimators  = 100,
            max_depth     = 4,
            learning_rate = 0.1,
            subsample     = 0.8,
            random_state  = 42,
        )
        self.pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("model",  MultiOutputRegressor(base, n_jobs=-1)),
        ])
        print("Parking model pipeline ready.")

    def train(self, df):
        print("Building features...")
        X = _make_features(df)
        y = _make_targets(df)

        split    = int(len(X) * 0.85)
        X_tr, X_val = X[:split], X[split:]
        y_tr, y_val = y[:split], y[split:]

        print(f"Train: {len(X_tr)} | Val: {len(X_val)}")
        print("Fitting... (~20-40 seconds)")

        self.pipeline.fit(X_tr, y_tr)

        y_pred = self.pipeline.predict(X_val)
        mae    = mean_absolute_error(y_val, y_pred)
        rmse   = np.sqrt(mean_squared_error(y_val, y_pred))

        print(f"MAE={mae:.4f}  RMSE={rmse:.4f}")
        self.is_trained = True
        return {"mae": round(mae, 4), "rmse": round(rmse, 4)}

    def predict(self, df):
        try:
            tail = df.tail(HISTORY + 2).reset_index(drop=True)
            X    = _make_features(tail)

            if len(X) == 0:
                row      = df.iloc[-1]
                h_sin    = np.sin(2 * np.pi * row["hour"]        / 24)
                h_cos    = np.cos(2 * np.pi * row["hour"]        / 24)
                d_sin    = np.sin(2 * np.pi * row["day_of_week"] / 7)
                d_cos    = np.cos(2 * np.pi * row["day_of_week"] / 7)
                m_sin    = np.sin(2 * np.pi * row["month"]       / 12)
                m_cos    = np.cos(2 * np.pi * row["month"]       / 12)
                lags     = df["total_occupancy"].values[-HISTORY:]
                zone_occs= [row[f"{z}_occupancy"] for z in ZONES]
                X        = np.concatenate([
                    [h_sin, h_cos, d_sin, d_cos, m_sin, m_cos,
                     row["is_weekend"], row["weather_code"], row["event"]],
                    zone_occs, lags
                ]).reshape(1, -1).astype(np.float32)

            pred = self.pipeline.predict(X[-1:])[0]
            result = {}
            for i, zone in enumerate(ZONES):
                occ       = float(np.clip(pred[i], 0.05, 0.99))
                cap       = int(df[f"{zone}_capacity"].iloc[-1])
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

        except Exception as e:
            print(f"Predict error: {e}")
            raise

    def save(self, path=None):
        if path is None:
            path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "saved_model", "parking_model.pkl"
            )
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.pipeline, path)
        print(f"Model saved -> {path}")

    def load(self, path=None):
        if path is None:
            path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "saved_model", "parking_model.pkl"
            )
        if os.path.exists(path):
            self.pipeline   = joblib.load(path)
            self.is_trained = True
            print(f"Model loaded from {path}")
            return True
        print("No saved model found.")
        return False


def _get_status(occupancy):
    if   occupancy < 0.5:  return "Available"
    elif occupancy < 0.75: return "Filling"
    elif occupancy < 0.90: return "Almost Full"
    else:                  return "Full"


if __name__ == "__main__":
    from data import load_data
    df = load_data()
    m  = ParkingModel()
    m.build()
    m.train(df)
    m.save()
    print("Done!")