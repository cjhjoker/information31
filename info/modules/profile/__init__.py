# -*- coding:utf8 -*-
from flask import Blueprint
# 创建蓝图对象 设置访问前缀
profile_blu = Blueprint("profile",__name__,url_prefix="/user")

from . import views