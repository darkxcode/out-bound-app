from django.shortcuts import render

def home(request):
    return render(request, 'campaigns/home.html')  # Create this template 