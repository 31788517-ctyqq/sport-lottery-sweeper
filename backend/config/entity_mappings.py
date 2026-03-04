"""
实体名称映射与别名关联配置
采用业务唯一标识符作为主键，支持多语言和别名映射
"""

# 球队名称映射表
TEAM_MAPPINGS = {
    "real_madrid": {
        "zh": ["皇家马德里", "皇马"],
        "en": ["Real Madrid", "RM"],
        "jp": ["レアル・マドリード"],
        "official_info": {
            "website": "https://www.realmadrid.com/",
            "twitter": "https://twitter.com/realmadrid",
            "facebook": "https://www.facebook.com/realmadrid",
            "instagram": "https://www.instagram.com/realmadrid/",
            "weibo": "https://weibo.com/realmadrid",
            "verified": True,
            "last_verified": "2026-02-28"
        },
        "source_aliases": {
            "sports_data_api": ["RMCF", "RealMadridCF"],
            "football_data_org": ["Real Madrid Club de Fútbol"]
        }
    },
    "barcelona": {
        "zh": ["巴塞罗那", "巴萨"],
        "en": ["FC Barcelona", "Barça"],
        "jp": ["FCバルセロナ"],
        "official_info": {
            "website": "https://www.fcbarcelona.com/",
            "twitter": "https://twitter.com/fcbarcelona",
            "facebook": "https://www.facebook.com/FCBarcelona",
            "instagram": "https://www.instagram.com/fcbarcelona/",
            "weibo": "https://weibo.com/fcbarcelona",
            "verified": True,
            "last_verified": "2026-02-28"
        },
        "source_aliases": {
            "sports_data_api": ["FCB", "Barca"],
            "football_data_org": ["Futbol Club Barcelona"]
        }
    }
    # 更多球队映射...
}

# 联赛名称映射表
LEAGUE_MAPPINGS = {
    "premier_league": {
        "zh": ["英超联赛", "英格兰超级联赛"],
        "en": ["Premier League"],
        "official_info": {
            "website": "https://www.premierleague.com/",
            "twitter": "https://twitter.com/premierleague",
            "facebook": "https://www.facebook.com/premierleague",
            "instagram": "https://www.instagram.com/premierleague/",
            "verified": True,
            "last_verified": "2026-02-28"
        },
        "source_aliases": {
            "sports_data_api": ["EPL"],
            "football_data_org": ["English Premier League"]
        }
    },
    "la_liga": {
        "zh": ["西甲联赛", "西班牙甲级联赛"],
        "en": ["La Liga"],
        "official_info": {
            "website": "https://www.laliga.com/",
            "twitter": "https://twitter.com/laliga",
            "facebook": "https://www.facebook.com/LaLiga",
            "instagram": "https://www.instagram.com/laliga/",
            "verified": True,
            "last_verified": "2026-02-28"
        },
        "source_aliases": {
            "sports_data_api": ["LALIGA"],
            "football_data_org": ["Primera División"]
        }
    }
    # 更多联赛映射...
}

def get_standard_name(entity_type, alias, source=None):
    """
    根据别名和来源获取标准业务ID
    entity_type: 实体类型('team'/'league')
    alias: 别名或原始名称
    source: 数据源标识符(可选)
    """
    mappings = TEAM_MAPPINGS if entity_type == 'team' else LEAGUE_MAPPINGS
    
    for standard_id, details in mappings.items():
        # 检查所有语言变体
        for lang in ['zh', 'en', 'jp']:
            if lang in details and alias in details[lang]:
                return standard_id
                
        # 检查来源特定别名
        if source and 'source_aliases' in details and source in details['source_aliases']:
            if alias in details['source_aliases'][source]:
                return standard_id
                
    return None