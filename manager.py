#coding:utf8
import logging

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


if __name__ == '__main__':
    print(app.url_map)

    manager.run()