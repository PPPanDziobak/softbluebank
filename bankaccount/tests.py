from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import AccountModel, CreditCardModel, TransactionHistoryModel


class HomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_view(self):
        response = self.client.get(reverse('bankaccount:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bankaccount/home.html')


class ErrorViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_error_view(self):
        response = self.client.get(reverse('bankaccount:error'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bankaccount/error.html')


class TransactionHistoryModelTest(TestCase):
    def setUp(self):
        self.transaction = TransactionHistoryModel.objects.create(
            sender_firstname='xxx',
            sender_lastname='yyy',
            sender_account_number='1234567890',
            receiver_firstname='zzz',
            receiver_lastname='vvv',
            receiver_account_number='0987654321',
            title='Test',
            amount=100.00
        )

    def test_transaction_created(self):
        self.assertIsNotNone(self.transaction)

    def test_transaction_date_set(self):
        self.assertIsNotNone(self.transaction.transaction_date)
