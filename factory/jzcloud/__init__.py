# -*- coding:utf-8 -*-
from flask import Blueprint
import os



def get_idcards_image_path():
    imglist = []
    _filepath = os.path.join(os.path.dirname(__file__), '../static/idCards')
    _filelist = os.listdir(_filepath)

    for i in range(len(_filelist)):
        if _filelist[i].lower().endswith('.jpg'):
            name = _filelist[i].split('-')[0]
            id = _filelist[i].split('-')[1].split('.')[0]
            path = os.path.join(_filepath, _filelist[i])
            imglist.append({'name': name,
                            'id': id,
                            'file_path': path})
    return imglist



# 新建蓝图
jzcloud = Blueprint('jzcloud', __name__)

from .views import *
# from .match_views import *
