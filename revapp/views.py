from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Candidate,TestCandidate
from .serializers import CandidateSerializer,TestCandidateSerializer
from authAPI.models import User

class CandidateView(APIView):
    def post(self, request, format=None):
        if isinstance(request.data, list):
            serializer = CandidateSerializer(data=request.data, many=True)
        else:
            serializer = CandidateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Candidate data stored successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class TestDetailsView(APIView):
    def get(self, request, email, format=None):
        try:
            user = User.objects.get(email=email)
            test_candidates = TestCandidate.objects.filter(user=user)
            serialized_data = TestCandidateSerializer(test_candidates, many=True)
            return Response(serialized_data.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
