from django.urls import path , include
from django.contrib import admin
from . import views

urlpatterns = [
     path('admin/', admin.site.urls, name='admin'),
    path('', views.home, name='home'),
    path('accounts/',include('accounts.urls',namespace='accounts')),
    path('chat/', include('chat.urls',namespace='chat')),
    path("__reload__/", include("django_browser_reload.urls")),
    
]
