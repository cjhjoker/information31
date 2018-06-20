#coding:utf8
import logging
import random

from datetime import timedelta, datetime

from info.models import User
from flask import current_app
from flask_migrate import Migrate,MigrateCommand
from flask_script import Manager
from info import create_app,db,models

#调用工厂方法

app = create_app("develop")


#配置数据库迁移命令
manager = Manager(app) #创建manager管理app
Migrate(app,db) #将app和db关联
manager.add_command("db",MigrateCommand)#给manager添加操作命令


@manager.option('-u', '--username', dest='username')
@manager.option('-p', '--password', dest='password')
def createsuperuser(username,password):

    #创建管理员对象
    admin = User()

    #设置属性
    admin.nick_name = username
    admin.mobile = username
    admin.password = password
    admin.is_admin = True

    #添加到数据库
    try:
        db.session.add(admin)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        print('创建失败')
        return '创建失败'

    print('创建成功')

def add_test_users():

    #获取当前时间
    now = datetime.now()

    #遍历创建好多个用户
    user_list = []
    for i in range(0,1000):
        #创建用户对象
        user = User()
        #设置属性
        username = "138%08d"%i
        user.mobile = username
        user.nick_name = username
        user.password_hash = "pbkdf2:sha256:50000$hjtIx0ht$aa18ba3fe123d7a8d09df80963cd4d2edf7e0a66e27ffddd92fbfcc9ae2ef450"
        user.is_admin = False
        #用当前时间-（一个月以内的任意秒数）=一个月以来的任意时间点
        user.last_login =  now - timedelta(seconds=random.randint(0,3600*24*31))

        user_list.append(user)

        print(user.mobile)

    # 添加到数据库中
    with app.app_context():  #解决工作范围超出应用上下文问题
        try:
            db.session.add_all(user_list)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            print("添加失败")

    print("添加成功")


if __name__ == '__main__':
    print(app.url_map)
    add_test_users()
    manager.run()