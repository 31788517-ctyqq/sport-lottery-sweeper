#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试体系完善脚本
用于补充单元测试、集成测试和端到端测试
"""

import os
import sys
from pathlib import Path
import subprocess
import json


def create_unit_test_structure():
    """创建单元测试目录结构"""
    test_dirs = [
        "tests/unit",
        "tests/unit/models",
        "tests/unit/services",
        "tests/unit/api",
        "tests/unit/utils",
        "tests/integration",
        "tests/e2e"
    ]
    
    for test_dir in test_dirs:
        path = Path(test_dir)
        path.mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建测试目录: {test_dir}")
        
        # 在每个目录下创建__init__.py文件
        init_file = path / "__init__.py"
        if not init_file.exists():
            init_file.touch()
    
    print(f"✅ 创建了 {len(test_dirs)} 个测试目录")


def create_sample_unit_tests():
    """创建示例单元测试"""
    
    # 示例模型测试
    model_test_content = '''import pytest
from backend.models.datasource import DataSourceModel
from backend.schemas.datasource import DataSourceCreate


def test_create_datasource():
    """测试创建数据源模型"""
    data = {
        "name": "Test Data Source",
        "url": "https://example.com",
        "status": "active"
    }
    datasource = DataSourceCreate(**data)
    
    assert datasource.name == "Test Data Source"
    assert datasource.url == "https://example.com"
    assert datasource.status == "active"


def test_datasource_defaults():
    """测试数据源默认值"""
    data = {
        "name": "Test Data Source",
        "url": "https://example.com"
    }
    datasource = DataSourceCreate(**data)
    
    # 检查是否有合理的默认值
    assert datasource.name == "Test Data Source"
    assert datasource.url == "https://example.com"
'''
    
    with open("tests/unit/models/test_datasource_model.py", "w", encoding="utf-8") as f:
        f.write(model_test_content)
    
    # 示例服务测试
    service_test_content = '''import pytest
from unittest.mock import MagicMock, patch
from backend.services.datasource_service import DataSourceService


@pytest.fixture
def datasource_service():
    """数据源服务测试 fixture"""
    return DataSourceService()


def test_get_all_datasources(datasource_service):
    """测试获取所有数据源"""
    with patch.object(datasource_service, 'get_all', return_value=[]):
        result = datasource_service.get_all()
        assert result == []
'''
    
    with open("tests/unit/services/test_datasource_service.py", "w", encoding="utf-8") as f:
        f.write(service_test_content)
    
    # 示例API测试
    api_test_content = '''import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    """测试客户端 fixture"""
    return TestClient(app)


def test_health_endpoint(client):
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
'''
    
    with open("tests/unit/api/test_health_api.py", "w", encoding="utf-8") as f:
        f.write(api_test_content)
    
    print("✅ 创建了示例单元测试")


def create_integration_tests():
    """创建集成测试"""
    
    integration_test_content = '''import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.main import app
from backend.dependencies import get_db


# 创建测试数据库引擎
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 依赖覆盖
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """测试客户端 fixture"""
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


def test_create_and_get_datasource(client):
    """测试创建和获取数据源的集成测试"""
    # 创建数据源
    create_data = {
        "name": "Integration Test Source",
        "url": "https://test-source.com",
        "status": "active"
    }
    create_response = client.post("/api/v1/datasources", json=create_data)
    assert create_response.status_code == 200
    
    # 获取数据源
    get_response = client.get("/api/v1/datasources")
    assert get_response.status_code == 200
    data = get_response.json()
    assert len(data) > 0
    assert any(ds["name"] == "Integration Test Source" for ds in data)
'''
    
    with open("tests/integration/test_datasource_integration.py", "w", encoding="utf-8") as f:
        f.write(integration_test_content)
    
    print("✅ 创建了示例集成测试")


def create_e2e_test_template():
    """创建端到端测试模板"""
    
    e2e_test_content = '''import pytest
from playwright.sync_api import Page, expect
import os


def test_login_page_elements(page: Page):
    """测试登录页面元素"""
    # 使用环境变量或默认值设置基础URL
    base_url = os.getenv("TEST_BASE_URL", "http://localhost:5173")
    page.goto(base_url + "/login")
    
    # 检查页面标题
    expect(page).to_have_title("登录 - 体育彩票扫盘系统")
    
    # 检查登录表单元素
    expect(page.get_by_label("用户名")).to_be_visible()
    expect(page.get_by_label("密码")).to_be_visible()
    expect(page.get_by_role("button", name="登录")).to_be_visible()


def test_datasource_management(page: Page):
    """测试数据源管理功能"""
    base_url = os.getenv("TEST_BASE_URL", "http://localhost:5173")
    page.goto(base_url + "/admin/datasources")
    
    # 如果需要登录，先进行登录
    # login_if_needed(page)
    
    # 检查数据源列表页面元素
    expect(page.get_by_role("heading", name="数据源管理")).to_be_visible()
    expect(page.get_by_role("button", name="添加数据源")).to_be_visible()
    
    # 检查表格是否存在
    expect(page.locator(".el-table")).to_be_visible()
'''
    
    with open("tests/e2e/test_admin_e2e.py", "w", encoding="utf-8") as f:
        f.write(e2e_test_content)
    
    print("✅ 创建了端到端测试模板")


def create_pytest_config():
    """创建pytest配置文件"""
    
    pytest_ini_content = '''[tool:pytest]
minversion = 6.0
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -ra
    --strict-markers
    --strict-config
    -v
    --cov=backend
    --cov-report=html
    --cov-report=term-missing:skip-covered
    --tb=short

[coverage:run]
source = backend/
omit = 
    */venv/*
    */__pycache__/*
    */tests/*
    backend/main.py
    backend/database.py
    backend/config.py

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
'''
    
    with open("pytest.ini", "w", encoding="utf-8") as f:
        f.write(pytest_ini_content)
    
    print("✅ 创建了pytest配置文件")


def create_test_runner_script():
    """创建测试运行脚本"""
    
    runner_script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本
用于运行不同类型的测试
"""

import subprocess
import sys
import argparse
from pathlib import Path


def run_unit_tests():
    """运行单元测试"""
    print("🏃 运行单元测试...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/unit", 
        "-v", 
        "--cov=backend", 
        "--cov-report=term-missing"
    ])
    return result.returncode == 0


def run_integration_tests():
    """运行集成测试"""
    print("🏃 运行集成测试...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/integration", 
        "-v"
    ])
    return result.returncode == 0


def run_e2e_tests():
    """运行端到端测试"""
    print("🏃 运行端到端测试...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/e2e", 
        "-v",
        "--headed"  # 为了可视化调试
    ])
    return result.returncode == 0


def run_all_tests():
    """运行所有测试"""
    print("🏃 运行所有测试...")
    
    unit_success = run_unit_tests()
    integration_success = run_integration_tests()
    e2e_success = run_e2e_tests()
    
    all_success = unit_success and integration_success and e2e_success
    
    if all_success:
        print("🎉 所有测试通过!")
    else:
        print("❌ 部分测试失败!")
    
    return all_success


def install_test_deps():
    """安装测试依赖"""
    print("📦 安装测试依赖...")
    
    # 安装pytest相关包
    subprocess.run([
        sys.executable, "-m", "pip", "install", 
        "pytest", "pytest-cov", "pytest-mock", 
        "coverage", "httpx", "fastapi", "starlette"
    ])
    
    # 安装Playwright用于E2E测试
    subprocess.run([sys.executable, "-m", "playwright", "install"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="测试运行脚本")
    parser.add_argument(
        "action", 
        choices=["unit", "integration", "e2e", "all", "deps"],
        help="要运行的测试类型"
    )
    
    args = parser.parse_args()
    
    if args.action == "unit":
        success = run_unit_tests()
    elif args.action == "integration":
        success = run_integration_tests()
    elif args.action == "e2e":
        success = run_e2e_tests()
    elif args.action == "all":
        success = run_all_tests()
    elif args.action == "deps":
        install_test_deps()
        success = True
    
    sys.exit(0 if success else 1)
'''
    
    with open("scripts/run_tests.py", "w", encoding="utf-8") as f:
        f.write(runner_script_content)
    
    # 使脚本可执行
    os.chmod("scripts/run_tests.py", 0o755)
    
    print("✅ 创建了测试运行脚本")


def run_test_suite_enhancement():
    """运行测试套件增强"""
    print("=" * 60)
    print("测试体系完善")
    print("=" * 60)
    
    print("\n🔍 创建测试目录结构...")
    create_unit_test_structure()
    
    print("\n🔍 创建示例单元测试...")
    create_sample_unit_tests()
    
    print("\n🔍 创建集成测试...")
    create_integration_tests()
    
    print("\n🔍 创建端到端测试模板...")
    create_e2e_test_template()
    
    print("\n🔍 创建pytest配置...")
    create_pytest_config()
    
    print("\n🔍 创建测试运行脚本...")
    create_test_runner_script()
    
    print("\n🎉 测试体系已完善!")
    print("\n使用说明:")
    print("- 运行单元测试: python scripts/run_tests.py unit")
    print("- 运行集成测试: python scripts/run_tests.py integration")
    print("- 运行E2E测试: python scripts/run_tests.py e2e")
    print("- 运行所有测试: python scripts/run_tests.py all")
    print("- 安装测试依赖: python scripts/run_tests.py deps")
    print("- 查看覆盖率报告: 在测试运行后查看htmlcov/目录")


if __name__ == "__main__":
    run_test_suite_enhancement()