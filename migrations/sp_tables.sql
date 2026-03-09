-- ========================================
-- SP管理系统数据库迁移脚本 (MySQL版本)
-- 创建足球SP管理相关的数据表
-- 执行时间: 2024年
-- ========================================

-- 设置字符集
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ========================================
-- 1. 数据源配置表 (data_sources)
-- ========================================
DROP TABLE IF EXISTS `data_sources`;
CREATE TABLE `data_sources` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `name` varchar(255) NOT NULL COMMENT '数据源名称',
  `type` enum('api','file') NOT NULL DEFAULT 'api' COMMENT '类型: api-接口, file-文件',
  `url` varchar(500) NOT NULL COMMENT 'API接口地址或文件路径',
  `config` json DEFAULT NULL COMMENT '配置信息(JSON格式)',
  `status` tinyint NOT NULL DEFAULT '1' COMMENT '状态: 1-启用, 0-停用',
  `last_update` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `error_rate` decimal(5,2) DEFAULT '0.00' COMMENT '错误率百分比',
  `description` text COMMENT '描述',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_name` (`name`),
  KEY `idx_status` (`status`),
  KEY `idx_type` (`type`),
  KEY `idx_last_update` (`last_update`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据源配置表';

-- ========================================
-- 2. 比赛信息表 (football_matches) - 避免与现有match表冲突
-- ========================================
DROP TABLE IF EXISTS `football_matches`;
CREATE TABLE `football_matches` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `match_id` varchar(100) NOT NULL COMMENT '比赛唯一标识',
  `home_team` varchar(200) NOT NULL COMMENT '主队名称',
  `away_team` varchar(200) NOT NULL COMMENT '客队名称',
  `league` varchar(200) DEFAULT NULL COMMENT '联赛/杯赛名称',
  `match_time` datetime NOT NULL COMMENT '比赛时间',
  `status` enum('pending','ongoing','finished','cancelled') NOT NULL DEFAULT 'pending' COMMENT '比赛状态',
  `home_score` int DEFAULT NULL COMMENT '主队得分',
  `away_score` int DEFAULT NULL COMMENT '客队得分',
  `final_result` varchar(50) DEFAULT NULL COMMENT '最终赛果',
  `sp_record_count` int DEFAULT '0' COMMENT '关联的SP记录数量',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_match_id` (`match_id`),
  KEY `idx_status` (`status`),
  KEY `idx_match_time` (`match_time`),
  KEY `idx_league` (`league`),
  KEY `idx_teams` (`home_team`, `away_team`),
  KEY `idx_date_range` (`match_time`, `status`),
  CONSTRAINT `chk_scores` CHECK ((`home_score` is null or `home_score` >= 0) and (`away_score` is null or `away_score` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='足球比赛信息表';

-- ========================================
-- 3. 赔率公司表 (odds_companies)
-- ========================================
DROP TABLE IF EXISTS `odds_companies`;
CREATE TABLE `odds_companies` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `name` varchar(255) NOT NULL COMMENT '公司名称',
  `code` varchar(50) NOT NULL COMMENT '公司编码',
  `website` varchar(500) DEFAULT NULL COMMENT '官网地址',
  `status` tinyint NOT NULL DEFAULT '1' COMMENT '状态: 1-启用, 0-停用',
  `accuracy_rate` decimal(5,4) DEFAULT NULL COMMENT '准确率',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_code` (`code`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='赔率公司表';

-- ========================================
-- 4. SP值记录表 (sp_records)
-- ========================================
DROP TABLE IF EXISTS `sp_records`;
CREATE TABLE `sp_records` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `match_id` int NOT NULL COMMENT '比赛ID',
  `company_id` int NOT NULL COMMENT '公司ID',
  `handicap_type` enum('no_handicap','handicap') NOT NULL DEFAULT 'no_handicap' COMMENT '盘口类型',
  `handicap_value` decimal(8,3) DEFAULT NULL COMMENT '让球数值',
  `sp_value` decimal(10,4) NOT NULL COMMENT 'SP值',
  `recorded_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录时间',
  `is_final` tinyint NOT NULL DEFAULT '0' COMMENT '是否最终结果: 1-是, 0-否',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_match_id` (`match_id`),
  KEY `idx_company_id` (`company_id`),
  KEY `idx_recorded_at` (`recorded_at`),
  KEY `idx_sp_value` (`sp_value`),
  KEY `idx_composite` (`match_id`, `company_id`, `handicap_type`, `handicap_value`),
  KEY `idx_time_range` (`recorded_at`, `match_id`),
  CONSTRAINT `fk_sp_match` FOREIGN KEY (`match_id`) REFERENCES `football_matches` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_sp_company` FOREIGN KEY (`company_id`) REFERENCES `odds_companies` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_sp_value` CHECK ((`sp_value` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='SP值记录表';

-- ========================================
-- 5. SP值修改日志表 (sp_modification_logs)
-- ========================================
DROP TABLE IF EXISTS `sp_modification_logs`;
CREATE TABLE `sp_modification_logs` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `sp_record_id` bigint NOT NULL COMMENT 'SP记录ID',
  `old_value` decimal(10,4) DEFAULT NULL COMMENT '旧值',
  `new_value` decimal(10,4) NOT NULL COMMENT '新值',
  `modified_by` int NOT NULL COMMENT '修改人ID',
  `reason` varchar(500) DEFAULT NULL COMMENT '修改原因',
  `ip_address` varchar(45) DEFAULT NULL COMMENT 'IP地址',
  `user_agent` text COMMENT '用户代理',
  `modified_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`id`),
  KEY `idx_sp_record_id` (`sp_record_id`),
  KEY `idx_modified_at` (`modified_at`),
  KEY `idx_modified_by` (`modified_by`),
  CONSTRAINT `fk_log_sp_record` FOREIGN KEY (`sp_record_id`) REFERENCES `sp_records` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='SP值修改日志表';

-- ========================================
-- 插入默认数据
-- ========================================

-- 插入默认赔率公司
INSERT INTO `odds_companies` (`name`, `code`, `website`, `status`) VALUES 
('竞彩官方', 'JC_OFFICIAL', 'https://www.lottery.gov.cn/', 1),
('威廉希尔', 'WILLIAM_HILL', 'https://www.williamhill.com/', 1),
('立博', 'LADBROKES', 'https://www.ladbrokes.com/', 1),
('Bet365', 'BET365', 'https://www.bet365.com/', 1),
('澳门彩票', 'MACAU_LOTTERY', 'https://www.macauslot.com/', 1);

-- 插入示例数据源
INSERT INTO `data_sources` (`name`, `type`, `url`, `status`, `config`, `description`) VALUES 
('竞彩官方API', 'api', 'https://api.jczq.com/v1/odds', 1, '{"headers": {"Authorization": "Bearer token"}, "timeout": 30}', '竞彩官方提供的实时赔率API接口'),
('本地比赛数据文件', 'file', '/data/matches/football_matches.json', 1, '{"encoding": "utf-8", "auto_reload": true}', '本地存储的足球比赛数据文件'),
('SP值历史数据', 'file', '/data/sp/historical_sp.csv', 0, '{"delimiter": ",", "encoding": "utf-8"}', '历史SP值数据文件，用于分析');

-- ========================================
-- 创建视图 (可选)
-- ========================================

-- 比赛SP汇总视图
CREATE OR REPLACE VIEW `match_sp_summary` AS
SELECT 
    fm.id as match_id,
    fm.match_id as match_unique_id,
    fm.home_team,
    fm.away_team,
    fm.league,
    fm.match_time,
    fm.status as match_status,
    oc.name as company_name,
    oc.code as company_code,
    sr.handicap_type,
    sr.handicap_value,
    AVG(sr.sp_value) as avg_sp_value,
    MIN(sr.sp_value) as min_sp_value,
    MAX(sr.sp_value) as max_sp_value,
    COUNT(sr.id) as record_count,
    MAX(sr.recorded_at) as last_record_time
FROM football_matches fm
LEFT JOIN sp_records sr ON fm.id = sr.match_id
LEFT JOIN odds_companies oc ON sr.company_id = oc.id
WHERE fm.status IN ('pending', 'ongoing', 'finished')
GROUP BY fm.id, oc.id, sr.handicap_type, sr.handicap_value;

-- ========================================
-- 创建存储过程 (可选)
-- ========================================

DELIMITER $$

-- 获取比赛SP统计信息的存储过程
CREATE PROCEDURE `GetMatchSPStatistics`(
    IN p_match_id INT,
    IN p_company_id INT
)
BEGIN
    SELECT 
        fm.match_id,
        fm.home_team,
        fm.away_team,
        fm.league,
        fm.match_time,
        oc.name as company_name,
        sr.handicap_type,
        sr.handicap_value,
        COUNT(sr.id) as total_records,
        AVG(sr.sp_value) as avg_sp,
        MIN(sr.sp_value) as min_sp,
        MAX(sr.sp_value) as max_sp,
        STDDEV(sr.sp_value) as std_sp,
        MIN(sr.recorded_at) as first_record,
        MAX(sr.recorded_at) as last_record
    FROM football_matches fm
    LEFT JOIN sp_records sr ON fm.id = sr.match_id
    LEFT JOIN odds_companies oc ON sr.company_id = oc.id
    WHERE fm.id = p_match_id
    AND (p_company_id IS NULL OR sr.company_id = p_company_id)
    GROUP BY fm.id, oc.id, sr.handicap_type, sr.handicap_value;
END$$

DELIMITER ;

-- ========================================
-- 完成迁移
-- ========================================

SET FOREIGN_KEY_CHECKS = 1;

-- 显示创建结果
SELECT 
    'data_sources' as table_name, 
    COUNT(*) as record_count 
FROM data_sources
UNION ALL
SELECT 
    'football_matches' as table_name, 
    COUNT(*) as record_count 
FROM football_matches
UNION ALL
SELECT 
    'odds_companies' as table_name, 
    COUNT(*) as record_count 
FROM odds_companies
UNION ALL
SELECT 
    'sp_records' as table_name, 
    COUNT(*) as record_count 
FROM sp_records
UNION ALL
SELECT 
    'sp_modification_logs' as table_name, 
    COUNT(*) as record_count 
FROM sp_modification_logs;