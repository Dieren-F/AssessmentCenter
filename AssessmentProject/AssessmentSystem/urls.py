from django.urls import path
from django.urls import re_path
from django.views.generic import RedirectView
from django.urls import include
from . import views

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.index, name='index'),
    path('quizzes', views.quizzhtmllist.as_view(), name='quizzes'),
    re_path(r'^api/getquizzes/(?P<QuizNumber>\d+)$', views.QuizzesList.as_view(), name='QuizzesList'),
]

urlpatterns += [
    re_path(r'^editquiz/(?P<quizid>[-\w]+)$', views.renew_quiz, name='renew-quiz'),
]

#handler404 = 'views.handler404'