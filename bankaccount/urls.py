from django.urls import path

from bankaccount.views import (
    AccountInfoView,
    AccountLogoutView,
    AccountHistoryView,
    CreateAccountView,
    HomeView,
    LoginView,
    BankPasswordChangeView,
    ChangePinView,
    TransferView,
    )

app_name = 'bankaccount'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('create-account/', CreateAccountView.as_view(), name='create-account'),
    path('transfer/', TransferView.as_view(), name='transfer'),
    path('account-info/', AccountInfoView.as_view(), name='account-info'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', AccountLogoutView.as_view(), name='logout'),
    path('change-password/', BankPasswordChangeView.as_view(), name='change-password'),
    path('change-pin/', ChangePinView.as_view(), name='change-pin'),
    path('account-history/', AccountHistoryView.as_view(), name='account-history'),
]
