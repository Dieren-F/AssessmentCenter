from django import forms
from .models import quizzes, qtypes, questions

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
            'question': forms.Textarea(attrs={"rows":3, "cols":30, "id":'smao'})
        }