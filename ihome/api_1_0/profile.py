# coding��utf8
from flask import request, jsonify, current_app, g, session

from ihome import db, constants
from ihome.api_1_0 import api, User
from ihome.utils.commons import login_required
from ihome.utils.image_storage import storage
from ihome.utils.response_code import RET


@api.route('/users/avatar', methods=['POST'])
@login_required
def set_user_avatar():
    """
    ����ͷ��
    ������ͼƬ(��ý�����ʽ) �û�id(g.user_id)
    :return:
    """
    user_id = g.user_id
    # ��ȡͼƬ
    image_file = request.files.get('avatar')

    if image_file is None:
        return jsonify(errno=RET.PARAMERR, errmsg="δ�ϴ�ͼƬ")

    image_data = image_file.read()

    # ������ţ�ϴ�ͼƬ
    try:
        file_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="�ϴ�ͼƬʧ��")

    # �����ļ��������ݿ���
    try:
        User.query.filter_by(id=user_id).update({"avatar_url": file_name})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="����ͼƬ��Ϣʧ��")
    avatar_url = constants.QINIU_URL_DOMAIN + file_name
    return jsonify(errno=RET.OK, errmsg="����ɹ�", data={'avatar_url': avatar_url})


@api.route("/users/name", methods=['PUT'])
@login_required
def change_user_name():
    """�޸��û���"""
    # ʹ��login_requiredװ�����󣬿��Դ�g�����л�ȡ�û�user_id
    user_id = g.user_id

    # ��ȡ�û���Ҫ���õ��û���
    req_data = request.get_json()
    if not req_data:
        return jsonify(errno=RET.PARAMERR, errmsg="����������")

    name = req_data.get("name")
    if not name:
        return jsonify(errno=RET.PARAMERR, errmsg="���ֲ���Ϊ��")

    # �����û��ǳ�name����ͬʱ�ж�name�Ƿ��ظ����������ݿ��Ψһ������
    try:
        User.query.filter_by(id=user_id).update({"name": name})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="�����û�����")

    # �޸�session������name�ֶ�
    session['name'] = name
    return jsonify(errno=RET.OK, errmsg="OK", data={"name": name})


@api.route("/user", methods=["GET"])
@login_required
def get_user_profile():
    """��ȡ������Ϣ"""
    user_id = g.user_id
    # ��ѯ���ݿ��ȡ������Ϣ
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="��ȡ�û���Ϣʧ��")

    if user is None:
        return jsonify(errno=RET.NODATA, errmsg='��Ч����')

    return jsonify(errno=RET.OK, errmsg="OK", data=user.to_dict())


@api.route("/user/auth", methods=["GET"])
@login_required
def get_user_auth():
    """��ȡ�û���ʵ����֤��Ϣ"""
    user_id = g.user_id

    # ��ѯ���ݿ��ȡ������Ϣ
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="��ȡ�û���Ϣʧ��")

    if user is None:
        return jsonify(errno=RET.NODATA, errmsg='��Ч����')

    return jsonify(errno=RET.OK, errmsg="OK", data=user.auth_to_dict())


@api.route("/users/auth", methods=["POST"])
@login_required
def set_user_auth():
    """����ʵ����֤��Ϣ"""
    user_id = g.user_id

    # ��ȡ����
    req_data = request.get_json()
    if not req_data:
        return jsonify(errno=RET.PARAMERR, errmsg="��������")

    real_name = req_data.get("real_name")  # ��ʵ����
    id_card = req_data.get("id_card")  # ���֤��

    # ����У��
    if not all([real_name, id_card]):
        return jsonify(errno=RET.PARAMERR, errmsg="��������")

    # �����û������������֤��
    try:
        User.query.filter_by(id=user_id, real_name=None, id_card=None).update(
            {"real_name": real_name, "id_card": id_card})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='�����û�ʵ����Ϣʧ��')

    return jsonify(errno=RET.OK, errmsg="OK")
