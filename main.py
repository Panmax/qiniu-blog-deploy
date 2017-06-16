# -*- coding: utf-8 -*-

import sys
import os

from qiniu import Auth, put_file, BucketManager, build_batch_delete
from workflow import Workflow

reload(sys)
sys.setdefaultencoding('utf-8')

access_key = 'your-access-key'
secret_key = 'your-secret-key'
bucket_name = 'your-bucket-name'
PATH = 'your-site-path'  # for example: /Users/jiapan/Google Drive/Blog/public/

ALL_FILES = []
DELETE_COUNT = 0


def clear_qiniu():
    global DELETE_COUNT
    q = Auth(access_key, secret_key)
    bucket = BucketManager(q)
    l = bucket.list(bucket_name)
    items = l[0].get('items')
    keys = [item.get('key') for item in items]
    DELETE_COUNT = len(keys)
    ops = build_batch_delete(bucket_name, keys)
    bucket.batch(ops)


def get_all_files(root_dir):
    for lists in os.listdir(root_dir):
        path = os.path.join(root_dir, lists)
        if os.path.isdir(path):
            get_all_files(path)
        else:
            ALL_FILES.append(path)


def upload_file(wf):
    count = 0
    q = Auth(access_key, secret_key)

    get_all_files(PATH)
    for f_path in ALL_FILES:
        key = f_path[len(PATH):]
        token = q.upload_token(bucket_name, key, 3600)
        put_file(token, key, f_path)
        count += 1

    wf.add_item('删除 %s 个旧文件' % DELETE_COUNT)
    wf.add_item('成功上传 %s 个文件' % count)
    wf.send_feedback()


if __name__ == '__main__':
    clear_qiniu()
    wf = Workflow()

    sys.exit(wf.run(upload_file))
