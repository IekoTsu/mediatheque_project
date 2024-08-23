from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy


class CustomLoginView(LoginView):
    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        error = self.request.GET.get('error')
        if error == 'not_authenticated':
            context['message'] = 'vous devez d\'abord vous connecter'
        elif error == 'not_bibliothecaire':
            context['message'] = 'Vous devez faire partie du groupe des bibliothécaires pour accéder à cette page.'

        # Check for form errors (login failure)
        if 'form' in context and context['form'].errors:
            context['message'] = 'Nom d\'utilisateur ou mot de passe incorrect.'

        return context

    def get_success_url(self):
        user = self.request.user

        if user.groups.filter(name='bibliothecaires').exists():
            return reverse_lazy('home')
        else:
            return reverse_lazy('membre_list_media')


def custom_logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect(reverse_lazy('main_home'))


def main_home(request):
    return render(request, 'main_home.html')
