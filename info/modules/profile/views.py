# -*- coding:utf8 -*-
from flask import current_app

from info import constants, db
from info.models import News, Category
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import profile_blu
from flask import render_template,g,redirect,request,jsonify

#新闻列表展示
@profile_blu.route('/news_list')
@user_login_data
def news_list():
    # 1.获取参数,分页
    page = request.args.get("p",1)

    # 2.参数类型转换
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    #3.分页查询
    try:
        paginate = News.query.filter(News.user_id == g.user.id).order_by(News.create_time.desc()).paginate(page,3,False)
    except Exception as e:
        current_app.logger.error(e)

        return jsonify(errno=RET.DBERR, errmsg="查询异常")

    # 4.获取分页对象数据
    total_page = paginate.pages
    current_page = paginate.page
    items = paginate.items

    #5.转成字典数据
    news_list = []
    for news in items:
        news_list.append(news.to_review_dict()) # review中带有控制审核状态的变量status

    #6.返回到页面中,渲染
    data = {
        "total_page":total_page,
        "current_page":current_page,
        "news_list":news_list
    }

    return render_template('news/user_news_list.html',data=data)

#新闻发布
# 请求路径: /user/news_release
# 请求方式:GET,POST
# 请求参数:GET无, POST ,title, category_id,digest,index_image,content
# 返回值:GET请求,user_news_release.html, data分类列表字段数据, POST,errno,errmsg
@profile_blu.route('/news_release', methods=['GET', 'POST'])
@user_login_data
def news_release():
    #1、第一次进来GET请求，直接渲染页面
    if request.method == "GET":

        #获取所有的分类列表
        try:
            categoies = Category.query.all()
            categoies.pop(0)#弹出编号为0最新分类
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="分类获取失败")

        #转成字典列表
        category_list = []
        for category in categoies:
            category_list.append(category.to_dict())

        return render_template('news/user_news_release.html',data={"categories":category_list})

    # 2.获取参数
    title = request.form.get("title") #新闻标题
    category_id = request.form.get("category_id") #分类id
    digest = request.form.get("digest") #摘要
    content = request.form.get("content") #内容
    index_image = request.files.get("index_image") #图片

    # 3.校验参数
    if not all([title, category_id, digest, content, index_image]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 4.上传新闻图片
    # try:
    #     # 读取图片内容
    #     image_data = index_image.read()
    #
    #     # 上传图片
    #     image_name = image_storage(image_data)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.THIRDERR, errmsg="七牛云异常")
    #
    # if not image_name:
    #     return jsonify(errno=RET.NODATA, errmsg="图片上传失败")

    # 5.创建新闻对象,设置新闻对象属性
    news = News()
    news.title = title
    news.source = "个人发布"
    news.digest = digest
    news.content = content
    # news.index_image_url = constants.QINIU_DOMIN_PREFIX + image_name
    news.category_id = category_id
    news.user_id = g.user.id
    #审核状态1
    news.status = 1

    # 6.提交到数据库中
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

        return jsonify(errno=RET.DBERR,errmsg="新闻发布失败")
    # 7.返回响应
    return jsonify(errno=RET.OK,errmsg="新闻发布成功")


#新闻收藏列表
@profile_blu.route('/collection')
@user_login_data
def news_collection():
    # 1.获取到参数,p
    page = request.args.get("p",1)

    # 2.参数类型转换
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    #3.分页查询
    try:
        #查询第page,每页展示10条,不进行错误输出
        paginate = g.user.collection_news.paginate(page,constants.USER_COLLECTION_MAX_NEWS,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询异常")

    # 4.将分页对象中的数据取出来,总页数,当前页,对象列表
    total_page = paginate.pages
    current_page = paginate.page
    items = paginate.items

    # 5.将对象列表转成字典列表
    news_list = []
    for news in items:
        news_list.append(news.to_dict())

    # 6.封装data数据
    data = {
        "total_page":total_page,
        "current_page":current_page,
        "news_list":news_list
    }
    # 7、返回相应
    return render_template("news/user_collection.html",data = data)



#密码修改
# 请求路径: /user/pass_info
# 请求方式:GET,POST
# 请求参数:GET无, POST有参数,old_password, new_password
# 返回值:GET请求: user_pass_info.html页面,data字典数据, POST请求: errno, errmsg
@profile_blu.route('/pass_info', methods=['GET','POST'])
@user_login_data
def pass_info():
    #1、 获取用户信息 第一次进来是get请求 直接渲染页面
    if request.method == 'GET':
        return render_template("news/user_pass_info.html")

    # 2、获取参数
    dict_data = request.json
    old_password = dict_data.get("old_password")
    new_password = dict_data.get("new_password")

    # 3、校验参数
    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 4、判断老密码的正确性
    if not g.user.check_passowrd(old_password):
        return jsonify(errno=RET.DATAERR, errmsg="原密码不正确")

    #5.设置新密码
    g.user.password = new_password

    #6.返回响应
    return jsonify(errno=RET.OK,errmsg="修改成功")


# 基本资料展示
# 请求路径: /user/base_info
# 请求方式:GET,POST
# 请求参数:POST请求有参数,nick_name,signature,gender
# 返回值:errno,errmsg
@profile_blu.route('/base_info',methods = ['GET', 'POST'])
@user_login_data
def base_info():
    #1、 获取用户信息 第一次进来是get请求 直接渲染页面
    if request.method == 'GET':
        data = {
            "user_info":g.user.to_dict()
        }
        return render_template("news/user_base_info.html",data = data)

    # 2、获取参数
    dict_data = request.json
    nick_name = dict_data.get("nick_name")
    signature = dict_data.get("signature")
    gender = dict_data.get("gender")

    # 3、校验参数
    if not all([nick_name,signature,gender]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    if not gender in ["MAN", "WOMAN"]:
        return jsonify(errno=RET.DATAERR, errmsg="参数类型不对")

    #4.设置参数到,用户对象属性中
    g.user.nick_name = nick_name
    g.user.signature = signature
    g.user.gender = gender

    #5.返回响应
    return jsonify(errno=RET.OK,errmsg="设置成功")


# 显示个人中心页面
@profile_blu.route('/user_info')
@user_login_data
def get_user_info():

    # 判断用户是否登陆
    if not g.user:
        return redirect('/')

    # 封装用户信息
    data={
        "user_info":g.user.to_dict()
    }

    return render_template("news/user.html",data = data)