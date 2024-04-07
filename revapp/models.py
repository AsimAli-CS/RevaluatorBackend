from django.db import models
from enum import Enum
import uuid


class AnswerChoices(Enum):
    OPTION_A = 'A'
    OPTION_B = 'B'
    OPTION_C = 'C'
    OPTION_D = 'D'

class Test(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    jobTitle = models.CharField(max_length=255)
    jobDescription = models.TextField()
    totalTime = models.IntegerField()
    totalScore = models.DecimalField(max_digits=5, decimal_places=2)
    testTime = models.DateTimeField()
    skills = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Questions(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    questionStatement = models.TextField()
    optionA = models.CharField(max_length=255)
    optionB = models.CharField(max_length=255)
    optionC = models.CharField(max_length=255)
    optionD = models.CharField(max_length=255)
    answer = models.CharField(
    max_length=1,
    choices=[(choice.value, choice.name) for choice in AnswerChoices])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Candidate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_no = models.CharField(max_length=15)
    cvTitle = models.CharField(max_length=255, null=True, blank=True)
    skills = models.JSONField()
    cvScore = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    testId = models.ForeignKey(Test, on_delete=models.CASCADE)
    testScore = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
