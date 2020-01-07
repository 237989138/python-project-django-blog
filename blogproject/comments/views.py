from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from blog.models import Post
from .models import Comment
from .forms import CommentForm
# Create your views here.

def post_comment(request,post_pk=None):
    print("进入comment")
    # 获取的文章（Post）存在时，则获取；否则返回 404 页面给用户。
    post = get_object_or_404(Post, pk=post_pk)
    print("comments=================",post.pk,post, type(post),reverse("comments:post_comment",kwargs={"post_pk":"789"}))
    if request.method == "POST":
        # 用户提交的数据存在 request.POST 中，这是一个类字典对象。
        # 构造 CommentForm 实例， Django 的表单就生成。
        form=Comment(request.POST)
        # form.is_valid()方法，Django自动帮我们检查表单的数据是否符合格式要求。
        if form.is_valid():
            # commit=False 的作用是仅仅利用表单的数据生成 Comment 模型类的实例，但还不保存评论数据到数据库。
            comment = form.save(commit=False)
            # 将评论和被评论的文章关联起来。
            comment.post = post
            # 将评论数据保存进数据库，调用模型实例的 save 方法
            comment.save()
            return redirect(post)
        else:
            # 检查到数据不合法，重新渲染详情页，并且渲染表单的错误。
            comment_list = post.comment_set.all()
            context = {'post': post,
                       'form': form,
                       'comment_list': comment_list
                       }
            return render(request, 'blog/detail.html', context=context)
        # redirect既可以接收一个URL作为参数，也可以接收一个模型的实例作为参数（例如这里的post）。
        # 如果接收一个模型的实例，那么这个实例必须实现了get_absolute_url方法，这样redirect会根据
        # get_absolute_url方法返回的URL值进行重定向。
    return redirect(post)
