# coding:utf-8
import Mail as Mail
from flask import Flask, render_template
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

app = Flask(__name__)


class Config(object):
    """配置参数"""
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root123@127.0.0.1:3306/my_test'

    SQLALCHEMY_TRACK_MODIFICATIONS = True

    SECRET_KEY = "12A3SDF465231R26%#$"


app.config.update(
    DEBUG=True,
    MAIL_SERVER='smtp.qq.com',
    MAIL_PORT=465,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='123412@qq.com',
    MAIL_PASSWORD='PASSWORD'
)
mail = Mail(app)

app.config.from_object(Config)

# 创建数据库sqlalchemy工具对象
db = SQLAlchemy(app)
# 创建flask脚本管理工具对象
manager = Manager(app)

# 创建数据库迁移工具对象
Migrate(app, db)

# 向manager对象中添加数据库的操作命令
manager.add_command("db", MigrateCommand)


class Author(db.Model):
    """作者表"""
    __tablename__ = "tbl_authors"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键 默认为自增
    name = db.Column(db.String(32), unique=True)
    books = db.relationship("Book", backref="author")


class Book(db.Model):
    """书籍"""
    __tablename__ = "tbl_books"
    id = db.Column(db.Integer, primary_key=True)  # 主键 默认为自增
    name = db.Column(db.String(32), unique=True)
    author_id = db.Column(db.Integer, db.ForeignKey("tbl_authors.id"))


# 创建表单类
class AuthorBookForm(FlaskForm):
    author_name = StringField(label="作者", validators=[DataRequired("作者必填")])
    book_name = StringField(label="书籍", validators=[DataRequired("书籍必填")])
    submit = StringField(label="保存")


@app.route("/", methods=["GET", "POST"])
def index():
    form = AuthorBookForm()
    if form.validate_on_submit():
        author_name = form.author_name.data
        book_name = form.book_name.data

        author = Author(name=author_name)
        db.session.add(author)
        db.session.commit()

        book = Book(name=book_name, author_id=author.id)
        db.session.add(book)
        db.session.commit()

    author_li = Author.query.all()
    return render_template("author_book.html", authors=author_li, form=form)


if __name__ == '__main__':
    # app.run(debug=True)
    # db.drop_all()  # 清理数据库
    # db.create_all()  # 创建所有的表
    manager.run()
