from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Candidate,TestCandidate,Questions,Test
from .serializers import CandidateSerializer,TestCandidateSerializer,CreateTestSerializer,QuestionSerializer
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

    def get(self, request, format=None):
        candidates = Candidate.objects.all()
        serializer = CandidateSerializer(candidates, many=True)
        return Response(serializer.data)


class TestDetailsView(APIView):
    def get(self, request, email, format=None):
        try:
            user = User.object.get(email=email)
            test_candidates = TestCandidate.objects.filter(user=user)
            serialized_data = TestCandidateSerializer(test_candidates, many=True)
            return Response(serialized_data.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class CreateTestView(APIView):
    def post(self, request, format=None):
        serializer = CreateTestSerializer(data=request.data)
        if serializer.is_valid():
            test = serializer.save()
            return Response({'id': str(test.id)}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AllQuestionsView(APIView):
    def get(self, request, format=None):
        questions = Questions.objects.all()
        serialized_questions = QuestionSerializer(questions, many=True)
        return Response(serialized_questions.data, status=status.HTTP_200_OK)
    

class QuestionsByTestIdView(APIView):
    def get(self, request, test_id, format=None):
        try:
            questions = Questions.objects.filter(testId=test_id)
            serialized_questions = QuestionSerializer(questions, many=True)
            return Response(serialized_questions.data, status=status.HTTP_200_OK)
        except Questions.DoesNotExist:
            return Response({'error': 'Questions not found'}, status=status.HTTP_404_NOT_FOUND)
        
class AddQuestionView(APIView):
    def post(self, request, format=None):
        data = request.data
        if isinstance(data, list):
            # If request data is a list of questions
            serializer_list = []
            for item in data:
                serializer = QuestionSerializer(data=item)
                if serializer.is_valid():
                    serializer.save()
                    serializer_list.append(serializer.data)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer_list, status=status.HTTP_201_CREATED)
        else:
            # If request data is a single question
            serializer = QuestionSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DeleteQuestionView(APIView):
    def delete(self, request, question_id, format=None):
        try:
            question = Questions.objects.get(id=question_id)
            question.delete()
            return Response({'message': 'Question deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Questions.DoesNotExist:
            return Response({'error': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)
        
class UpdateQuestionView(APIView):
    def put(self, request, question_id, format=None):
        try:
            question = Questions.objects.get(id=question_id)
            serializer = QuestionSerializer(question, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Questions.DoesNotExist:
            return Response({'error': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)
        
class TestCandidateCreateView(APIView):
    def post(self, request, format=None):
        # Ensure user, candidate, and test IDs are provided in the request data
        user_id = request.data.get('user')
        candidate_id = request.data.get('candidate')
        test_id = request.data.get('testId')
        if not user_id or not candidate_id or not test_id:
            return Response({'error': 'User ID, candidate ID, and test ID are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user, candidate, and test IDs exist in the database
        try:
            user = User.object.get(id=user_id)
            candidate = Candidate.objects.get(id=candidate_id)
            test = Test.objects.get(id=test_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Candidate.DoesNotExist:
            return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)
        except Test.DoesNotExist:
            return Response({'error': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)

        # Continue with serializer validation and saving
        serializer = TestCandidateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class RecruiterCandidateResults(APIView):
    def get(self, request, recruiter_id, format=None):
        # Retrieve all candidates' results/data specific to the recruiter
        candidates_results = TestCandidate.objects.filter(user__id=recruiter_id)
        serializer = TestCandidateSerializer(candidates_results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class TestSubmissionView(APIView):
    def post(self, request, test_id="6a4c817e-c1c0-4bee-9160-448be2e99cc7", candidate_id="028da5b2-8cee-4ec4-be39-d7a6b4fc8755" ,format=None):
        try:
            test = Test.objects.get(id=test_id)
        except Test.DoesNotExist:
            return Response({"detail": "Test not found"}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            candidate = Candidate.objects.get(id=candidate_id)
        except Test.DoesNotExist:
            return Response({"detail": "Candidate not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Assuming request.data contains the dictionary of question IDs and user answers

        #candidate_answers = request.data.get('answers', {})
        candidate_answers_dict = {
            "011b9dde-5911-4c18-ba1b-f72a9c76afd1": "B",
            "076473f1-c9b4-4f47-a819-0a57a5de3ea6": "B",
            "2b8d3a30-9736-47d4-aff5-ef317bd0de3b": "B",
            "328348b2-7518-4dce-9f6b-1b78b064e394": "D",
            "516156c7-86d4-4392-8f70-2eb9398f267e": "C",
            "71e85260-9019-4782-857f-496e55b49e2b": "C"
        }

        correct_answers = 0
        
        for question_id, user_answer in candidate_answers_dict.items():
            try:
                question = Questions.objects.get(id=question_id, testId=test)
            except Questions.DoesNotExist:
                return Response({"detail": f"Question with ID {question_id} not found in the test"}, status=status.HTTP_404_NOT_FOUND)
            
            if user_answer == question.answer:
                correct_answers += 1
        
        # Calculate the score based on the number of correct answers
        total_questions = len(candidate_answers_dict)
        if total_questions == 0:
            return Response({"detail": "No questions found in the test"}, status=status.HTTP_404_NOT_FOUND)
        
        score = (correct_answers / total_questions) * 100
        
        try:
            test_candidates = TestCandidate.objects.filter(candidate=candidate, testId=test)
            if test_candidates.exists():
                for test_candidate in test_candidates:
                    test_candidate.testScore = score
                    test_candidate.save()
            else:
                return Response({'msg': 'Test candidate not found'}, status=status.HTTP_404_NOT_FOUND)
        except TestCandidate.MultipleObjectsReturned:
            return Response({'msg': 'Multiple TestCandidate instances found for candidate and test'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({'msg': 'Test submitted successfully', 'score': score}, status=status.HTTP_201_CREATED)
