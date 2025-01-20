from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_home, name='home'),
    path('api/messages/<int:user_id>/', views.get_messages, name='get_messages'),
    path('api/messages/<int:user_id>/read/', views.mark_messages_read, name='mark_messages_read'),
]