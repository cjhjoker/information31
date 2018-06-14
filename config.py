#coding:utf8
import logging

import redis

#基本配置信息
class Config(object):

    DEBUG = True
    SECRET_KEY = "fjdkjfkdjfkdfjd"

    #数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/information31"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True # 数据库内容发送改变之后自动提交

    #redis的配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    #指定session配置信息
    SESSION_TYPE = "redis"
    SESSION_USE_SIGNER = True #session签名存储
    SESSION_REDIS = redis.StrictRedis(REDIS_HOST,REDIS_PORT)
    PERMANENT_SESSION_LIFETIME = 3600 * 24 * 2 #设置session有效时间

    #默认日志等级
    LEVEL = logging.DEBUG

#开发模式
class DeveloperConfig(Config):
    pass

#生产模式
class ProductConfig(Config):
    DEBUG = False
    LEVEL = logging.ERROR
    pass


#测试模式
class TestingConfig(Config):
    pass

#设置统一访问入口,使用config_dict
config_dict = {
    "develop":DeveloperConfig,
    "product":ProductConfig,
    "testing":TestingConfig
}