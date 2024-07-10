from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class TASK(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    taskTitle = models.CharField(max_length=30)
    taskDesc = models.TextField()
    deadline = models.DateTimeField()

    def __str__(self):
        return self.taskTitle
    