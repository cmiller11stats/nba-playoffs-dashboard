"""
data_loader.py
--------------
Fetches NBA game data via nba_api and caches results to disk as JSON.
Falls back to bundled sample data when the API is unreachable.
"""

import json
import os
import time
from pathlib import Path

CACHE_DIR = Path(__file__).parent / "data"
CACHE_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Sample data – 2024 NBA Finals, Game 1: Celtics 107 @ Mavericks 89 (Jun 6 2024)
# game_id = "0042300401"
# ---------------------------------------------------------------------------
SAMPLE_GAME = {
    "game_id": "0042300401",
    "game_date": "June 6, 2024",
    "season": "2023-24",
    "series_info": "NBA Finals – Game 1",
    "arena": "American Airlines Center, Dallas TX",
    "home_team": {
        "team_id": 1610612742,
        "abbreviation": "DAL",
        "name": "Dallas Mavericks",
        "city": "Dallas",
        "color": "#00538C",
        "secondary_color": "#B8C4CA",
    },
    "away_team": {
        "team_id": 1610612738,
        "abbreviation": "BOS",
        "name": "Boston Celtics",
        "city": "Boston",
        "color": "#007A33",
        "secondary_color": "#BA9653",
    },
    "line_score": {
        "home": {"q1": 27, "q2": 20, "q3": 17, "q4": 25, "total": 89},
        "away": {"q1": 28, "q2": 29, "q3": 24, "q4": 26, "total": 107},
    },
    "home_players": [
        {"name": "Luka Doncic",     "position": "PG", "min": "38:00", "pts": 30, "reb": 7, "ast": 4, "stl": 1, "blk": 0, "fg": "10-23", "fg3": "3-9",  "ft": "7-8",  "to": 5, "pf": 2, "pm": -17},
        {"name": "Kyrie Irving",    "position": "SG", "min": "36:00", "pts": 22, "reb": 4, "ast": 7, "stl": 1, "blk": 0, "fg": "8-17",  "fg3": "2-6",  "ft": "4-4",  "to": 2, "pf": 2, "pm": -11},
        {"name": "Dereck Lively",   "position": "C",  "min": "19:00", "pts":  6, "reb": 7, "ast": 1, "stl": 0, "blk": 2, "fg": "3-4",   "fg3": "0-0",  "ft": "0-0",  "to": 1, "pf": 4, "pm":  -5},
        {"name": "P.J. Washington", "position": "PF", "min": "32:00", "pts": 12, "reb": 6, "ast": 2, "stl": 0, "blk": 1, "fg": "5-11",  "fg3": "2-5",  "ft": "0-0",  "to": 0, "pf": 2, "pm":  -6},
        {"name": "Josh Green",      "position": "SF", "min": "24:00", "pts":  4, "reb": 2, "ast": 0, "stl": 1, "blk": 0, "fg": "2-5",   "fg3": "0-2",  "ft": "0-0",  "to": 0, "pf": 1, "pm":  -8},
        {"name": "Daniel Gafford",  "position": "C",  "min": "18:00", "pts":  5, "reb": 4, "ast": 1, "stl": 0, "blk": 0, "fg": "2-4",   "fg3": "0-0",  "ft": "1-2",  "to": 0, "pf": 4, "pm":  -9},
        {"name": "Maxi Kleber",     "position": "PF", "min": "14:00", "pts":  4, "reb": 2, "ast": 0, "stl": 0, "blk": 1, "fg": "2-3",   "fg3": "0-1",  "ft": "0-0",  "to": 0, "pf": 1, "pm":  -4},
        {"name": "Tim Hardaway Jr", "position": "SG", "min": "16:00", "pts":  4, "reb": 1, "ast": 2, "stl": 0, "blk": 0, "fg": "2-6",   "fg3": "0-3",  "ft": "0-0",  "to": 0, "pf": 0, "pm": -10},
        {"name": "Dwight Powell",   "position": "C",  "min": " 3:00", "pts":  2, "reb": 0, "ast": 0, "stl": 0, "blk": 0, "fg": "1-1",   "fg3": "0-0",  "ft": "0-0",  "to": 0, "pf": 0, "pm":  -1},
    ],
    "away_players": [
        {"name": "Jayson Tatum",    "position": "SF", "min": "38:00", "pts": 23, "reb": 11, "ast": 8, "stl": 0, "blk": 2, "fg": "8-21",  "fg3": "1-6",  "ft": "6-8",  "to": 1, "pf": 2, "pm": +20},
        {"name": "Jaylen Brown",    "position": "SG", "min": "38:00", "pts": 22, "reb":  5, "ast": 4, "stl": 2, "blk": 0, "fg": "9-17",  "fg3": "1-4",  "ft": "3-4",  "to": 0, "pf": 1, "pm": +12},
        {"name": "Jrue Holiday",    "position": "PG", "min": "35:00", "pts": 13, "reb":  3, "ast": 7, "stl": 3, "blk": 1, "fg": "5-11",  "fg3": "1-3",  "ft": "2-2",  "to": 0, "pf": 1, "pm": +19},
        {"name": "Al Horford",      "position": "C",  "min": "28:00", "pts": 17, "reb":  9, "ast": 2, "stl": 0, "blk": 4, "fg": "6-11",  "fg3": "3-6",  "ft": "2-2",  "to": 1, "pf": 2, "pm": +20},
        {"name": "Derrick White",   "position": "SG", "min": "30:00", "pts": 12, "reb":  5, "ast": 5, "stl": 1, "blk": 0, "fg": "4-11",  "fg3": "2-5",  "ft": "2-2",  "to": 0, "pf": 2, "pm": +16},
        {"name": "Kristaps Porzingis","position": "C","min": "18:00", "pts": 11, "reb":  5, "ast": 0, "stl": 0, "blk": 1, "fg": "4-8",   "fg3": "1-3",  "ft": "2-4",  "to": 2, "pf": 4, "pm":  +3},
        {"name": "Sam Hauser",      "position": "SF", "min": "18:00", "pts":  6, "reb":  2, "ast": 1, "stl": 0, "blk": 0, "fg": "2-5",   "fg3": "2-4",  "ft": "0-0",  "to": 0, "pf": 0, "pm":  +8},
        {"name": "Payton Pritchard","position": "PG", "min": "14:00", "pts":  3, "reb":  0, "ast": 2, "stl": 0, "blk": 0, "fg": "1-4",   "fg3": "1-3",  "ft": "0-0",  "to": 0, "pf": 1, "pm":  +3},
    ],
    "quarter_leaders": {
        "q1": {
            "home": {"name": "Luka Doncic",  "pts": 11},
            "away": {"name": "Jayson Tatum", "pts": 9},
        },
        "q2": {
            "home": {"name": "Kyrie Irving", "pts": 9},
            "away": {"name": "Jaylen Brown", "pts": 11},
        },
        "q3": {
            "home": {"name": "Luka Doncic",  "pts": 8},
            "away": {"name": "Jrue Holiday", "pts": 7},
        },
        "q4": {
            "home": {"name": "Luka Doncic",  "pts": 11},
            "away": {"name": "Jayson Tatum", "pts": 8},
        },
    },
    "game_notes": {
        "q1": "The Celtics opened on a 10-2 run before Dallas answered. Tatum and Horford combined for 15 first-quarter points while Luka Doncic kept Dallas within striking distance with 11.",
        "q2": "Boston seized momentum in the second quarter, outscoring Dallas 29-20 behind balanced scoring from Tatum, Brown, and Holiday. The Celtics entered halftime with a 57-47 lead.",
        "q3": "Despite an 8-point Doncic quarter, Boston maintained control as Horford anchored the paint and Jrue Holiday kept the defense stingy. Celtics led 81-64 heading into the fourth.",
        "q4": "Dallas cut into the deficit behind a Doncic flurry, but Boston's bench depth and clutch shooting sealed a comfortable 107-89 victory and a commanding Game 1 win.",
    },
}


# ---------------------------------------------------------------------------
# nba_api helpers
# ---------------------------------------------------------------------------

import re

# NBA game IDs are always exactly 10 decimal digits.
_GAME_ID_RE = re.compile(r'^\d{10}$')


def _validate_game_id(game_id: str) -> str:
    """Raise ValueError if game_id is not a safe 10-digit NBA game ID string."""
    if not _GAME_ID_RE.match(game_id):
        raise ValueError(f"Invalid game_id: {game_id!r}")
    return game_id


def _cache_path(game_id: str) -> Path:
    return CACHE_DIR / f"game_{_validate_game_id(game_id)}.json"


def _load_cache(game_id: str) -> dict | None:
    p = _cache_path(game_id)
    if p.exists():
        return json.loads(p.read_text())
    return None


def _save_cache(game_id: str, data: dict) -> None:
    _cache_path(game_id).write_text(json.dumps(data, indent=2))


def _fetch_from_api(game_id: str) -> dict | None:
    """Attempt to fetch game data from stats.nba.com. Returns None on failure."""
    try:
        from nba_api.stats.endpoints import (
            boxscoresummaryv2,
            boxscoretraditionalv2,
        )
        from nba_api.stats.static import teams as nba_teams

        time.sleep(0.6)  # respect rate limit

        summary_ep = boxscoresummaryv2.BoxScoreSummaryV2(game_id=game_id, timeout=15)
        summary_dfs = summary_ep.get_data_frames()
        game_summary = summary_dfs[0].iloc[0]
        line_score_df = summary_dfs[5]

        time.sleep(0.6)
        box_ep = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id, timeout=15)
        box_dfs = box_ep.get_data_frames()
        team_df = box_dfs[1]
        player_df = box_dfs[0]

        # Build line score
        home_row = line_score_df[line_score_df["TEAM_ABBREVIATION"] == game_summary["HOME_TEAM_ABBREVIATION"]].iloc[0]
        away_row = line_score_df[line_score_df["TEAM_ABBREVIATION"] == game_summary["VISITOR_TEAM_ABBREVIATION"]].iloc[0]

        def parse_line(row):
            return {
                "q1": int(row.get("PTS_QTR1", 0) or 0),
                "q2": int(row.get("PTS_QTR2", 0) or 0),
                "q3": int(row.get("PTS_QTR3", 0) or 0),
                "q4": int(row.get("PTS_QTR4", 0) or 0),
                "total": int(row.get("PTS", 0) or 0),
            }

        # Team color lookup (approximate)
        TEAM_COLORS = {
            "BOS": "#007A33", "LAL": "#552583", "MIA": "#98002E",
            "GSW": "#1D428A", "DAL": "#00538C", "DEN": "#0E2240",
            "MIL": "#00471B", "PHX": "#1D1160", "CLE": "#860038",
            "NYK": "#006BB6", "MIN": "#236192", "OKC": "#007AC1",
            "IND": "#002D62", "MEM": "#5D76A9", "NOP": "#0C2340",
            "SAC": "#5A2D81", "ATL": "#E03A3E", "CHI": "#CE1141",
            "TOR": "#CE1141", "HOU": "#CE1141", "SAS": "#C4CED4",
            "POR": "#E03A3E", "UTA": "#002B5C", "ORL": "#0077C0",
            "BKN": "#000000", "CHA": "#1D1160", "DET": "#C8102E",
            "LAC": "#C8102E", "WAS": "#002B5C", "PHI": "#006BB6",
        }

        def build_team(row, summary_row, key):
            abbr = summary_row[f"{key}_TEAM_ABBREVIATION"] if f"{key}_TEAM_ABBREVIATION" in summary_row.index else row["TEAM_ABBREVIATION"]
            city = summary_row.get(f"{key}_TEAM_CITY", "") or ""
            name = summary_row.get(f"{key}_TEAM_NICKNAME", "") or row.get("TEAM_NAME", abbr)
            return {
                "team_id": int(summary_row.get(f"{key}_TEAM_ID", 0) or 0),
                "abbreviation": abbr,
                "name": f"{city} {name}".strip(),
                "city": city,
                "color": TEAM_COLORS.get(abbr, "#1a1a2e"),
                "secondary_color": "#cccccc",
            }

        def build_players(team_abbr):
            rows = player_df[player_df["TEAM_ABBREVIATION"] == team_abbr]
            players = []
            for _, p in rows.iterrows():
                fg_m = int(p.get("FGM", 0) or 0)
                fg_a = int(p.get("FGA", 0) or 0)
                fg3_m = int(p.get("FG3M", 0) or 0)
                fg3_a = int(p.get("FG3A", 0) or 0)
                ft_m = int(p.get("FTM", 0) or 0)
                ft_a = int(p.get("FTA", 0) or 0)
                players.append({
                    "name": str(p.get("PLAYER_NAME", "")),
                    "position": str(p.get("START_POSITION", "")).strip() or "—",
                    "min": str(p.get("MIN", "0:00")),
                    "pts": int(p.get("PTS", 0) or 0),
                    "reb": int(p.get("REB", 0) or 0),
                    "ast": int(p.get("AST", 0) or 0),
                    "stl": int(p.get("STL", 0) or 0),
                    "blk": int(p.get("BLK", 0) or 0),
                    "fg": f"{fg_m}-{fg_a}",
                    "fg3": f"{fg3_m}-{fg3_a}",
                    "ft": f"{ft_m}-{ft_a}",
                    "to": int(p.get("TO", 0) or 0),
                    "pf": int(p.get("PF", 0) or 0),
                    "pm": int(p.get("PLUS_MINUS", 0) or 0),
                })
            return sorted(players, key=lambda x: x["pts"], reverse=True)

        home_abbr = game_summary["HOME_TEAM_ABBREVIATION"]
        away_abbr = game_summary["VISITOR_TEAM_ABBREVIATION"]
        home_players = build_players(home_abbr)
        away_players = build_players(away_abbr)

        # Quarter leaders
        def quarter_leader(players, q_key):
            # We don't have per-quarter player splits in this endpoint; approximate
            best = max(players, key=lambda p: p["pts"]) if players else {"name": "—", "pts": 0}
            return {"name": best["name"], "pts": best["pts"]}

        data = {
            "game_id": game_id,
            "game_date": str(game_summary.get("GAME_DATE_EST", "")).split("T")[0],
            "season": str(game_summary.get("SEASON", "")),
            "series_info": f"NBA Playoffs – {game_id}",
            "arena": str(game_summary.get("ARENA_NAME", "")),
            "home_team": build_team(home_row, game_summary, "HOME"),
            "away_team": build_team(away_row, game_summary, "VISITOR"),
            "line_score": {
                "home": parse_line(home_row),
                "away": parse_line(away_row),
            },
            "home_players": home_players,
            "away_players": away_players,
            "quarter_leaders": {
                f"q{q}": {
                    "home": quarter_leader(home_players, f"q{q}"),
                    "away": quarter_leader(away_players, f"q{q}"),
                }
                for q in range(1, 5)
            },
            "game_notes": {
                "q1": "First quarter highlights.",
                "q2": "Second quarter highlights.",
                "q3": "Third quarter highlights.",
                "q4": "Fourth quarter highlights.",
            },
        }
        return data

    except Exception as exc:  # noqa: BLE001
        print(f"[data_loader] API fetch failed for {game_id}: {exc}")
        return None


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def get_game_data(game_id: str | None = None) -> dict:
    """
    Return game data dict.
    Priority: 1) disk cache  2) live API  3) sample data
    """
    if game_id is None:
        game_id = SAMPLE_GAME["game_id"]

    # Try cache first
    cached = _load_cache(game_id)
    if cached:
        return cached

    # Try live API
    live = _fetch_from_api(game_id)
    if live:
        _save_cache(game_id, live)
        return live

    # Fall back to sample data (or minimal skeleton if unknown id)
    if game_id == SAMPLE_GAME["game_id"]:
        _save_cache(game_id, SAMPLE_GAME)
        return SAMPLE_GAME

    # Unknown game_id with no cache and no API: return sample with id replaced
    fallback = dict(SAMPLE_GAME)
    fallback["game_id"] = game_id
    fallback["series_info"] = f"NBA Playoffs – Game {game_id}"
    return fallback


def list_cached_games() -> list[dict]:
    """Return a list of cached game summaries for the game-selector page."""
    games = []
    for p in sorted(CACHE_DIR.glob("game_*.json"), reverse=True):
        try:
            d = json.loads(p.read_text())
            games.append({
                "game_id": d.get("game_id"),
                "game_date": d.get("game_date"),
                "series_info": d.get("series_info"),
                "home": d.get("home_team", {}).get("abbreviation"),
                "away": d.get("away_team", {}).get("abbreviation"),
                "home_pts": d.get("line_score", {}).get("home", {}).get("total"),
                "away_pts": d.get("line_score", {}).get("away", {}).get("total"),
            })
        except Exception:  # noqa: BLE001
            pass
    # Always include sample game
    sample_id = SAMPLE_GAME["game_id"]
    if not any(g["game_id"] == sample_id for g in games):
        games.append({
            "game_id": sample_id,
            "game_date": SAMPLE_GAME["game_date"],
            "series_info": SAMPLE_GAME["series_info"],
            "home": SAMPLE_GAME["home_team"]["abbreviation"],
            "away": SAMPLE_GAME["away_team"]["abbreviation"],
            "home_pts": SAMPLE_GAME["line_score"]["home"]["total"],
            "away_pts": SAMPLE_GAME["line_score"]["away"]["total"],
        })
    return games


def get_scoreboard_for_date(date_str: str) -> list[dict]:
    """Return game summaries for a given date (YYYY-MM-DD). Caches completed past dates."""
    from datetime import datetime, date as _date

    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return []

    cache_path = CACHE_DIR / f"scoreboard_{date_str}.json"
    today = _date.today()

    # Serve from cache for past dates (results are final)
    if dt < today and cache_path.exists():
        try:
            return json.loads(cache_path.read_text())
        except Exception:
            pass

    try:
        from nba_api.stats.endpoints import scoreboardv2

        time.sleep(0.6)
        sb = scoreboardv2.ScoreboardV2(
            game_date=dt.strftime("%m/%d/%Y"),
            league_id="00",
            day_offset=0,
            timeout=15,
        )
        dfs = sb.get_data_frames()
        header_df = dfs[0]
        line_df = dfs[1]
        series_df = dfs[2] if len(dfs) > 2 else None

        def _safe_int(val):
            try:
                if val is None:
                    return None
                f = float(val)
                return None if f != f else int(f)  # NaN guard
            except (TypeError, ValueError):
                return None

        def _team_name(ls, abbr):
            if ls is None:
                return abbr
            city = str(ls["TEAM_CITY_NAME"]) if "TEAM_CITY_NAME" in ls.index else ""
            nick = str(ls["TEAM_NICKNAME"]) if "TEAM_NICKNAME" in ls.index else abbr
            return f"{city} {nick}".strip() or abbr

        games = []
        for _, hrow in header_df.iterrows():
            gid = str(hrow["GAME_ID"])
            status = str(hrow.get("GAME_STATUS_TEXT", "")).strip()
            home_tid = _safe_int(hrow.get("HOME_TEAM_ID"))
            away_tid = _safe_int(hrow.get("VISITOR_TEAM_ID"))

            gls = line_df[line_df["GAME_ID"] == gid]
            home_rows = gls[gls["TEAM_ID"] == home_tid] if home_tid is not None else gls.iloc[0:0]
            away_rows = gls[gls["TEAM_ID"] == away_tid] if away_tid is not None else gls.iloc[0:0]
            hls = home_rows.iloc[0] if not home_rows.empty else None
            als = away_rows.iloc[0] if not away_rows.empty else None

            home_abbr = str(hls["TEAM_ABBREVIATION"]) if hls is not None else "HOM"
            away_abbr = str(als["TEAM_ABBREVIATION"]) if als is not None else "AWY"
            home_pts = _safe_int(hls["PTS"] if hls is not None else None)
            away_pts = _safe_int(als["PTS"] if als is not None else None)

            # Build series standing label
            series_info = "NBA Playoffs"
            if series_df is not None and not series_df.empty and "GAME_ID" in series_df.columns:
                sr_rows = series_df[series_df["GAME_ID"] == gid]
                if not sr_rows.empty:
                    sr = sr_rows.iloc[0]
                    hw = _safe_int(sr.get("HOME_TEAM_WINS")) or 0
                    hl = _safe_int(sr.get("HOME_TEAM_LOSSES")) or 0
                    leader = str(sr.get("SERIES_LEADER", "")).strip()
                    if leader and leader.lower() not in ("", "nan"):
                        w, l = max(hw, hl), min(hw, hl)
                        series_info = (
                            f"{leader} leads {w}\u20133{l}"
                            if w != l
                            else f"Series tied {w}\u2013{w}"
                        )
                    elif hw + hl > 0:
                        series_info = f"Series {hw}\u2013{hl}"

            games.append({
                "game_id": gid,
                "game_date": date_str,
                "series_info": series_info,
                "home": home_abbr,
                "away": away_abbr,
                "home_name": _team_name(hls, home_abbr),
                "away_name": _team_name(als, away_abbr),
                "home_pts": home_pts,
                "away_pts": away_pts,
                "status": status,
            })

        # Cache completed past dates
        if games and dt < today:
            cache_path.write_text(json.dumps(games, indent=2))

        return games

    except Exception as exc:
        print(f"[data_loader] Scoreboard fetch failed for {date_str}: {exc}")
        return []
