import re

from flask import request, jsonify, current_app, session
from pymysql import IntegrityError

from ihome import redis_store, db
from ihome.utils.response_code import RET
from . import api, User


@api.route('/users', methods=['POST'])
def register():
    """
    regiter
    ����������ֻ��ţ����룬������֤��
    ������ʽ��json
    :return:
    """
    req_dict = request.get_json()
    mobile = req_dict.get('mobile')
    sms_code = req_dict.get('sms_code')
    password = req_dict.get('password')
    password2 = req_dict.get('password2')

    # У�����
    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="����������")

    # �ж��ֻ��Ÿ�ʽ
    if not re.match(r"1[34578]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='�ֻ��Ÿ�ʽ����')

    if password != password2:
        return jsonify(errno=RET.PARAMERR, errmsg='�������벻��')

    # ��redis��ȡ��������֤��
    try:
        real_sms_code = redis_store.get('sms_code_%s' % mobile)
    except Exception as e:
        current_app.logger.error(e)

    # �ж϶�����֤���Ƿ����
    if real_sms_code is None:
        return jsonify(errno=RET.NODATA, errmsg='������֤��ʧЧ')

    # ɾ��redis�ж�����֤�룬��ֹ�ظ�ʹ��
    try:
        redis_store.delete('sms_code_%s' % mobile)
    except Exception as e:
        current_app.logger.error(e)

    # �ж��û���д������֤�����ȷ��
    if real_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg='������֤�����')
    # �ж��û��Ķ��ֻ����Ƿ�ע���
    # try:
    #     user = User.query.filter_by(mobile=mobile).first()
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.DBERR, errmsg='���ݿ��쳣')
    # else:
    #     if user is not None:
    #         return jsonify(errno=RET.DATAEXIST, errmsg='�ֻ����Ѵ���')
    # �����û���ע�����ݵ����ݿ���
    user = User(name=mobile, mobile=mobile)
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        # ���ݿ���������Ļع�
        db.session.rollback()
        # ��ʾ�ֻ��ų����ظ������ֻ�ע���
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg='�ֻ����Ѵ���')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='���ݿ��쳣')

    # �����¼״̬session��
    session['name'] = mobile
    session['mobile'] = mobile
    session['user_id'] = user.id
    # ���ؽ��
    return jsonify(errno=RET.OK, errmsg='ע��ɹ�')
