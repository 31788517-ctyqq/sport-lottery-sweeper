from fastapi import APIRouter, Query
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path as SysPath
import traceback
import logging
import json
import os

from backend.schemas.response import UnifiedResponse, PageResponse
from backend.core.cache_manager import get_cache_manager
from backend.scrapers.sporttery_scraper import sporttery_scraper

router = APIRouter(prefix="/lottery", tags=["Sports Lottery"])
logger = logging.getLogger(__name__)


def load_500_com_data(filter_day: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load 500.com data from debug directory."""
    try:
        project_root = SysPath(__file__).parent.parent.parent.parent
        debug_dir = project_root / "debug"
        if not debug_dir.exists():
            logger.warning(f"debug directory not found: {debug_dir}")
            return []
        files = [f for f in os.listdir(debug_dir) if f.startswith("500_com_matches_")]
        if not files:
            logger.info("No 500.com data files found")
            return []
        latest_file = sorted(files)[-1]
        file_path = debug_dir / latest_file
        with open(file_path, 'r', encoding='utf-8') as f:
            matches = json.load(f)

        matches = [m for m in matches if m.get('match_id') != '??']
        if filter_day:
            matches = [m for m in matches if m.get('match_id', '').startswith(filter_day)]

        formatted_matches = []
        for idx, m in enumerate(matches, 1):
            match_time = m.get("match_time", "")
            match_date = match_time.split(' ')[0] if match_time and ' ' in match_time else match_time
            formatted_matches.append({
                "id": idx,
                "match_id": m.get("match_id"),
                "league": m.get("league"),
                "home_team": m.get("home_team"),
                "away_team": m.get("away_team"),
                "match_time": match_time,
                "match_date": match_date,
                "odds_home_win": m.get("odds_home_win", 0),
                "odds_draw": m.get("odds_draw", 0),
                "odds_away_win": m.get("odds_away_win", 0),
                "status": m.get("status", "scheduled"),
                "score": m.get("score", "-:-"),
                "popularity": m.get("popularity", 70),
                "source": "500.com",
            })
        logger.info(f"Loaded 500.com data: {len(formatted_matches)} matches")
        return formatted_matches
    except Exception as e:
        logger.error(f"Failed to load 500.com data: {e}")
        return []


@router.get("/matches", response_model=UnifiedResponse[PageResponse[Dict[str, Any]]])
async def get_lottery_matches(
    page: int = Query(1, ge=1, description="page"),
    size: int = Query(10, ge=1, le=50, description="page size"),
    source: str = Query("auto", description="source: auto/500/sporttery"),
    date_from: Optional[str] = Query(None, description="start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="end date (YYYY-MM-DD)"),
    league: Optional[str] = Query(None, description="league filter"),
    day_filter: Optional[str] = Query(None, description="weekday filter"),
    sort: Optional[str] = Query("date", description="sort: date/popularity"),
    order: Optional[str] = Query("asc", description="order: asc/desc"),
) -> Dict[str, Any]:
    """Get lottery matches."""
    try:
        cache_manager = get_cache_manager()
        cache_key = f"jczq_v2:{source}:{page}:{size}:{date_from}:{date_to}:{league}:{day_filter}:{sort}:{order}"

        cached_data = await cache_manager.get(cache_key)
        if cached_data:
            logger.info(f"[cache hit] lottery matches (source={source})")
            matches = cached_data.get('matches', [])
            data_source = cached_data.get('source', 'cache')
        else:
            logger.info(f"[cache miss] fetch lottery matches (source={source})")
            matches = []
            data_source = "unknown"

            if source == "500":
                matches = load_500_com_data(filter_day=day_filter)
                data_source = "500.com"
            elif source == "sporttery":
                try:
                    async with sporttery_scraper:
                        raw_matches = await sporttery_scraper.get_recent_matches(7)
                    matches = [
                        {
                            "id": m.get('id', ''),
                            "match_date": m.get('match_date', ''),
                            "home_team": m.get('home_team', 'Home'),
                            "away_team": m.get('away_team', 'Away'),
                            "league": m.get('league', 'Unknown'),
                            "odds_home_win": m.get('odds_home_win', 0.0),
                            "odds_draw": m.get('odds_draw', 0.0),
                            "odds_away_win": m.get('odds_away_win', 0.0),
                            "popularity": m.get('popularity', 0),
                            "status": m.get('status', 'scheduled'),
                            "score": m.get('score', '0:0'),
                            "match_time": m.get('match_time', ''),
                            "match_id": m.get('match_id', ''),
                            "source": "sporttery",
                        }
                        for m in raw_matches
                    ]
                    data_source = "sporttery"
                except Exception as e:
                    logger.error(f"sporttery scraper failed: {e}")
                    matches = []
            else:
                matches = load_500_com_data(filter_day=day_filter)
                if matches:
                    data_source = "500.com"
                else:
                    try:
                        async with sporttery_scraper:
                            raw_matches = await sporttery_scraper.get_recent_matches(7)
                        matches = [
                            {
                                "id": m.get('id', ''),
                                "match_date": m.get('match_date', ''),
                                "home_team": m.get('home_team', 'Home'),
                                "away_team": m.get('away_team', 'Away'),
                                "league": m.get('league', 'Unknown'),
                                "odds_home_win": m.get('odds_home_win', 0.0),
                                "odds_draw": m.get('odds_draw', 0.0),
                                "odds_away_win": m.get('odds_away_win', 0.0),
                                "popularity": m.get('popularity', 0),
                                "status": m.get('status', 'scheduled'),
                                "score": m.get('score', '0:0'),
                                "match_time": m.get('match_time', ''),
                                "match_id": m.get('match_id', ''),
                                "source": "sporttery",
                            }
                            for m in raw_matches
                        ]
                        data_source = "sporttery (fallback)"
                    except Exception as e:
                        logger.error(f"all sources failed: {e}")
                        matches = []

            if league:
                matches = [m for m in matches if m.get('league') == league]
            if sort == "popularity":
                matches.sort(key=lambda x: x.get('popularity', 0), reverse=(order == "desc"))
            elif sort == "date":
                matches.sort(key=lambda x: x.get('match_time', ''), reverse=(order == "desc"))

            cache_data = {
                'matches': matches,
                'total': len(matches),
                'source': data_source,
                'timestamp': datetime.now().isoformat(),
            }
            await cache_manager.set(cache_key, cache_data, 300)

        total_matches = len(matches)
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paginated_matches = matches[start_idx:end_idx]
        pages = (total_matches + size - 1) // size if size > 0 else 0

        page_response = PageResponse(
            code=200,
            message="Success",
            data=paginated_matches,
            total=total_matches,
            page=page,
            size=size,
            pages=pages,
            timestamp=datetime.now(),
        )
        return UnifiedResponse(
            code=200,
            message=f"ok: {len(paginated_matches)}",
            data=page_response,
            timestamp=datetime.now(),
        )
    except Exception as e:
        logger.error(f"Failed to get lottery matches: {e}")
        traceback.print_exc()
        page_response = PageResponse(
            code=500,
            message="Error",
            data=[],
            total=0,
            page=page,
            size=size,
            pages=0,
            timestamp=datetime.now(),
        )
        return UnifiedResponse(
            code=500,
            message=f"Failed to get lottery matches: {str(e)}",
            data=page_response,
            timestamp=datetime.now(),
        )


@router.get("/leagues", summary="Get league list")
async def get_lottery_leagues(
    source: str = Query("auto", description="source: auto/500/sporttery")
) -> Dict[str, Any]:
    """Get available leagues."""
    try:
        matches_response = await get_lottery_matches(page=1, size=1000, source=source)
        if getattr(matches_response, "code", 500) != 200:
            return matches_response
        page_data = matches_response.data
        matches = page_data.data if page_data else []

        leagues: Dict[str, Dict[str, Any]] = {}
        for match in matches:
            league_name = match.get("league", "Unknown")
            if league_name not in leagues:
                leagues[league_name] = {"name": league_name, "count": 0}
            leagues[league_name]["count"] += 1

        league_list = sorted(leagues.values(), key=lambda x: x["count"], reverse=True)
        return {
            "success": True,
            "data": league_list,
            "total": len(league_list),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to get leagues: {e}")
        return {
            "success": False,
            "message": f"Failed to get leagues: {str(e)}",
            "data": [],
        }


@router.post("/refresh", summary="Refresh data cache")
async def refresh_lottery_cache() -> Dict[str, Any]:
    """Clear lottery cache."""
    try:
        cache_manager = get_cache_manager()
        await cache_manager.invalidate_pattern("jczq_v2:*")
        logger.info("Lottery cache cleared")
        return {
            "success": True,
            "message": "Cache cleared, next request will refetch data",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to refresh cache: {e}")
        return {
            "success": False,
            "message": f"Failed to refresh cache: {str(e)}",
        }
