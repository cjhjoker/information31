# -*- coding:utf8 -*-
from flask import current_app
from flask import make_response
from flask import request

from info import redis_store
from info.utils.captcha.captcha import captcha
from . import passport_blu
from info import constants
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