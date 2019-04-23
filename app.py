from flask import Flask, current_app

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
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
