# -*- coding:utf8 -*-
import datetime
import time
from flask import url_for,redirect,g, jsonify

from info import constants
from info.models import User, News
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import admin_blu
from flask import render_template,request,current_app,session

#新闻审核, 详情
# 请求路径: /admin/news_review_detail
# 请求方式: GET,POST
# 请求参数: GET, news_id, POST,news_id, action
# 返回值:GET,渲染news_review_detail.html页面,data字典数据
@admin_blu.route('/news_review_detail',methods=["GET","POST"])
def news_review_detail():
    # 一、如果是get请求
    if request.method == "GET":
        #1、get请求，获取参数news_id
        news_id = request.args.get("news_id")

        #2、检验参数是否为空
        if not news_id: return jsonify(errno=RET.PARAMERR, errmsg="新闻编号不存在")

        #3、查询新闻对象，判断是否为空
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询失败")

        if not news:
            return jsonify(errno=RET.NODATA, errmsg="新闻不存在")


        #4、返回数据
        return render_template('admin/news_review_detail.html', news=news.to_dict())
    # 二、如果是POST请求，说明做了审核操作
    #1.获取参数
    news_id = request.json.get("news_id")
    action = request.json.get("action")

    #2.校验参数
    if not all([news_id,action]):
        return jsonify(errno=RET.NODATA,errmsg="参数不全")

    #校验操作类型
    if not action in ["accept","reject"]:
        return jsonify(errno=RET.DATAERR, errmsg="操作类型有误")

    #3.查询新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询异常")

    #4.判断新闻是否存在
    if not news: return jsonify(errno=RET.NODATA,errmsg="新闻不存在")

    #5.根据操作类型,通过/拒绝
    if action == "accept":
        news.status = 0
    else:
        reason = request.json.get("reason")
        if not reason: return jsonify(errno=RET.NODATA,errmsg="需要填写拒绝原因")
        news.status = -1
        news.reason = reason

    #5.返回响应
    return jsonify(errno=RET.OK,errmsg="操作成功")


#新闻审核列表
# 请求路径: /admin/news_review
# 请求方式: GET
# 请求参数: GET, p,keywords
# 返回值:渲染user_list.html页面,data字典数据
#新闻审核列表
@admin_blu.route('/news_review')
def news_review():
    #1、获取参数
    page = request.args.get("p",1)
    keywords = request.args.get("keywords")

    #2、转换int类型
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    #3、分页查询
    try:

        # 判断是否有搜索关键字
        filters = [News.status != 0]
        if keywords:
            filters.append(News.title.contains(keywords)) #contains搜索包含有关键字的新闻标题，
            # endswith以关键字结尾，startswith以关键字开始

        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, 10, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")

    #4、获取分页查询数据：总页数，当前页，对象列表
    total_page = paginate.pages
    current_page = paginate.page
    items = paginate.items

    #5、转换成字典列表
    news_list = []
    for news in items:
        news_list.append(news.to_review_dict())

    #6、拼接data，返回响应
    data = {
        "total_page":total_page,
        "current_page":current_page,
        'news_list':news_list
    }

    return render_template('admin/news_review.html',data=data)


#获取用户列表
# 请求路径: /admin/user_list
# 请求方式: GET
# 请求参数: p
# 返回值:渲染user_list.html页面,data字典数据
@admin_blu.route('/user_list')
def user_list():
    """
    #1、获取参数，page页数p
    #2、转成整数
    #3、分页查询
    #4、获取分页对象数据：总页数、当前页、对象列表
    #5、转换成字典列表
    #6、拼接data，返回数据
    :return:
    """
    #1、获取参数，page页数p
    page = request.args.get("p",1)

    #2、转成整数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    #3、分页查询
    try:
        paginate = User.query.filter(User.is_admin == False).order_by(User.last_login.desc()).paginate(page,10,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")

    #4、获取分页对象数据：总页数、当前页、对象列表
    total_page = paginate.pages
    current_page = paginate.page
    items = paginate.items

    #5、转换成字典列表
    user_list = []
    for user in items:
        user_list.append(user.to_admin_dict())

    #6、拼接data，返回数据
    data = {
        "total_page": total_page,
        "current_page": current_page,
        "user_list": user_list
    }

    return render_template("admin/user_list.html",data = data)



#管理员退出
@admin_blu.route('/logout', methods=['DELETE'])
def logout():

    session.pop("user_id","")
    session.pop("nick_name","")
    session.pop("mobile","")
    session.pop("is_admin","")

    return jsonify(errno=RET.OK,errmsg="退出成功")



#管理员,用户列表页面统计
# 请求路径: /admin/user_count
# 请求方式: GET
# 请求参数: 无
# 返回值:渲染页面user_count.html,字典数据
@admin_blu.route('/user_count')
def user_count():

    # 1.获取当前程序总人数
    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询总人数错误")

    #2、获取月活人数
    cal = time.localtime()# 当前时间
    try:

        # 计算月初时间
        mon_start_str = "%d-%d-01"%(cal.tm_year,cal.tm_mon)
        mon_start_date = datetime.strptime(mon_start_str,"%Y-%m-%d")

        #查询当前月活人数
        mon_count =  User.query.filter(User.last_login >= mon_start_date,User.is_admin == False).count()

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询月活人数错误")

    #3.日活人数
    try:

        #计算日初时间,6月19, 0:00
        day_start_str = "%d-%d-%d"%(cal.tm_year,cal.tm_mon,cal.tm_mday)
        day_start_date =  datetime.strptime(day_start_str,"%Y-%m-%d")

        #查询当前月活人数
        day_count =  User.query.filter(User.last_login >= day_start_date,User.is_admin == False).count()

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询总人数错误")


    # 4.日期活跃, 日期活跃所对应的人数
    active_date = []
    active_count = []

    for i in range(0, 31):
        # 当天开始时间A
        begin_date = day_start_date - datetime.timedelta(days=i)
        # 当天开始时间, 的后一天B
        end_date = day_start_date - datetime.timedelta(days=i - 1)

        # 添加当天开始时间字符串到, 活跃日期中
        active_date.append(begin_date.strftime("%Y-%m-%d")) #显示x轴数据，可修改：%m-%d

        # 查询时间A到B这一天的注册人数
        everyday_active_count = User.query.filter(User.is_admin == False, User.last_login >= begin_date,
                                                  User.last_login <= end_date).count()

        # 添加当天注册人数到,获取数量中
        active_count.append(everyday_active_count)


    #反转日期和人数
    active_date.reverse()
    active_count.reverse()

    # 5.拼接成data展示到页面中
    data = {
        "total_count": total_count,
        "mon_count": mon_count,
        "day_count": day_count,
        "active_date": active_date,
        "active_count": active_count
    }

    return render_template('admin/user_count.html', data=data)


#管理员首页
@admin_blu.route('/index')
@user_login_data
def index():

    return render_template('admin/index.html',user=g.user.to_admin_dict())



#显示管理员登陆页面
# 请求路径: /admin/login
# 请求方式: GET,POST
# 请求参数:GET,无, POST,username,password
# 返回值: GET渲染login.html页面, POST,login.html页面,errmsg
@admin_blu.route('/login',methods=['GET','POST'])
def admin_login():

    # 1、第一次进入管理员登录页面
    if request.method == 'GET':
        return render_template("admin/index.html")

    #2、form表单提交、获取参数
    username = request.form.get('username')
    password = request.form.get('password')

    #3、根据参数查询用户对象
    try:
        user = User.query.filter(User.mobile == username,User.is_admin == True).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/login.html', errmsg="用户查询异常")

    #4、判断用户对象是否存在
    if not user:
        return render_template('admin/login.html', errmsg="用户不存在")

    #5、校验密码
    if not user.check_passowrd(password):
        return render_template('admin/login.html', errmsg="密码不正确")

    # 保存用户信息到session中
    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile
    session["is_admin"] = user.is_admin

    #6、跳转到首页
    return redirect(url_for('admin.index'))

