from django.urls import path
from .views import CandidateView,TestDetailsView,CreateTestView,AllQuestionsView,QuestionsByTestIdView,AddQuestionView,DeleteQuestionView,UpdateQuestionView,TestCandidateCreateView,RecruiterCandidateResults,TestSubmissionView,SendEmailView
# from .views import send_mailtrap_email
urlpatterns = [
    path('testSubmission/', TestSubmissionView.as_view(), name='Submission'),
    path('candidates/', CandidateView.as_view(), name='candidates'),
    path('test-details/<str:email>/', TestDetailsView.as_view(), name='test_details'),
    path('create-test/', CreateTestView.as_view(), name='create_test'),
    path('questions/', AllQuestionsView.as_view(), name='all_questions'),
    path('questions/<uuid:test_id>/', QuestionsByTestIdView.as_view(), name='questions_by_test_id'),
    path('add-question/<uuid:test_id>/', AddQuestionView.as_view(), name='add_question'),
    path('questions/delete/<uuid:question_id>/', DeleteQuestionView.as_view(), name='delete_question'),
    path('questions/update/<uuid:question_id>/', UpdateQuestionView.as_view(), name='update_question'),
    path('test-candidates/', TestCandidateCreateView.as_view(), name='create_test_candidate'),
    path('recruiters/<uuid:recruiter_id>/candidates-results/', RecruiterCandidateResults.as_view(), name='recruiter_candidate_results'),
    path('send-email/<uuid:candidate_id>/', SendEmailView.as_view(), name='send-email'),
    
 ]
