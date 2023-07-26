from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    DetailView,
    UpdateView,
)

from bankaccount.forms import LoginForm, CreateAccountForm, ChangePinForm, BankPasswordChangeForm, TransferForm
from bankaccount.models import AccountModel
from bankaccount.models import AccountOwnerModel, CreditCardModel, TransactionHistoryModel


class HomeView(View):
    template_name = 'bankaccount/home.html'

    def get(self, request):
        return render(request, self.template_name)


class BankLoginView(LoginView):
    # logowanie z uzyciem wbudowanego widoku django
    template_name = 'registration/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('bankaccount:account-info')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.get_form()
        return context


class CreateAccountView(View):
    template_name = 'registration/create_account.html'

    def get(self, request, *args, **kwargs):
        form = CreateAccountForm()
        context = {'form': form}
        return render(request, self.template_name, context)

    # Tworzenie nowego użytkownika na podstawie danych z formularza + wykorzystanie modeli żeby wygenerować nr konta
    # i nr karty kredytowej itp
    def post(self, request, *args, **kwargs):
        form = CreateAccountForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Generowanie danych dla CreditCardModel
            credit_card = CreditCardModel()
            credit_card.save()

            # Generowanie danych dla AccountModel
            account = AccountModel()
            account.account_owner = user
            account.credit_card = credit_card
            account.balance = 0
            account.save()
            login(request, user)

            return redirect('bankaccount:account-info')
        else:
            context = {'form': form}
            return render(request, self.template_name, context)


class AccountInfoView(LoginRequiredMixin, DetailView):
    template_name = 'bankaccount/account_info.html'
    model = AccountOwnerModel

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        account_owner = self.request.user
        try:
            account = AccountModel.objects.get(account_owner=account_owner)
            context['account'] = account
            context['account_owner'] = account.account_owner
            context['account_number'] = account.account_number
            context['balance'] = account.balance
            context['credit_card'] = account.credit_card
        except AccountModel.DoesNotExist:
            return redirect('bankaccount:error')

        return context


class AccountHistoryView(View):
    template_name = 'bankaccount/account_history.html'

    # sprawdzenie historii przelewów, przychodzące / wychodzące
    def get(self, request, *args, **kwargs):
        account_owner = request.user
        try:
            account = AccountModel.objects.get(account_owner=account_owner)
            acc_number = account.account_number
            transactions_in = TransactionHistoryModel.objects.filter(receiver_account_number=acc_number)
            transactions_out = TransactionHistoryModel.objects.filter(sender_account_number=acc_number)
            context = {'transactions_in': transactions_in, 'transactions_out': transactions_out}
            return render(request, self.template_name, context)
        except AccountModel.DoesNotExist:
            return redirect('bankaccount:error')


class AccountLogoutView(LogoutView):
    # wylogowywanie z uzyciem wbudowanego widoku django
    next_page = reverse_lazy('bankaccount:home')


class TransferView(View):
    template_name = 'bankaccount/transfer.html'

    def get(self, request, *args, **kwargs):
        form = TransferForm()
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = TransferForm(request.POST)
        if form.is_valid():
            # Pobranie danych z formularza
            receiver_firstname = form.cleaned_data['receiver_firstname']
            receiver_lastname = form.cleaned_data['receiver_lastname']
            title = form.cleaned_data['title']
            receiver_account_number = form.cleaned_data['receiver_account_number']
            amount = form.cleaned_data['amount']

            # Sprawdzenie, czy konto nadawcy istnieje
            try:
                account_owner = request.user
                account = AccountModel.objects.get(account_owner=account_owner)
            except AccountModel.DoesNotExist:
                return redirect('bankaccount:error')

            # Tworzenie obiektu TransactionHistory
            sender_firstname = account_owner.firstname
            sender_lastname = account_owner.lastname
            sender_account_number = account.account_number
            transaction = TransactionHistoryModel.objects.create(
                sender_firstname=sender_firstname,
                sender_lastname=sender_lastname,
                sender_account_number=sender_account_number,
                receiver_firstname=receiver_firstname,
                receiver_lastname=receiver_lastname,
                receiver_account_number=receiver_account_number,
                title=title,
                amount=amount
            )
            transaction.save()

            # Aktualizacja stanu konta nadawcy
            account.balance -= amount
            account.save()

            # Aktualizacja stanu konta odbiorcy
            try:
                receiver_account = AccountModel.objects.get(account_number=receiver_account_number)
                receiver_account.balance += amount
                receiver_account.save()
            except AccountModel.DoesNotExist:
                return redirect('bankaccount:error')

            return redirect('bankaccount:account-info')
        else:
            context = {'form': form}
            return render(request, self.template_name, context)


class ChangePinView(LoginRequiredMixin, UpdateView):
    # zmiana pin przy użyciu wbudowanego widoku django
    template_name = 'registration/change_pin.html'
    form_class = ChangePinForm
    success_url = reverse_lazy('bankaccount:account-info')

    def get_object(self, queryset=None):
        account_owner = self.request.user
        return AccountModel.objects.get(account_owner=account_owner)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        account = self.get_object()
        kwargs['credit_card'] = account.credit_card
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class BankPasswordChangeView(PasswordChangeView):
    # zmiana hasła przy użyciu wbudowanego widoku django
    template_name = 'registration/change_password.html'
    form_class = BankPasswordChangeForm
    success_url = reverse_lazy('bankaccount:account-info')

    def form_valid(self, form):
        self.request.user.set_password(form.cleaned_data['new_password'])
        self.request.user.save()
        return super().form_valid(form)


class ErrorView(View):
    template_name = 'bankaccount/error.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
