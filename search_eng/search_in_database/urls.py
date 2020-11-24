from django.conf.urls import url

from . import views

app_name = 'search_in_database'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search',views.search_result,name='search_result'),
    url(r'^scrapy',views.get_scrapy_search,name='scrapy'),
    url(r'^exact/(?P<entity_mainname>.*)',views.get_exact_entity, name='exact_entity'),
    url(r'^crawler', views.crawler_form, name='crawler_form')
]
