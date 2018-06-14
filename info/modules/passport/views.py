#coding:utf8
import random
import re
from datetime import datetime
from flask import request, current_app, make_response, json, jsonify, session
from info import redis_store, constants, db
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.utils.captcha.captcha import  captcha
from info.utils.response_code import RET
from . import passport_blu

#退出登陆(restful)
# 请求路径: /passport/logout
# 请求方式: POST
# 请求参数: 无
# 返回值: errno, errmsg
@passport_blu.route('/logout', methods=['POST'])
def logout():

    #清除session中的数据
    # session.clear()
    session.pop("user_id","")
    session.pop("nick_name","")
    session.pop("mobile","")

    #返回响应
    return jsonify(errno=RET.OK,errmsg="退出成功")



#登陆用户
# 请求路径: /passport/login
# 请求方式: POST
# 请求参数: mobile,password
# 返回值: errno, errmsg
@passport_blu.route('/login', methods=['POST'])
def login():
    """
    1.获取参数
    2.校验参数
    3.通过手机号取出用户对象
    4.判断用户对象是否存在
    5.判断密码是否正确
    6.记录用户登陆状态
    7.返回前端页面
    :return:
    """
    # 1.获取参数
    dict_data = request.json
    mobile = dict_data.get("mobile")
    password = dict_data.get("password")

    # 2.校验参数
    if not all([mobile,password]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不完整")

    # 3.通过手机号取出用户对象
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询异常")

    # 4.判断用户对象是否存在
    if not user:
        return jsonify(errno=RET.NODATA, errmsg="该用户不存在")

    # 5.判断密码是否正确
    if not user.check_passowrd(password):
        return jsonify(errno=RET.DATAERR, errmsg="密码输入错误")

    # 6.记录用户登陆状态
    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile

    #记录用户最后登陆时间
    user.last_login = datetime.now()

    # 7.返回前端页面
    return jsonify(errno=RET.OK,errmsg="登陆成功")



#注册用户
# 请求路径: /passport/register
# 请求方式: POST
# 请求参数: mobile, sms_code,password
# 返回值: errno, errmsg
@passport_blu.route('/register', methods=['POST'])
def register():
    """
    1.获取参数
    2.校验参数(为空校验,手机号格式校验)
    3.通过手机号取出redis中的短信验证码
    4.判断是否过期
    5.判断是否相等
    6.创建用户对象,设置属性
    7.保存到数据库
    8.返回前端页面
    :return:
    """
    # 1.获取参数,三种方式获取到字典,先转成json,再次转成字典/ get_json / json
    #第一种:
    # json_data = request.data
    # dict_data = json.loads(json_data)
    #第二种:
    # dict_data =  request.get_json()
    #第三种:
    dict_data =  request.json

    mobile = dict_data.get("mobile")
    sms_code = dict_data.get("sms_code")
    password = dict_data.get("password")

    # 2.校验参数(为空校验,手机号格式校验)
    if not all([mobile,sms_code,password]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不完整")

    # 2.1验证手机号格式
    if not re.match('1[356789]\\d{9}',mobile):
        return jsonify(errno=RET.DATAERR,errmsg="手机号格式不正确")

    # 3.通过手机号取出redis中的短信验证码
    try:
        redis_sms_code = redis_store.get("sms_code:%s"%mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取短信验证码异常")

    # 4.判断是否过期
    if not redis_sms_code:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码过期")

    # 5.判断是否相等
    if sms_code != redis_sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码填写错误")

    # 6.创建用户对象,设置属性
    user = User()
    user.nick_name = mobile
    user.mobile = mobile
    #普通方式
    # user.password_hash = jia_mi_fangfa(password)
    #使用@propert装饰之后,可以直接当成属性的形式来调用
    user.password = password

    # user.password_hash = user.jiami_secret(password)

    # 7.保存到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="用户保存异常")

    # 8.返回前端页面
    return jsonify(errno=RET.OK,errmsg="注册成功")


#短信验证码
# 请求路径: /passport/sms_code
# 请求方式: POST
# 请求参数: mobile, image_code,image_code_id
# 返回值: errno, errmsg
@passport_blu.route('/sms_code', methods=['POST'])
def get_sms_code():
    """
    1.获取参数,request.data,  json.loads(json)
    2.校验参数为空情况
    3.验证手机号格式
    4.通过image_code_id取出redis中的图片验证码
    5.判断取出的图片验证码是否过期
    6.判断两者图片验证码是否相等
    7.生成短信验证码
    8.调用云通讯发送(手机号,短信验证码,有效期,模板id)
    9.保存到redis
    10.返回前端
    :return:
    """
    # 1.获取参数,request.data,  json.loads(json)
    json_data = request.data
    dict_data = json.loads(json_data)
    mobile = dict_data.get("mobile")
    image_code = dict_data.get("image_code")
    image_code_id = dict_data.get("image_code_id")


    # 2.校验参数为空情况
    if not all([mobile,image_code,image_code_id]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不完整")

    # 3.验证手机号格式
    if not re.match('1[356789]\\d{9}',mobile):
        return jsonify(errno=RET.DATAERR,errmsg="手机号格式不正确")

    # 4.通过image_code_id取出redis中的图片验证码
    try:
       redis_image_code = redis_store.get("image_code:%s"%image_code_id)
    except Exception as e:
       current_app.logger.error(e)
       return jsonify(errno=RET.DBERR,errmsg="查找图片验证码失败")

    # 5.判断取出的图片验证码是否过期
    if not redis_image_code:
        return jsonify(errno=RET.NODATA,errmsg="图片验证码过期")

    # 6.判断两者图片验证码是否相等
    if image_code.lower() != redis_image_code.lower():
        return jsonify(errno=RET.DATAERR,errmsg="图片验证码不正确")

    # 7.生成短信验证码
    sms_code = "%06d"%random.randint(0,999999)

    # 8.调用云通讯发送(手机号,短信验证码,有效期,模板id)
    # ccp = CCP()
    # result =  ccp.send_template_sms(mobile,[sms_code,5],1)
    #
    # if result == -1:
    #     return jsonify(errno=RET.THIRDERR, errmsg="短信验证码发送失败")

    current_app.logger.debug("短信验证码是 = %s"%sms_code)

    # 9.保存到redis
    try:
       redis_store.set("sms_code:%s"%mobile,sms_code,constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="短信保存失败")

    # 10.返回前端
    return jsonify(errno=RET.OK,errmsg="发送成功")





#图片验证码
@passport_blu.route('/image_code')
def get_image_code():
    """
    1.获取请求参数
    2.生成图片验证码
    3.保存到reids
    4.返回图片验证码
    :return:
    """
    # 1.获取请求参数,args是获取?后面的参数  www.baidu.com?name=zhangsan&age=13
    cur_id = request.args.get("cur_id")
    pre_id = request.args.get("pre_id")

    # 2.生成图片验证码
    name,text,image_data =  captcha.generate_captcha()

    # 3.保存到reids
    try:
        # key + value +time
        redis_store.set("image_code:%s"%cur_id,text,constants.IMAGE_CODE_REDIS_EXPIRES)

        #判断是否有上一个uuid,如果存在则删除
        if pre_id:
            redis_store.delete("image_code:%s"%pre_id)

    except Exception as e:
        current_app.logger.error(e)

    # 4.返回图片验证码
    response = make_response(image_data)
    response.headers["Content-Type"] = "image/jpg"

    return response
