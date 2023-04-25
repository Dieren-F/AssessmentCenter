from django.urls import path
from django.urls import re_path
from django.views.generic import RedirectView
from django.urls import include
from . import views
from .views import (
    delete_one_question, delete_one_answer
)

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.index, name='index'),
    
    #work with questions
    re_path(r'quiz/(?P<QuizNumber>\d+)$', views.questionhtmllist.as_view(), name='questions'),
    re_path(r'quiz/(?P<QuizNumber>\d+)/addquestion/?$', views.QuestionCreate.as_view(), name='addquestion'),
    re_path(r'quiz/(?P<QuizNumber>\d+)/editquestion/(?P<pk>\d+)$', views.QuestionUpdate.as_view(), name='editquestion'),
    re_path(r'quiz/(?P<QuizNumber>\d+)/delquestion/(?P<pk>\d+)$', delete_one_question, name='deletequestion'),

    #work with answers
    re_path(r'quiz/(?P<QuizNumber>\d+)/editquestion/(?P<QuestNumber>\d+)/answer/(?P<pk>\d+)/delete/?$', delete_one_answer, name='deleteanswer'),    
    
    #work with quizzes
    path('quizzes', views.quizzhtmllist.as_view(), name='quizzes'),
    path('addquiz', views.QuizCreate.as_view(), name='quizcreate'),
    re_path(r'^editquiz/(?P<pk>[-\w]+)$', views.QuizUpdate.as_view(), name='renew-quiz'),
    re_path(r'^delquiz/(?P<pk>[-\w]+)$', views.QuizDelete.as_view(), name='delet-quiz'),
    

    re_path(r'^api/getquizzes/(?P<QuizNumber>\d+)$', views.QuizzesList.as_view(), name='QuizzesList'),

    #work with answers
    re_path(r'questions/(?P<QuizNumber>\d+)/editanswers/(?P<QuestNumber>[-\w]+)$', views.edit_answers, name='editanswers')
]

#handler404 = 'views.handler404'