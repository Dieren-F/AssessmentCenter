from django import forms
from django.forms import inlineformset_factory
from .models import quizzes, qtypes, questions, answers

class login_form(forms.Form):
    renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3).")

class RenewQuizForm(forms.Form):
    renewal_name = forms.CharField(max_length=50, help_text="Test name")

    def clean_renew(self):
        data = self.cleaned_data['renewal_name']
        return data

class QuestionCreateForm(forms.ModelForm):
    class Meta:
        model = questions
        #fields= ('question', 'sequence', 'version', 'weight', 'quizID', 'qtypesID')
        fields= ('question', 'weight', 'qtypesID')
        widgets = {
            'question': forms.Textarea(attrs={"style":'flex 1;resize: none;', "rows":3, "id":'smao'})
        }

class EditAnswers(forms.Form):
    renewal_name = forms.CharField(max_length=50, help_text="Test name")

    def clean_renew(self):
        data = self.cleaned_data['renewal_name']
        return data
    
class QuestionForm(forms.ModelForm):
    class Meta:
        model = questions
        fields= ('question', 'weight', 'qtypesID')
        widgets = {
            'question': forms.Textarea(attrs={"rows":3, "cols":30, "id":'smao'})
        }

class AnswersForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['recorrect'].required = False
        
    class Meta:
        model = answers
        fields = '__all__'#('answer', 'questionID', 'iscorrect')#'__all__'
        recorrect = forms.CharField(required=False)
        
        widgets = {
            'answer': forms.TextInput(
                attrs={
                    'class': 'form-control'
                    }
                ),
            'recorrect': forms.TextInput(
                attrs={
                    'class': 'answer-change-r recorrect'
                    }
                ),
            'iscorrect': forms.TextInput(
                attrs={
                    'class': 'answer-change-i iscorrect'
                    }
                ),
        }

AnswersFormSet = inlineformset_factory(
    questions, answers, form=AnswersForm,
    extra=1, can_delete=True, can_delete_extra=True,
)