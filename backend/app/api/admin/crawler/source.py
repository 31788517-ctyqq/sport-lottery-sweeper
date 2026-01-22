from flask import Blueprint, request, jsonify
from datetime import datetime

bp = Blueprint('crawler_source', __name__, url_prefix='/api/admin/crawler/sources')

@bp.route('', methods=['GET'])
def list_sources():
    mock_data = [
        {
            'id': 1,
            'name': '新浪体育',
            'url': 'https://sports.sina.com.cn/',
            'status': 'online',
            'last_crawl_time': datetime.utcnow().isoformat(),
            'success_rate': 98.5,
            'response_time': 120.3,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        },
        {
            'id': 2,
            'name': '腾讯体育',
            'url': 'https://sports.qq.com/',
            'status': 'offline',
            'last_crawl_time': None,
            'success_rate': 0.0,
            'response_time': 0.0,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
    ]
    return jsonify(mock_data)

@bp.route('/<int:id>/health', methods=['GET'])
def health_check(id):
    # 简单判断 id
    if id == 1:
        return jsonify({'status': 'online', 'response_time_ms': 115, 'status_code': 200})
    else:
        return jsonify({'status': 'offline', 'response_time_ms': None, 'status_code': None})

@bp.route('/<int:id>/status', methods=['PUT'])
def update_status(id):
    data = request.get_json()
    # Mock 返回
    return jsonify({'message': 'status updated', 'id': id, 'new_status': data.get('status')})