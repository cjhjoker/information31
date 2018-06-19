# -*- coding:utf8 -*-
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import profile_blu
from flask import render_template,g,redirect,request,jsonify

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