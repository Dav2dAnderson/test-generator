from django.db import models
from django.contrib.auth import get_user_model

from base.models import BaseModel

User = get_user_model()

# Create your models here.

class Passage(BaseModel):
    title = models.CharField(max_length=255)
    text = models.TextField()  # extract qilingan matn
    source_file = models.FileField(upload_to='passages/', null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Test(BaseModel):
    passage = models.ForeignKey(Passage, on_delete=models.CASCADE, related_name='tests')
    title = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.passage.title

class Question(BaseModel):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=[('mcq', 'MCQ'), ('true_false', 'True/False')])

    def __str__(self):
        return self.test.title

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    label = models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C'),('D','D')])
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.question.text

    class Meta:
        unique_together = ('question', 'label')
    