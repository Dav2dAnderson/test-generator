from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction

from .models import Passage, Test, Question, Choice
from .serializers import PassageSerializer, QuestionSerializer, TestSerializer, ChoiceSerializer

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


class TestListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TestSerializer

    def get_queryset(self):
        return Test.objects.all().prefetch_related('questions__choices').order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TestDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Test.objects.all()
    serializer_class = TestSerializer

    def perform_update(self, serializer):
        serializer.save(created_by=self.request.user)


class QuestionListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionSerializer

    def get_queryset(self):
        test = get_object_or_404(Test, pk=self.kwargs['test_id'])
        return test.questions.all().prefetch_related('choices')

    def perform_create(self, serializer):
        test = get_object_or_404(Test, pk=self.kwargs['test_id'])
        serializer.save(test=test)


class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class ChoiceListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChoiceSerializer

    def get_queryset(self):
        question = get_object_or_404(Question, pk=self.kwargs['question_id'])
        return question.choices.all()

    def perform_create(self, serializer):
        question = get_object_or_404(Question, pk=self.kwargs['question_id'])
        serializer.save(question=question)


class ChoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer


class PassageView(APIView):
    permission_classes = [permissions.IsAdminUser]
    def get(self, request):
        passages = Passage.objects.all()
        serializer = PassageSerializer(passages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        if pk:
            passage = Passage.objects.get(pk=pk)
            passage.delete()
        return Response({"pk": "pk is required."})