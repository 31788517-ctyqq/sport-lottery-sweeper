from sqlalchemy import Column, Integer, String, Float, Text, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from backend.database import Base

class CaipiaoData(Base):
    """
    竞彩数据模型，用于存储从API获取的竞彩数据
    """
    __tablename__ = "caipiao_data"

    id = Column(Integer, primary_key=True, index=True)
    line_id = Column(String(10), index=True)  # lineId
    rq = Column(String(10))  # rq (让球)
    home_team = Column(String(100), index=True)  # homeTeam (主队)
    guest_team = Column(String(100), index=True)  # guestTeam (客队)
    home_power = Column(Integer)  # homePower (主队实力值)
    guest_power = Column(Integer)  # guestPower (客队实力值)
    home_win_pan = Column(Float)  # homeWinPan (主胜盘口)
    home_win_qiu_0 = Column(Integer)  # homeWinQiu_0 (主胜进0球次数)
    home_win_qiu_1 = Column(Integer)  # homeWinQiu_1 (主胜进1球次数)
    home_win_qiu_2 = Column(Integer)  # homeWinQiu_2 (主胜进2球次数)
    home_lose_qiu_0 = Column(Integer)  # homeLoseQiu_0 (主负失0球次数)
    home_lose_qiu_1 = Column(Integer)  # homeLoseQiu_1 (主负失1球次数)
    home_lose_qiu_2 = Column(Integer)  # homeLoseQiu_2 (主负失2球次数)
    guest_win_pan = Column(Float)  # guestWinPan (客胜盘口)
    away_win_qiu_0 = Column(Integer)  # awayWinQiu_0 (客胜进0球次数)
    away_win_qiu_1 = Column(Integer)  # awayWinQiu_1 (客胜进1球次数)
    away_win_qiu_2 = Column(Integer)  # awayWinQiu_2 (客胜进2球次数)
    away_lose_qiu_0 = Column(Integer)  # awayLoseQiu_0 (客负失0球次数)
    away_lose_qiu_1 = Column(Integer)  # awayLoseQiu_1 (客负失1球次数)
    away_lose_qiu_2 = Column(Integer)  # awayLoseQiu_2 (客负失2球次数)
    home_feature = Column(String(200))  # homeFeature (主队特点)
    guest_feature = Column(String(200))  # guestFeature (客队特点)
    home_enter_efficiency = Column(String(100))  # homeEnterEfficiency (主队进攻效率)
    home_prevent_efficiency = Column(String(100))  # homePreventEfficiency (主队防守效率)
    guest_enter_efficiency = Column(String(100))  # guestEnterEfficiency (客队进攻效率)
    guest_prevent_efficiency = Column(String(100))  # guestPreventEfficiency (客队防守效率)
    home_spf = Column(String(50))  # homeSpf (主队胜负平)
    guest_spf = Column(String(50))  # guestSpf (客队胜负平)
    home_win_gap_1 = Column(Integer)  # homeWinGap_1 (主队胜场净胜1球次数)
    home_win_gap_2 = Column(Integer)  # homeWinGap_2 (主队胜场净胜2球次数)
    home_lose_gap_1 = Column(Integer)  # homeLoseGap_1 (主队负场净负1球次数)
    home_lose_gap_2 = Column(Integer)  # homeLoseGap_2 (主队负场净负2球次数)
    away_win_gap_1 = Column(Integer)  # awayWinGap_1 (客队胜场净胜1球次数)
    away_win_gap_2 = Column(Integer)  # awayWinGap_2 (客队胜场净胜2球次数)
    away_lose_gap_1 = Column(Integer)  # awayLoseGap_1 (客队负场净负1球次数)
    away_lose_gap_2 = Column(Integer)  # awayLoseGap_2 (客队负场净负2球次数)
    home_dxq_percent_str = Column(String(10))  # homeDxqPercentStr (主队大小球百分比)
    guest_dxq_percent_str = Column(String(10))  # guestDxqPercentStr (客队大小球百分比)
    home_dxq_desc = Column(String(200))  # homeDxqDesc (主队大小球描述)
    guest_dxq_desc = Column(String(200))  # guestDxqDesc (客队大小球描述)
    home_dxq_same10_desc = Column(String(200))  # homeDxqSame10Desc (主队主场大小球描述)
    away_dxq_same10_desc = Column(String(200))  # awayDxqSame10Desc (客队客场大小球描述)
    jiao_fen_desc = Column(Text)  # jiaoFenDesc (交锋描述)
    jiao_fen_match1 = Column(Text)  # jiaoFenMatch1 (最近交战记录1)
    jiao_fen_match2 = Column(Text)  # jiaoFenMatch2 (最近交战记录2)
    match_time_str = Column(String(20))  # matchTimeStr (比赛时间字符串)
    game_short_name = Column(String(50))  # gameShortName (赛事简称)
    home_win_award = Column(String(10))  # homeWinAward (主胜奖金)
    guest_win_award = Column(String(10))  # guestWinAward (客胜奖金)
    draw_award = Column(String(10))  # drawAward (平局奖金)
    
    # 以下字段用于其他联赛数据
    home_ji_fen_home_all = Column(String(10))  # homeJiFenHomeAll (主队积分主场总计)
    home_ji_fen_home = Column(String(10))  # homeJiFenHome (主队积分主场)
    away_ji_fen_home_all = Column(String(10))  # awayJiFenHomeAll (客队积分客场总计)
    away_ji_fen_home = Column(String(10))  # awayJiFenHome (客队积分客场)
    away_ji_fen_guest = Column(String(10))  # awayJiFenGuest (客队积分客场)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())