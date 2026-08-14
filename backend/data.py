"""
Generate synthetic urban parking data.
Simulates realistic parking patterns for
6 parking zones in a city.
"""

import numpy as np
import pandas as pd
import os


def generate_data(days=365):
    np.random.seed(42)
    hours      = days * 24
    timestamps = pd.date_range(start="2023-01-01", periods=hours, freq="h")

    zones = {
        "mall"      : {"capacity": 500, "base_factor": 1.2},
        "hospital"  : {"capacity": 300, "base_factor": 0.9},
        "office"    : {"capacity": 400, "base_factor": 1.1},
        "station"   : {"capacity": 250, "base_factor": 1.0},
        "market"    : {"capacity": 200, "base_factor": 0.8},
        "airport"   : {"capacity": 600, "base_factor": 0.7},
    }

    rows = []
    for ts in timestamps:
        h  = ts.hour
        wd = ts.weekday()
        m  = ts.month

        # Base occupancy by hour
        if   0  <= h <  6:  base_occ = 0.10
        elif 6  <= h <  9:  base_occ = 0.55
        elif 9  <= h < 12:  base_occ = 0.75
        elif 12 <= h < 14:  base_occ = 0.85
        elif 14 <= h < 17:  base_occ = 0.70
        elif 17 <= h < 20:  base_occ = 0.90
        elif 20 <= h < 22:  base_occ = 0.65
        else:                base_occ = 0.20

        # Weekend effect
        weekend = 1.15 if wd >= 5 else 1.0

        # Season effect
        season = 1 + 0.1 * np.sin(2 * np.pi * (m - 3) / 12)

        # Weather
        weather_code   = np.random.choice([0, 1, 2], p=[0.6, 0.3, 0.1])
        weather_factor = {0: 1.0, 1: 0.85, 2: 0.70}[weather_code]
        weather_names  = {0: "clear", 1: "rain", 2: "heavy_rain"}

        # Event probability
        event = 1 if np.random.random() < 0.05 else 0
        event_factor = 1.3 if event else 1.0

        row = {
            "timestamp"   : ts,
            "hour"        : h,
            "day_of_week" : wd,
            "month"       : m,
            "is_weekend"  : int(wd >= 5),
            "weather_code": weather_code,
            "weather"     : weather_names[weather_code],
            "event"       : event,
        }

        total_capacity  = 0
        total_occupied  = 0
        total_available = 0

        for zone, info in zones.items():
            cap     = info["capacity"]
            factor  = info["base_factor"]

            # Zone specific patterns
            if zone == "office":
                z_occ = base_occ if 8 <= h <= 18 and wd < 5 else 0.15
            elif zone == "mall":
                z_occ = base_occ * (1.2 if wd >= 5 else 1.0)
            elif zone == "hospital":
                z_occ = 0.70 + np.random.normal(0, 0.05)
            elif zone == "station":
                z_occ = base_occ * 1.1 if h in [7,8,9,17,18,19] else base_occ * 0.6
            elif zone == "airport":
                z_occ = 0.60 + np.random.normal(0, 0.08)
            else:
                z_occ = base_occ

            # Apply all factors
            final_occ = z_occ * factor * weekend * season * weather_factor * event_factor
            final_occ = np.clip(final_occ + np.random.normal(0, 0.05), 0.05, 0.99)

            occupied  = int(cap * final_occ)
            available = cap - occupied

            row[f"{zone}_capacity"]   = cap
            row[f"{zone}_occupied"]   = occupied
            row[f"{zone}_available"]  = available
            row[f"{zone}_occupancy"]  = round(final_occ, 3)

            total_capacity  += cap
            total_occupied  += occupied
            total_available += available

        row["total_capacity"]   = total_capacity
        row["total_occupied"]   = total_occupied
        row["total_available"]  = total_available
        row["total_occupancy"]  = round(total_occupied / total_capacity, 3)

        rows.append(row)

    df = pd.DataFrame(rows)

    save_dir  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, "parking.csv")
    df.to_csv(save_path, index=False)
    print(f"Generated {len(df)} records -> {save_path}")
    return df


def load_data():
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data", "parking.csv"
    )
    if not os.path.exists(path):
        print("No data found - generating...")
        return generate_data()
    df = pd.read_csv(path, parse_dates=["timestamp"])
    print(f"Loaded {len(df)} records")
    return df


if __name__ == "__main__":
    generate_data(days=365)
    print("Done!")