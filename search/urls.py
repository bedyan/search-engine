from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.url_list, name='url_list'),
    url(r'^request', views.url_answer, name='url_answer'),
    url(r'^add-doc', views.add_doc, name='add_doc'),
    url(r'^all-docs', views.all_docs, name='all_docs'),

]