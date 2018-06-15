# -*- 若无相欠，怎会相见 -*-
from flask import g
from flask import request, jsonify
from flask import session

from info import constants
from info import redis_store
from info.models import User,News,Category
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import index_blue
from flask import render_template, current_app

# 1、首页新闻列表
# 请求路径: /newslist
# 请求方式: GET
# 请求参数: cid,page,per_page
# 返回值: data数据
@index_blue.route('/newslist')
def newslist():
    """
    思路分析
    1、获取参数
    2、校验参数，转换参数类型
    3、根据条件查询数据对象
    4.将查询到的分类对象数据,转成字典
    5.返回响应请求
    :return:
    """
    # 1.获取参数
    cid =  request.args.get("cid") # 分类编号
    page =  request.args.get("page",1) #分页数
    per_page =  request.args.get("per_page",10) #每页多少数据
    # 2.校验参数,转换参数类型(出现异常可以设置默认参数)
    try:
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
        per_page = 10
    # 3.根据条件查询数据
    try:
        # 判断分类编号是否不等于 1
        filters=[]
        if cid != "1":
            filters.append(News.category_id == cid) #新闻分类id==分类编号
        # 查询新闻数据根据条件 获取paginate对象
        # *list 对列表进行解包，取出列表中数据 News.query.filter精确查找
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)

        #获取分页中的内容,总页数,当前页,当前页的所有对象
        totalPage = paginate.pages
        currentPage = paginate.page
        items = paginate.items

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    # 4.将查询到的分类对象数据,转成字典
    newsList = []
    for news in items:
        newsList.append(news.to_dict())

    # 5.返回响应请求
    return jsonify(errno=RET.OK,errmsg="获取数据成功",cid=cid,currentPage=currentPage,totalPage=totalPage,newsList=newsList)






# 2、首页新闻信息
@index_blue.route('/',methods=["GET","POST"])
@user_login_data
def index():
    # #获取用户编号
    # user_id = session.get("user_id")
    # #通过编号获取数据库用户对象
    # user = None
    # if user_id:
    #     try:
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)

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
        "user_info":g.user.to_dict() if g.user else None,
        "click_news_list":click_news_list,
        "categoies":category_list
    }

    return render_template('news/index.html', data=data)


#每个网站都会去设置/favicon.ico小logo图标
#可以使用current_app.send_static_file(),自动加载static静态文件下面的内容
@index_blue.route('/favicon.ico')
def web_logo():

    return current_app.send_static_file("news/favicon.ico")