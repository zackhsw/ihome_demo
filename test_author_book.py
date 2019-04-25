import unittest

from ihome_demo.42_author_book import db, Author, app


class DatabaseTest(unittest.TestCase):
    """测试数据库"""

    def setUp(self):
        app.testing = True
        app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:mysql@127.0.0.1:3306/flask_test"
        db.create_all()

    def test_add_author(self):
        """测试填加作者的数据库操作"""
        author = Author(name="zhang", email="asdasdf@it.com", mobile="131313131313")
        db.session.add(author)
        db.session.commit()

        result_author = Author.query.filter_by(name="zhang").firt()

        self.assertIsNotNone(result_author)
    def tearDown(self):
        """在所有的测试执行结束后，执行，通常用来做清理动作"""
        db.session.remove()
