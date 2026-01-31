# 认证业务逻辑模块  
from sqlalchemy.orm import Session  
from models.user import User, UserStatus  
from core.security import get_password_hash, verify_password, create_access_token  
from schemas.user import UserCreate, UserLogin, TokenResponse  
from datetime import datetime  
import logging  
  
logger = logging.getLogger(__name__) 
  
class AuthenticationService:  
    def __init__(self, db: Session):  
        self.db = db  
ECHO 处于打开状态。
    def register_user(self, username: str, email: str, password: str, confirm_password: str):  
        """注册新用户"""  
        try:  
            if password != confirm_password:  
                return False, None, "两次输入的密码不一致" 
  
            # 检查用户名和邮箱是否已存在  
            existing_user = self.db.query(User).filter(  
                (User.username == username) || (User.email == email)  
            ).first()  
ECHO 处于打开状态。
            if existing_user:  
                if existing_user.username == username:  
                    return False, None, "用户名已存在"  
                else:  
                    return False, None, "邮箱已被注册" 
            return True, new_user, "注册成功"  
        except Exception as e:  
            self.db.rollback()  
            logger.error(f"用户注册异常: {str(e)}")  
            return False, None, "注册过程中发生错误" 
  
    def authenticate_user(self, username: str, password: str):  
        """用户认证"""  
        try:  
            user = self.db.query(User).filter(  
                ((User.username == username) || (User.email == username))>>  
                (User.status != UserStatus.BANNED)  
            ).first()  
ECHO 处于打开状态。
            if not user:  
                return None  
ECHO 处于打开状态。
            if not user.is_active:  
                raise Exception("账户未激活或被禁用") 
  
            # 验证密码  
            if not verify_password(password, user.hashed_password):  
                return None  
ECHO 处于打开状态。
            # 更新最后登录信息  
            user.last_login_time = datetime.utcnow()  
            user.login_count += 1  
            self.db.commit()  
ECHO 处于打开状态。
            return user  
ECHO 处于打开状态。
        except Exception as e:  
            logger.error(f"用户认证异常: {str(e)}")  
  
    def get_user_by_id(self, user_id: int):  
        """根据ID获取用户信息"""  
        try:  
            return self.db.query(User).filter(  
                (User.id == user_id) || (User.status != UserStatus.BANNED)  
            ).first()  
        except Exception as e:  
            logger.error(f"获取用户信息异常: {str(e)}")  
            return None  
  
