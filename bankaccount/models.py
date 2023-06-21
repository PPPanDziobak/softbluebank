from django.db import models
from django.contrib.auth.models import AbstractUser

from datetime import datetime, timedelta
import random
import string
import uuid


class BaseModel(models.Model):
    @classmethod
    def generate_number(cls, length):
        digits = string.digits
        return ''.join(random.choice(digits) for _ in range(length))

    @classmethod
    def generate_uuid_nr(cls):
        return uuid.uuid4().hex[:10]

    @classmethod
    def generate_card_number(cls):
        unique_card_number = None
        while not unique_card_number:
            card_number = ''.join(str(random.randint(0, 9)) for _ in range(10))
            if not CreditCardModel.objects.filter(card_number=card_number).exists():
                unique_card_number = card_number
        return unique_card_number


class AccountOwnerModel(AbstractUser):
    username = models.CharField(u'Nazwa użytkownika', max_length=150, unique=True, default='')
    firstname = models.CharField(u'Imię', max_length=50, blank=True)
    lastname = models.CharField(u'Nazwisko', max_length=50, blank=True)
    email = models.EmailField(u'Email', max_length=50, blank=True, unique=True)
    password = models.CharField(u'Hasło', max_length=8, blank=True)
    phone = models.CharField(u'Telefon', max_length=12, blank=True)
    address = models.CharField(u'Adres', max_length=250, blank=True)
    city = models.CharField(u'Miasto', max_length=250, blank=True)
    country = models.CharField(u'Kraj', max_length=250, blank=True)
    date_of_birth = models.DateField(u'Data urodzenia', blank=True)


class CreditCardModel(models.Model):
    card_number = models.CharField('Numer karty', max_length=10, unique=True, default=BaseModel.generate_card_number)
    expiration_date = models.DateField('Data ważności', default=datetime.now() + timedelta(days=5 * 365))
    cvc_number = models.CharField('Numer CVC', max_length=3, default=BaseModel.generate_number(3))
    payment_amount = models.IntegerField('Kwota transakcji', default=0.00)
    payment_date = models.DateField('Data transakcji', auto_now_add=True, blank=True)
    payments_counter = models.IntegerField('Licznik transakcji', default=0)
    pin_number = models.CharField('Kod PIN', max_length=4, default=BaseModel.generate_number(4))
    transaction_counter = models.IntegerField('Licznik transakcji', default=0)

    def __str__(self):
        return self.card_number

    def save(self, *args, **kwargs):
        if not self.card_number:
            self.card_number = self.generate_card_number()
        if not self.pk:
            self.transaction_counter = 0
        super().save(*args, **kwargs)

    def counter(self):
        self.transaction_counter += 1
        self.save()

    def generate_card_number(self):
        digits = string.digits
        card_number = ''.join(random.choice(digits) for _ in range(10))
        return card_number

    def generate_card_cvc_number(self):
        digits = string.digits
        cvc_number = ''.join(random.choice(digits) for _ in range(3))
        return cvc_number

    def generate_card_pin_number(self):
        digits = string.digits
        pin_number = ''.join(random.choice(digits) for _ in range(4))
        return pin_number


class AccountModel(models.Model):
    account_owner = models.ForeignKey(AccountOwnerModel, on_delete=models.CASCADE)
    credit_card = models.ForeignKey(CreditCardModel, on_delete=models.CASCADE)
    account_number = models.CharField(
        u'Numer konta', max_length=10, blank=False, unique=True, default=BaseModel.generate_number(10)
    )
    balance = models.IntegerField(u'Stan konta')
    transaction_counter = models.IntegerField('Licznik transakcji', default=0)

    def __str__(self):
        return self.account_number

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.generate_account_number()
        if not self.pk:
            self.transaction_counter = 0
        super().save(*args, **kwargs)
        super(AccountModel, self).save(*args, **kwargs)

    def generate_account_number(self):
        digits = string.digits
        account_number = ''.join(random.choice(digits) for _ in range(10))
        return account_number

    def counter(self):
        self.transaction_counter += 1
        self.save()


class TransactionHistoryModel(models.Model):
    sender_firstname = models.CharField(max_length=50)
    sender_lastname = models.CharField(max_length=50)
    sender_account_number = models.CharField(max_length=10)
    receiver_firstname = models.CharField(max_length=50)
    receiver_lastname = models.CharField(max_length=50)
    receiver_account_number = models.CharField(max_length=10)
    title = models.CharField(max_length=100)
    transaction_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
