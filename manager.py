# -*- 若无相欠，怎会相见 -*-
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app,db

# 调用工厂方法
app = create_app("develop")
# 1、配置SQLAlchemy 导入数据库扩展，并在配置中填写相关配置
# 2、创建redis存储对象，并在配置中填写相关配置
# 3、CSRF 包含请求体的请求都需要开启CSRF
# 4、设置session 利用 flask-session扩展，将 session 数据保存到 Redis 中
# 5、Flask-Script与数据库迁移扩展

# 数据库迁移
manager = Manager(app)
Migrate(app, db)
manager.add_command("db", MigrateCommand)

@app.route('/',methods=['get', 'post'])
def index():


    return "index"


if __name__ == '__main__':
    manager.run()