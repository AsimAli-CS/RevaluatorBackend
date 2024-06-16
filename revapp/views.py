from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import jwt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from revaluator import settings
import google.generativeai as genai
from .models import Candidate,TestCandidate,Questions,Test
from .serializers import CandidateSerializer,TestCandidateSerializer,CreateTestSerializer,QuestionSerializer
from authAPI.models import User
from django.core.mail import EmailMessage
from django.core.files.storage import default_storage
from django.core.mail import send_mail

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from pprint import pprint
from .extraction import extract_details_from_pdf
import logging
import os

user_id =None
def get_user_id_from_token(request):
    global user_id
    auth_header = request.headers.get('token')
    print(auth_header)
    if auth_header:
        try:
            # token = auth_header.split(' ')[1]  # Assuming the header is 'Bearer <token>'
            decoded_token = jwt.decode(auth_header, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = decoded_token.get('user_id')
            return user_id
        except (jwt.DecodeError) as e:
            # Handle token errors
            print(f"Token error: {e}")
            return None

def get_candidate_id_from_token(request):
    cand_header = request.headers.get('Candidatetoken')
    print("heee"+ cand_header)
    if cand_header:
        try:
            # token = auth_header.split(' ')[1]  # Assuming the header is 'Bearer <token>'
            decoded_token = jwt.decode(cand_header, settings.SECRET_KEY, algorithms=['HS256'])
            candidate_id = decoded_token.get('candidate_id')
            
            return candidate_id
        except (jwt.DecodeError) as e:
            # Handle token errors
            print(f"Token error: {e}")
            return None
    return None

class CandidateView(APIView):
    def post(self, request, format=None):
        recruiter_id = get_user_id_from_token(request)

        if isinstance(request.data, list):
            for candidate_data in request.data:
                candidate_data['recruiterId'] = recruiter_id
        else:
            request.data['recruiterId'] = recruiter_id
            
        if isinstance(request.data, list):
            serializer = CandidateSerializer(data=request.data, many=True)
        else:
            serializer = CandidateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Candidate data stored successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        recruiter_id = get_user_id_from_token(request)

        candidates = Candidate.objects.filter(recruiterId=recruiter_id)
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

class TestData(APIView):
    def get(self, request, id, recruiter_id , candidate_id , format=None):
        try:
            test = Test.objects.get(id=id)
            recruiter = get_object_or_404(User, id=recruiter_id)
            candidate = get_object_or_404(Candidate, id=candidate_id)
            serialized_data = CreateTestSerializer(test)
            return Response(serialized_data.data, status=status.HTTP_200_OK)
        except Test.DoesNotExist:
            return Response({'error': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)


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
    def post(self, request, test_id , format=None):
        data = request.data
        if isinstance(data, list):
            # If request data is a list of questions
            serializer_list = []
            for item in data:
                item['testId'] = test_id
                serializer = QuestionSerializer(data=item)
                if serializer.is_valid():
                    serializer.save()
                    serializer_list.append(serializer.data)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer_list, status=status.HTTP_201_CREATED)
        else:
            data['testId'] = test_id
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
        test_score = request.data.get('testScore')  # Added to fetch testScore from request

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
        
        candidate.testScore = test_score
        candidate.save()
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



# logger = logging.getLogger(__name__)

# class SendEmailView(APIView):
#     def post(self, request,candidate_id):
#         user_id = get_user_id_from_token(request)  # Assuming this function is defined correctly
#         # print(user_id)
#         try:
#             user = User.object.get(pk=user_id)
#         except User.DoesNotExist:
#             return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        
#         print(candidate_id)
#         try:
#             candidate = Candidate.objects.get(pk=candidate_id)
#             print(candidate.email)
#             return Response({'email': candidate.email}, status=status.HTTP_200_OK)
#         except Candidate.DoesNotExist:
#             return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)

#         # Logging the emails for debugging purposes - consider removing or changing the log level in production
#         logger.info(f"User Email: {user.email}, Candidate Email: {candidate.email}")

#         # Configure the SendinBlue API
#         configuration = sib_api_v3_sdk.Configuration()
#         configuration.api_key['api-key'] = settings.SENDINBLUE_API_KEY
#         api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
#         sender = {"email": user.email, "name": "From name"}
#         recipients = [{"email": candidate.email}]  # Correct assignment of email

#         subject = "My subject"
#         content = "Congratulations! You successfully sent this example email via the SendinBlue API."

#         send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
#             to=recipients,
#             sender=sender,
#             subject=subject,
#             html_content=content
#         )

#         try:
#             api_response = api_instance.send_transac_email(send_smtp_email)
#             return Response(api_response.to_dict(), status=status.HTTP_200_OK)
#         except ApiException as e:
#             logger.error(f"SendinBlue API exception: {str(e)}")
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         except Exception as e:
#             logger.error(f"Unexpected error: {str(e)}")
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

logger = logging.getLogger(__name__)

class SendEmailView(APIView):
    global user_id
    def post(self, request,candidate_id , test_id):
        # user_id ="58c10b93-1305-41fa-b7bd-3656cc6211f2"  # Assuming this function is defined correctly
        print("user_id" , user_id)
        try:
            user = User.object.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

          # Assuming this function is defined correctly
        try:
            candidate = Candidate.objects.get(pk=candidate_id)
        except Candidate.DoesNotExist:
            return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)

        # Logging the emails for debugging purposes - consider removing or changing the log level in production
        logger.info(f"User Email: {user.email}, Candidate Email: {candidate.email}")
        print("recepient:" + candidate.email + "   " + "sender:  " + user.email )
        # Configure the SendinBlue API
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = settings.SENDINBLUE_API_KEY
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        sender = {"email": user.email, "name": "From name"}
        recipients = [{"email": candidate.email}]  # Correct assignment of email

        subject = "Test Credentials"
        content = """
     <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <p style="font-size: 18px; color: #333; margin-bottom: 15px;">Here are the credentials for your test:</p>
    <ul style="list-style-type: none; padding-left: 0;">
        <li style="font-size: 16px; color: #666; margin-bottom: 5px;">TestId: <span style="font-weight: bold; color: #000;">{test_id}</span></li>
        <li style="font-size: 16px; color: #666; margin-bottom: 5px;">RecruiterId: <span style="font-weight: bold; color: #000;">{recruiter_id}</span></li>
        <li style="font-size: 16px; color: #666; margin-bottom: 5px;">CandidateId: <span style="font-weight: bold; color: #000;">{candidate_id}</span></li>
    </ul>
    <p style="font-size: 18px; color: #333; margin-top: 15px;">Click the link below to take the test:</p>
    <a href="http://localhost:3000/appPages/candidate-testId" style="display: inline-block; background-color: #007bff; color: #fff; text-decoration: none; padding: 10px 20px; font-size: 16px; border-radius: 5px;">Take Test</a>
</body>
        </html>

    """.format(test_id=test_id, candidate_id=candidate_id, recruiter_id=user_id)

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=recipients,
            sender= sender,
            subject=subject,
            html_content=content
        )

        try:
            api_response = api_instance.send_transac_email(send_smtp_email)
            return Response(api_response.to_dict(), status=status.HTTP_200_OK)
        except ApiException as e:
             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UploadResumeView(APIView):
    def post(self, request, format=None):
        files = request.FILES.getlist('resumes')
        recruiter_id = get_user_id_from_token(request)

        extracted_data = []

        for file in files:
            # Save the uploaded file to a temporary location
            file_path = default_storage.save(file.name, file)
            file_path = os.path.join(default_storage.location, file_path)
            
            # Extract details from the PDF
            details = extract_details_from_pdf(file_path, file)
            details['recruiterId'] = recruiter_id
            extracted_data.append(details)
            
            # Clean up the temporary file
            os.remove(file_path)

        # Save the extracted data to the database
        serializer = CandidateSerializer(data=extracted_data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Candidate data stored successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Configure the Gemini API
genai.configure(api_key=settings.GOOGLE_API_KEY)

logger = logging.getLogger(__name__)
class GenerateMCQsView(APIView):
    def post(self, request, format=None):
        skills = request.data.get('skills', '')

        if not skills:
            return Response({'error': 'Skills are required'}, status=status.HTTP_400_BAD_REQUEST)

        prompt = f"""
        Create 15 medium difficulty level MCQs short descriptive based on the following skills: {skills} with correct answers.
        It should be an array of objects and The pattern should be like this:
        
            "questionStatement": "Where does Shazil live?",
            "optionA": "Lahore",
            "optionB": "Multan",
            "optionC": "London",
            "optionD": "Karachi",
            "answer": "B"
    
        """
        
        logger.info(f'Generated prompt: {prompt}')

        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            logger.info('Received response from the AI model')

            questions_data = self.parse_response(response.text)
            

            # logger.info(f'Parsed questions data: {questions_data}')

            # if not questions_data:
            #     logger.error('Failed to parse generated questions')
            #     return Response({'error': 'Failed to parse generated questions'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # saved_questions = self.save_questions_to_db(questions_data)
            # logger.info(f'Saved questions to database: {saved_questions}')
            return Response(questions_data, status=status.HTTP_201_CREATED)

        except genai.TimeoutException as e:
            logger.error(f"Request timed out: {str(e)}")
            return Response({'error': 'Request timed out'}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            return Response({'error': 'Failed to generate questions'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def parse_response(self, response_text):
        questions_data = []
        try:
            questions = response_text.strip().split('\n\n')
            for question in questions:
                question_dict = {}
                lines = question.strip().split('\n')
                print("lines", lines)
                if len(lines) == 6:
                    question_dict['questionStatement'] = lines[0].split(": ", 1)[1].strip()
                    question_dict['optionA'] = lines[1].split(": ", 1)[1].strip()
                    question_dict['optionB'] = lines[2].split(": ", 1)[1].strip()
                    question_dict['optionC'] = lines[3].split(": ", 1)[1].strip()
                    question_dict['optionD'] = lines[4].split(": ", 1)[1].strip()
                    question_dict['answer'] = lines[5].split(": ", 1)[1].strip()
                    questions_data.append(question_dict)
                else:

                    logger.warning(f"Invalid question format, skipping: {question}")
                
                print("question",question)
        except Exception as e:
            logger.error(f"Error parsing response: {str(e)}")
        return question

    def save_questions_to_db(self, questions_data):
        saved_questions = []
        test_instance = Test.objects.first()  # Replace with appropriate test instance lookup
        for question_data in questions_data:
            try:
                question = Questions.objects.create(
                    questionStatement=question_data['questionStatement'],
                    optionA=question_data['optionA'],
                    optionB=question_data['optionB'],
                    optionC=question_data['optionC'],
                    optionD=question_data['optionD'],
                    answer=question_data['answer'],
                    testId=test_instance
                )
                saved_questions.append({
                    'id': question.id,
                    'questionStatement': question.questionStatement,
                    'optionA': question.optionA,
                    'optionB': question.optionB,
                    'optionC': question.optionC,
                    'optionD': question.optionD,
                    'answer': question.answer
                })
            except Exception as e:
                logger.error(f"Error saving question to DB: {str(e)}")
        return saved_questions