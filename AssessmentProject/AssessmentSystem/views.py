from django.shortcuts import render, get_object_or_404
from .models import quizzes, editors, questions, answers, assignment, results
from django.http.response import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User

from .models import quizzes
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

class QuizCreate(LoginRequiredMixin, CreateView):
    model = quizzes
    fields = ('quizname', 'clientID')
    success_url = reverse_lazy('quizzes')
    #initial={'clientID':User,}
    
    def get_initial(self):
        initial = super().get_initial()
        #for providing initial values to the form
        initial['clientID'] = self.request.user.id 
        return initial.copy()

class QuizDelete(DeleteView):
    model = quizzes
    success_url = reverse_lazy('quizzes')

class questionhtmllist(LoginRequiredMixin, generic.ListView):
    models = questions

    def get_queryset(self):
        return questions.objects.filter(quizID=self.kwargs["QuizNumber"])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем новую переменную к контексту и инициализируем её некоторым значением
        context['QuizNumber'] = self.kwargs["QuizNumber"]
        return context
    
class QuestionCreate(LoginRequiredMixin, CreateView):
    model = questions
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('questions', kwargs={'QuizNumber': self.kwargs["QuizNumber"]})

    
