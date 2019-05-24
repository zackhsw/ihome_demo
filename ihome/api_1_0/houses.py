from flask import current_app, jsonify

from ihome.api_1_0 import api
from ihome.models import Area
from ihome.utils.response_code import RET


@api.route('/areas')
def get_area_info():
    """获取城区"""
    # 查询数据库，读取城区信息
    try:
        area_li = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    area_dict_li = []
    # 将对象转换为字典
    for area in area_li:
        area_dict_li.append(area.to_dict())

    return jsonify(errno=RET.OK, errmsg='数据库异常', data=area_dict_li)
