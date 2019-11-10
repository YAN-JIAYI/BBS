from django.template import Library
from app01 import models
from django.db.models.functions import TruncMonth
from django.db.models import Count

register = Library()

@register.inclusion_tag('left.html')
def index(username):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    category_list = models.Category.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list\
        ('name','count_num', 'pk')   #统计文章数
    tag_list = models.Tag.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list\
        ('name','count_num', 'pk')
    date_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values('month')\
        .annotate(count_num=Count('pk')).order_by('-month').values_list('month','count_num')
    return locals()