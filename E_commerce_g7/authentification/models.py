from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import datetime

class Utilisateur(AbstractUser):
    # Les choix pour les champs nécessitant un choix
    ETAT_COMPTE_CHOICES = [
        ('A', 'Active'),
        ('D', 'Desactive'),
    ]

    PRIVILEGE_UTILISATEUR_CHOICES = [
        ('C', 'Client'),
        ('AD', 'Administrateur')
    ]

    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    adresse = models.CharField(max_length=100, blank=True, null=True)
    numero_tel = models.CharField(max_length=20)  # Changé de TextField à CharField
    etatCompte = models.CharField(max_length=100, choices=ETAT_COMPTE_CHOICES, default='A')
    DateCreation = models.DateTimeField(auto_now_add=True)  # Utilisez auto_now_add
    privilege = models.CharField(max_length=100, choices=PRIVILEGE_UTILISATEUR_CHOICES, default='C')
    derniere_modification = models.CharField(max_length=100, null=True, blank=True)
    heure_derniere_modification = models.DateTimeField(null=True, blank=True)

    # Configurons les constantes pour nos utilisateurs
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "numero_tel"]

    def __str__(self):
        return f"{self.email}"