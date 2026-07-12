from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction

from .models import Passage, Test, Question, Choice
from .services.extract import extract_text_from_file, UnsupportedFileTypeError
from .services.question_generator import generate_questions_from_passage, QuestionGenerationError
# Create your views here.

class GenerateTestFromPassageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        source_file = request.FILES.get('source_file')
        title = request.data.get('title', 'Nomsiz test')
        num_questions = int(request.data.get('num_questions', 5))

        if not source_file:
            return Response(
                {"error": "source_file is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            passage_text = extract_text_from_file(source_file)
        except UnsupportedFileTypeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        if not passage_text:
            return Response(
                {"error": "Extracting failed. File might be empty or formated incorrectly."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            source_file.seek(0)  # faylni qayta saqlash uchun pointerni qaytarish
            generated_questions = generate_questions_from_passage(passage_text, num_questions)
        except QuestionGenerationError as e:
            return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)
        
        with transaction.atomic():
            passage = Passage.objects.create(
                title=title,
                text=passage_text,
                source_file=source_file,
                uploaded_by=request.user,
            )
            test = Test.objects.create(
                passage=passage,
                title=title,
                created_by=request.user,
            )
            for q_data in generated_questions:
                question = Question.objects.create(
                    test=test,
                    text=q_data['text'],
                    question_type='mcq',
                )
                for c_data in q_data['choices']:
                    Choice.objects.create(
                        question=question,
                        label=c_data['label'],
                        text=c_data['text'],
                        is_correct=c_data['is_correct'],
                    )
        return Response(
            {"test_id": test.id, "message": "Test generated successfully."},
            status=status.HTTP_201_CREATED
        )
