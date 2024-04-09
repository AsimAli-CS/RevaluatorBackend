from django.urls import path
from .views import CandidateView,TestDetailsView,CreateTestView

urlpatterns = [
    path('candidates/', CandidateView.as_view(), name='candidates'),
    path('test-details/<str:email>/', TestDetailsView.as_view(), name='test_details'),
    path('create-test/', CreateTestView.as_view(), name='create_test'),
]
