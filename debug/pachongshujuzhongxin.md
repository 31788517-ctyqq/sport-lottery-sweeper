

爬虫管理模块爬虫数据中心页面，并按照以下布局设计生成页面：

1、在系统架构参考其布局和代码；
2、页面布局在后台管理系统侧边栏爬虫管理菜单的新子菜单数据中心上，对应在整个页面的在右边页面区域；
3、功能和布局设计以代码里面的为主；
4、在不和项目系统发生冲突的基础上计量去设计。
5.扫描系统中有相同的数据库表可以参考这个文件中的代码去完善；
6.这个页面包含以下部分：数据查询接口

以下是包含部分的页面代码布局参考：

1.数据查询接口
# api/data.py
@router.get("/matches", response_model=List[MatchResponse])
async def query_matches(
    db: Session = Depends(get_db),
    league: Optional[str] = Query(None, description="联赛"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    team: Optional[str] = Query(None, description="球队名称"),
    status: Optional[str] = Query(None, description="比赛状态"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """查询比赛数据"""
    query = db.query(Match)
    
    # 构建查询条件
    if league:
        query = query.filter(Match.league == league)
    if start_date:
        query = query.filter(Match.match_time >= start_date)
    if end_date:
        query = query.filter(Match.match_time <= end_date)
    if team:
        query = query.filter(
            or_(
                Match.home_team_name.ilike(f"%{team}%"),
                Match.away_team_name.ilike(f"%{team}%")
            )
        )
    if status:
        query = query.filter(Match.status == status)
    
    # 排序
    query = query.order_by(Match.match_time.desc())
    
    # 分页
    total = query.count()
    matches = query.offset((page - 1) * page_size).limit(page_size).all()
    
    # 获取关联数据
    result = []
    for match in matches:
        match_data = match.to_dict()
        
        # 获取赔率数据
        odds_query = db.query(Odds).filter(Odds.match_id == match.id)
        match_data['odds'] = odds_query.order_by(Odds.odds_time.desc()).all()
        
        # 获取统计数据
        stats = db.query(MatchStats).filter(MatchStats.match_id == match.id).first()
        match_data['stats'] = stats.to_dict() if stats else None
        
        # 获取事件数据
        events = db.query(MatchEvent).filter(MatchEvent.match_id == match.id).all()
        match_data['events'] = [e.to_dict() for e in events]
        
        result.append(match_data)
    
    return {
        "items": result,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/matches/export")
async def export_matches(
    export_format: str = Query("csv", regex="^(csv|json|excel)$"),
    export_fields: List[str] = Query(None),
    **filters
):
    """导出比赛数据"""
    # 查询数据
    matches = await query_matches(**filters)
    
    # 根据格式导出
    if export_format == "csv":
        return export_to_csv(matches, export_fields)
    elif export_format == "json":
        return export_to_json(matches, export_fields)
    elif export_format == "excel":
        return export_to_excel(matches, export_fields)

@router.get("/matches/stats")
async def get_match_statistics(
    league: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """获取比赛统计信息"""
    query = db.query(Match)
    
    if league:
        query = query.filter(Match.league == league)
    if start_date:
        query = query.filter(Match.match_time >= start_date)
    if end_date:
        query = query.filter(Match.match_time <= end_date)
    
    # 基础统计
    total_matches = query.count()
    completed_matches = query.filter(Match.status == 'finished').count()
    
    # 按联赛统计
    league_stats = db.query(
        Match.league,
        func.count(Match.id).label('total'),
        func.count(case((Match.status == 'finished', 1))).label('completed')
    ).group_by(Match.league).all()
    
    # 按日期统计
    date_stats = db.query(
        func.date(Match.match_time).label('match_date'),
        func.count(Match.id).label('count')
    ).group_by(func.date(Match.match_time)).order_by(func.date(Match.match_time)).all()
    
    return {
        "summary": {
            "total_matches": total_matches,
            "completed_matches": completed_matches,
            "completion_rate": completed_matches / total_matches if total_matches > 0 else 0
        },
        "by_league": [
            {"league": stat.league, "total": stat.total, "completed": stat.completed}
            for stat in league_stats
        ],
        "by_date": [
            {"date": stat.match_date.isoformat(), "count": stat.count}
            for stat in date_stats
        ]
    }



核心数据表结构
-- 比赛主表
CREATE TABLE matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id VARCHAR(100) UNIQUE NOT NULL,           -- 比赛唯一标识
    source_match_id VARCHAR(100),                     -- 源比赛ID
    
    -- 基础信息
    league VARCHAR(50) NOT NULL,                      -- 联赛
    season VARCHAR(20),                               -- 赛季
    round VARCHAR(20),                                -- 轮次
    match_time TIMESTAMP WITH TIME ZONE NOT NULL,     -- 比赛时间
    status VARCHAR(20) DEFAULT 'scheduled',           -- 比赛状态
    
    -- 球队信息
    home_team_id UUID REFERENCES teams(id),
    away_team_id UUID REFERENCES teams(id),
    home_team_name VARCHAR(100) NOT NULL,
    away_team_name VARCHAR(100) NOT NULL,
    
    -- 比分信息
    home_score INTEGER,
    away_score INTEGER,
    half_home_score INTEGER,
    half_away_score INTEGER,
    
    -- 比赛详情
    venue VARCHAR(200),                               -- 比赛场地
    referee VARCHAR(100),                             -- 裁判
    attendance INTEGER,                               -- 观众人数
    weather VARCHAR(50),                              -- 天气
    
    -- 数据质量
    data_completeness FLOAT DEFAULT 0.0,              -- 数据完整度
    last_updated TIMESTAMP WITH TIME ZONE,
    
    -- 索引
    INDEX idx_match_time (match_time),
    INDEX idx_league_status (league, status),
    INDEX idx_teams (home_team_name, away_team_name)
);

-- 赔率表
CREATE TABLE odds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID REFERENCES matches(id),
    provider VARCHAR(50) NOT NULL,                    -- 赔率提供商
    odds_type VARCHAR(20) NOT NULL,                   -- 赔率类型
    
    -- 亚盘数据
    handicap NUMERIC(5, 2),                           -- 让球数
    home_odds NUMERIC(8, 2),
    away_odds NUMERIC(8, 2),
    
    -- 欧赔数据
    win_odds NUMERIC(8, 2),
    draw_odds NUMERIC(8, 2),
    lose_odds NUMERIC(8, 2),
    
    -- 大小球
    over_under_line NUMERIC(5, 2),
    over_odds NUMERIC(8, 2),
    under_odds NUMERIC(8, 2),
    
    -- 时间信息
    odds_time TIMESTAMP WITH TIME ZONE NOT NULL,
    is_closing BOOLEAN DEFAULT FALSE,                 -- 是否封盘
    
    INDEX idx_match_odds (match_id, odds_time),
    INDEX idx_provider_type (provider, odds_type)
);

-- 比赛事件表
CREATE TABLE match_events (
    id UUID PRIMARY KEY,
    match_id UUID REFERENCES matches(id),
    event_type VARCHAR(50) NOT NULL,                  -- 事件类型
    minute INTEGER NOT NULL,                          -- 发生分钟
    team_side VARCHAR(10),                            -- 主队/客队
    player_name VARCHAR(100),                         -- 球员名称
    description TEXT,                                 -- 事件描述
    
    INDEX idx_match_events (match_id, minute)
);

-- 比赛统计表
CREATE TABLE match_stats (
    id UUID PRIMARY KEY,
    match_id UUID REFERENCES matches(id) UNIQUE,
    
    -- 射门数据
    home_shots INTEGER,
    away_shots INTEGER,
    home_shots_on_target INTEGER,
    away_shots_on_target INTEGER,
    
    -- 控球率
    home_possession FLOAT,
    away_possession FLOAT,
    
    -- 其他数据
    home_corners INTEGER,
    away_corners INTEGER,
    home_fouls INTEGER,
    away_fouls INTEGER,
    home_offsides INTEGER,
    away_offsides INTEGER,
    
    -- 守门员数据
    home_saves INTEGER,
    away_saves INTEGER,
    
    created_at TIMESTAMP WITH TIME ZONE
);


    