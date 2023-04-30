from django.db import models
from django.contrib.auth.models import User

# Create your models here.

"""
table clients = table user
class clients(models.Model):

    # Fields
    #clientID = models.ForeignKey(unique=True, help_text="Unique identifier of client")
    nickname = models.CharField(unique=True, max_length=50, help_text="Client's nickname")
    realname = models.CharField(max_length=255, help_text="Client's name")
    secondname = models.CharField(max_length=255, help_text="Client's secondname")
    patronymic = models.CharField(max_length=255, help_text="Client's patronymic")
    email = models.CharField(unique=True, max_length=320, help_text="Client's email")
    password = models.CharField(max_length=64, help_text="SHA256 hash of password")
    rights = models.IntegerField(default=0, help_text="Rights of the client")
    dateins = models.DateTimeField(auto_now_add=True, help_text="Date when the row was append")
    datechange = models.DateTimeField(blank=True, help_text="Date when the row was changed")
    fromIP = models.CharField(max_length=15, help_text="Client's last login IP")
"""

class quizzes(models.Model):

    # Fields
    quizname = models.CharField(unique=True, max_length=512, help_text="Name of the quiz")
    duration = models.IntegerField(default=0, help_text="Duration of tests")
    countofquestions = models.IntegerField(default=0, help_text="ammount of questions in this test")
    clientID = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)

class editors(models.Model):

    # Fields
    #dateend = models.CharField(auto_now = True, help_text="Date of expiration of the editing right")
    clientID = models.ForeignKey(User, on_delete=models.CASCADE)
    quizID = models.ForeignKey(quizzes, on_delete=models.CASCADE)

class qtypes(models.Model):

    # Fields
    typename = models.CharField(max_length=30, help_text="Question type") #один ответ; несколько ответов; значения с клавиатуры;

    def __str__(self):
        return self.typename

class questions(models.Model):

    # Fields
    question = models.CharField(max_length=1024, help_text="Question")
    sequence = models.IntegerField(default=0, help_text="Order for submitting questions")
    version = models.IntegerField(default=0, help_text="Test version")
    weight = models.FloatField(default=0, help_text="Test version")
    quizID = models.ForeignKey(quizzes, on_delete=models.CASCADE)
    qtypesID = models.ForeignKey(qtypes, on_delete=models.CASCADE, help_text="Type of question")

class answers(models.Model):

    # Fields
    answer = models.CharField(default="", max_length=1024, help_text="Question")
    iscorrect = models.PositiveSmallIntegerField(default=0, help_text="is answer correct")#not sure
    recorrect = models.CharField(default="", max_length=255, help_text="Regular expression to correct the response")
    #document = models.FileField()#not sure
    questionID = models.ForeignKey(questions, on_delete=models.CASCADE)

class assignment(models.Model):

    # Fields
    #datestart = models.DateTimeField(auto_now = True, help_text="Date when the assignment starts")
    #dateend = models.DateTimeField(auto_now = True, help_text="Date when the assignment ends")
    attempts = models.IntegerField(default=0, help_text="Number of attempts")
    version = models.IntegerField(default=0, help_text="Test version") # Necessary when quiz have several version for questions.
    randomseq = models.BooleanField(default=0, help_text="is sequence random") # Necessary when questions must have random order
    randomver = models.BooleanField(default=0, help_text="is variant random") # Necessary when questions must have random version
    maxpoints = models.IntegerField(default=0, help_text="maximum possible points")
    duration = models.IntegerField(default=0, help_text="duration of the test")
    resultready = models.BooleanField(default=0, help_text="Test passed but dont calculated") # added later for testng system
    currentpoints = models.IntegerField(default=0, help_text="Result of test in points") # added later for testng system
    clientID = models.ForeignKey(User, on_delete=models.CASCADE)
    quizID = models.ForeignKey(quizzes, on_delete=models.CASCADE)

class results(models.Model):

    # Fields
    #answerdate = models.DateTimeField(auto_now = True, help_text="Date of answer")
    assignmentID = models.ForeignKey(assignment, on_delete=models.CASCADE)
    questionID = models.ForeignKey(questions, on_delete=models.CASCADE)
    qtypeID = models.IntegerField(default=0, help_text="Type of question") # added later for testng system
    answerID = models.ForeignKey(answers, on_delete=models.CASCADE) # added later for testng system
    value = models.CharField(default="0", max_length=255, help_text="Answer") # added later for testng system

class textresult(models.Model):
    sigmin = models.IntegerField(default=0, help_text="Result of test in points, lower bound") # added later for testng system
    sigmax = models.IntegerField(default=0, help_text="Result of test in points, upper bound") # added later for testng system
    description = models.CharField(default="There is no description for this number of points yet.", max_length=7168, help_text="Description of achievements") # added later for testng system