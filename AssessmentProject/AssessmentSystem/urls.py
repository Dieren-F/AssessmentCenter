from django.urls import path
from django.urls import re_path
from django.views.generic import RedirectView
from django.urls import include
from . import views

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.index, name='index'),
    
    #work with questions
    re_path(r'questions/(?P<QuizNumber>\d+)$', views.questionhtmllist.as_view(), name='questions'),
    re_path(r'questions/(?P<QuizNumber>\d+)/addquestion/?$', views.QuestionCreate.as_view(), name='addquestion'),
    re_path(r'questions/(?P<QuizNumber>\d+)/editquestion/(?P<pk>[-\w]+)$', views.QuestionUpdate.as_view(), name='editquestion'),
    re_path(r'questions/(?P<QuizNumber>\d+)/delquestion/(?P<pk>[-\w]+)$', views.QuestionDelete.as_view(), name='deletequestion'),
    
    
    
    #work with quizzes
    path('quizzes', views.quizzhtmllist.as_view(), name='quizzes'),
    path('addquiz', views.QuizCreate.as_view(), name='quizcreate'),
    re_path(r'^api/getquizzes/(?P<QuizNumber>\d+)$', views.QuizzesList.as_view(), name='QuizzesList'),
    re_path(r'^editquiz/(?P<quizid>[-\w]+)$', views.renew_quiz, name='renew-quiz'),
    re_path(r'^delquiz/(?P<pk>[-\w]+)$', views.QuizDelete.as_view(), name='delet-quiz'),
]

#handler404 = 'views.handler404'