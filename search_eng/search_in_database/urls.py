from django.conf.urls import url

from . import views

app_name = 'search_in_database'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search',views.search_result,name='search_result'),
    url(r'^scrapy',views.get_scrapy_search,name='scrapy'),
    url(r'^exact-tree/(?P<entity_mainname>.*)',views.exact_entity_tree_mode, name='exact_entity_tree_mode'),
    url(r'^crawler', views.crawler_form, name='crawler_form'),
    url(r'^exact/(?P<entity_mainname>.*)',views.exact_entity,name='exact_entity'),
]
