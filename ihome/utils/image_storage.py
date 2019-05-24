from qiniu import Auth, put_file, etag
import qiniu.config

# ��Ҫ��д��� Access Key �� Secret Key

access_key = 'Access_Key'
secret_key = 'Secret_Key'


def storage(file_data):
    """
    �ϴ��ļ�����ţ
    :param file_data:Ҫ�ϴ����ļ�����
    :return:
    """
    # ������Ȩ����
    q = Auth(access_key, secret_key)

    # Ҫ�ϴ��Ŀռ�
    bucket_name = 'Bucket_Name'

    # �����ϴ� Token������ָ������ʱ���
    token = q.upload_token(bucket_name, None, 3600)

    ret, info = put_file(token, None, file_data)
    if info.status_code ==200:
        return ret.get('key')
    else:
        raise Exception("�ϴ���ţʧ��")
    # print(info)
    # print("*" * 10)
    # print(ret)


if __name__ == '__main__':
    with open("./1.png", "rb") as f:
        file_data = f.read()
        storage(file_data)
