# -*- 若无相欠，怎会相见 -*-
import logging
from logging.handlers import RotatingFileHandler

import redis
from flask import Flask
from flask_wtf.csrf import CSRFProtect,generate_csrf
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session #Session是用来指定session的存储位置
from config import config_dict
from info.utils.common import do_index_filter


# 1、配置SQLAlchemy 导入数据库扩展，并在配置中填写相关配置
# 2、创建redis存储对象，并在配置中填写相关配置
# 3、CSRF 包含请求体的请求都需要开启CSRF
# 4、设置session 利用 flask-session扩展，将 session 数据保存到 Redis 中
# 5、Flask-Script与数据库迁移扩展
# 创建对象db


db = SQLAlchemy()

redis_store = None

#调用工厂方法 根据不同参数，创建不同环境下的app对象
def create_app(config_name):
    app = Flask(__name__)


    #根据传入的config_name获取到对应的配置类
    config = config_dict[config_name]

    #调用日志函数
    log_file(config.LEVEL)

    #加载配置类中的配置信息
    app.config.from_object(config)

    # 初始化db中的app
    db.init_app(app)

    # decode_responses将byts格式转成str格式
    global redis_store
    redis_store = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses = True)

    # CSRFProtect只做验证工作，cookie中的 csrf_token 和表单中的 csrf_token 需要我们自己实现

    #设置应用程序CSRF保护
    # 开了了csrf保护之后,会对['POST', 'PUT', 'PATCH', 'DELETE']类型的请求方法做校验
    # 获取cookie中的csrf_token, 获取headers请求头里面的csrf_token做校验,只做校验
    # 开发者: 需要手动设置,cookie, headers中的csrf_token
    CSRFProtect(app)

    # 创建对象关联app
    Session(app)

    # 注册首页蓝图对象
    from info.modules.index import index_blue
    app.register_blueprint(index_blue)

    #注册验证蓝图对象
    from info.modules.passport import passport_blu
    app.register_blueprint(passport_blu)

    #设置请求钩子,after_request,每次请求完成之后都会走该钩子修饰的方法
    @app.after_request
    def after_request(resp):
        csrf_token = generate_csrf()
        resp.set_cookie("csrf_token",csrf_token)
        return resp

    #将过滤器添加到模板过滤器列表中
    app.add_template_filter(do_index_filter,"index_filter")

    return app

# 日志文件
def log_file(level):
    # 设置日志的记录等级
    """
    CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0

    """
    logging.basicConfig(level=level)  # 调试debug级

    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)

    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')

    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)

    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)