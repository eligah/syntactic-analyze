from django.conf.urls import url

from batching import views

app_name = 'batching'
urlpatterns = [
    url(r'^$', views.batching, name='input'),
    url(r'^analysis$', views.analysis, name='analysis'),
    url(r'^(?P<pk>[0-9]+)/results$', views.ResultView.as_view(), name='result'),
]
