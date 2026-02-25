from backend.api.v1.admin import lottery_schedule as ls


def test_map_yingqiu_dom_row_extracts_full_and_half_scores():
    row = {
        "number": "1",
        "source_match_id": "114486949",
        "league_name": "UCL",
        "home_team": "Atletico",
        "away_team": "ClubBrugge",
        "kickoff_text": "02-25 01:45",
        "status_des": "finished",
        "score_text": "4 - 1",
        "half_score_text": "1 - 1",
        "handicap": "-1",
        "odds_win": "2.15",
        "odds_draw": "3.51",
        "odds_lose": "3.98",
    }

    mapped = ls._map_yingqiu_dom_row(row, "2026-02-24", "https://www.ttyingqiu.com/bjdc")

    assert mapped["home_score"] == 4
    assert mapped["away_score"] == 1
    assert mapped["halftime_score"] == "1-1"
    assert mapped["kickoff"].strftime("%Y-%m-%d %H:%M") == "2026-02-25 01:45"


def test_map_yingqiu_match_supports_half_full_score_array_order():
    item = {
        "matchNoCn": "1",
        "matchId": 6032553,
        "matchDate": "2026-02-25",
        "matchTime": "01:45",
        "leagueName": "UCL",
        "homeName": "Atletico",
        "awayName": "ClubBrugge",
        "status": 2,
        "statusDes": "finished",
        "score": ["1:1", "4:1", "", ""],
        "oddsEurope": "1.39;5.40;7.20",
        "oddsAsia": "1.04;1.5;0.85",
        "oddsAsiaHandicapDesc": "1.5",
    }

    mapped = ls._map_yingqiu_match(item, "https://www.ttyingqiu.com/bjdc", "2026-02-24")

    assert mapped["home_score"] == 4
    assert mapped["away_score"] == 1
    assert mapped["halftime_score"] == "1-1"
