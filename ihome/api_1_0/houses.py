from flask import current_app, jsonify

from ihome.api_1_0 import api
from ihome.models import Area
from ihome.utils.response_code import RET


@api.route('/areas')
def get_area_info():
    """��ȡ����"""
    # ��ѯ���ݿ⣬��ȡ������Ϣ
    try:
        area_li = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='���ݿ��쳣')

    area_dict_li = []
    # ������ת��Ϊ�ֵ�
    for area in area_li:
        area_dict_li.append(area.to_dict())

    return jsonify(errno=RET.OK, errmsg='���ݿ��쳣', data=area_dict_li)
