from django.conf.urls import url

from simple import views

app_name = 'simple'
urlpatterns = [
    url(r'^$', views.simple, name='input'),
    url(r'^analysis', views.analysis, name='analysis'),
    url(r'^(?P<pk>[0-9]+)/results$', views.ResultView.as_view(), name='results'),
]
