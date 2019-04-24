# coding:utf-8

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


class Config(object):
    """配置参数"""
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root123@127.0.0.1:3306/my_test'

    SQLALCHEMY_TRACK_MODIFICATIONS = True


app.config.from_object(Config)

# 创建数据库sqlalchemy工具对象
db = SQLAlchemy(app)


@app.route("/")
def index():
    return "index page"


# 表名的常见规范
# ihome -> ih_user  数据库名缩写_表名
# tbl_user   tbl_表名
class User(db.Model):
    """用户表"""
    __tablename__ = "tbl_users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键 默认为自增
    name = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey("tbl_roles.id"))

    def __repr__(self):
        """定义之后，可以让显示的对象时候更直观"""
        return "Role object: name=%" % self.name


class Role(db.Model):
    """用户角色"""
    __tablename__ = "tbl_roles"
    id = db.Column(db.Integer, primary_key=True)  # 主键 默认为自增
    name = db.Column(db.String(32), unique=True)
    users = db.relationship("User", backref="role")

    def __repr__(self):
        """定义之后，可以让显示的对象时候更直观"""
        return "Role object: name=%" % self.name


if __name__ == '__main__':
    # app.run(debug=True)
    # db.drop_all()  # 清理数据库
    db.create_all()  # 创建所有的表
