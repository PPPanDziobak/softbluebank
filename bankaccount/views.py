from django.shortcuts import render
from django.views import View


class HomeView(View):
    def get(self):
        pass


class AccountView(HomeView):
    def get(self):
        pass
