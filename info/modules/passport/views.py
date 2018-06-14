# -*- coding:utf8 -*-
import random
import re

from flask import current_app, jsonify
from flask import make_response
from flask import request

from info import redis_store
from info.utils.captcha.captcha import captcha
from . import passport_blu
from info import constants
from info.utils.response_code import RET
#登陆用户
# 请求路径: /passport/login
# 请求方式: POST
# 请求参数: mobile,password
# 返回值: errno, errmsg




#短信验证码
# 请求路径: /passport/sms_code
# 请求方式: POST
# 请求参数: mobile, image_code,image_code_id
# 返回值: errno, errmsg
@passport_blu.route('/smscode')
def send_sms():
    """
    1. 接收参数
    2、判断是否为空
    3. 校验手机号格式是否正确
    4. 判断图片验证码是否过期
    5. 通过传入的图片编码去redis中取出真实的图片验证码内容
    6、校验验证码是否相等
    7. 生成短信验证码
    8、发送短信
    9. redis中保存短信验证码内容
    10. 返回发送成功的响应
    :return:
    """
    # 1.获取参数,request.data,  json.loads(json)
    dict_data = request.json
    mobile = dict_data.get("mobile")
    image_code = dict_data.get("image_code")
    image_code_id = dict_data.get("image_code_id")

    # 2.校验参数为空情况
    if not all([mobile,image_code,image_code_id]):
        return jsonify(error=RET.PARAMERR, errmsg = "参数不完整")

    # 3.验证手机号格式
    if re.match(r'1[356789]\d{9}',mobile):
        return jsonify(error=RET.DATAERR, errmsg="手机号格式不正确")
    # 4.通过image_code_id取出redis中的图片验证码
    try:
        redis_image_code = redis_store.get("image_code_id")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查找图片验证码失败")
    # 5.判断取出的图片验证码是否过期
    if not redis_image_code:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码过期")
    # 6.判断两者图片验证码是否相等
    if image_code.lower() != redis_image_code.lower():
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码不正确")
    # 7.生成短信验证码
    sms_code = "%06d" % random.randint(0, 999999)
    # 8.调用云通讯发送(手机号,短信验证码,有效期,模板id)
    # ccp = CCP()
    # result =  ccp.send_template_sms(mobile,[sms_code,5],1)
    #
    # if result == -1:
    #     return jsonify(errno=RET.THIRDERR, errmsg="短信验证码发送失败")

    current_app.logger.debug("短信验证码是 = %s" % sms_code)
    # 9.保存到redis
    try:
       redis_store.set("sms_code:%s"%mobile,sms_code,constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="短信保存失败")
    # 10.返回前端
    return jsonify(errno=RET.OK, errmsg="发送成功")




#图片验证码
@passport_blu.route('/image_code')
def get_image_code():
    """
    1、获取请求参数
    2、生成图片验证码
    3、保存到redis
    4、返回图片验证码到前端
    :return:
    """
    # 1、获取get请求参数,args获取地址里的参数，(根据key值获取value值),获取的是？后面的参数 www.baidu.com?name=haha&age=12
    cur_id = request.args.get("cur_id")
    pre_id = request.args.get("pre_id")
    # 2、生成图片验证码
    name,text,image_data = captcha.generate_captcha()
    # 3、保存到redis
    try:
        #key+value+time
        redis_store.set("image_code:%s"%cur_id,text,constants.IMAGE_CODE_REDIS_EXPIRES)

        #判断是否有上一个UUID，如果有就删除
        if pre_id:
            redis_store.delete("image_code:%s"%pre_id)

    except Exception as e:
        current_app.logger.error(e)

    # 4、返回图片验证码到前端
    response = make_response(image_data)
    response.headers["Content-Type"] = "image/jpg"

    return response