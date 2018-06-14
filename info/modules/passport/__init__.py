# -*- coding:utf8 -*-
from flask import Blueprint
# 创建蓝图对象 设置访问前缀
passport_blu = Blueprint("passport",__name__,url_prefix="/passport")

from . import views