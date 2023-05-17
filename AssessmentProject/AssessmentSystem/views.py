import math
import json
import logging
from django.db import connection
from django.shortcuts import render, get_object_or_404, redirect
from .models import quizzes, editors, questions, answers, assignment, results, textresult
from django.http.response import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.core.serializers import serialize
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.forms import formset_factory
from .forms import (
    QuestionForm, AnswersForm, AnswersFormSet, ClientsForm, ClientUpdForm, ResultCreateForm
)


from .models import quizzes
from .forms import RenewQuizForm, QuestionCreateForm, EditAnswers

logger = logging.getLogger(__name__)

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

class QuizDelete(LoginRequiredMixin, DeleteView):
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
        initial['weight'] = 1
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

class assigmentslist(LoginRequiredMixin, generic.ListView):
    models = assignment

    def get_queryset(self):
        if(self.request.user.is_staff or self.request.user.is_superuser):
            assignment_list = assignment.objects.order_by('-id')
        else:
            assignment_list = assignment.objects.filter(clientID_id=self.request.user.id).order_by('-id')
        return assignment_list

class assigmentcreate(LoginRequiredMixin, CreateView):
    models = assignment
    template_name = "AssessmentSystem/assigments_add.html"
    fields = '__all__'
    success_url = reverse_lazy('assigments')
    #initial={'clientID':User,}
    
    def get_initial(self):
        initial = super().get_initial()
        #for providing initial values to the form
        initial['clientID'] = self.request.user.id 
        initial['version'] = 1
        initial['randomseq'] = False
        initial['randomver'] = False
        initial['resultready'] = False
        return initial.copy()
    
    def get_queryset(self):
        assignment_list = assignment.objects.filter(clientID_id=self.request.user.id).order_by('-id')
        return assignment_list
    
class editassigment(LoginRequiredMixin, UpdateView):
    models = assignment
    template_name = "AssessmentSystem/assigments_add.html"
    fields = '__all__'
    success_url = reverse_lazy('assigments')

    def get_queryset(self):
        assignment_list = assignment.objects.filter(id=self.kwargs["pk"])
        return assignment_list
    
class deleteassigment(LoginRequiredMixin, DeleteView):
    models = assignment
    template_name = "AssessmentSystem/assigment_confirm_delete.html"
    fields = '__all__'
    success_url = reverse_lazy('assigments')

    def get_queryset(self):
        assignment_list = assignment.objects.filter(id=self.kwargs["pk"])
        return assignment_list

class resultslist(LoginRequiredMixin, generic.ListView):
    models = assignment
    fields = '__all__'
    template_name = "AssessmentSystem/results_list.html"

    def get_queryset(self):
        if(self.request.user.is_staff or self.request.user.is_superuser):
            assignment_list = assignment.objects.filter(currentpoints__gt=0).order_by('-id')
        else:
            assignment_list = assignment.objects.filter(clientID_id=self.request.user.id, currentpoints__gt=0).order_by('-id')
        return assignment_list
    
class resultsdetail(LoginRequiredMixin, generic.ListView):
    models = textresult
    fields = '__all__'
    template_name = "AssessmentSystem/results_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super(resultsdetail, self).get_context_data(**kwargs)
        ctx['result_detail'] = self.get_queryset()
        logger.warning("ctx")
        logger.warning(ctx['result_detail'])
        return ctx

    def get_queryset(self):
        result_detail = textresult.objects.filter(sigmin__lt=self.kwargs["pk"],sigmax__gt=self.kwargs["pk"]).first()

        return result_detail

class userslist(LoginRequiredMixin, generic.ListView):
    models = User
    template_name = "AssessmentSystem/user_list.html"
    fields = '__all__'
    #success_url = reverse_lazy('assigments')

    def get_queryset(self):
        return User.objects.filter(is_superuser=False).order_by('-id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем новую переменную к контексту и инициализируем её некоторым значением
        context['itm_list'] = self.get_queryset()
        #context['quiz'] = quizzes.objects.filter(id=self.kwargs["QuizNumber"]).values_list('quizname', flat=True).first()
        return context
    
class usercreate(LoginRequiredMixin, CreateView):
    models = User
    template_name = "AssessmentSystem/client_add.html"
    form_class = ClientsForm
    success_url = reverse_lazy('clients')
    #initial={'clientID':User,}
    
    def get_initial(self):
        initial = super().get_initial()
        return initial.copy()
    
    def get_queryset(self):
        return User.objects.filter(is_superuser=False)
    
    def form_valid(self, form):
        request = self.request
        if self.request.method == 'POST':
            User.objects.create_user(
                username = request.POST['username'],
                password = request.POST['password'],
                is_active = (True if request.POST.get('is_active', 'off')=='on' else False),
                is_staff = (True if request.POST.get('is_staff', 'off')=='on' else False),
                first_name = request.POST['first_name'],
                last_name = request.POST['last_name'],
                email = request.POST['email']
            )
            #User.objects.update_or_create()
            logger.warning('user created')
        return redirect(self.success_url) #super().form_valid(form)


class userupdate(LoginRequiredMixin, UpdateView):
    models = User
    template_name = "AssessmentSystem/client_update.html"
    form_class = ClientUpdForm
    success_url = reverse_lazy('clients')
    #initial={'clientID':User,}
    
    def get_initial(self):
        initial = super().get_initial()
        return initial.copy()
    
    def get_queryset(self):
        return User.objects.filter(id=self.kwargs["pk"], is_superuser=False)
    
    def form_valid(self, form):
        request = self.request
        if self.request.method == 'POST':
            User.objects.filter(id = self.kwargs["pk"]).update(
                username = request.POST['username'],
                is_active = (True if request.POST.get('is_active', 'off')=='on' else False),
                is_staff = (True if request.POST.get('is_staff', 'off')=='on' else False),
                first_name = request.POST['first_name'],
                last_name = request.POST['last_name'],
                email = request.POST['email']
            )
            #User.objects.update_or_create()
            logger.info('user created')
        return redirect(self.success_url) #super().form_valid(form)

class createresult(LoginRequiredMixin, CreateView):
    models = textresult
    template_name = "AssessmentSystem/textresult_add_update.html"
    #fields = '__all__'
    success_url = reverse_lazy('results')
    form_class = ResultCreateForm
    #initial={'clientID':User,}
    
    def get_initial(self):
        initial = super().get_initial()
        #for providing initial values to the form
        return initial.copy()
    
    def get_queryset(self):
        return textresult.objects.filter(id=0)
    
class updateresult(LoginRequiredMixin, UpdateView):
    models = textresult
    template_name = "AssessmentSystem/textresult_add_update.html"
    #fields = '__all__'
    success_url = reverse_lazy('results')
    form_class = ResultCreateForm
    #initial={'clientID':User,}
    
    def get_initial(self):
        initial = super().get_initial()
        #for providing initial values to the form
        return initial.copy()
    
    def get_queryset(self):
        return textresult.objects.filter(id=self.kwargs["pk"])
    
class editresults(LoginRequiredMixin, generic.ListView):
    models = textresult

    def get_queryset(self):
        textresult_list = textresult.objects.all()
        return textresult_list
    
class deleteresult(LoginRequiredMixin, DeleteView):
    models = textresult
    template_name = "AssessmentSystem/textresult_confirm_delete.html"
    fields = '__all__'
    success_url = reverse_lazy('editresults')

    def get_queryset(self):
        return textresult.objects.filter(id=self.kwargs["pk"])

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

#test loader
@login_required
def load_test(request, AssignmentNumber):
    data = {}
    assignment_point = assignment.objects.filter(id=AssignmentNumber).first()
    data['assignment'] = AssignmentNumber
    data['duration'] = assignment_point.duration
    data['quizname'] = assignment_point.quizID.quizname
    data['quizid'] = assignment_point.quizID_id
    data['randomseq'] = assignment_point.randomseq
    data['randomver'] = assignment_point.randomver
    data['questions'] = []
    questions_list = questions.objects.filter(quizID_id = assignment_point.quizID_id)
    for question in questions_list:
        data['questions'] .append(
            {
                'questid':question.id,
                'question':question.question,
                'type':question.qtypesID.id,
                'answers':[{'answerid':answer.id, 'answer':answer.answer} for answer in answers.objects.filter(questionID_id=question.id)]
            }
        )
        
    return JsonResponse(data) #HttpResponse(data, content_type="application/json")

#this function update count of attempts
@login_required
def attempt_started(request, AssignmentNumber):
    attemp = get_object_or_404(assignment, id=AssignmentNumber)
    attemp.attempts -= 1
    attemp.resultready = True
    attemp.save()
    return JsonResponse({'status': 'success'})

@login_required
def results_save(request):
    #resdb = get_object_or_404(results, id=0)

    if request.method == 'POST':
        body = json.loads(request.body)
        for k in body:
            result = results()
            result.assignmentID_id = body[k]['assignmentid']
            result.questionID_id = body[k]['questid']
            result.answerID_id = body[k]['answer']
            result.qtypeID = body[k]['type']
            result.attempt = body[k]['attempt']
            result.value = body[k]['value']
            result.save(force_insert=True)
    else:
        return JsonResponse({'status': 'fail'})

    return JsonResponse({'status': 'success'})

@login_required
def get_result(request, AssignmentNumber, AttemptNumber):
    assignment_row = get_object_or_404(assignment, id=AssignmentNumber)
    cursor = connection.cursor()
    rawallpoints = 0

    cursor.execute('''SELECT sum(qst.weight) \
                        FROM public."AssessmentSystem_assignment" as ass inner join \
                        public."AssessmentSystem_quizzes" as qzs on (ass."quizID_id"=qzs.id) inner join \
                        public."AssessmentSystem_questions" as qst on (qzs.id=qst."quizID_id") \
                        where ass.id = ''' + str(AssignmentNumber) + ''' group by qst."quizID_id"
                    ''')
    row = cursor.fetchone()
    if(row):
        rawallpoints = row[0]
    else:
        return redirect('assigments')

    rawpoints = []
    swpoint = 0
    questid = -1
    textquests = []
    cursor.execute('''SELECT qst.id, qst.weight, ans.iscorrect, res.value, res."qtypeID" \
                    from public."AssessmentSystem_questions" as qst inner join \
                    public."AssessmentSystem_answers" as ans on (qst.id = ans."questionID_id") left join \
                    public."AssessmentSystem_results" as res on (ans.id=res."answerID_id") \
                    where   res."assignmentID_id"=''' + str(AssignmentNumber) + ''' and \
                            res.attempt=''' + str(int(AttemptNumber)+1) + ''' \
                    order by res."questionID_id" \
                    ''')
    for row in cursor.fetchall():
        if(swpoint!=row[0]):
            swpoint=row[0]
            questid += 1
            if(row[4] == 3):
                rawpoints.append(0)
            else:
                rawpoints.append(row[1])
        
        if(row[4] == 1 and int(row[2])==1 or row[4] == 2):
            if int(row[2])!=int(row[3]):
                rawpoints[questid] = 0
        if(row[4] == 3):
            textquests.append((row[0], row[1], row[3]))
    
    
    for vals in textquests:
        cursor.execute('''SELECT id FROM public."AssessmentSystem_answers" where \'''' + str(vals[2]) + '''\' SIMILAR TO recorrect and "questionID_id" = '''  + str(vals[0]))
        row = cursor.fetchone()
        if row:
            rawpoints.append(vals[1])


    assignment_row.resultready = False
    assignment_row.currentpoints = max(math.ceil(assignment_row.maxpoints * (sum(rawpoints)/rawallpoints)), assignment_row.currentpoints)
    assignment_row.save()

    return redirect('assigments')
