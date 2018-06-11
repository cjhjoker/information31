# -*- 若无相欠，怎会相见 -*-
from info import redis_store
from . import index_blue
from flask import render_template, current_app

# 2、装饰视图函数
@index_blue.route('/',methods=["GET","POST"])
def hello_world():


    return render_template('news/index.html')


#每个网站都会去设置/favicon.ico小logo图标
#可以使用current_app.send_static_file(),自动加载static静态文件下面的内容
@index_blue.route('/favicon.ico')
def web_logo():

    return current_app.send_static_file("news/favicon.ico")