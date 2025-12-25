from django.shortcuts import render

# Create your views here.

def pageAccueilSite(request):
    return render(request,'pageAccueil/index.html')
