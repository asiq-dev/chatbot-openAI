from django.urls import path
from .views import chat_view

urlpatterns = [
    path('chat/<int:customer_id>/', chat_view, name='chat'),
]
