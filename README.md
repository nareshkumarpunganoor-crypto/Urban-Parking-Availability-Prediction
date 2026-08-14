# 🅿️ Urban Parking Availability Prediction

<p align="center">

**AI-Powered Smart Parking Prediction System**

Predict parking availability, monitor occupancy, analyze parking zones, and forecast future parking demand using Machine Learning.

</p>

<p align="center">

[![Live Demo](https://img.shields.io/badge/🚀%20Live%20Demo-Urban%20Parking-success?style=for-the-badge)](https://urban-parking-availability-prediction.onrender.com)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?style=for-the-badge\&logo=github)](https://github.com/nareshkumarpunganoor-crypto/Urban-Parking-Availability-Prediction)

</p>

---

## 🌐 Live Demo

🚀 **Try the application here:**

👉 https://urban-parking-availability-prediction.onrender.com

The deployed application provides a dashboard for monitoring parking availability, viewing parking zones, checking forecasts, reviewing historical data, and predicting parking availability.

---

## 📸 Screenshots

### 🏠 Dashboard

![Urban Parking Dashboard](images/dashboard.png)

The dashboard provides an overview of parking availability, occupancy, total capacity, peak hours, events, and overall parking status.

### 🅿️ Parking Zones

![Parking Zones](images/zones.png)

View the availability and occupancy status of different parking zones.

### 📈 Parking Forecast

![Parking Forecast](images/forecast.png)

View the predicted parking availability for upcoming hours.

### 🕐 Parking History

![Parking History](images/history.png)

Analyze historical parking availability along with weather and event information.

### 🔮 Parking Predictor

![Parking Predictor](images/predictor.png)

Enter factors such as hour, day, weather, and special events to predict parking availability.

> **Note:** Add your actual application screenshots to the `images` folder using the filenames shown above.

---

## 📌 Project Overview

Finding available parking in busy urban areas is a major challenge. Drivers may spend significant time searching for parking, resulting in increased traffic congestion, fuel consumption, and unnecessary emissions.

**Urban Parking Availability Prediction** is a Machine Learning-based web application designed to predict parking availability and provide useful insights into parking occupancy.

The system analyzes factors such as:

* 🕐 Time of day
* 📅 Day of the week
* 🌤️ Weather conditions
* 🎪 Special events
* 🅿️ Parking-zone information
* 📊 Historical parking data

The application then provides parking availability predictions and forecasts to support smarter parking decisions.

---

## 🎯 Objectives

* Predict parking-space availability.
* Monitor parking occupancy.
* Analyze multiple parking zones.
* Forecast future parking availability.
* Identify peak parking hours.
* Analyze the effect of weather and events.
* Reduce the time spent searching for parking.
* Support intelligent and sustainable urban transportation.

---

## ✨ Key Features

### 📊 Dashboard

Provides a centralized view of the parking system, including:

* Total available spaces
* Occupancy percentage
* Total parking capacity
* Peak hour
* Events
* Overall parking status

The live application currently exposes these dashboard metrics.

### 🅿️ Parking Zone Monitoring

The system monitors parking availability across multiple zones.

The application is designed to train an ML model for **6 parking zones**.

### 📈 24-Hour Forecast

Provides predicted parking availability for upcoming hours, including:

* Available spots
* Occupied spots
* Occupancy percentage
* Parking status

### 🕐 Historical Analysis

Historical parking information can be analyzed using:

* Timestamp
* Available spaces
* Occupancy percentage
* Weather
* Events

### 🔮 Parking Predictor

Users can provide:

* Hour
* Day of week
* Weather condition
* Special event

The system then predicts parking availability.

### 🧠 Machine Learning

The application includes functionality for training an ML model to predict parking availability.

---

## 🏗️ System Architecture

```text
              ┌──────────────────────┐
              │        User          │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │     Web Dashboard    │
              │  HTML/CSS/JavaScript │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │      Flask API       │
              │       Backend        │
              └──────────┬───────────┘
                         │
              ┌──────────┴───────────┐
              ▼                      ▼
     ┌─────────────────┐    ┌─────────────────┐
     │ Parking Dataset │    │ ML Prediction   │
     │ Historical Data │    │     Model       │
     └─────────────────┘    └────────┬────────┘
                                    │
                                    ▼
                         ┌────────────────────┐
                         │ Parking Prediction │
                         │ & Forecast Results │
                         └────────────────────┘
```

---

## 🛠️ Technologies Used

### Frontend

* HTML5
* CSS3
* JavaScript
* Chart.js

### Backend

* Python
* Flask

### Machine Learning

* Machine Learning
* Data preprocessing
* Predictive modeling
* Historical data analysis

### Deployment

* Render
* Gunicorn
* Procfile

The GitHub repository contains separate `backend` and `frontend` folders along with deployment configuration such as `Procfile`, `render.yaml`, `requirements.txt`, `run.py`, and `runtime.txt`.

---

## 📂 Project Structure

```text
Urban-Parking-Availability-Prediction/
│
├── backend/
│   ├── Application files
│   └── ML / prediction logic
│
├── frontend/
│   ├── HTML files
│   ├── CSS files
│   └── JavaScript files
│
├── images/
│   ├── dashboard.png
│   ├── zones.png
│   ├── forecast.png
│   ├── history.png
│   └── predictor.png
│
├── chart.min.js
├── requirements.txt
├── Procfile
├── render.yaml
├── run.py
├── runtime.txt
├── .gitignore
└── README.md
```

---

## ⚙️ How It Works

### Step 1 — Data Collection

Parking-related historical data is collected with information such as time, weather, events, and parking occupancy.

### Step 2 — Data Processing

The backend processes the input data and prepares it for the ML model.

### Step 3 — Model Training

The ML model learns patterns from historical parking data.

### Step 4 — Prediction

The model predicts parking availability based on user-provided conditions.

### Step 5 — Forecast

The system generates future parking availability forecasts.

### Step 6 — Visualization

Results are displayed through the web dashboard using charts, tables, and parking-status indicators.

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/nareshkumarpunganoor-crypto/Urban-Parking-Availability-Prediction.git
```

### 2. Open the Project

```bash
cd Urban-Parking-Availability-Prediction
```

### 3. Create Virtual Environment

```bash
python -m venv venv
```

### 4. Activate Virtual Environment

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Application

```bash
python run.py
```

Open the local URL shown in the terminal.

---

## 🌐 Deployment

The application is deployed using **Render**.

### Live Application

👉 **https://urban-parking-availability-prediction.onrender.com**

### GitHub Repository

👉 **https://github.com/nareshkumarpunganoor-crypto/Urban-Parking-Availability-Prediction**

---

## 📊 Prediction Inputs

| Input            | Description                        |
| ---------------- | ---------------------------------- |
| 🕐 Hour          | Hour of the day                    |
| 📅 Day           | Day of the week                    |
| 🌤️ Weather      | Current/expected weather condition |
| 🎪 Special Event | Whether an event is occurring      |
| 🅿️ Zone         | Parking zone being analyzed        |

---

## 📈 Prediction Outputs

The system can provide:

* 🅿️ Available parking spaces
* 🚗 Occupied parking spaces
* 📊 Occupancy percentage
* 🚦 Parking status
* 📈 Future availability forecast
* 🕐 Peak-hour information

---

## 🌆 Applications

This project can be used for:

* Smart city parking
* Shopping mall parking
* Airport parking
* College/university parking
* Office parking
* Public parking facilities
* Urban transportation management
* Intelligent transportation systems

---

## 🔮 Future Enhancements

* 📍 GPS-based nearest parking recommendation
* 📷 Real-time CCTV parking detection
* 📱 Android/iOS mobile application
* 🔔 Parking availability notifications
* 🗺️ Interactive parking map
* 🚗 Automatic parking-slot detection
* 🤖 Advanced Deep Learning models
* ☁️ Real-time cloud database
* 📊 Advanced analytics dashboard
* 🚦 Integration with smart-city traffic systems

---

## 👨‍💻 Author

### Naresh Kumar Punganoor

**B.Tech – Artificial Intelligence & Data Science**

Interested in **Data Analytics, Machine Learning, Artificial Intelligence, and Smart City Applications**.

---

## ⭐ Support

If you find this project useful, please consider giving the repository a ⭐ on GitHub.

### 🔗 Project Links

**Live Demo:**
https://urban-parking-availability-prediction.onrender.com

**GitHub Repository:**
https://github.com/nareshkumarpunganoor-crypto/Urban-Parking-Availability-Prediction

---

## 📜 License

This project is developed for **educational and academic purposes**.
