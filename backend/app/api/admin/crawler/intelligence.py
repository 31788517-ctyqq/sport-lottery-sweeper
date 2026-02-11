from flask import Blueprint, request, jsonify
import logging
logger = logging.getLogger(__name__)
from datetime import datetime, timedelta
import random

bp = Blueprint('crawler_intelligence', __name__, url_prefix='/api/admin/crawler/intelligence')

@bp.route('/stats', methods=['GET'])
def get_stats():
    return jsonify({
        'today_total': 1250,
        'today_success': 1230,
        'today_failed': 20,
        'overall_success_rate': 98.4
    })

@bp.route('/data', methods=['GET'])
def get_data():
    # 支持按日期范围、数据源、状态筛选（这里只做 Mock）
    mock_data = [
        {
            'id': 1,
            'date': (datetime.utcnow().date() - timedelta(days=1)).isoformat(),
            'source_id': 1,
            'total_count': 600,
            'success_count': 590,
            'failed_count': 10
        },
        {
            'id': 2,
            'date': datetime.utcnow().date().isoformat(),
            'source_id': 1,
            'total_count': 650,
            'success_count': 640,
            'failed_count': 10
        }
    ]
    return jsonify(mock_data)

@bp.route('/export', methods=['GET'])
def export_data():
    # Mock 下载链接
    return jsonify({'download_url': '/exports/crawler_data_20250620.csv'})