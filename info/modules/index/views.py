# -*- 若无相欠，怎会相见 -*-
from flask import session

from info import constants
from info import redis_store
from info.models import User,News,Category
from . import index_blue
from flask import render_template, current_app

# 2、装饰视图函数
@index_blue.route('/',methods=["GET","POST"])
def hello_world():
    #获取用户编号
    user_id = session.get("user_id")
    #通过编号获取数据库用户对象
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # 查询数据库,按照点击量,前10名的新闻(反向排序)
    try:
        click_news = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS).all()
    except Exception as e:
        current_app.logger.error(e)

    #将对象列表,转成字典列表
    click_news_list = []
    for news in click_news:
        click_news_list.append(news.to_dict())

    #获取所有的分类数据
    try:
        categoies =  Category.query.all()
    except Exception as e:
        current_app.logger.error(e)

    #将分类对象列表转成字典列表
    category_list = []
    for categoy in categoies:
        category_list.append(categoy.to_dict())

    #返回前端页面
    data = {
        #如果user为空反会None,如果有内容返回左边
        "user_info":user.to_dict() if user else None,
        "click_news_list":click_news_list,
        "categoies":category_list
    }

    return render_template('news/index.html', data=data)


#每个网站都会去设置/favicon.ico小logo图标
#可以使用current_app.send_static_file(),自动加载static静态文件下面的内容
@index_blue.route('/favicon.ico')
def web_logo():

    return current_app.send_static_file("news/favicon.ico")