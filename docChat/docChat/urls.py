
from django.contrib import admin
from django.urls import path
from chatbot.views import Bot_Home , Bot_login , Bot_register,Bot_logout

urlpatterns = [
    #-----------------Core-----------
    path('admin/', admin.site.urls),
    #-------------------------------
    
    #-----------------Bot-----------
    path('',Bot_Home,name="root"),
    path('login',Bot_login,name="login"),
    path('register',Bot_register,name="register"),
    path('logout',Bot_logout,name="logout"),   
    #-------------------------------
]
