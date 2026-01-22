from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta

bp = Blueprint('crawler_task', __name__, url_prefix='/api/admin/crawler/tasks')

@bp.route('', methods=['GET'])
def list_tasks():
    now = datetime.utcnow()
    mock_data = [
        {
            'id': 1,
            'name': '新浪体育赛程抓取',
            'source_id': 1,
            'cron_expr': '*/10 * * * *',
            'next_run_time': (now + timedelta(minutes=10)).isoformat(),
            'status': 'idle',
            'created_at': now.isoformat(),
            'updated_at': now.isoformat()
        },
        {
            'id': 2,
            'name': '腾讯体育新闻抓取',
            'source_id': 2,
            'cron_expr': '0 */1 * * *',
            'next_run_time': (now + timedelta(hours=1)).isoformat(),
            'status': 'running',
            'created_at': now.isoformat(),
            'updated_at': now.isoformat()
        }
    ]
    return jsonify(mock_data)

@bp.route('', methods=['POST'])
def create_task():
    data = request.get_json()
    return jsonify({'message': 'created', 'id': 999}), 201

@bp.route('/<int:id>', methods=['PUT'])
def update_task(id):
    data = request.get_json()
    return jsonify({'message': 'updated', 'id': id})

@bp.route('/<int:id>/trigger', methods=['POST'])
def trigger_task(id):
    return jsonify({'message': 'triggered', 'id': id})

@bp.route('/<int:id>/logs', methods=['GET'])
def get_logs(id):
    mock_logs = [
        {'time': datetime.utcnow().isoformat(), 'level': 'INFO', 'msg': f'Task {id} started'},
        {'time': datetime.utcnow().isoformat(), 'level': 'INFO', 'msg': f'Task {id} finished, 100 items fetched'}
    ]
    return jsonify(mock_logs)