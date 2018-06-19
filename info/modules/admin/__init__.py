# -*- coding:utf8 -*-
from flask import Blueprint
from flask import redirect
from flask import request
from flask import session

admin_blu = Blueprint('admin',__name__,url_prefix='/admin')

from . import views

#请求钩子,只要使用admin_blu装饰的函数都会走以下函数
#1.过滤普通用户,访问的是非登陆页面,都要做拦截
#2.如果是管理员不用处理
@admin_blu.before_request
def before_request():
    print(request.url)

    #判断,如果访问的是非登陆页面
    if not request.url.endswith('/admin/login'):
        #判断是否是管理员
        if not session.get("is_admin"):
            return redirect('/')