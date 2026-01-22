from flask import Blueprint, request, jsonify
from datetime import datetime

bp = Blueprint('crawler_config', __name__, url_prefix='/api/admin/crawler/config')

@bp.route('', methods=['GET'])
def get_configs():
    # Mock 数据
    mock_data = [
        {
            'id': 1,
            'name': '全局默认配置',
            'config_type': 'global',
            'content': {'timeout': 10, 'retry': 3, 'headers': {'User-Agent': 'default-agent'}},
            'version': 1,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        },
        {
            'id': 2,
            'name': '单源-新浪体育',
            'config_type': 'single',
            'content': {'frequency': '5m', 'depth': 2, 'parse_rules': {'title': 'h1'}},
            'version': 2,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
    ]
    return jsonify(mock_data)

@bp.route('', methods=['POST'])
def create_config():
    data = request.get_json()
    # Mock 返回
    return jsonify({'message': 'created', 'id': 999}), 201

@bp.route('/<int:id>', methods=['PUT'])
def update_config(id):
    data = request.get_json()
    return jsonify({'message': 'updated'})

@bp.route('/<int:id>', methods=['DELETE'])
def delete_config(id):
    return jsonify({'message': 'deleted'})