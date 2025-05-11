from django.db import models
from user.models import User
import secrets
import string

class Form(models.Model):
    id = models.CharField(primary_key=True, max_length=10, editable=False)
    title = models.CharField(max_length=150)
    creat_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forms')
    
    def save(self, *args, **kwargs):
        if not self.id:
            alphabet = string.ascii_letters + string.digits
            self.id = ''.join(secrets.choice(alphabet) for _ in range(10))
        super().save(*args, **kwargs)
class Question(models.Model):
    QUESTION_TYPES = (
        ('text','Text field'),
        ('radio','Single options'),
        ('checkbox','Multiple options'),
    )
    form  = models.ForeignKey(Form, on_delete = models.CASCADE, related_name = 'questions')
    text = models.CharField(max_length = 600)
    type = models.CharField(max_length = 20, choices = QUESTION_TYPES)
    required = models.BooleanField(default = True)

class Response(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='responses')
    respondent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    creat_time = models.DateTimeField(auto_now_add=True)

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=200)

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete = models.CASCADE)
    response = models.ForeignKey(Response,on_delete = models.CASCADE, related_name = 'answers')
    select = models.ManyToManyField(Option , blank = True)
    text = models.TextField(blank = True, null = True)