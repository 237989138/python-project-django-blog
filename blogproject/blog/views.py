from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, DetailView

from .models import *
import markdown
from comments.forms import CommentForm


# Create your views here.
# def index(request):
#     res=reverse("blog:index")
#     print("------------------",res)
#     # return HttpResponse("<h1>Welcome to my blog<h1>")
#     # return render(request,"blog/index.html",{"title":"我的博客首页","welcome":"欢迎访问我的博客首页"})
#     post_list = Post.objects.all().order_by('-created_time')
#     print("post_list-----------------------------",post_list)
#     print(post_list.values())
#     for i in post_list:
#         print("~~~~~~~~~~~~~~~~~~~~",i.pk)
#     resp=render(request, 'blog/index.html', context={'post_list': post_list})
#     print("resp--------------------------",resp)
#     return resp

class IndexViews(ListView):
    model = Post
    template_name = "blog/index.html"
    context_object_name = 'post_list'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')
        pagination_data = self.pagination_data(paginator, page, is_paginated)
        context.update(pagination_data)
        return context

    def pagination_data(self, paginator, page, is_paginated):
        if not is_paginated:
            # 如果没有分页，则无需显示分页导航条，不用任何分页导航条的数据，因此返回一个空的字典
            return {}
        # 当前页左边连续的页码号，初始值为空
        left = []
        # 当前页右边连续的页码号，初始值为空
        right = []
        # 标示第 1 页页码后是否需要显示省略号
        left_has_more = False
        # 标示最后一页页码前是否需要显示省略号
        right_has_more = False
        # 标示是否需要显示第 1 页的页码号。
        # 因为如果当前页左边的连续页码号中已经含有第 1 页的页码号，此时就无需再显示第 1 页的页码号，
        # 其它情况下第一页的页码是始终需要显示的。
        # 初始值为 False
        first = False
        # 标示是否需要显示最后一页的页码号。
        # 需要此指示变量的理由和上面相同。
        last = False
        # 获得用户当前请求的页码号
        page_number = page.number
        # 获得分页后的总页数
        total_pages = paginator.num_pages
        # 获得整个分页页码列表，比如分了四页，那么就是 [1, 2, 3, 4]
        page_range = paginator.page_range
        if page_number == 1:
            # 如果用户请求的是第一页的数据，那么当前页左边的不需要数据，因此 left=[]（已默认为空）。
            # 此时只要获取当前页右边的连续页码号，
            # 比如分页页码列表是 [1, 2, 3, 4]，那么获取的就是 right = [2, 3]。
            # 注意这里只获取了当前页码后连续两个页码，你可以更改这个数字以获取更多页码。
            right = page_range[page_number:page_number + 2]
            # 如果最右边的页码号比最后一页的页码号减去 1 还要小，
            # 说明最右边的页码号和最后一页的页码号之间还有其它页码，因此需要显示省略号，通过 right_has_more 来指示。
            if right[-1] < total_pages - 1:
                right_has_more = True
            # 如果最右边的页码号比最后一页的页码号小，说明当前页右边的连续页码号中不包含最后一页的页码
            # 所以需要显示最后一页的页码号，通过 last 来指示
            if right[-1] < total_pages:
                last = True
        elif page_number == total_pages:
            # 如果用户请求的是最后一页的数据，那么当前页右边就不需要数据，因此 right=[]（已默认为空），
            # 此时只要获取当前页左边的连续页码号。
            # 比如分页页码列表是 [1, 2, 3, 4]，那么获取的就是 left = [2, 3]
            # 这里只获取了当前页码后连续两个页码，你可以更改这个数字以获取更多页码。
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]

            # 如果最左边的页码号比第 2 页页码号还大，
            # 说明最左边的页码号和第 1 页的页码号之间还有其它页码，因此需要显示省略号，通过 left_has_more 来指示。
            if left[0] > 2:
                left_has_more = True

            # 如果最左边的页码号比第 1 页的页码号大，说明当前页左边的连续页码号中不包含第一页的页码，
            # 所以需要显示第一页的页码号，通过 first 来指示
            if left[0] > 1:
                first = True
        else:
            # 用户请求的既不是最后一页，也不是第 1 页，则需要获取当前页左右两边的连续页码号，
            # 这里只获取了当前页码前后连续两个页码，你可以更改这个数字以获取更多页码。
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]
            right = page_range[page_number:page_number + 2]

            # 是否需要显示最后一页和最后一页前的省略号
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True

            # 是否需要显示第 1 页和第 1 页后的省略号
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True

        data = {
            'left': left,
            'right': right,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'first': first,
            'last': last,
        }

        return data


def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # 阅读量 +1
    post.increase_views()

    post.body = markdown.markdown(post.body,
                                  extensions=[
                                      'markdown.extensions.extra',
                                      'markdown.extensions.codehilite',
                                      'markdown.extensions.toc',
                                  ])
    form = CommentForm()
    comment_list = post.comment_set.all()
    context = {'post': post,
               'form': form,
               'comment_list': comment_list
               }
    print("~~~~~~~~~~~~~~~~~",context,reverse("comments:post_comment",kwargs={"post_pk":"789"}))
    return render(request, 'blog/detail.html', context=context)

# class PostDetailView(DetailView):
#     # 这些属性的含义和 ListView 是一样的
#     model = Post
#     template_name = 'blog/detail.html'
#     context_object_name = 'post'
#
#     def get(self, request, *args, **kwargs):
#         # 覆写 get 方法的目的是因为每当文章被访问一次，就得将文章阅读量 +1
#         # get 方法返回的是一个 HttpResponse 实例
#         # 之所以需要先调用父类的 get 方法，是因为只有当 get 方法被调用后，
#         # 才有 self.object 属性，其值为 Post 模型实例，即被访问的文章 post
#         response = super(PostDetailView, self).get(request, *args, **kwargs)
#
#         # 将文章阅读量 +1
#         # 注意 self.object 的值就是被访问的文章 post
#         self.object.increase_views()
#
#         # 视图必须返回一个 HttpResponse 对象
#         return response
#
#     def get_object(self, queryset=None):
#         # 覆写 get_object 方法的目的是因为需要对 post 的 body 值进行渲染
#         post = super(PostDetailView, self).get_object(queryset=None)
#         post.body = markdown.markdown(post.body,
#                                       extensions=[
#                                           'markdown.extensions.extra',
#                                           'markdown.extensions.codehilite',
#                                           'markdown.extensions.toc',
#                                       ])
#         return post

    # def get_context_data(self, **kwargs):
    #     # 覆写 get_context_data 的目的是因为除了将 post 传递给模板外（DetailView 已经帮我们完成），
    #     # 还要把评论表单、post 下的评论列表传递给模板。
    #     context = super(PostDetailView, self).get_context_data(**kwargs)
    #     form = CommentForm()
    #     comment_list = self.object.comment_set.all()
    #     context.update({
    #         'form': form,
    #         'comment_list': comment_list,
    #     })
    #     return context
    #
    # def get_queryset(self):
    #
    #     return super(PostDetailView, self).get_queryset().all()


# def archives(request, year, month):
#     post_list = Post.objects.filter(created_time__year=year,
#                                     created_time__month=month
#                                     ).order_by('-created_time')
#     return render(request, 'blog/index.html', context={'post_list': post_list})
class ArchivesView(IndexViews):
    def get_queryset(self):
        # cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        create = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        print("create-------------",create)
        return super(ArchivesView, self).get_queryset().filter(created_time__year=create.year,created_time__month=create.month).order_by('-created_time')

class CategoryView(IndexViews):
     def get_queryset(self):
        cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        print(cate)
        return super(CategoryView, self).get_queryset().filter(category=cate).order_by("-created_time")


# def category(request, pk):
#     cate = get_object_or_404(Category, pk=pk)
#     print(cate,type(cate))
#     post_list = Post.objects.filter(category=cate).order_by('-created_time')
#     return render(request, 'blog/index.html', context={'post_list': post_list})


class TagView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        tag = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        print("tag------------------------------",tag)
        return super(TagView, self).get_queryset().filter(tags=tag)

def search(request):
    if request.method == "GET":
        q = request.GET.get('q')
        print("q===============",q)
        error_msg=''
        if not q:
            error_msg = "请输入关键词"
            return render(request, 'blog/index.html', {'error_msg': error_msg})
        post_list = Post.objects.filter(Q(title__icontains=q) | Q(body__icontains=q))
        return render(request, 'blog/index.html', {'error_msg': error_msg,'post_list': post_list})

def lianxi(request):
    return render(request,'blog/lianxi.html')

def about(request):
    return render(request, 'blog/about.html')

def page_not_found(request,exception):
#404
    return render(request,"blog/404.html",status=404)

def page_error(exception):
    #500
    return render("blog/500.html",status=500)
# ERRORS:
# ?: (urls.E007) The custom handler500 view 'blog.views.page_error' does not take the correct number of arguments (request).
def permission_denied(request,exception):
#403
    return render(request, "blog/403.html",status=403)
# ERRORS:
# ?: (urls.E007) The custom handler403 view 'blog.views.permission_denied' does not take the correct number of arguments (request, exception).

def bad_request(request,exception):
#400
    return render(request, "blog/400.html",status=400)
