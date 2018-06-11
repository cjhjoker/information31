# -*- 若无相欠，怎会相见 -*-
import logging
import redis
# 1、配置SQLAlchemy 导入数据库扩展，并在配置中填写相关配置
# 2、创建redis存储对象，并在配置中填写相关配置
# 3、CSRF 包含请求体的请求都需要开启CSRF
# 4、设置session 利用 flask-session扩展，将 session 数据保存到 Redis 中
# 5、Flask-Script与数据库迁移扩展
class Config(object):
    """工程配置信息"""
    DEBUG = True
    SERECT_KEY = "asdqwewdaczx"
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/information31"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # redis配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = "5000"
    # Session配置
    SESSION_TYPE = "redis" # 指定 session 保存到 redis 中
    SESSION_USE_SIGNER = True #让 cookie 中的 session_id 被加密签名处理
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT) # 使用 redis 的实例
    PERMANENT_SESSION_LIFETIME = 3600 * 24 * 2 # session 的有效期，单位是秒

    # 设置默认日志等级
    LEVEL = logging.DEBUG


class DevelopementConfig(Config):
    """开发模式下的配置"""
    pass

class ProductionConfig(Config):
    """生产模式下的配置"""
    DEBUG = False
    LEVEL = logging.ERROR
    pass

class TestingConfig(Config):
    """测试模式下的配置"""
    pass


# 由于类会越来越多，设置统一访问入口，使用dict管理
config_dict = {
    "develop":DevelopementConfig,
    "produc":ProductionConfig,
    "test":TestingConfig

}
