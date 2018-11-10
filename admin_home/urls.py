from django.conf.urls import url
from . import views
urlpatterns=[
    url(r'^$', views.indexview, name='index'),
    url(r'^signin/$', views.signinview, name='signin'),
    url(r'^signup/$', views.registerview, name='register'),
    url(r'^logout/$', views.logoutview, name='logout'),
    url(r'^signup/saveimage$', views.saveimageview, name='saveimage'),
    url(r'^signin/takeattendance/$', views.takeattendanceview, name='takeattendance'),
    url(r'^signin/viewattendance/$', views.viewattendanceview, name='viewattendance')
]