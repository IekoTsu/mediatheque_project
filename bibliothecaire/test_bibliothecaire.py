import os
from datetime import timedelta

import django
import pytest
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.utils import timezone
from bibliothecaire.models import Membre, Livre, Emprunt, Reservation, JeuDePlateau, Cd, Dvd

# Set up Django settings before any other Django imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mediatheque_project.settings')
django.setup()


@pytest.fixture(scope='function')
def bibliothecaire_user():
    # Create the group if it doesn't exist
    group, created = Group.objects.get_or_create(name='bibliothecaires')

    # Create the user and add to the group
    user = User.objects.create_user(username='bibliothecaire', password='password')
    user.groups.add(group)

    return user


@pytest.fixture
def create_member():
    def make_member(name='Default Name', email='default@example.com'):
        return Membre.objects.create(name=name, email=email)
    return make_member


@pytest.fixture
def create_livre():
    def _create_livre(title, author, publication_date):
        return Livre.objects.create(
            title=title,
            author=author,
            publication_date=publication_date
        )
    return _create_livre


@pytest.fixture
def create_cd():
    def _create_cd(title, author, publication_date, artiste):
        return Cd.objects.create(
            title=title,
            author=author,
            publication_date=publication_date,
            artiste=artiste
        )
    return _create_cd


@pytest.fixture
def create_dvd():
    def _create_dvd(title, author, publication_date, duration):
        return Dvd.objects.create(
            title=title,
            author=author,
            publication_date=publication_date,
            duration=duration  # This should be a timedelta object
        )
    return _create_dvd


@pytest.fixture
def create_jeu_de_plateau():
    def _create_jeu_de_plateau(title, createur):
        return JeuDePlateau.objects.create(
            title=title,
            createur=createur
        )
    return _create_jeu_de_plateau


@pytest.fixture
def create_emprunt(create_member, create_livre):
    def _create_emprunt(member=None, media=None, loan_date=None, return_date=None, returned=False):
        # Ensure we have a member and media to create a loan
        if member is None:
            member = create_member()
        if media is None:
            media = create_livre(title='Sample Book', author='Book Author', publication_date='2024-01-01')

        # Default dates if not provided
        if loan_date is None:
            loan_date = timezone.now()
        if return_date is None:
            return_date = loan_date + timedelta(days=7)

        # Create and return an Emprunt instance
        emprunt = Emprunt.objects.create(
            media=media,
            member=member,
            loan_date=loan_date,
            return_date=return_date,
            returned=returned
        )

        return emprunt

    return _create_emprunt


@pytest.fixture
def create_reservation(create_member, create_jeu_de_plateau):
    def _create_reservation(member=None,
                            jeu_de_plateau=None,
                            reservation_time=None,
                            reservation_end=None,
                            reserved=True
                            ):
        # Ensure we have a member and game to create a reservation
        if member is None:
            member = create_member()
        if jeu_de_plateau is None:
            jeu_de_plateau = create_jeu_de_plateau(title='Sample Game', createur='Game Creator')

        # Default times if not provided
        if reservation_time is None:
            reservation_time = timezone.now()
        if reservation_end is None:
            reservation_end = reservation_time + timedelta(hours=2)

        # Create and return a Reservation instance
        reservation = Reservation.objects.create(
            jeuDePlateau=jeu_de_plateau,
            member=member,
            reservation_time=reservation_time,
            reservation_end=reservation_end,
            reserved=reserved
        )

        return reservation

    return _create_reservation


@pytest.mark.django_db
def test_home_view(client, bibliothecaire_user):
    client.login(username='bibliothecaire', password='password')

    response = client.get(reverse('home'))
    assert response.status_code == 200
    assert 'home.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_list_members_view(client, bibliothecaire_user):
    client.login(username='bibliothecaire', password='password')

    response = client.get(reverse('list_members'))
    assert response.status_code == 200
    assert 'members/list_members.html' in [t.name for t in response.templates]
    assert 'members' in response.context


@pytest.mark.django_db
def test_create_member_view_get(client, bibliothecaire_user):
    client.login(username='bibliothecaire', password='password')

    response = client.get(reverse('create_member'))
    assert response.status_code == 200
    assert 'members/create_member.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_create_member_view_post(client, bibliothecaire_user):
    client.login(username='bibliothecaire', password='password')

    response = client.post(reverse('create_member'), data={
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        # Add other necessary fields
    })
    assert response.status_code == 302  # Redirect after successful creation
    assert response.url == reverse('list_members')


@pytest.mark.django_db
def test_update_member_view(client, create_member, bibliothecaire_user):
    client.login(username='bibliothecaire', password='password')

    member = create_member()
    response = client.post(reverse('update_member', args=[member.id]), data={
        'name': 'Updated Name',
        'email': 'updated@example.com',
        # Other fields as needed
    })
    assert response.status_code == 302
    assert response.url == reverse('list_members')
    member.refresh_from_db()
    assert member.name == 'Updated Name'


@pytest.mark.django_db
def test_delete_member_view(client, create_member, bibliothecaire_user):
    client.login(username='bibliothecaire', password='password')

    member = create_member()
    response = client.post(reverse('delete_member', args=[member.id]))
    assert response.status_code == 302
    assert response.url == reverse('list_members')
    assert not Membre.objects.filter(id=member.id).exists()


@pytest.mark.django_db
def test_list_media_view(client, bibliothecaire_user):
    client.login(username='bibliothecaire', password='password')

    response = client.get(reverse('list_media'))
    assert response.status_code == 200
    assert 'media/list_media.html' in [t.name for t in response.templates]
    assert 'livres' in response.context
    assert 'dvds' in response.context
    assert 'cds' in response.context
    assert 'jeux' in response.context


@pytest.mark.django_db
def test_create_media_view_post(client, bibliothecaire_user):
    client.login(username='bibliothecaire', password='password')

    response = client.post(reverse('create_media'), data={
        'media_type': 'livre',
        'title': 'New Book',
        'author': 'Author Name',
        'publication_date': '2024-01-01',
    })
    assert response.status_code == 302
    assert response.url == reverse('home')
    assert Livre.objects.filter(title='New Book').exists()


@pytest.mark.django_db
def test_create_loan_view_post(client, create_member, create_livre, bibliothecaire_user):
    client.login(username='bibliothecaire', password='password')

    member = create_member()
    media = create_livre('New Book', 'Author Name', '2024-01-01')
    response = client.post(reverse('create_loan'), data={
        'member': member.id,
        'media': media.id,
        'loan_date': timezone.now(),
        'return_date': timezone.now() + timezone.timedelta(days=7),
    })
    assert response.status_code == 302
    assert response.url == reverse('list_members')
    assert Emprunt.objects.filter(member=member, media=media).exists()


@pytest.mark.django_db
def test_return_loan_view(client, create_emprunt, bibliothecaire_user):
    client.login(username='bibliothecaire', password='password')

    emprunt = create_emprunt()
    response = client.post(reverse('return_loan', args=[emprunt.id]))
    assert response.status_code == 302
    emprunt.refresh_from_db()
    assert emprunt.returned is True


@pytest.mark.django_db
def test_create_reservation_view_post(client, create_member, create_jeu_de_plateau, bibliothecaire_user):
    client.login(username='bibliothecaire', password='password')

    member = create_member()
    game = create_jeu_de_plateau('Sample Board Game', 'Game creator')
    response = client.post(reverse('create_reservation'), data={
        'member': member.id,
        'jeuDePlateau': game.id,
        'reservation_time': timezone.now(),
        'reservation_end': timezone.now() + timezone.timedelta(days=7),
    })
    assert response.status_code == 302
    assert response.url == reverse('home')
    assert Reservation.objects.filter(member=member, jeuDePlateau=game).exists()


@pytest.mark.django_db
def test_manage_reservation_view(client, create_member, create_reservation, bibliothecaire_user):
    client.login(username='bibliothecaire', password='password')

    member = create_member()
    create_reservation(member=member)
    response = client.get(reverse('manage_reservation', args=[member.id]))
    assert response.status_code == 200
    assert 'boardGames/manage_reservation.html' in [t.name for t in response.templates]
    assert 'reservations' in response.context


@pytest.mark.django_db
def test_end_reservation_view(client, create_reservation, bibliothecaire_user):
    client.login(username='bibliothecaire', password='password')

    reservation = create_reservation()
    response = client.post(reverse('end_reservation', args=[reservation.id]))
    assert response.status_code == 302
    reservation.refresh_from_db()
    assert reservation.reserved is False
