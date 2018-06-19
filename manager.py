#coding:utf8
import logging
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



if __name__ == '__main__':
    print(app.url_map)

    manager.run()