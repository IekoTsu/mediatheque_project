from django import forms
from django.utils import timezone
from datetime import timedelta
from bibliothecaire.models import Membre, Emprunt, Media, Livre, Dvd, Cd, JeuDePlateau, Reservation


class MembreForm(forms.ModelForm):
    class Meta:
        model = Membre
        fields = ['name', 'email']
        labels = {
            'name': 'Nom',
            'email': 'Email',
        }


class MediaForm(forms.ModelForm):
    MEDIA_TYPE_CHOICES = [
        ('dvd', 'DVD'),
        ('livre', 'Livre'),
        ('cd', 'CD'),
        ('jeu', 'Jeu'),
    ]
    media_type = forms.ChoiceField(choices=MEDIA_TYPE_CHOICES)

    publication_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Media
        fields = ['title', 'author', 'publication_date']
        labels = {
            'title': 'Titre',
            'author': 'Auteur',
        }

    def __init__(self, *args, **kwargs):
        super(MediaForm, self).__init__(*args, **kwargs)
        self.fields['publication_date'].label = 'Date de publication'


class LivreForm(MediaForm):
    class Meta(MediaForm.Meta):
        model = Livre
        fields = MediaForm.Meta.fields


class DvdForm(MediaForm):
    duration = forms.DurationField(
        widget=forms.TimeInput(attrs={'type': 'time', 'step': '1'})  # step='1' allows seconds
    )

    class Meta(MediaForm.Meta):
        model = Dvd
        fields = MediaForm.Meta.fields + ['duration']

    def __init__(self, *args, **kwargs):
        super(DvdForm, self).__init__(*args, **kwargs)
        self.fields['duration'].label = 'Durée du dvd'


class CdForm(MediaForm):
    artiste = forms.CharField(max_length=255)

    class Meta(MediaForm.Meta):
        model = Cd
        fields = MediaForm.Meta.fields + ['artiste']


class JeuDePlateauForm(forms.ModelForm):
    class Meta:
        model = JeuDePlateau
        fields = ['title', 'createur']
        labels = {
            'title': 'Titre',
            'createur': 'Créateur du jeu',
        }


class EmpruntForm(forms.ModelForm):
    loan_date = forms.DateTimeField(
        initial=timezone.now,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    return_date = forms.DateTimeField(
        initial=lambda: timezone.now() + timedelta(days=7),
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    class Meta:
        model = Emprunt
        fields = ['media', 'member', 'loan_date', 'return_date']
        labels = {
            'media': 'Media',
            'member': 'Membre',
        }

    def __init__(self, *args, **kwargs):
        super(EmpruntForm, self).__init__(*args, **kwargs)
        # Filter media to show only those that are available
        self.fields['media'].queryset = Media.objects.filter(available=True)

        self.fields['loan_date'].label = 'Date de l\'emprunt'
        self.fields['return_date'].label = 'Date de retour'


class ReservationForm(forms.ModelForm):
    reservation_time = forms.DateTimeField(
        initial=timezone.now,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    reservation_end = forms.DateTimeField(
        initial=timezone.now() + timedelta(hours=2),
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    class Meta:
        model = Reservation
        fields = ['jeuDePlateau', 'member', 'reservation_time', 'reservation_end']
        labels = {
            'jeuDePlateau': 'Jeu de plateau',
            'member': 'Membre',
        }

    def __init__(self, *args, **kwargs):
        super(ReservationForm, self).__init__(*args, **kwargs)
        # Filter games to show only those that are available
        self.fields['jeuDePlateau'].queryset = JeuDePlateau.objects.filter(available=True)

        self.fields['reservation_time'].label = 'Date et heure de réservation'
        self.fields['reservation_end'].label = 'Fin de réservation'
