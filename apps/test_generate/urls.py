from django.urls import path

from .views import GenerateTestFromPassageView

urlpatterns = [
    path('generate/', GenerateTestFromPassageView.as_view(), name='generate-test')
]