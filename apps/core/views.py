from django.shortcuts import render

def home(request):
    """Homepage view"""
    return render(request, 'homepage.html')

