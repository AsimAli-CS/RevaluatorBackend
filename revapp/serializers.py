from rest_framework import serializers
from .models import Candidate
from .models import TestCandidate

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = '__all__'

# class TestCandidateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TestCandidate
#         fields = '__all__'

