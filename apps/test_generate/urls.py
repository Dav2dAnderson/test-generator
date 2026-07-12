from django.urls import path

from .views import (
    ChoiceDetailView,
    ChoiceListCreateView,
    GenerateTestFromPassageView,
    QuestionDetailView,
    QuestionListCreateView,
    TestDetailView,
    TestListCreateView,
)

urlpatterns = [
    path('generate/', GenerateTestFromPassageView.as_view(), name='generate-test'),
    path('', TestListCreateView.as_view(), name='test-list-create'),
    path('<uuid:pk>/', TestDetailView.as_view(), name='test-detail'),
    path('<uuid:test_id>/questions/', QuestionListCreateView.as_view(), name='question-list-create'),
    path('questions/<uuid:pk>/', QuestionDetailView.as_view(), name='question-detail'),
    path('questions/<uuid:question_id>/choices/', ChoiceListCreateView.as_view(), name='choice-list-create'),
    path('choices/<int:pk>/', ChoiceDetailView.as_view(), name='choice-detail'),
]