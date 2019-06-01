import json

from flask import current_app, jsonify, request, g, session

from ihome import redis_store, constants, db
from ihome.api_1_0 import api
from ihome.models import Area, House, Facility, HouseImage, User
from ihome.utils.commons import login_required
from ihome.utils.image_storage import storage
from ihome.utils.response_code import RET


@api.route('/areas')
def get_area_info():
    """��ȡ����"""
    try:
        resp_json = redis_store.get("area_info")
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json is not None:
            # redis�л�������
            current_app.logger.info("hit redis area_info")
            return resp_json, 200, {"Content-Type": "application/json"}

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

    # ������ת��Ϊjson�ַ���
    resp_dict = dict(errno=RET.OK, errmsg="OK", data=area_dict_li)
    resp_json = json.dumps(resp_dict)

    # �����ݱ��浽redis��
    try:
        redis_store.setex("area_info", constants.AREA_INFO_REDIS_CACHE_EXPIRES, resp_json)
    except Exception as e:
        current_app.logger.error(e)

    return resp_json, 200, {"Content-Type": "application/json"}

    return jsonify(errno=RET.OK, errmsg='���ݿ��쳣', data=area_dict_li)


@api.route("/houses/info", methods=["POST"])
@login_required
def save_house_info():
    """���淿�ݵĻ�����Ϣ"""
    # ��ȡ����
    user_id = g.user_id
    house_data = request.get_json()

    title = house_data.get("title")
    price = house_data.get("price")
    area_id = house_data.get("area_id")  # ��������������
    address = house_data.get("address")
    room_count = house_data.get("room_count")
    acreage = house_data.get("acreage")  # �������
    unit = house_data.get("unit")
    capacity = house_data.get("capacity")  # ������������
    beds = house_data.get("beds")  # �����Դ���Ŀ
    deposit = house_data.get("deposit")  # Ѻ��
    min_days = house_data.get("min_days")  # ��С��ס����
    max_days = house_data.get("max_days")  # �����ס����

    # У�����
    if not all(
            [title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg="����������")

    # �жϽ���Ƿ���ȷ
    try:
        price = int(float(price) * 100)
        deposit = int(float(deposit) * 100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="��������")

    # �жϳ���id�Ƿ����
    try:
        area = Area.query.get(area_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="�����쳣")

    if area is None:
        return jsonify(errno=RET.NODATA, errmsg="������Ϣ����")

    # ���淿����Ϣ
    house = House(
        user_id=user_id,
        area_id=area_id,
        title=title,
        price=price,
        address=address,
        room_count=room_count,
        acreage=acreage,
        unit=unit,
        capacity=capacity,
        beds=beds,
        deposit=deposit,
        min_days=min_days,
        max_days=max_days
    )

    # �����ݵ���ʩ��Ϣ
    facility_ids = house_data.get("facility")

    # ����û���ѡ����ʩ��Ϣ���ڱ������ݿ�
    if facility_ids:
        try:
            facilites = Facility.query.filter(Facility.id.in_(facility_ids)).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="���ݿ��쳣")

        if facilites:
            # ��ʾ�кϷ�����ʩ����
            # ������ʩ����
            house.facilities = facilites

    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="��������ʧ��")

    return jsonify(errno=RET.Ok, errmsg="OK", data={"house_id": house.id})


@api.route("/houses/image", methods=["POST"])
@login_required
def save_house_image():
    """���淿�ݵ�ͼƬ
    ���� ͼƬ ���ݵ�id
    """
    image_file = request.files.get("house_image")
    house_id = request.form.get("house_id")

    if not all([image_file, house_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="��������")

    # �ж�house_id��ȷ��
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="���ݿ��쳣")

    if house is None:
        return jsonify(errno=RET.NODATA, errmsg="���ݲ�����")

    image_data = image_file.read()
    # ����ͼƬ����ţ����
    try:
        file_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="����ͼƬ�쳣")

    # ����ͼƬ��Ϣ�����ݿ���
    house_image = HouseImage(house_id=house_id, url=file_name)
    db.session.add(house_image)

    # �����ݵ���ͼƬ
    if not house.index_image_url:
        house.index_image_url = file_name
        db.session.add(house)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="����ͼƬ�����쳣")

    image_url = constants.QINIU_DOMAIN + file_name
    return jsonify(errno=RET.OK, errmsg="OK", data={"image_url": image_url})


@api.route("/user/houses", methods=["GET"])
@login_required
def get_user_houses():
    """��ȡ���������ķ�Դ��Ϣ��Ŀ"""
    user_id = g.user_id

    try:
        user = User.query.get(user_id)
        houses = user.houses
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="��ȡ����ʧ��")

    # ���鵽�ķ�����Ϣת��Ϊ�ֵ��ŵ��б���
    houses_list = []
    if houses:
        for house in houses:
            houses_list.append(house.to_basic_dict())
    return jsonify(errno=RET.OK, errmsg="OK", data={"houses": houses_list})


@api.route("/houses/index", methods=["GET"])
def get_house_index():
    """��ȡ��ҳ�õ�Ƭչʾ�ķ��ݻ�����Ϣ"""
    # �ӻ����г��Ի�ȡ����
    try:
        ret = redis_store.get("home_page_data")
    except Exception as e:
        current_app.logger.error(e)
        ret = None

    if ret:
        current_app.logger.info("hit house index info redis")
        # ��Ϊredis�б������json�ַ���������ֱ�ӽ����ַ���ƴ�ӷ���
        return '{"errno":0, "errmsg":"OK", "data":%s}' % ret, 200, {"Content-Type": "application/json"}
    else:
        try:
            # ��ѯ���ݿ⣬���ط��ݶ�����Ŀ����5������
            houses = House.query.order_by(House.order_count.desc()).limit(constants.HOME_PAGE_MAX_HOUSES)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="��ѯ����ʧ��")

        if not houses:
            return jsonify(errno=RET.NODATA, errmsg="��ѯ������")

        houses_list = []
        for house in houses:
            # �������δ������ͼƬ��������
            if not house.index_image_url:
                continue
            houses_list.append(house.to_basic_dict())

        # ������ת��Ϊjson�������浽redis����
        json_houses = json.dumps(houses_list)  # "[{},{},{}]"
        try:
            redis_store.setex("home_page_data", constants.HOME_PAGE_DATA_REDIS_EXPIRES, json_houses)
        except Exception as e:
            current_app.logger.error(e)

        return '{"errno":0, "errmsg":"OK", "data":%s}' % json_houses, 200, {"Content-Type": "application/json"}


@api.route("/houses/<int:house_id>", methods=["GET"])
def get_house_detail(house_id):
    """��ȡ��������"""
    # ǰ���ڷ�������ҳ��չʾʱ��������ҳ����û����Ǹ÷��ݵķ�������չʾԤ����ť������չʾ��
    # ������Ҫ��˷��ص�¼�û���user_id
    # ���Ի�ȡ�û���¼����Ϣ������¼���򷵻ظ�ǰ�˵�¼�û���user_id�����򷵻�user_id=-1
    user_id = session.get("user_id", "-1")

    # У�����
    if not house_id:
        return jsonify(errno=RET.PARAMERR, errmsg="����ȷʵ")

    # �ȴ�redis�����л�ȡ��Ϣ
    try:
        ret = redis_store.get("house_info_%s" % house_id)
    except Exception as e:
        current_app.logger.error(e)
        ret = None
    if ret:
        current_app.logger.info("hit house info redis")
        return '{"errno":"0", "errmsg":"OK", "data":{"user_id":%s, "house":%s}}' % (user_id, ret), \
               200, {"Content-Type": "application/json"}

    # ��ѯ���ݿ�
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="��ѯ����ʧ��")

    if not house:
        return jsonify(errno=RET.NODATA, errmsg="���ݲ�����")

    # �����ݶ�������ת��Ϊ�ֵ�
    try:
        house_data = house.to_full_dict()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="���ݳ���")

    # ���뵽redis��
    json_house = json.dumps(house_data)
    try:
        redis_store.setex("house_info_%s" % house_id, constants.HOUSE_DETAIL_REDIS_EXPIRE_SECOND, json_house)
    except Exception as e:
        current_app.logger.error(e)

    resp = '{"errno":"0", "errmsg":"OK", "data":{"user_id":%s, "house":%s}}' % (user_id, json_house), \
           200, {"Content-Type": "application/json"}
    return resp