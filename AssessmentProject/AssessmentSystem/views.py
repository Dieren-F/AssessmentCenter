from django.shortcuts import render
from .models import themes, quizzes, editors, questions, answers, assignment, results
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin

def handler404(request, *args, **kwargs):
    return HttpResponseRedirect('/')

# Create your views here.

def index(request):
    """
    Функция отображения для домашней страницы сайта.
    """

    # Генерация "количеств" некоторых главных объектов
    smart_var = "ururu"

    # Отрисовка HTML-шаблона index.html с данными внутри
    # переменной контекста context
    return render(
        request,
        'index.html',
        context={'smart_var':smart_var},
    )

def login(request):
    return render(
        request,
        'login.html',
        context={},
    )

class ThemesList(generic.ListView):
    model = themes
    
    def get_queryset(self):
        return themes.objects.filter()

    def get_context_data(self, **kwargs):
        # В первую очередь получаем базовую реализацию контекста
        context = super(ThemesList, self).get_context_data(**kwargs)
        # Добавляем новую переменную к контексту и инициализируем её некоторым значением
        context['some_data'] = 'This is just some data'
        return context
    
    def get(self, request, *args, **kwargs):
        db = self.get_queryset()
        data = []
        for row in db:
            data.append({"id":row.id, "themename":row.themename})
        return JsonResponse({"root":data})

class QuizzesList(LoginRequiredMixin, generic.ListView):
    model = quizzes
    
    def get_queryset(self, QuizNumber):
        return quizzes.objects.filter(themeID = QuizNumber)
    
    def get(self, request, *args, **kwargs):
        db = self.get_queryset(kwargs["QuizNumber"])
        data = []
        for row in db:
            data.append({"id":row.id, "quizname":row.quizname,
            "duration":row.duration, "countofquestions":row.countofquestions,
            "themeID":row.themeID.id, "clientID":row.clientID.id})
        return JsonResponse({"root":data})
        