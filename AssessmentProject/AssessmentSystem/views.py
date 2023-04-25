from django.shortcuts import render, get_object_or_404, redirect
from .models import quizzes, editors, questions, answers, assignment, results
from django.http.response import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.forms import formset_factory
from .forms import (
    QuestionForm, AnswersForm, AnswersFormSet
)


from .models import quizzes
from .forms import RenewQuizForm, QuestionCreateForm, EditAnswers

def handler404(request, *args, **kwargs):
    return HttpResponseRedirect('/')

# Create your views here.

#@login_required(login_url='accounts/login/')
def index(request):
    if not request.user.is_authenticated:
        form = AuthenticationForm()
        return render(request, 'registration/login.html', context={'form':form},)
    
    return render(request, 'index.html', context={'name':'form'},)

def login(request):
    return render(
        request,
        'registration/login.html',
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
    
class QuizUpdate(LoginRequiredMixin, UpdateView):
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
        context['quiz'] = quizzes.objects.filter(id=self.kwargs["QuizNumber"]).values_list('quizname', flat=True).first()
        return context


class QuestionInline():
    form_class = QuestionForm
    model = questions
    template_name = "AssessmentSystem/question_answer_form.html"

    def form_valid(self, form):
        named_formsets = self.get_named_formsets()
        if not all((x.is_valid() for x in named_formsets.values())):
            return self.render_to_response(self.get_context_data(form=form))

        self.object = form.save()

        # for every formset, attempt to find a specific formset save function
        # otherwise, just save.
        for name, formset in named_formsets.items():
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()
        return redirect('editquestion', QuizNumber=self.kwargs["QuizNumber"], pk=self.kwargs["pk"]) #redirect('editquestion', kwargs={'QuizNumber': self.kwargs["QuizNumber"], 'pk': self.kwargs["pk"]})

    def formset_answers_valid(self, formset):
        """
        Hook for custom formset saving.Useful if you have multiple formsets
        """
        answers = formset.save(commit=False)  # self.save_formset(formset, contact)
        # add this 2 lines, if you have can_delete=True parameter 
        # set in inlineformset_factory func
        for obj in formset.deleted_objects:
            obj.delete()
        for answer in answers:
            answer.questions = self.object
            answer.save()

class QuestionDelete(LoginRequiredMixin, DeleteView):
    model = questions
    success_url = reverse_lazy('questions', kwargs={ "QuizNumber": 1 }) #reverse_lazy('questions')
    
class QuestionCreate(LoginRequiredMixin, QuestionInline, CreateView):
    model = questions
    form_class = QuestionCreateForm
    #fields = '__all__'
    success_url = reverse_lazy('questions')

    def get_success_url(self):
        return reverse_lazy('editquestion', kwargs={'QuizNumber': self.kwargs["QuizNumber"], 'pk': self.kwargs["QuestNumber"]})

    def get_initial(self):
        initial = super().get_initial()
        initial['qtypesID'] = 1
    #    #for providing initial values to the form
    #    initial['quizID'] = self.kwargs['QuizNumber'] 
        return initial.copy()

    def form_invalid(self, form):
        print("form is invalid")
        return http.HttpResponse("form is invalid.. this is just an HttpResponse object")

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        instance = form.save(commit=False)
        instance.sequence = 1
        instance.version = 1
        instance.quizID_id = self.kwargs['QuizNumber']
        instance.save()
        self.kwargs['QuestNumber'] = instance.id
        return redirect(self.get_success_url())  #redirect(self.get_success_url()) #super().form_valid(form)
   
    def get_context_data(self, **kwargs):
        ctx = super(QuestionCreate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        ctx['QuizNumber'] = self.kwargs["QuizNumber"]
        return ctx

    def get_named_formsets(self):
        if self.request.method == "GET":
            return {
                'answers': AnswersForm(prefix='answers'),
            }
        else:
            return {
                'answers': AnswersForm(self.request.POST or None, self.request.FILES or None, prefix='answers'),
            }

class QuestionUpdate(LoginRequiredMixin, QuestionInline, UpdateView):
    model = questions
    form_class = QuestionCreateForm
    #fields = '__all__'
    success_url = reverse_lazy('questions')

    def get_success_url(self):
        return reverse_lazy('editquestion', kwargs={'QuizNumber': self.kwargs["QuizNumber"], 'pk': self.kwargs["pk"]})

    def form_invalid(self, form):
        print("form is invalid")
        return http.HttpResponse("form is invalid.. this is just an HttpResponse object")

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        instance = form.save(commit=False)
        instance.sequence = 1
        instance.version = 1
        instance.quizID_id = self.kwargs['QuizNumber']
        instance.save()
        return super().form_valid(form) #redirect(self.get_success_url()) #super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        ctx = super(QuestionUpdate, self).get_context_data(**kwargs)
        #context['quiz'] = quizzes.objects.filter(id=self.kwargs["QuizNumber"]).values_list('quizname', flat=True).first()
        ctx['named_formsets'] = self.get_named_formsets()
        ctx['QuizNumber'] = self.kwargs["QuizNumber"]
        ctx['QuestNumber'] = self.kwargs["pk"]
        return ctx

    def get_named_formsets(self):
        return {
            'answers': AnswersFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='answers'),
        }
    

#Lines below are for custom functions


def delete_one_question(request, QuizNumber, pk):
    """Function for deleting questions"""
    try:
        onequest = questions.objects.get(id=pk)
    except questions.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('questions', QuizNumber=QuizNumber)

    onequest.delete()
    messages.success(
            request, 'Question deleted successfully'
            )
    return redirect('questions', QuizNumber=QuizNumber)


def delete_one_answer(request, QuizNumber, QuestNumber, pk):
    """Function for deleting answers in update question form"""
    try:
        oneanswer = answers.objects.get(id=pk)
    except answers.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('editquestion', QuizNumber=QuizNumber, pk=QuestNumber)

    oneanswer.delete()
    messages.success(
            request, 'Answer deleted successfully'
            )
    return redirect('editquestion', QuizNumber=QuizNumber, pk=QuestNumber)

def edit_answers(request, QuizNumber, QuestNumber):
    """Deprecated function for custom uupdate names of answers"""

    quest = get_object_or_404(questions, id=QuestNumber)
    #quest = questions.objects.filter(id=QuestNuber)
    answer = answers.objects.filter(questionID=QuestNumber)

    # Если данный запрос типа POST, тогда
    #if request.method == 'POST':

        # Создаём экземпляр формы и заполняем данными из запроса (связывание, binding):
    form = formset_factory(EditAnswers(request.POST))

        # Проверка валидности данных формы:
        #if form.is_valid():
            # Обработка данных из form.cleaned_data
            #(здесь мы просто присваиваем их полю due_back)
            #quiz_inst.quizname = form.cleaned_data['renewal_name']
            #quiz_inst.save()

            # Переход по адресу 'all-borrowed':
            #return HttpResponseRedirect(reverse('quizzes') )
        
    # Если это GET (или какой-либо ещё), создать форму по умолчанию.
    #else:
        #form = EditAnswers(initial={'quizID': QuizNumber,})

    return render(request, 'AssessmentSystem/answer_form.html', {'form': form, 'questions': quest, "answers_list": answer})

def renew_quiz(request, quizid):
    """Deprecated function for custom uupdate names of quizes"""
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