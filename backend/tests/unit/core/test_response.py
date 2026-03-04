"""
响应格式和异常处理单元测试
"""
import pytest
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from backend.core.response import success_response, error_response, APIResponse
from backend.core.exception_handlers import (
    sqlalchemy_exception_handler, general_exception_handler,
    http_exception_handler, validation_exception_handler
)

class TestSuccessResponse:
    """测试成功响应格式"""
    
    def test_success_response_basic(self):
        """测试基本成功响应"""
        message = "操作成功"
        data = {"id": 1, "name": "test"}
        
        result = success_response(data=data, message=message)
        
        assert result["code"] == 200
        assert result["message"] == message
        assert result["data"] == data
    
    def test_success_response_no_data(self):
        """测试无数据的成功响应"""
        message = "操作完成"
        
        result = success_response(message=message)
        
        assert result["code"] == 200
        assert result["message"] == message
        assert result["data"] is None
    
    def test_success_response_custom_code(self):
        """测试自定义状态码的成功响应"""
        message = "创建成功"
        data = {"id": 1}
        
        result = success_response(data=data, message=message, code=201)
        
        assert result["code"] == 201
        assert result["message"] == message
        assert result["data"] == data
    
    def test_success_response_empty_message(self):
        """测试空消息的成功响应"""
        data = {"status": "ok"}
        
        result = success_response(data=data)
        
        assert result["code"] == 200
        assert result["message"] == ""
        assert result["data"] == data

class TestErrorResponse:
    """测试错误响应格式"""
    
    def test_error_response_basic(self):
        """测试基本错误响应"""
        message = "操作失败"
        error_code = "VALIDATION_ERROR"
        
        result = error_response(message=message, error_code=error_code)
        
        assert result["code"] == 400
        assert result["message"] == message
        assert result["error_code"] == error_code
        assert "timestamp" in result
    
    def test_error_response_custom_code(self):
        """测试自定义错误码的错误响应"""
        message = "未授权访问"
        error_code = "UNAUTHORIZED"
        
        result = error_response(message=message, error_code=error_code, code=401)
        
        assert result["code"] == 401
        assert result["message"] == message
        assert result["error_code"] == error_code
    
    def test_error_response_with_details(self):
        """测试带详情的错误响应"""
        message = "参数验证失败"
        error_code = "VALIDATION_ERROR"
        details = {"field": "username", "issue": "不能为空"}
        
        result = error_response(message=message, error_code=error_code, details=details)
        
        assert result["code"] == 400
        assert result["message"] == message
        assert result["error_code"] == error_code
        assert result["details"] == details

class TestAPIResponseClass:
    """测试APIResponse类"""
    
    def test_api_response_init(self):
        """测试APIResponse初始化"""
        response = APIResponse(
            code=200,
            message="成功",
            data={"key": "value"},
            error_code=None
        )
        
        assert response.code == 200
        assert response.message == "成功"
        assert response.data == {"key": "value"}
        assert response.error_code is None
    
    def test_api_response_to_dict(self):
        """测试APIResponse转换为字典"""
        response = APIResponse(
            code=201,
            message="创建成功",
            data={"id": 1},
            error_code=None
        )
        
        result = response.to_dict()
        
        assert isinstance(result, dict)
        assert result["code"] == 201
        assert result["message"] == "创建成功"
        assert result["data"] == {"id": 1}
        assert "timestamp" in result

class TestExceptionHandlers:
    """测试异常处理器"""
    
    @pytest.fixture
    def mock_request(self):
        """模拟请求对象"""
        return Mock(spec=Request)
    
    def test_http_exception_handler(self, mock_request):
        """测试HTTP异常处理器"""
        exc = HTTPException(status_code=404, detail="资源未找到")
        
        response = http_exception_handler(mock_request, exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 404
        
        content = response.body.decode()
        assert '"code":404' in content
        assert '"message":"资源未找到"' in content
    
    def test_sqlalchemy_exception_handler(self, mock_request):
        """测试SQLAlchemy异常处理器"""
        from sqlalchemy.exc import SQLAlchemyError
        
        exc = SQLAlchemyError("数据库连接失败")
        
        response = sqlalchemy_exception_handler(mock_request, exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        
        content = response.body.decode()
        assert '"code":500' in content
        assert '数据库错误' in content
    
    def test_general_exception_handler(self, mock_request):
        """测试通用异常处理器"""
        exc = Exception("未知错误")
        
        response = general_exception_handler(mock_request, exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        
        content = response.body.decode()
        assert '"code":500' in content
        assert '服务器内部错误' in content
    
    def test_validation_exception_handler(self, mock_request):
        """测试验证异常处理器"""
        from fastapi.exceptions import RequestValidationError
        from pydantic import ValidationError
        
        # 创建验证错误
        exc = RequestValidationError([{"loc": ["body", "username"], "msg": "field required", "type": "value_error.missing"}])
        
        response = validation_exception_handler(mock_request, exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 422
        
        content = response.body.decode()
        assert '"code":422' in content
        assert '请求参数验证失败' in content