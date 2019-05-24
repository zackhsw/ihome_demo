import functools

from flask import session, jsonify, g
from werkzeug.routing import BaseConverter

# ��������ת����
from ihome.utils.response_code import RET


class ReConverter(BaseConverter):
    """"""

    def __init__(self, url_map, regex):
        super(ReConverter, self).__init__(url_map)
        self.regex = regex


# �������֤��¼״̬��װ����
def login_required(view_func):
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        # �ж��û��ĵ�¼״̬
        user_id = session.get('user_id')
        # ����û��ǵ�¼�ģ�ִ����ͼ����
        if user_id is not None:
            # ��user_id���浽g,����ͼ������ͨ��g�����ȡ��������
            g.user_id = user_id
            return view_func(*args, **kwargs)
        else:
            # ���δ��¼������δ��¼��Ϣ
            return jsonify(errno=RET.SESSIONERR, errmsg='�û�δ��¼')
        return wrapper
