"""BBS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from app01 import views
from django.views.static import serve
from BBS import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home),
    url(r'^register/', views.register),
    url(r'^login/', views.login),

    # 图片验证码相关
    url(r'^get_code/', views.get_code),
    # 首页
    url(r'^home/', views.home),
    # 注销
    url(r'^logout/', views.logout),
    # 修改密码
    url(r'^set_password/', views.set_password),
    # 点赞点踩
    url(r'^up_down/', views.up_down),
    #评论
    url(r'^comment/', views.comment),
    #后台管理
    url(r'^backend/', views.backend),
    url(r'^add_article/', views.add_article),
    # 文本编辑器上传文件
    url(r'^upload_img/', views.upload_img),
    #修改头像
    url(r'^set_img/', views.set_img),
    #删除文章
    url(r'^del_article/', views.del_article),
    #编辑文章
    url(r'^edit_article/', views.edit_article),

    # 暴露给外界的后端文件资源
    url(r'^media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}),
    #相当于将media文件夹下的资源暴露给外界

    #个人站点
    url(r'^(?P<username>\w+)/(?P<condition>category|tag|archive)/(?P<param>.*)/', views.site),
    url(r'^(?P<username>\w+)/$',views.site),

    #文章详情页
    url(r'^(?P<username>\w+)/article/(?P<article_id>\d+)/', views.article_detail),




]
