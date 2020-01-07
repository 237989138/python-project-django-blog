from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.IndexViews.as_view(), name='index'),
    url(r'post/(?P<pk>[0-9]+)/$', views.detail, name='detail'),
    url(r'^archives/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/$', views.ArchivesView.as_view(), name='archives'),
    url(r'^category/(?P<pk>[0-9]+)/$', views.CategoryView.as_view(), name='category'),
    url(r'^tag/(?P<pk>[0-9]+)/$', views.TagView.as_view(), name='tag'),
    # url(r'^search/$', views.search, name='search'),
    url(r'^lianxi/$', views.lianxi,name="lianxi"),
    url(r'^about/$', views.about,name="about"),

]