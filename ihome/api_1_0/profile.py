from flask import request, jsonify, current_app, g

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
    return jsonify(errno=RET.OK, errmsg="����ɹ�",data={'avatar_url':avatar_url})
