from django.urls import path

# from .views import Accountiew, HomeView

app_name = 'bankaccount'

urlpatterns = [
    path('/', HomeView.as_view(), name='home'),
    path('account/', AccountView.as_view(), name='account'),
]
