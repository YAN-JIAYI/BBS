from django.shortcuts import render, HttpResponse, redirect
from app01 import myforms
from app01 import models
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from utils.mypage import Pagination
from django.db.models import Count
from django.db.models.functions import TruncMonth
import json
from django.db.models import F
from django.utils.safestring import mark_safe
from django.db import transaction
from bs4 import BeautifulSoup
from BBS import settings
import os


# Create your views here.
def register(request):
    # 产生一个空对象
    form_obj = myforms.MyRegForm()
    if request.method == 'POST':
        back_dic = {'code': 1000, 'msg': ''}
        # 校验数据
        form_obj = myforms.MyRegForm(request.POST)
        if form_obj.is_valid():
            clean_data = form_obj.cleaned_data
            clean_data.pop('confirm_password')
            file_obj = request.FILES.get('avatar')
            if file_obj:
                clean_data['avatar'] = file_obj
            models.UserInfo.objects.create_user(**clean_data)
            back_dic['url'] = '/login/'

        else:
            back_dic['code'] = 2000
            back_dic['msg'] = form_obj.errors
        return JsonResponse(back_dic)
    return render(request, 'register.html', locals())


def login(request):
    if request.method == "POST":
        back_dic = {'code': 1000, 'msg': ''}
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')
        # 校验验证码是否正确
        if request.session.get('code').upper() == code.upper():
            user_obj = auth.authenticate(username=username, password=password)
            if user_obj:
                # 保存用户登录状态
                auth.login(request, user_obj)
                back_dic['url'] = '/home/'

            else:
                back_dic['code'] = 2000
                back_dic['msg'] = '用户名或密码错误'
        else:
            back_dic['code'] = 3000
            back_dic['msg'] = '验证码错误'
        return JsonResponse(back_dic)
    return render(request, 'login.html')


from PIL import Image, ImageDraw, ImageFont
import random
from io import BytesIO, StringIO


def get_random():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


# 图片验证相关
def get_code(request):
    img_obj = Image.new('RGB', (310, 35), get_random())
    img_draw = ImageDraw.Draw(img_obj)  # 生成一个画笔对象
    img_font = ImageFont.truetype('static/font/111.ttf', 30)  # 字体样式

    # 生成随机验证码
    code = ''
    for i in range(5):
        random_upper = chr(random.randint(65, 90))
        random_lower = chr(random.randint(97, 122))
        random_int = str(random.randint(0, 9))
        temp = random.choice([random_upper, random_lower, random_int])
        # 将产生的随机字符写在图片上
        img_draw.text((i * 45 + 45, 0), temp, get_random(), img_font)
        code += temp

    print(code)
    # 将随机验证码存储起来，以便其它函数调用
    request.session['code'] = code

    io_obj = BytesIO()
    img_obj.save(io_obj, 'png')
    return HttpResponse(io_obj.getvalue())


# 首页
def home(request):
    article_list = models.Article.objects.all()
    page_obj = Pagination(current_page=request.GET.get('page', 1), all_count=article_list.count())
    page_queryset = article_list[page_obj.start:page_obj.end]
    for article in page_queryset:
        print(article.blog)
    return render(request, 'home.html', locals())


@login_required
def logout(request):
    # 删除用户session信息
    auth.logout(request)  # 相当于request.session.flush()
    return redirect('/login/')


@login_required
def set_password(request):
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ''}
        if request.method == 'POST':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            # 校验两次密码是否一致
            if new_password == confirm_password:
                # 先校验旧密码是否正确
                is_right = request.user.check_password(old_password)
                if is_right:
                    request.user.set_password(new_password)
                    request.user.save()  # 一定要记得保存
                    back_dic['url'] = '/login/'
                else:
                    back_dic['code'] = 2000
                    back_dic['msg'] = '原密码错误'
            else:
                back_dic['code'] = 3000
                back_dic['msg'] = '两次密码不一致'
            return JsonResponse(back_dic)


def site(request, username, **kwargs):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    if not user_obj:
        return render(request, 'errors.html')
    blog = user_obj.blog
    # 查询当前用户所有的文章数
    article_list = models.Article.objects.filter(blog=blog)
    '''侧边栏筛选'''
    if kwargs:
        condition = kwargs.get('condition')
        param = kwargs.get('param')
        if condition == 'category':
            article_list = article_list.filter(category_id=param)
        elif condition == 'tag':
            article_list = article_list.filter(tags__id=param)  # 跨表查询
        else:
            year, month = param.split('-')
            print(year)
            print(month)
            article_list = article_list.filter(create_time__year=year, create_time__month=month)  # 双下滑线操作
            print(article_list)
            print(year)
            print(month)

    category_list = models.Category.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list(
        'name', 'count_num', 'pk')  # 统计文章数
    tag_list = models.Tag.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list('name',
                                                                                                         'count_num',
                                                                                                         'pk')
    date_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values(
        'month').annotate(count_num=Count('pk')).order_by('-month').values_list('month', 'count_num')
    print(date_list)
    return render(request, 'site.html', locals())


def article_detail(request, username, article_id):
    article_obj = models.Article.objects.filter(pk=article_id).first()
    comment_list = models.Comment.objects.filter(article=article_obj)
    print(article_id)
    return render(request, 'article_detail.html', locals())


def up_down(request):
    if request.is_ajax():
        if request.method == 'POST':
            back_dic = {'code': 1000, 'msg': ''}
            print(123456)
            if request.user.is_authenticated():
                article_id = request.POST.get('article_id')
                is_up = request.POST.get('is_up')
                is_up = json.loads(is_up)
                article_obj = models.Article.objects.filter(pk=article_id).first()
                if not article_obj.blog.userinfo == request.user:
                    is_click = models.UpAndDown.objects.filter(user=request.user, article=article_obj)
                    if not is_click:
                        if is_up:
                            models.Article.objects.filter(pk=article_id).update(up_num=F('up_num') + 1)
                            back_dic['msg'] = '点赞成功'
                        else:
                            models.Article.objects.filter(pk=article_id).update(down_num=F('down_num') + 1)
                            back_dic['msg'] = '点踩成功'
                        models.UpAndDown.objects.create(user=request.user, article=article_obj, is_up=is_up)
                    else:
                        back_dic['code'] = 1001
                        back_dic['msg'] = '你已经点过了'
                else:
                    back_dic['code'] = 1002
                    back_dic['msg'] = '自己不能给自己点赞'
            else:
                back_dic['code'] = 1003
                back_dic['msg'] = mark_safe('请先<a href="/login/">登录</a>')
            return JsonResponse(back_dic)


def comment(request):
    if request.is_ajax():
        if request.method == "POST":
            back_dic = {'code': 1000, 'msg': ''}
            article_id = request.POST.get('article_id')
            print(article_id)
            content = request.POST.get('content')
            parent_id = request.POST.get('parent_id')
            with transaction.atomic():
                models.Article.objects.filter(pk=article_id).update(comment_num=F("comment_num") + 1)
                models.Comment.objects.create(user=request.user, content=content, article_id=article_id,
                                              parent_id=parent_id)
            back_dic['msg'] = '评论成功'
            return JsonResponse(back_dic)


@login_required
def backend(request):
    article_list = models.Article.objects.filter(blog=request.user.blog)
    return render(request, 'backend/backend.html', locals())


def add_article(request):
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        tag_list = request.POST.getlist('tag')
        soup = BeautifulSoup(content, 'html.parser')
        tags = soup.find_all()
        for tag in tags:
            if tag.name == 'script':
                tag.decompose()
        desc = soup.text[0:150]
        article_obj = models.Article.objects.create(title=title, content=str(soup), desc=desc, category_id=category_id,
                                                    blog=request.user.blog)
        # 批量插入
        tag_article_list = []
        for i in tag_list:
            tag_article_list.append(models.Article2Tag(article=article_obj, tag_id=i))
        models.Article2Tag.objects.bulk_create(tag_article_list)
        return redirect('/backend/')
    category_list = models.Category.objects.filter(blog=request.user.blog)
    tag_list = models.Tag.objects.filter(blog=request.user.blog)
    return render(request, 'backend/add_article.html', locals())


def upload_img(request):
    if request.method == 'POST':
        back_dic = {'error': 0, 'message': ''}
        file_obj = request.FILES.get('imgFile')
        file_pp = os.path.join(settings.BASE_DIR, 'media', 'article_img')
        if not os.path.isdir(file_pp):
            os.mkdir(file_pp)
        file_path = os.path.join(file_pp, file_obj.name)
        with open(file_path, 'wb') as f:
            for line in file_obj:
                f.write(line)
        back_dic['url'] = '/media/article_img/%s' % file_obj.name
        return JsonResponse(back_dic)


@login_required
def set_img(request):
    username = request.user.username
    if request.method == 'POST':
        file_obj = request.FILES.get('avatar')
        # models.UserInfo.objects.filter(pk=request.user.pk).update(avatar=file_obj)
        user_obj = request.user
        user_obj.avatar = file_obj
        user_obj.save()
    return render(request, 'set_img.html', locals())



@login_required
def del_article(request):
    del_id = request.GET.get('del_id')
    models.Article.objects.filter(pk=del_id).delete()
    return redirect('/backend/backend')


@login_required
def edit_article(request):
    edit_id = request.GET.get('edit_id')
    edit_obj = models.Article.objects.filter(pk=edit_id).first()
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        tag_list = request.POST.get('tag')
        soup = BeautifulSoup(content, 'html.parser')
        tags = soup.find_all()
        for tag in tags:
            if tag.name == 'script':
                tag.decompose()
        desc = soup.text[0:150]
        models.Article.objects.filter(pk=edit_id).update(title=title, content=str(soup), desc=desc,
                                                    category_id=category_id,
                                                    blog=request.user.blog)
        tag_article_list = []
        for i in tag_list:
            tag_article_list.append(models.Article2Tag(article_id=edit_id, tag_id=i))
        models.Article2Tag.objects.bulk_create(tag_article_list)
        return redirect('/backend')
    category_list = models.Category.objects.filter(blog=request.user.blog)
    tag_list = models.Tag.objects.filter(blog=request.user.blog)
    return render(request, 'backend/edit_article.html', locals())

