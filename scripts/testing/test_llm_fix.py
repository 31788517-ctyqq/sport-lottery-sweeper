import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal
from backend.crud.llm_provider import llm_provider

def test_llm_count():
    """测试LLM Provider计数功能"""
    db = SessionLocal()
    try:
        count = llm_provider.get_count(db)
        print(f"LLM Provider count: {count}")
    except Exception as e:
        print(f"Error: {e}")
        print(f"DB type: {type(db)}")
    finally:
        db.close()

if __name__ == "__main__":
    test_llm_count()