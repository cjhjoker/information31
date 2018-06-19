# -*- coding:utf8 -*-
from flask import url_for,redirect,g
from info.models import User
from info.utils.common import user_login_data
from . import admin_blu
from flask import render_template,request,current_app,session


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

