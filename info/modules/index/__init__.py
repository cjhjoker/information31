# -*- 若无相欠，怎会相见 -*-
from flask import Blueprint

# 1、创建首页蓝图对象
index_blue = Blueprint("index",__name__)

# 3、将蓝图注册到app中
from . import views