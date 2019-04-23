from flask import Flask, current_app, url_for, redirect, request
from werkzeug.routing import BaseConverter

app = Flask(__name__,
            static_url_path="/static_python",  # 访问静态资源的url前缀，默认是static
            )


# 配置参数的使用方式
# 1.使用配置文件
# app.config.from_pyfile("config.cfg")

# 2.使用对象配置参数
class Config(object):
    DEBUG = True
    ITCAST = "python"


app.config.from_object(Config)


# 3.直接操作（针对配置参数少的时候）
# app.config["DEBUG"] = True

@app.route('/')
def hello_world():
    # a = 1 / 0
    # 1.直接全局config对象取值
    # print(app.config.get("ITCAST"))
    # 2.通过current_app获取参数
    print(current_app.config.get("ITCAST"))
    return 'Hello flask World!'


@app.route("/hello", methods=["POST"])
def hello():
    return "hello 1"


@app.route("/hello", methods=["GET"])
def hello2():
    return "hello 2"


@app.route("/hello")
@app.route("/hi")
def hi():
    return "hi``"


@app.route('/login')
def login():
    # 使用url_for，通过视图函数的名字找到视图对应的url路径
    url = url_for("hello_world")
    return redirect(url)


# 转换器
# @app.route('/goods/<int:goods_id>')
@app.route('/goods/<goods_id>')  # 不加转换器 默认是普通字符串规则 除了/的字符
def goods_detail(goods_id):
    """定义的视图函数"""
    return "goods detail page:{}".format(goods_id)


# 1.自定义转换器
class MobileConverter(BaseConverter):
    def __init__(self, url_map):
        super(MobileConverter, self).__init__(url_map)
        self.regex = r'1[345678]\d{9}'


class RegexConverter(BaseConverter):
    def __init__(self, url_map, regex):
        # 调用父类的初始化方法
        super(RegexConverter, self).__init__(url_map)
        # 将正则表达式的参数保存到对象的属性中，flask会使用这个属性来进行路由的正则匹配
        self.regex = regex

    def to_python(self, value):
        """value是在路径进行正则表达式匹配的时候提取的参数"""
        print('to_python 方法被调用')
        return 'assss--' + value

    def to_url(self, value):
        """使用url_for的方法的时候被调用"""
        return value


# 2.将自定义的转换器添加到flask的应用中
app.url_map.converters["re"] = RegexConverter
app.url_map.converters["mobile"] = MobileConverter


@app.route("/send/<re(r'1[234578]\d{9}'):mobile_num>")
# @app.route("/send/<mobile:mobile_num>")
def send_sms(mobile_num):
    return "send sms to %s" % mobile_num


@app.route('/index')
def index():
    url = url_for("send_sms", mobile_num="13131313113")  # mobile_num 传入到RegexConverter的to_url函数中
    # /send/13131313113
    return redirect(url)


@app.route('/index',methods=["GET","POST"])
def index():
    # request中包含了前端发过来的所有请求数据
    # 通过request.form 可以直接提取请求体中德表单格式的数据
    #
    # 通过get方法只能拿到多个同名参数的第一个值
    name = request.form.get("name")
    city = request.args.get("city")  # 链接url中请求参数的值
    return "hello name=%" % name

if __name__ == '__main__':
    # 通过url_map可以查看真个flask中路由信息
    print(app.url_map)
    app.run(debug=True)
