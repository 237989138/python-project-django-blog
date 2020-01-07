from django.db.models import Count

from ..models import *
from django import template
register = template.Library()

@register.simple_tag
def get_recent_posts(num=5):
    #倒序排列最近的5篇文章
    return Post.objects.all().order_by('-created_time')[:num]


@register.simple_tag
def archives():
    res=Post.objects.dates('created_time', 'month', order='DESC')
    print(res)
    return res

@register.simple_tag
def get_categories():

    return Category.objects.all()


@register.simple_tag
def get_tags():
    # 记得在顶部引入 count 函数
    # Count 计算分类下的文章数，其接受的参数为需要计数的模型的名称
    return Category.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)

