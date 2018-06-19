# -*- coding:utf8 -*-
from flask import current_app

from info import constants
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import profile_blu
from flask import render_template,g,redirect,request,jsonify

#新闻收藏列表
@profile_blu.route('/collection')
@user_login_data
def news_collection():
    # 1.获取到参数,p
    page = request.args.get("p",1)

    # 2.参数类型转换
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    #3.分页查询
    try:
        #查询第page,每页展示10条,不进行错误输出
        paginate = g.user.collection_news.paginate(page,constants.USER_COLLECTION_MAX_NEWS,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询异常")

    # 4.将分页对象中的数据取出来,总页数,当前页,对象列表
    total_page = paginate.pages
    current_page = paginate.page
    items = paginate.items

    # 5.将对象列表转成字典列表
    news_list = []
    for news in items:
        news_list.append(news.to_dict())

    # 6.封装data数据
    data = {
        "total_page":total_page,
        "current_page":current_page,
        "news_list":news_list
    }
    # 7、返回相应
    return render_template("news/user_collection.html",data = data)




#密码修改
# 请求路径: /user/pass_info
# 请求方式:GET,POST
# 请求参数:GET无, POST有参数,old_password, new_password
# 返回值:GET请求: user_pass_info.html页面,data字典数据, POST请求: errno, errmsg
@profile_blu.route('/pass_info', methods=['GET','POST'])
@user_login_data
def pass_info():
    #1、 获取用户信息 第一次进来是get请求 直接渲染页面
    if request.method == 'GET':
        return render_template("news/user_pass_info.html")

    # 2、获取参数
    dict_data = request.json
    old_password = dict_data.get("old_password")
    new_password = dict_data.get("new_password")

    # 3、校验参数
    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 4、判断老密码的正确性
    if not g.user.check_passowrd(old_password):
        return jsonify(errno=RET.DATAERR, errmsg="原密码不正确")

    #5.设置新密码
    g.user.password = new_password

    #6.返回响应
    return jsonify(errno=RET.OK,errmsg="修改成功")


# 基本资料展示
# 请求路径: /user/base_info
# 请求方式:GET,POST
# 请求参数:POST请求有参数,nick_name,signature,gender
# 返回值:errno,errmsg
@profile_blu.route('/base_info',methods = ['GET', 'POST'])
@user_login_data
def base_info():
    #1、 获取用户信息 第一次进来是get请求 直接渲染页面
    if request.method == 'GET':
        data = {
            "user_info":g.user.to_dict()
        }
        return render_template("news/user_base_info.html",data = data)

    # 2、获取参数
    dict_data = request.json
    nick_name = dict_data.get("nick_name")
    signature = dict_data.get("signature")
    gender = dict_data.get("gender")

    # 3、校验参数
    if not all([nick_name,signature,gender]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    if not gender in ["MAN", "WOMAN"]:
        return jsonify(errno=RET.DATAERR, errmsg="参数类型不对")

    #4.设置参数到,用户对象属性中
    g.user.nick_name = nick_name
    g.user.signature = signature
    g.user.gender = gender

    #5.返回响应
    return jsonify(errno=RET.OK,errmsg="设置成功")


# 显示个人中心页面
@profile_blu.route('/user_info')
@user_login_data
def get_user_info():

    # 判断用户是否登陆
    if not g.user:
        return redirect('/')

    # 封装用户信息
    data={
        "user_info":g.user.to_dict()
    }

    return render_template("news/user.html",data = data)