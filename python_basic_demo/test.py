import json
import unittest
from python_basic_demo.login import app


class LoginTest(unittest.TestCase):
    """构造单元测试"""

    def setUp(self):
        """在进行测试之前，先被执行"""
        # app.config['TESTING'] = True
        # app.testing = True
        self.client = app.test_client()

    def test_empty_user_name_password(self):
        """测试用户名密码不完整的情况"""
        # 创建进行web请求的客户端，使用flask提供的
        # client = app.test_client()

        # 利用client客户端模拟发送web请求
        ret = self.client.post("/login", data={})
        # ret是视图返回的响应对象
        resp = ret.data
        # 因为login视图返回的是json字符串
        resp = json.loads(resp)

        # 拿到返回值后进行断言测试
        self.assertIn("code", resp)
        self.assertEqual(resp["code"], 1)

        # 测试只传用户名
        # 利用client客户端模拟发送web请求
        ret = self.client.post("/login", data={"user_name": "admin"})
        # ret是视图返回的响应对象
        resp = ret.data
        # 因为login视图返回的是json字符串
        resp = json.loads(resp)

        # 拿到返回值后进行断言测试
        self.assertIn("code", resp)
        self.assertEqual(resp["code"], 1)

        # 测试只传用密码
        # 利用client客户端模拟发送web请求
        ret = self.client.post("/login", data={"password": "123465"})
        # ret是视图返回的响应对象
        resp = ret.data
        # 因为login视图返回的是json字符串
        resp = json.loads(resp)

        # 拿到返回值后进行断言测试
        self.assertIn("code", resp)
        self.assertEqual(resp["code"], 1)

    def test_wrong_user_name_password(self):
        """测试用户名或密码错误"""
        ret = self.client.post("/login", data={"user_name": "admin", "password": "python"})
        # ret是视图返回的响应对象
        resp = ret.data
        # 因为login视图返回的是json字符串
        resp = json.loads(resp)

        # 拿到返回值后进行断言测试
        # self.assertIn("code", resp)
        self.assertEqual(resp["code"], 0)


if __name__ == '__main__':
    unittest.main()
