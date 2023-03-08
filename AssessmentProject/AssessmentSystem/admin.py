from django.contrib import admin
from .models import themes, quizzes, editors, questions, answers, assignment, results

# Register your models here.

#admin.site.register(clients)
admin.site.register(themes)
admin.site.register(quizzes)
admin.site.register(editors)
admin.site.register(questions)
admin.site.register(answers)
admin.site.register(assignment)
admin.site.register(results)