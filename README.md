# NBA Playoffs Dashboard

A **Flask** web app that tells the story of an NBA playoff game through a full-page scroll experience — think interactive blog meets box score.

## Features

- **Scroll-through sections**: Overview → Q1 → Q2 → Q3 → Q4 → Full Box Score  
- **Live NBA data** via [`nba_api`](https://github.com/swar/nba_api) with JSON disk-caching  
- **Offline sample data** (2024 NBA Finals Game 1) when the API is unreachable  
- **Cumulative scoring chart** and **per-quarter bar charts** powered by Chart.js  
- **Side navigation** with active-section highlighting  

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python app.py
# → open http://localhost:5000
```

The app opens a game-selector page. Click the pre-loaded sample game (2024 Finals G1) or enter any NBA `game_id` to load a different game.

## Project Structure

```
nba-playoffs-dashboard/
├── app.py            # Flask routes
├── data_loader.py    # nba_api fetching + JSON caching + sample data
├── requirements.txt
├── data/             # Cached game JSON files (auto-created)
├── templates/
│   ├── base.html
│   ├── index.html    # Game selector
│   └── game.html     # Full-page scroll dashboard
└── static/
    ├── css/style.css
    └── js/main.js    # Chart.js charts + scroll-nav
```

## Loading a Different Game

1. Find the NBA `game_id` (10-digit string, e.g. `0042300401`) from the NBA stats site.
2. Enter it in the selector page, or navigate directly to `/game/<game_id>`.
3. Data is fetched live on first load and cached to `data/game_<id>.json`.

## Running in Production

```bash
pip install gunicorn
gunicorn -w 2 -b 0.0.0.0:8000 app:app
```
