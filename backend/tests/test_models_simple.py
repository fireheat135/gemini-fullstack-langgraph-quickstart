"""Simple test to verify model file structure without dependencies."""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_file_structure():
    """Test that model files exist and can be imported syntactically."""
    print("🧪 Testing file structure...")
    
    # Test model files exist
    model_files = [
        'models/__init__.py',
        'models/base.py',
        'models/user.py',
        'models/api_key.py',
        'models/article.py',
        'models/keyword.py',
        'models/project.py'
    ]
    
    src_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
    
    for model_file in model_files:
        file_path = os.path.join(src_dir, model_file)
        if os.path.exists(file_path):
            print(f"✅ {model_file} exists")
        else:
            print(f"❌ {model_file} missing")
            return False
    
    return True

def test_syntax_validity():
    """Test that Python files have valid syntax."""
    print("\n🔍 Testing Python syntax...")
    
    import ast
    
    model_files = [
        'models/base.py',
        'models/user.py', 
        'models/api_key.py',
        'models/article.py',
        'models/keyword.py',
        'models/project.py'
    ]
    
    src_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
    
    for model_file in model_files:
        file_path = os.path.join(src_dir, model_file)
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            ast.parse(content)
            print(f"✅ {model_file} has valid syntax")
        except SyntaxError as e:
            print(f"❌ {model_file} syntax error: {e}")
            return False
        except Exception as e:
            print(f"❌ {model_file} error: {e}")
            return False
    
    return True

def test_api_directory():
    """Test API directory structure."""
    print("\n📁 Testing API structure...")
    
    api_files = [
        'api/__init__.py',
        'api/v1/__init__.py',
        'api/v1/api.py',
        'api/v1/endpoints/__init__.py',
        'api/v1/endpoints/auth.py',
        'api/v1/endpoints/users.py',
        'api/v1/endpoints/api_keys.py'
    ]
    
    src_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
    
    for api_file in api_files:
        file_path = os.path.join(src_dir, api_file)
        if os.path.exists(file_path):
            print(f"✅ {api_file} exists")
        else:
            print(f"❌ {api_file} missing")
            return False
    
    return True

def test_services_structure():
    """Test services directory structure."""
    print("\n🔧 Testing services structure...")
    
    service_files = [
        'services/__init__.py',
        'services/user_service.py',
        'services/api_key_service.py',
        'services/ai/__init__.py',
        'services/ai/ai_service_manager.py',
        'services/ai/gemini_service.py',
        'services/ai/openai_service.py',
        'services/ai/anthropic_service.py'
    ]
    
    src_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
    
    for service_file in service_files:
        file_path = os.path.join(src_dir, service_file)
        if os.path.exists(file_path):
            print(f"✅ {service_file} exists")
        else:
            print(f"❌ {service_file} missing")
            return False
    
    return True

def run_simple_tests():
    """Run simple structure tests."""
    print("🚀 Running simple structure tests...\n")
    
    tests = [
        ("File Structure", test_file_structure),
        ("Python Syntax", test_syntax_validity),
        ("API Structure", test_api_directory),
        ("Services Structure", test_services_structure)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"🔄 Running {test_name} test:")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} test passed\n")
            else:
                print(f"❌ {test_name} test failed\n")
        except Exception as e:
            print(f"❌ {test_name} test error: {e}\n")
    
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All structure tests passed!")
        print("📦 SEO Agent integration appears to be correctly structured!")
    else:
        print("⚠️ Some structure tests failed - checking integration...")
    
    return passed == total

if __name__ == "__main__":
    success = run_simple_tests()
    exit(0 if success else 1)