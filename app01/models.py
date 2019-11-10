from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class UserInfo(AbstractUser):
    phone = models.BigIntegerField(null=True, blank=True)  #blank=True后台管理不填写手机号
    avatar = models.FileField(upload_to='avatar/', default='avatar/default.png')
    create_time = models.DateField(auto_now_add=True)
    blog = models.OneToOneField(to='Blog', null=True)

    class Meta:
        verbose_name_plural='用户表'
    def __str__(self):
        return self.username


class Blog(models.Model):
    site_name = models.CharField(max_length=32)
    site_title = models.CharField(max_length=64)
    # 存css，js文件路径
    site_theme = models.CharField(max_length=64)
    class Meta:
        verbose_name_plural= '个人站点表'
    def __str__(self):
        return self.site_name


class Category(models.Model):
    name = models.CharField(max_length=32)
    blog = models.ForeignKey(to='Blog', null=True)
    class Meta:
        verbose_name_plural='分类表'
    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=32)
    blog = models.ForeignKey(to='Blog', null=True)
    class Meta:
        verbose_name_plural= '标签表'
    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=64)
    desc = models.CharField(max_length=255)
    content = models.TextField()  # 大段文本
    create_time = models.DateField(auto_now_add=True)

    # 数据库优化
    comment_num = models.BigIntegerField(default=0)
    up_num = models.BigIntegerField(default=0)
    down_num = models.BigIntegerField(default=0)

    # 外键字段
    blog = models.ForeignKey(to='Blog', null=True)
    tags = models.ManyToManyField(to='Tag', through='Article2Tag', through_fields=('article', 'tag'))
    category = models.ForeignKey(to='Category', null=True)
    class Meta:
        verbose_name_plural= '文章表'
    def __str__(self):
        return self.title


class Article2Tag(models.Model):
    article = models.ForeignKey(to='Article')
    tag = models.ForeignKey(to='Tag')
    class Meta:
        verbose_name_plural='文章标签表'



class UpAndDown(models.Model):
    user = models.ForeignKey(to='UserInfo')
    article = models.ForeignKey(to='Article')
    is_up = models.BooleanField()
    class Meta:
        verbose_name_plural='点赞点踩表'



class Comment(models.Model):
    user = models.ForeignKey(to='UserInfo')
    article = models.ForeignKey(to='Article')
    content = models.CharField(max_length=255)
    create_time = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(to='self', null=True)
    class Meta:
        verbose_name_plural='评论表'
