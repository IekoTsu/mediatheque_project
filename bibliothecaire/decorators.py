# bibliothecaire/decorators.py
from django.shortcuts import redirect, render
from django.urls import reverse


def is_bibliothecaire(user):
    return user.groups.filter(name='bibliothecaires').exists()


def bibliothecaire_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?error=not_authenticated")
        if not is_bibliothecaire(request.user):
            return redirect(f"{reverse('login')}?error=not_bibliothecaire")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
