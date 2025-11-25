from backend.utils.security import check_permission
from backend.config.settings import Settings

def test_security_default_permissions():
    s = Settings()
    assert check_permission(s, 'drive') == False
