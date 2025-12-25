from django.shortcuts import render

# Create your views here.

def pageLoginUser(request):
    return render(request,'pageAuth/login.html')

def pageIncription(request):
    return render(request,'pageAuth/inscription.html')
