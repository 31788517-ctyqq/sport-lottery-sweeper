@echo off
cd /d c:\Users\11581\Downloads\sport-lottery-sweeper\backend

sqlite3 sport_lottery.db "DELETE FROM football_matches;"

sqlite3 sport_lottery.db "INSERT INTO football_matches (match_id, home_team, away_team, match_time, league, status, odds_home_win, odds_draw, odds_away_win, popularity, created_at) VALUES ('周一001', '北京国安', '上海申花', '2026-01-27 19:35:00', '中超', '未开始', 2.15, 3.20, 2.85, 8500, datetime('now'));"

sqlite3 sport_lottery.db "INSERT INTO football_matches (match_id, home_team, away_team, match_time, league, status, odds_home_win, odds_draw, odds_away_win, popularity, created_at) VALUES ('周一002', '山东泰山', '广州恒大', '2026-01-27 20:00:00', '中超', '未开始', 1.95, 3.40, 3.10, 9200, datetime('now'));"

sqlite3 sport_lottery.db "INSERT INTO football_matches (match_id, home_team, away_team, match_time, league, status, odds_home_win, odds_draw, odds_away_win, popularity, created_at) VALUES ('周二001', '江苏苏宁', '河南建业', '2026-01-28 15:30:00', '中超', '未开始', 2.40, 3.15, 2.60, 6800, datetime('now'));"

sqlite3 sport_lottery.db "INSERT INTO football_matches (match_id, home_team, away_team, match_time, league, status, odds_home_win, odds_draw, odds_away_win, popularity, created_at) VALUES ('周二002', '天津泰达', '重庆当代', '2026-01-28 19:35:00', '中超', '未开始', 2.80, 3.05, 2.35, 5400, datetime('now'));"

sqlite3 sport_lottery.db "INSERT INTO football_matches (match_id, home_team, away_team, match_time, league, status, odds_home_win, odds_draw, odds_away_win, popularity, created_at) VALUES ('周三001', '武汉卓尔', '石家庄永昌', '2026-01-29 19:35:00', '中超', '未开始', 2.10, 3.25, 2.90, 7200, datetime('now'));"

echo.
echo ✅ 第一步完成！已插入5场比赛
echo.
sqlite3 sport_lottery.db "SELECT match_id, home_team, away_team, match_time FROM football_matches ORDER BY match_time;"
echo.
pause
