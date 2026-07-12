from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Choice, Passage, Question, Test


class TestApiViewsTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='tester',
            email='tester@example.com',
            password='StrongPass123',
            phone_number='1234567890',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        self.passage = Passage.objects.create(
            title='Sample Passage',
            text='This is a sample passage.',
            uploaded_by=self.user,
        )
        self.test = Test.objects.create(
            passage=self.passage,
            title='Sample Test',
            created_by=self.user,
        )

    def test_can_list_and_create_tests(self):
        response = self.client.get(reverse('test-list-create'))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json()), 1)

        create_response = self.client.post(reverse('test-list-create'), {
            'title': 'New Test',
            'passage': self.passage.id,
        })
        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(create_response.json()['title'], 'New Test')

    def test_can_manage_questions_and_choices(self):
        question_response = self.client.post(
            reverse('question-list-create', args=[self.test.id]),
            {'text': 'What is 2 + 2?', 'question_type': 'mcq'},
        )
        self.assertEqual(question_response.status_code, 201)
        question_id = question_response.json()['id']

        choice_response = self.client.post(
            reverse('choice-list-create', args=[question_id]),
            {'label': 'A', 'text': '4', 'is_correct': True},
        )
        self.assertEqual(choice_response.status_code, 201)

        detail_response = self.client.get(reverse('question-detail', args=[question_id]))
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()['text'], 'What is 2 + 2?')

        choice_detail_response = self.client.get(reverse('choice-detail', args=[choice_response.json()['id']]))
        self.assertEqual(choice_detail_response.status_code, 200)
        self.assertEqual(choice_detail_response.json()['label'], 'A')
