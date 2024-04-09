from rest_framework import serializers
from .models import Candidate
from .models import TestCandidate,Test,Questions

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = '__all__'

class TestCandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCandidate
        fields = '__all__'


class CreateTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questions
        fields = '__all__'