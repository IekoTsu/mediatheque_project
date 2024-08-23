import pytest
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.test import Client


@pytest.mark.django_db
class TestCustomLoginView:

    def setup_method(self):
        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = Client()

    def test_login_view_no_error(self):
        # Test the login view without any error

        response = self.client.get(reverse('login'))
        assert response.status_code == 200
        assert 'message' not in response.context

    def test_login_view_not_authenticated_error(self):
        # Test the login view with the 'not_authenticated' error
        response = self.client.get(reverse('login'), {'error': 'not_authenticated'})
        assert response.status_code == 200
        assert response.context['message'] == 'vous devez d\'abord vous connecter'

    def test_login_view_not_bibliothecaire_error(self):
        # Test the login view with the 'not_bibliothecaire' error
        response = self.client.get(reverse('login'), {'error': 'not_bibliothecaire'})
        assert response.status_code == 200
        assert response.context['message'] == ('Vous devez faire partie du groupe des bibliothécaires pour accéder à '
                                               'cette page.')

    def test_login_view_invalid_login(self):
        # Test an invalid login attempt
        response = self.client.post(reverse('login'), {'username': 'wronguser', 'password': 'wrongpassword'})
        assert response.status_code == 200
        assert 'Nom d\'utilisateur ou mot de passe incorrect.' in response.context['message']

    def test_login_view_redirect_bibliothecaire(self):
        # Add user to bibliothecaires group
        group = Group.objects.create(name='bibliothecaires')
        self.user.groups.add(group)
        self.client.login(username='testuser', password='password')

        # Test successful login and redirection for bibliothecaires
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'password'})
        assert response.status_code == 302
        assert response.url == reverse('home')

    def test_login_view_redirect_non_bibliothecaire(self):
        # Test successful login and redirection for non-bibliothecaires
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'password'})
        assert response.status_code == 302
        assert response.url == reverse('membre_list_media')


@pytest.mark.django_db
class TestCustomLogoutView:

    def setup_method(self):
        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = Client()

    def test_logout_view(self):
        # Log in the user
        self.client.login(username='testuser', password='password')

        # Test logging out
        response = self.client.post(reverse('logout'))
        assert response.status_code == 302
        assert response.url == reverse('main_home')
        assert '_auth_user_id' not in self.client.session  # Ensure user is logged out
