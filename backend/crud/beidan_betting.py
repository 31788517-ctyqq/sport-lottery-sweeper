#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""北单投注模拟 CRUD"""

import logging
from typing import List, Optional, Tuple
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from backend.models.beidan_betting import BeidanBettingScheme, BeidanBettingSchemeItem

logger = logging.getLogger(__name__)


def ensure_betting_tables(db: Session) -> None:
    bind = db.get_bind()
    if bind is None:
        return
    inspector = inspect(bind)
    if not inspector.has_table(BeidanBettingScheme.__tablename__):
        BeidanBettingScheme.__table__.create(bind=bind, checkfirst=True)
    else:
        columns = {col["name"] for col in inspector.get_columns(BeidanBettingScheme.__tablename__)}
        if "ticketed" not in columns:
            db.execute(text("ALTER TABLE beidan_betting_schemes ADD COLUMN ticketed BOOLEAN DEFAULT 0"))
            db.commit()
    if not inspector.has_table(BeidanBettingSchemeItem.__tablename__):
        BeidanBettingSchemeItem.__table__.create(bind=bind, checkfirst=True)


def create_scheme(
    db: Session,
    admin_user_id: int,
    expect: str,
    name: str,
    stake: float,
    pass_type: str,
    split_mode: str,
    selections: List[dict]
) -> BeidanBettingScheme:
    ensure_betting_tables(db)

    scheme = BeidanBettingScheme(
        admin_user_id=admin_user_id,
        expect=expect,
        name=name,
        stake=stake,
        pass_type=pass_type,
        split_mode=split_mode
    )
    db.add(scheme)
    db.flush()

    items = []
    for selection in selections:
        item = BeidanBettingSchemeItem(
            scheme_id=scheme.id,
            match_seq=str(selection.get("matchSeq", "")),
            home_team=selection.get("homeTeam", ""),
            away_team=selection.get("awayTeam", ""),
            match_time=selection.get("matchTime"),
            selected_result=selection.get("selectedResult"),
            odds=float(selection.get("odds") or 0.0)
        )
        items.append(item)
    db.add_all(items)

    db.commit()
    db.refresh(scheme)
    return scheme


def list_schemes(
    db: Session,
    admin_user_id: int,
    expect: Optional[str],
    page: int,
    page_size: int
) -> Tuple[List[BeidanBettingScheme], int]:
    ensure_betting_tables(db)

    query = db.query(BeidanBettingScheme).filter(BeidanBettingScheme.admin_user_id == admin_user_id)
    if expect:
        query = query.filter(BeidanBettingScheme.expect == expect)

    total = query.count()
    items = query.order_by(BeidanBettingScheme.created_at.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()
    return items, total


def get_scheme(db: Session, admin_user_id: int, scheme_id: int) -> Optional[BeidanBettingScheme]:
    ensure_betting_tables(db)
    return db.query(BeidanBettingScheme) \
        .filter(BeidanBettingScheme.admin_user_id == admin_user_id, BeidanBettingScheme.id == scheme_id) \
        .first()


def delete_scheme(db: Session, admin_user_id: int, scheme_id: int) -> bool:
    ensure_betting_tables(db)
    scheme = get_scheme(db, admin_user_id, scheme_id)
    if not scheme:
        return False

    db.delete(scheme)
    db.commit()
    return True


def update_scheme_results(
    db: Session,
    scheme: BeidanBettingScheme,
    win_amount: float,
    profit: float,
    status: str
) -> BeidanBettingScheme:
    scheme.win_amount = win_amount
    scheme.profit = profit
    scheme.status = status
    db.commit()
    db.refresh(scheme)
    return scheme


def update_item_results(db: Session, scheme: BeidanBettingScheme, results_map: dict) -> None:
    for item in scheme.items:
        result = results_map.get(item.match_seq)
        if result:
            item.result = result
    db.commit()


def replace_scheme_items(db: Session, scheme: BeidanBettingScheme, selections: List[dict]) -> None:
    db.query(BeidanBettingSchemeItem).filter(BeidanBettingSchemeItem.scheme_id == scheme.id).delete()
    items = []
    for selection in selections:
        item = BeidanBettingSchemeItem(
            scheme_id=scheme.id,
            match_seq=str(selection.get("matchSeq", "")),
            home_team=selection.get("homeTeam", ""),
            away_team=selection.get("awayTeam", ""),
            match_time=selection.get("matchTime"),
            selected_result=selection.get("selectedResult"),
            odds=float(selection.get("odds") or 0.0)
        )
        items.append(item)
    db.add_all(items)
    db.commit()
