from flask import Blueprint
from ihome.models import *

# 创建蓝图对象
api = Blueprint("api_1_0", __name__)

# 导入蓝图的视图
from ihome.api_1_0 import demo, verify_code, postport, profile,houses
