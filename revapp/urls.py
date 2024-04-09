from django.urls import path
from .views import CandidateView,TestDetailsView,CreateTestView,AllQuestionsView,QuestionsByTestIdView,AddQuestionView

urlpatterns = [
    path('candidates/', CandidateView.as_view(), name='candidates'),
    path('test-details/<str:email>/', TestDetailsView.as_view(), name='test_details'),
    path('create-test/', CreateTestView.as_view(), name='create_test'),
    path('questions/', AllQuestionsView.as_view(), name='all_questions'),
    path('questions/<uuid:test_id>/', QuestionsByTestIdView.as_view(), name='questions_by_test_id'),
    path('add-question/', AddQuestionView.as_view(), name='add_question')
]
