from django.shortcuts import render , redirect
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat
from .Doc_Chat_functions import Get_Response
from django.utils import timezone

# Create your views here.
def Bot_Home(request):
    chats = None
    try:
        chats = Chat.objects.filter(user = request.user)
    except:
        pass
    if (request.method == 'POST'):
        message = request.POST.get('message')
        response = Get_Response(message , chats)
        #saving history
        chat_user = Chat(user=request.user , message = message , response = response , created_at=timezone.now())
        chat_user.save()
        return JsonResponse({'message':message , 'response':response})
    return render(request , 'chatbot/bot.html' , {
        'chats':chats
    })

def Bot_login(request):
    error_message= None
    if (request.method == 'POST'):
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request , username=username , password=password)
        if user is not None:
            auth.login(request , user)
            return redirect('/')
        else:
            error_message = "Invalid Username or Password"
            
    return render(request , 'chatbot/login.html' , {
        "error_message":error_message
    })

def Bot_register(request):
    if (request.method == 'POST'):
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        if password1 == password2:
            try:
                user = User.objects.create_user(username , email , password1)
                user.save()
                auth.login(request , user)
                #print('done')
                return redirect('/')
            except:
                error_message = 'Error Creating Account'
        else:
            error_message = 'PASSWORD dont Match'
            return render(request , 'chatbot/register.html',
                          {
                              'error_message':error_message
                          })
    return render(request , 'chatbot/register.html')

def Bot_logout(request):
    auth.logout(request)
    return redirect('login')

