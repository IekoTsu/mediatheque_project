from django.shortcuts import render, get_object_or_404, redirect
from bibliothecaire.models import Membre, Livre, Dvd, Cd, JeuDePlateau, Emprunt, Reservation
from bibliothecaire.forms import MembreForm, MediaForm, EmpruntForm, LivreForm, DvdForm, CdForm, JeuDePlateauForm, \
    ReservationForm
import logging
from django.utils import timezone
from .decorators import bibliothecaire_required

# Set up logging
logger = logging.getLogger('bibliothecaire')


def get_user(request):
    user = request.user
    return user


@bibliothecaire_required
# Home view for the librarian app
def home(request):

    logger.info(f"User {get_user(request).username} accessed the home view.")
    return render(request, 'home.html')


@bibliothecaire_required
# List of members
def list_members(request):
    members = Membre.objects.all()
    logger.info(f"User {get_user(request).username} listed all members.")
    return render(request, 'members/list_members.html', {'members': members})


@bibliothecaire_required
# Create a new member
def create_member(request):
    if request.method == 'POST':
        form = MembreForm(request.POST)
        if form.is_valid():
            form.save()
            logger.info(f"User {get_user(request).username} created a new member.")
            return redirect('list_members')
        else:
            logger.warning(f"User {get_user(request).username} failed to create a new member. Invalid form data.")
    else:
        form = MembreForm()
    return render(request, 'members/create_member.html', {'form': form})


@bibliothecaire_required
# Update a member
def update_member(request, member_id):
    member = get_object_or_404(Membre, pk=member_id)
    if request.method == 'POST':
        form = MembreForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            logger.info(f"User {get_user(request).username} updated member with ID {member_id}.")
            return redirect('list_members')
        else:
            logger.warning(f"User {get_user(request).username} failed to update member with ID {member_id}. Invalid "
                           f"form data.")
    else:
        form = MembreForm(instance=member)
    return render(request, 'members/update_member.html', {'form': form})


@bibliothecaire_required
# Delete a member
def delete_member(request, member_id):
    member = get_object_or_404(Membre, pk=member_id)
    if request.method == 'POST':
        member.delete()
        logger.info(f"User {get_user(request).username} deleted member with ID {member_id}.")
        return redirect('list_members')
    return render(request, 'members/delete_member.html', {'member': member})


@bibliothecaire_required
# List all media
def list_media(request):
    livres = Livre.objects.all()
    dvds = Dvd.objects.all()
    cds = Cd.objects.all()
    jeux = JeuDePlateau.objects.all()
    logger.info(f"User {get_user(request).username} listed all media items.")
    return render(request, 'media/list_media.html', {
        'livres': livres,
        'dvds': dvds,
        'cds': cds,
        'jeux': jeux
    })


@bibliothecaire_required
def create_media(request):
    media_type = request.POST.get('media_type')
    livreForm = LivreForm(request.POST)
    dvdForm = DvdForm(request.POST)
    cdForm = CdForm(request.POST)
    mediaForm = MediaForm(request.POST)
    jeuDePlateauForm = JeuDePlateauForm(request.POST)

    if request.method == 'POST':
        if media_type == 'livre':
            form = livreForm
        elif media_type == 'dvd':
            form = dvdForm
        elif media_type == 'cd':
            form = cdForm
        elif media_type == 'jeu':
            form = jeuDePlateauForm
        else:
            form = MediaForm(request.POST)

        if form.is_valid():
            form.save()
            logger.info(f"User {get_user(request).username} created a new media item of type {media_type}.")
            return redirect('home')
        else:
            logger.warning(f"User {get_user(request).username} failed to create media of type {media_type}. Invalid "
                           f"form data.")

    return render(request, 'media/create_media.html', {
        'dvdForm': dvdForm,
        'livreForm': livreForm,
        'cdForm': cdForm,
        'mediaForm': mediaForm,
        'jeuDePlateauForm': jeuDePlateauForm,
        'media_type': media_type
    })


@bibliothecaire_required
# Create a new loan
def create_loan(request):
    errorUrl = ['create_loan', 'retourner à la page du création']
    if request.method == 'POST':
        form = EmpruntForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            if loan.member.active_loans >= 3:
                logger.warning(f"Member {loan.member.name} has reached the loan "
                               f"limit.")
                return render(request, 'error.html', {
                    'message': f"{loan.member.name}, ne peut pas avoir plus de 3 emprunts actifs.",
                    'url': errorUrl[0],
                    'urlTitle': errorUrl[1],
                })
            else:
                overdue_loans = []

                # Iterate through all emprunt objects related to the member
                for emprunt in loan.member.emprunt_set.all():
                    if not emprunt.returned and timezone.now() > emprunt.return_date:
                        overdue_loans.append(emprunt)

            # If there are any overdue loans, generate an error message
            if overdue_loans:
                overdue_message = f"Les emprunts suivants pour {loan.member.name} sont en retard:<br>"
                for emprunt in overdue_loans:
                    formatted_date = emprunt.return_date.strftime("%Y-%m-%d %H:%M")
                    overdue_message += f"- {emprunt.media.title} (Due le {formatted_date})<br>"

                logger.warning(f"Member {loan.member.name} has overdue loans.")
                return render(request, 'error.html', {
                    'message': overdue_message,
                    'url': errorUrl[0],
                    'urlTitle': errorUrl[1],
                })

            elif loan.loan_date > loan.return_date:
                logger.warning("loan date was set incorrectly.")
                return render(request, 'error.html', {
                    'message': "La date du emprunt a été mal définie, indiquez une date correcte.",
                    'url': errorUrl[0],
                    'urlTilte': errorUrl[1],
                })

            loan.save_emprunt()
            logger.info(f"User {get_user(request).username} created a loan for member {loan.member.name}.")
            return redirect('list_members')
    else:
        form = EmpruntForm()
    return render(request, 'loan/create_loan.html', {'form': form})


@bibliothecaire_required
# Return a loanbibliothecaire_emprunt
def return_loan(request, loan_id):
    loan = get_object_or_404(Emprunt, pk=loan_id)
    loan.returned = True
    loan.save_emprunt()
    logger.info(f"Loan with ID {loan_id} has been returned.")
    return redirect('manage_loans', member_id=loan.member.pk)


@bibliothecaire_required
def manage_loans(request, member_id):
    member = get_object_or_404(Membre, pk=member_id)

    # Get the sorting parameter from the query string, default to 'date'
    sort_by = request.GET.get('sort_by', 'date')  # 'date' or 'returned'

    member_emprunts = member.emprunt_set.all()

    # Sorting logic
    if sort_by == 'returned':
        sorted_emprunts = sorted(member_emprunts, key=lambda e: (e.returned, -e.loan_date.timestamp()))
    elif sort_by == 'date':
        sorted_emprunts = sorted(member_emprunts, key=lambda e: e.loan_date)
    else:
        sorted_emprunts = member_emprunts  # No sorting or default

    logger.info(f"User {get_user(request).username} is managing loans for member with ID {member_id}." 
                f"Sorted by {sort_by}.")
    return render(request, 'loan/manage_loans.html',
                  {
                      'member': member,
                      'member_emprunts': sorted_emprunts,
                      'sort_by': sort_by
                  })


@bibliothecaire_required
def create_reservation(request):
    errorUrl = ['create_reservation', 'Retour à la réservation']
    logger.info(f'User {get_user(request).username} accessed the reservation page.')
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            if not reservation.jeuDePlateau.available:
                logger.warning("Attempted to reserve an already reserved game.")
                return render(request, 'error.html', {
                    'message': "Ce jeu est déjà réservé. ",
                    'url': errorUrl[0],
                    'urlTilte': errorUrl[1],

                })

            elif reservation.reservation_time > reservation.reservation_end:
                logger.warning("Reservation time was set incorrectly.")
                return render(request, 'error.html', {
                    'message': "Mettez une heure de réservation correcte.",
                    'url': errorUrl[0],
                    'urlTilte': errorUrl[1],
                })

            if reservation.member.active_reservation >= 1:
                logger.warning(f"Member {reservation.member.name} has reached the reservation limit.")
                return render(request, 'error.html', {
                    'message': f"{reservation.member.name}, ne peut pas réserver plus d'un jeu en même temps. ",
                    'url': errorUrl[0],
                    'urlTilte': errorUrl[1],
                })

            reservation.save_reservation()
            logger.info(f"User {get_user(request).username} created a reservation" 
                        f"for member {reservation.member.name}.")
            return redirect('home')
        else:
            logger.warning("Failed to create reservation. Invalid form data.")

    return render(request, 'boardGames/reserve_game.html', {'form': ReservationForm})


@bibliothecaire_required
def manage_reservation(request, member_id):
    member = get_object_or_404(Membre, pk=member_id)
    member_reservation = sorted(member.reservation_set.all(), key=lambda r: (
        not r.reserved,
        -r.reservation_time.timestamp())
        )
    logger.info(f"User {get_user(request).username} is managing reservations for member with ID {member_id}.")
    return render(request, 'boardGames/manage_reservation.html', {'member': member, 'reservations': member_reservation})


@bibliothecaire_required
def end_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    reservation.reserved = False
    reservation.save_reservation()
    logger.info(f"User {get_user(request).username} ended reservation with ID {reservation_id}.")
    return redirect('manage_reservation', member_id=reservation.member.pk)
