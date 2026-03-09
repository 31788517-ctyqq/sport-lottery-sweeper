"""
Example Data Processor Module.

This module takes raw scraped data and processes it into a format suitable for
storage in the database or further analysis.
"""
import logging
from typing import Dict, List
from datetime import datetime
from dateutil import parser # pip install python-dateutil

from ..schemas.match import MatchCreate # Import relevant schemas

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Processes raw data (e.g., from scrapers) into validated Pydantic models.
    """
    @staticmethod
    def clean_and_validate_datetime(dt_str: str) -> datetime:
        """
        Parses and validates a datetime string.
        """
        try:
            # Use dateutil.parser for flexible parsing, then convert to UTC-aware datetime
            dt = parser.isoparse(dt_str)
            if dt.tzinfo is None:
                 # Assume naive datetime is local time and make it timezone-aware
                 # Or handle it according to your system's expectations (e.g., treat as UTC)
                 # For this example, let's assume it's in local timezone and convert to UTC
                 import zoneinfo
                 local_tz = zoneinfo.ZoneInfo("Asia/Shanghai") # Or get from config
                 dt = dt.replace(tzinfo=local_tz)
            return dt.astimezone(datetime.timezone.utc)
        except ValueError as e:
            logger.error(f"Error parsing datetime '{dt_str}': {e}")
            # Return a default past time or raise an exception depending on requirements
            return datetime.min.replace(tzinfo=datetime.timezone.utc)

    @staticmethod
    def process_scraped_match(raw_match_data: Dict[str, str]) -> MatchCreate:
        """
        Transforms raw match data dictionary into a validated MatchCreate schema object.

        Args:
            raw_match_data: Dictionary containing raw data keys like 'home_team', 'away_team', etc.

        Returns:
            A validated MatchCreate object ready for database insertion.
        """
        processed_data = {}
        processed_data['home_team'] = raw_match_data.get('home_team', '').strip().title()
        processed_data['away_team'] = raw_match_data.get('away_team', '').strip().title()
        processed_data['match_time'] = DataProcessor.clean_and_validate_datetime(
            raw_match_data.get('time', '')
        )
        processed_data['league'] = raw_match_data.get('league', 'Unknown').strip()
        processed_data['venue'] = raw_match_data.get('venue', '').strip() or None # Convert empty string to None

        # Create and validate the Pydantic object
        match_schema = MatchCreate(**processed_data)
        logger.debug(f"Processed match data: {match_schema}")
        return match_schema

    @staticmethod
    def process_scraped_intelligence(raw_intel_data: Dict[str, str]) -> Dict[str, any]:
        """
        Processes raw intelligence data. Similar pattern to process_scraped_match.
        Implementation depends on the structure of raw_intel_data and the IntelligenceCreate schema.
        """
        # Example placeholder logic
        processed_data = {}
        processed_data['title'] = raw_intel_data.get('title', '').strip()
        processed_data['content'] = raw_intel_data.get('content', '').strip()
        processed_data['source'] = raw_intel_data.get('source', '').strip()
        processed_data['intelligence_type'] = raw_intel_data.get('type', 'other').lower()
        processed_data['match_id'] = int(raw_intel_data.get('match_id', 0)) # Assuming match_id comes from raw data
        # Validate and return as needed, perhaps an IntelligenceCreate schema object
        return processed_data