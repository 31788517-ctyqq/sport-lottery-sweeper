from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum  
from sqlalchemy.orm import relationship  
from database import Base  
from datetime import datetime  
import enum  
  
class UserStatus(enum.Enum):  
    ACTIVE = "active"  
    INACTIVE = "inactive"  
    PENDING = "pending" 
  
    def __repr__(self):  
        return f"^<User(id=^>{self.id}^<, username=^>'{self.username}'^<)^>"  
ECHO 处于打开状态。
    @property  
    def is_active(self):  
        return self.status == UserStatus.ACTIVE 
