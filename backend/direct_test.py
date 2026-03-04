import sys
import logging
logger = logging.getLogger(__name__)
sys.path.insert(0, '.')

logger.debug("测试导入...")
try:
    from pathlib import Path
    project_root = Path(__file__).parent.parent
    logger.debug(f"项目根目录: {project_root}")
    
    debug_dir = project_root / "debug"
    logger.debug(f"Debug目录: {debug_dir}")
    logger.debug(f"Debug目录存在: {debug_dir.exists()}")
    
    if debug_dir.exists():
        import os
        files = [f for f in os.listdir(debug_dir) if f.startswith("500_com_matches_")]
        logger.debug(f"找到文件: {files}")
        
        if files:
            import json
            latest = sorted(files)[-1]
            path = debug_dir / latest
            logger.debug(f"读取: {path}")
            
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"数据条数: {len(data)}")
            if data:
                logger.debug(f"第一条: {data[0]}")
    
except Exception as e:
    logger.debug(f"错误: {e}")
    import traceback
    traceback.print_exc()
