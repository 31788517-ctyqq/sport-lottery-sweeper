from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CaipiaoDataBase(BaseModel):
    line_id: str = Field(..., max_length=10, description="比赛线路ID")
    rq: str = Field(..., max_length=10, description="让球数")
    home_team: str = Field(..., max_length=100, description="主队名称")
    guest_team: str = Field(..., max_length=100, description="客队名称")
    home_power: int = Field(..., ge=0, description="主队实力值")
    guest_power: int = Field(..., ge=0, description="客队实力值")
    home_win_pan: float = Field(..., ge=0, description="主胜盘口")
    home_win_qiu_0: int = Field(..., ge=0, description="主胜进0球次数")
    home_win_qiu_1: int = Field(..., ge=0, description="主胜进1球次数")
    home_win_qiu_2: int = Field(..., ge=0, description="主胜进2球次数")
    home_lose_qiu_0: int = Field(..., ge=0, description="主负失0球次数")
    home_lose_qiu_1: int = Field(..., ge=0, description="主负失1球次数")
    home_lose_qiu_2: int = Field(..., ge=0, description="主负失2球次数")
    guest_win_pan: float = Field(..., ge=0, description="客胜盘口")
    away_win_qiu_0: int = Field(..., ge=0, description="客胜进0球次数")
    away_win_qiu_1: int = Field(..., ge=0, description="客胜进1球次数")
    away_win_qiu_2: int = Field(..., ge=0, description="客胜进2球次数")
    away_lose_qiu_0: int = Field(..., ge=0, description="客负失0球次数")
    away_lose_qiu_1: int = Field(..., ge=0, description="客负失1球次数")
    away_lose_qiu_2: int = Field(..., ge=0, description="客负失2球次数")
    home_feature: Optional[str] = Field(None, max_length=200, description="主队特点")
    guest_feature: Optional[str] = Field(None, max_length=200, description="客队特点")
    home_enter_efficiency: Optional[str] = Field(None, max_length=100, description="主队进攻效率")
    home_prevent_efficiency: Optional[str] = Field(None, max_length=100, description="主队防守效率")
    guest_enter_efficiency: Optional[str] = Field(None, max_length=100, description="客队进攻效率")
    guest_prevent_efficiency: Optional[str] = Field(None, max_length=100, description="客队防守效率")
    home_spf: Optional[str] = Field(None, max_length=50, description="主队胜负平")
    guest_spf: Optional[str] = Field(None, max_length=50, description="客队胜负平")
    home_win_gap_1: int = Field(0, ge=0, description="主队胜场净胜1球次数")
    home_win_gap_2: int = Field(0, ge=0, description="主队胜场净胜2球次数")
    home_lose_gap_1: int = Field(0, ge=0, description="主队负场净负1球次数")
    home_lose_gap_2: int = Field(0, ge=0, description="主队负场净负2球次数")
    away_win_gap_1: int = Field(0, ge=0, description="客队胜场净胜1球次数")
    away_win_gap_2: int = Field(0, ge=0, description="客队胜场净胜2球次数")
    away_lose_gap_1: int = Field(0, ge=0, description="客队负场净负1球次数")
    away_lose_gap_2: int = Field(0, ge=0, description="客队负场净负2球次数")
    home_dxq_percent_str: Optional[str] = Field(None, max_length=10, description="主队大小球百分比")
    guest_dxq_percent_str: Optional[str] = Field(None, max_length=10, description="客队大小球百分比")
    home_dxq_desc: Optional[str] = Field(None, max_length=200, description="主队大小球描述")
    guest_dxq_desc: Optional[str] = Field(None, max_length=200, description="客队大小球描述")
    home_dxq_same10_desc: Optional[str] = Field(None, max_length=200, description="主队主场大小球描述")
    away_dxq_same10_desc: Optional[str] = Field(None, max_length=200, description="客队客场大小球描述")
    jiao_fen_desc: Optional[str] = Field(None, description="交锋描述")
    jiao_fen_match1: Optional[str] = Field(None, description="最近交战记录1")
    jiao_fen_match2: Optional[str] = Field(None, description="最近交战记录2")
    match_time_str: str = Field(..., max_length=20, description="比赛时间字符串")
    game_short_name: str = Field(..., max_length=50, description="赛事简称")
    home_win_award: str = Field(..., max_length=10, description="主胜奖金")
    guest_win_award: str = Field(..., max_length=10, description="客胜奖金")
    draw_award: str = Field(..., max_length=10, description="平局奖金")
    
    # 以下字段用于其他联赛数据
    home_ji_fen_home_all: Optional[str] = Field(None, max_length=10, description="主队积分主场总计")
    home_ji_fen_home: Optional[str] = Field(None, max_length=10, description="主队积分主场")
    away_ji_fen_home_all: Optional[str] = Field(None, max_length=10, description="客队积分客场总计")
    away_ji_fen_home: Optional[str] = Field(None, max_length=10, description="客队积分客场")
    away_ji_fen_guest: Optional[str] = Field(None, max_length=10, description="客队积分客场")


class CaipiaoDataCreate(CaipiaoDataBase):
    pass


class CaipiaoDataUpdate(BaseModel):
    home_power: Optional[int] = Field(None, ge=0, description="主队实力值")
    guest_power: Optional[int] = Field(None, ge=0, description="客队实力值")
    home_win_pan: Optional[float] = Field(None, ge=0, description="主胜盘口")
    home_win_qiu_0: Optional[int] = Field(None, ge=0, description="主胜进0球次数")
    home_win_qiu_1: Optional[int] = Field(None, ge=0, description="主胜进1球次数")
    home_win_qiu_2: Optional[int] = Field(None, ge=0, description="主胜进2球次数")
    home_lose_qiu_0: Optional[int] = Field(None, ge=0, description="主负失0球次数")
    home_lose_qiu_1: Optional[int] = Field(None, ge=0, description="主负失1球次数")
    home_lose_qiu_2: Optional[int] = Field(None, ge=0, description="主负失2球次数")
    guest_win_pan: Optional[float] = Field(None, ge=0, description="客胜盘口")
    away_win_qiu_0: Optional[int] = Field(None, ge=0, description="客胜进0球次数")
    away_win_qiu_1: Optional[int] = Field(None, ge=0, description="客胜进1球次数")
    away_win_qiu_2: Optional[int] = Field(None, ge=0, description="客胜进2球次数")
    away_lose_qiu_0: Optional[int] = Field(None, ge=0, description="客负失0球次数")
    away_lose_qiu_1: Optional[int] = Field(None, ge=0, description="客负失1球次数")
    away_lose_qiu_2: Optional[int] = Field(None, ge=0, description="客负失2球次数")
    updated_at: Optional[str] = Field(None, max_length=20, description="更新时间")


class CaipiaoData(CaipiaoDataBase):
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True