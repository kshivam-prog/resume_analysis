from django.urls import path
from django.views.generic.base import RedirectView
from .views import dashboard

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('dashboard/', RedirectView.as_view(url='/', permanent=False)),
]
