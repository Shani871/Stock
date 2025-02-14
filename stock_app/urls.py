from django.urls import path
from .views import stock_analysis, home

urlpatterns = [

    path('', home, name='home'),  # Home page
    path('api/stock/<str:ticker>/', stock_analysis, name='stock_analysis'),
]