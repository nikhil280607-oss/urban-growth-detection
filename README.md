# Urban Growth Detection System

Change Detection from Multi-Temporal Satellite Images

**Course:** AI212 — Artificial Intelligence  
**Institute:** IIT Ropar  
**Student:** I Nikhil RM Varma (2024AIB1350)  
**Department:** AI & Data Engineering

---

## What This Project Does

Upload any two satellite images (same location at different times, or two different regions) and the system automatically detects and visualises the changes using image processing and machine learning.

**Example:** Gurugram, India — 1985 vs 2025 → 25.91% area changed, classified as Significant Urban Growth.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite |
| Backend | FastAPI (Python) |
| CV Pipeline | OpenCV, NumPy, SciPy |
| ML | scikit-learn (KMeans) |
| Containers | Docker + Docker Compose |
| Gen AI | Google Gemini API |

---

## How to Run

### Option 1 — Docker (Recommended)
```bash
docker compose up --build
```
Open http://localhost:5173

### Option 2 — Local
```bash
# Terminal 1
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 2
cd frontend
npm install
npm run dev
```

---

## Project Structure

```
urban-growth-detection/
├── backend/
│   ├── main.py
│   ├── models/change_detector.py
│   ├── utils/image_utils.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   └── package.json
├── docker-compose.yml
└── setup.sh
```
