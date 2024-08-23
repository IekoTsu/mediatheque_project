from django.shortcuts import render
from bibliothecaire.models import Livre, Dvd, Cd, JeuDePlateau


# List all media available to the public
def list_media(request):
    livres = Livre.objects.filter(available=True)
    dvds = Dvd.objects.filter(available=True)
    cds = Cd.objects.filter(available=True)
    jeux = JeuDePlateau.objects.filter(available=True)
    return render(request, 'list_media.html', {
        'livres': livres,
        'dvds': dvds,
        'cds': cds,
        'jeux': jeux
    })

