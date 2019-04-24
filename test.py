import unittest

class LoginTest(unittest.TestCase):
    """构造单元测试案例"""
    def test_empty_user_name_password(self):
        """测试用户名密码不完整的情况"""
