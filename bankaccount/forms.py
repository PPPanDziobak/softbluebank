from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from bankaccount.models import CreditCardModel, AccountOwnerModel


class CreateAccountForm(UserCreationForm):
    date_of_birth = forms.DateField(
        label='Data urodzenia',
        widget=forms.TextInput(attrs={'placeholder': 'yyyy-mm-dd'})
    )

    class Meta(UserCreationForm.Meta):
        model = AccountOwnerModel
        fields = (
            'username', 'first_name', 'last_name',
            'email', 'phone', 'address', 'city', 'country', 'date_of_birth'
        )


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email', max_length=50)
    password = forms.CharField(widget=forms.PasswordInput())


class ChangePinForm(forms.ModelForm):
    validator = RegexValidator(r'^\d{4}$', 'Wprowadź czterocyfrowy numer PIN.')

    current_pin = forms.CharField(
        label='Podaj aktualny nr PIN',
        max_length=4,
        validators=[validator]
    )
    new_pin = forms.CharField(
        label='Podaj nowy nr PIN',
        max_length=4,
        validators=[validator]
    )

    class Meta:
        model = CreditCardModel
        fields = []

    def __init__(self, *args, **kwargs):
        self.credit_card = kwargs.pop('credit_card', None)
        super().__init__(*args, **kwargs)

    def clean_current_pin(self):
        current_pin = self.cleaned_data.get('current_pin')
        if current_pin != self.credit_card.pin_number:
            raise forms.ValidationError('Podano niepoprawny aktualny nr PIN.')
        return current_pin

    def save(self, commit=True):
        new_pin = self.cleaned_data.get('new_pin')
        self.credit_card.pin_number = new_pin
        if commit:
            self.credit_card.save()
        return self.credit_card


class BankPasswordChangeForm(forms.ModelForm):
    current_password = forms.CharField(
        label='Podaj aktualne hasło',
        max_length=8,
        widget=forms.PasswordInput()
    )
    new_password = forms.CharField(
        label='Podaj nowe hasło',
        max_length=8,
        widget=forms.PasswordInput()
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError('Podano niepoprawne hasło.')
        return current_password

    def save(self, commit=True):
        new_password = self.cleaned_data.get('new_password')
        self.user.set_password(new_password)
        if commit:
            self.user.save()
        return self.user

    class Meta:
        model = AccountOwnerModel
        fields = ['current_password', 'new_password']


class TransferForm(forms.Form):

    def validate_positive(self, value):
        if value <= 0:
            raise ValidationError('Wprowadź dodatnią kwotę.')

    validator = RegexValidator(r'^\d{10}$', 'Wprowadź 10-cyfrowy numer konta.')
    receiver_firstname = forms.CharField(
        label='Wpisz imię odbiorcy',
        max_length=50,
        required=True
    )
    receiver_lastname = forms.CharField(
        label='Wpisz nazwisko odbiorcy',
        max_length=50,
        required=True
    )
    title = forms.CharField(
        label='Wpisz tytuł',
        max_length=100,
        required=True
    )
    receiver_account_number = forms.CharField(
        label='Wpisz nr konta',
        max_length=10,
        validators=[validator],
        required=True
    )
    amount = forms.DecimalField(
        label='Podaj kwotę',
        max_digits=10,
        decimal_places=2,
        required=True
    )
