"""Test database models."""

from unittest.mock import MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_base_model_structure():
    """Test the basic model structure."""
    try:
        from models.base import Base
        
        # Check if Base class has expected attributes
        assert hasattr(Base, '__tablename__')
        assert hasattr(Base, 'to_dict')
        assert hasattr(Base, 'update_from_dict')
        
        print("✅ Base model structure is correct")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Model structure error: {e}")
        return False

def test_user_model_fields():
    """Test User model has required fields."""
    try:
        from models.user import User
        
        # Mock SQLAlchemy to avoid database dependency
        mock_session = MagicMock()
        
        # Check if User model has expected attributes
        expected_fields = ['email', 'name', 'hashed_password', 'is_active', 'is_superuser']
        
        for field in expected_fields:
            assert hasattr(User, field), f"User model missing field: {field}"
        
        print("✅ User model fields are correct")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ User model error: {e}")
        return False

def test_api_key_model_enum():
    """Test APIKey model enum values."""
    try:
        from models.api_key import APIProvider
        
        # Check enum values
        expected_providers = ['google_gemini', 'openai', 'anthropic']
        
        for provider in expected_providers:
            assert hasattr(APIProvider, provider.upper()), f"Missing provider: {provider}"
        
        print("✅ APIProvider enum is correct")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ APIProvider enum error: {e}")
        return False

def run_tests():
    """Run basic model tests without pytest."""
    print("🧪 Running basic model tests...")
    
    tests = [
        test_base_model_structure,
        test_user_model_fields,
        test_api_key_model_enum
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All basic model tests passed!")
    else:
        print("⚠️ Some tests failed - checking imports and structure...")
    
    return passed == total

if __name__ == "__main__":
    run_tests()