from django.shortcuts import render, get_object_or_404
from .models import quizzes, editors, questions, answers, assignment, results
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import RenewQuizForm

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

class QuizzesList(LoginRequiredMixin, generic.ListView):
    model = quizzes
    
    def get_queryset(self):
        return quizzes.objects.filter()
    
    def get(self, request, *args, **kwargs):
        db = self.get_queryset(kwargs["QuizNumber"])
        data = []
        for row in db:
            data.append({"id":row.id, "quizname":row.quizname,
            "duration":row.duration, "countofquestions":row.countofquestions,
            "clientID":row.clientID.id})
        return JsonResponse({"root":data})
    
class quizzhtmllist(LoginRequiredMixin, generic.ListView):
    models = quizzes

    def get_queryset(self):
        return quizzes.objects.filter()
    

def renew_quiz(request, quizid):
    quiz_inst = get_object_or_404(quizzes, id=quizid)

    # Если данный запрос типа POST, тогда
    if request.method == 'POST':

        # Создаём экземпляр формы и заполняем данными из запроса (связывание, binding):
        form = RenewQuizForm(request.POST)

        # Проверка валидности данных формы:
        if form.is_valid():
            # Обработка данных из form.cleaned_data
            #(здесь мы просто присваиваем их полю due_back)
            quiz_inst.quizname = form.cleaned_data['renewal_name']
            quiz_inst.save()

            # Переход по адресу 'all-borrowed':
            return HttpResponseRedirect(reverse('quizzes') )

    # Если это GET (или какой-либо ещё), создать форму по умолчанию.
    else:
        proposed_renewal_name = ""
        form = RenewQuizForm(initial={'renewal_name': proposed_renewal_name,})

    return render(request, 'quizzes_renew.html', {'form': form, 'quizinst':quiz_inst})