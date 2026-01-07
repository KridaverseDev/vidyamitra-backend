from django.db import models

from silicon.user.models import CustomUser

# Create your models here.


class Quiz(models.Model):
    topic = models.CharField(max_length=512, verbose_name="Topic")
    question = models.TextField(max_length=1024, verbose_name="Quizes")
    options = models.JSONField(verbose_name="Options")
    correct = models.CharField(max_length=8)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    users = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="quiz_creater"
    )


"""
options = {
'option_a': '<>',
'b': '<>',
'c': '<>',
'd': '<>',
}
correct: 'a'


"""
