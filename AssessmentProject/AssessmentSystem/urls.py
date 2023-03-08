from django.urls import path
from django.urls import re_path
from django.views.generic import RedirectView
from django.urls import include
from . import views

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.index, name='index'),
    path('api/ThemesList', views.ThemesList.as_view(), name='ThemesList'),
    re_path(r'^api/QuizzesList/(?P<QuizNumber>\d+)$', views.QuizzesList.as_view(), name='QuizzesList')
]


#handler404 = 'views.handler404'