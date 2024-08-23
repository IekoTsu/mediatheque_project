from django.db import models
from django.utils import timezone
from datetime import timedelta


# Base class for all media types
class Media(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publication_date = models.DateField()
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} by {self.author}"


# Derived classes for specific media types
class Livre(Media):
    pass


class Dvd(Media):
    duration = models.DurationField()


class Cd(Media):
    artiste = models.CharField(max_length=255)


# Separate class for board games
class JeuDePlateau(models.Model):
    title = models.CharField(max_length=255)
    createur = models.CharField(max_length=255)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.title


# Membre class
class Membre(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    active_loans = models.IntegerField(default=0)
    active_reservation = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Emprunt(models.Model):
    media = models.ForeignKey(Media, on_delete=models.CASCADE)
    member = models.ForeignKey(Membre, on_delete=models.CASCADE)
    loan_date = models.DateTimeField(default=timezone.now)
    return_date = models.DateTimeField(default=timezone.now() + timedelta(days=7))
    returned = models.BooleanField(default=False)

    def save_emprunt(self, *args, **kwargs):
        # Update the availability of the media
        if not self.returned:
            self.media.available = False
        else:
            self.media.available = True
        self.media.save()

        # Update member's active loans count
        if not self.returned and self.member.active_loans < 3:
            self.member.active_loans += 1
        elif self.returned and self.member.active_loans > 0:
            self.member.active_loans -= 1
        self.member.save()

        super().save(*args, **kwargs)


class Reservation(models.Model):
    jeuDePlateau = models.ForeignKey(JeuDePlateau, on_delete=models.CASCADE)
    member = models.ForeignKey(Membre, on_delete=models.CASCADE)
    reservation_time = models.DateTimeField(default=timezone.now)
    reservation_end = models.DateTimeField(default=timezone.now() + timedelta(hours=2))
    reserved = models.BooleanField(default=True)

    def save_reservation(self, *args, **kwargs):
        # Update the availability of the game
        if self.reserved:
            self.jeuDePlateau.available = False
        else:
            self.jeuDePlateau.available = True
        self.jeuDePlateau.save()

        # Update member's active reservation count
        if self.reserved and self.member.active_reservation < 1:
            self.member.active_reservation += 1
        elif not self.reserved and self.member.active_reservation > 0:
            self.member.active_reservation -= 1
        self.member.save()

        super().save(*args, **kwargs)
