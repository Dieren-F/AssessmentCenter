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
    re_path(r'questions/(?P<QuizNumber>\d+)/editanswers/(?P<QuestNumber>[-\w]+)$', views.edit_answers, name='editanswers'),

    #work with assigments
    path('assigments', views.assigmentslist.as_view(), name='assigments'),
    path('assignquiz', views.assigmentcreate.as_view(), name='assignquiz'),
    re_path(r'^assignedit/(?P<pk>[-\w]+)$', views.editassigment.as_view(), name='editassign'),
    re_path(r'^assigndelete/(?P<pk>[-\w]+)$', views.deleteassigment.as_view(), name='deleteassign'),
    re_path(r'^getresult/(?P<AssignmentNumber>\d+)/(?P<AttemptNumber>\d+)$', views.get_result, name='getresult'),

    #work with tests
    re_path(r'test/(?P<AssignmentNumber>\d+)$', views.load_test, name='loadtest'),
    re_path(r'attemptstarted/(?P<AssignmentNumber>\d+)$', views.attempt_started, name='teststarted'),
    path(r'saveresults', views.results_save, name='saveresults'),

    #work with results
    path('results', views.resultslist.as_view(), name='results'),
    re_path(r'resultdetail/(?P<pk>\d+)$', views.resultsdetail.as_view(), name='resultdetail'),
    path('createresult', views.createresult.as_view(), name='resultcreate'),
    re_path(r'updateresult/(?P<pk>\d+)$', views.updateresult.as_view(), name='updateresult'),
    path('editresults', views.editresults.as_view(), name='editresults'),
    re_path(r'deleteresult/(?P<pk>\d+)$', views.deleteresult.as_view(), name='deleteresult'),

    #work with clients
    path('clients', views.userslist.as_view(), name='clients'),
    path('clientcreate', views.usercreate.as_view(), name='clientcreate'),
    re_path(r'clientupdate/(?P<pk>\d+)$', views.userupdate.as_view(), name='clientupdate'),
]

#handler404 = 'views.handler404'