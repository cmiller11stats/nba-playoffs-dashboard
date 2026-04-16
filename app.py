"""
app.py
------
Flask application for the NBA Playoffs Dashboard.

Routes:
  GET /                   – game selector (lists cached games + sample)
  GET /game/<game_id>     – full-page scroll game dashboard
  GET /api/game/<game_id> – JSON data endpoint (useful for debugging)
  POST /fetch/<game_id>   – trigger a fresh API fetch and cache
"""

import os

from flask import Flask, render_template, jsonify, redirect, url_for, request, abort
from data_loader import get_game_data, list_cached_games, _validate_game_id

app = Flask(__name__)


@app.route("/")
def index():
    games = list_cached_games()
    return render_template("index.html", games=games)


@app.route("/game/<game_id>")
def game(game_id: str):
    try:
        _validate_game_id(game_id)
    except ValueError:
        abort(400)
    data = get_game_data(game_id)
    if not data:
        abort(404)

    # Pre-compute running score totals for cumulative chart
    ls = data["line_score"]
    cumulative = {
        "home": [],
        "away": [],
        "labels": ["Q1", "Q2", "Q3", "Q4"],
    }
    home_total = away_total = 0
    for q in ("q1", "q2", "q3", "q4"):
        home_total += ls["home"][q]
        away_total += ls["away"][q]
        cumulative["home"].append(home_total)
        cumulative["away"].append(away_total)

    # Quarter-by-quarter bar chart data
    quarter_bars = {
        "home": [ls["home"][q] for q in ("q1", "q2", "q3", "q4")],
        "away": [ls["away"][q] for q in ("q1", "q2", "q3", "q4")],
        "labels": ["Q1", "Q2", "Q3", "Q4"],
    }

    # Top scorers for each team (top 5)
    home_top = sorted(data["home_players"], key=lambda p: p["pts"], reverse=True)[:5]
    away_top = sorted(data["away_players"], key=lambda p: p["pts"], reverse=True)[:5]

    return render_template(
        "game.html",
        game=data,
        cumulative=cumulative,
        quarter_bars=quarter_bars,
        home_top=home_top,
        away_top=away_top,
    )


@app.route("/api/game/<game_id>")
def api_game(game_id: str):
    try:
        _validate_game_id(game_id)
    except ValueError:
        return jsonify({"error": "Invalid game_id"}), 400
    data = get_game_data(game_id)
    if not data:
        return jsonify({"error": "Game not found"}), 404
    return jsonify(data)


@app.route("/fetch/<game_id>", methods=["POST"])
def fetch_game(game_id: str):
    """Force a live API re-fetch for a given game_id."""
    from pathlib import Path
    import os

    try:
        _validate_game_id(game_id)
    except ValueError:
        abort(400)

    cache_file = Path(__file__).parent / "data" / f"game_{game_id}.json"
    if cache_file.exists():
        os.remove(cache_file)

    data = get_game_data(game_id)
    if data:
        return redirect(url_for("game", game_id=game_id))
    return jsonify({"error": "Could not fetch game data – check game_id or network"}), 502


if __name__ == "__main__":
    # Bind to loopback by default and prefer port 5000 unless overridden.
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5000"))
    app.run(debug=False, host=host, port=port)
