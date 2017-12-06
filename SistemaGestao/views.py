from django.shortcuts import render
from user.forms import LoginForm


def index(request, login_form=LoginForm()):
    if hasattr(request, 'user') and request.user.is_authenticated():
        return render(request, 'SistemaGestao/home.html', {})
    else:
        return render(request, 'SistemaGestao/index.html', {'form': login_form})


def faq(request):
    return render(request, 'SistemaGestao/faq.html')
