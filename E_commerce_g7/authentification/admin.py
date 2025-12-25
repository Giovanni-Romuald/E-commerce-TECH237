# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils import timezone
from .models import Utilisateur

class UtilisateurAdmin(UserAdmin):
    # Configuration de la liste d'affichage
    list_display = [
        'email', 
        'username', 
        'numero_tel', 
        'privilege_display',
        'etat_compte_display', 
        'date_creation_format',
        'heure_derniere_modification_format'
    ]
    
    list_filter = [
        'privilege', 
        'etatCompte',
        'DateCreation',
    ]
    
    search_fields = [
        'email', 
        'username', 
        'numero_tel',
        'adresse'
    ]
    
    ordering = ['-DateCreation']
    
    # Configuration du formulaire d'édition
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Informations personnelles', {
            'fields': ('username', 'adresse', 'numero_tel')
        }),
        ('Permissions et statut', {
            'fields': (
                'privilege', 
                'etatCompte', 
                'is_active', 
                'is_staff', 
                'is_superuser',
                'groups', 
                'user_permissions'
            )
        }),
        ('Dates importantes', {
            'fields': ('DateCreation', 'derniere_modification', 'heure_derniere_modification')
        }),
    )
    
    readonly_fields = [
        'DateCreation', 
        'derniere_modification', 
        'heure_derniere_modification'
    ]
    
    # Configuration du formulaire d'ajout
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 
                'username', 
                'numero_tel',
                'password1', 
                'password2',
                'privilege',
                'etatCompte'
            ),
        }),
    )
    
    # Méthodes personnalisées pour l'affichage
    def privilege_display(self, obj):
        color = {
            'C': 'green',  # Client
            'AD': 'red',   # Administrateur
        }.get(obj.privilege, 'gray')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_privilege_display()
        )
    privilege_display.short_description = 'Privilège'
    privilege_display.admin_order_field = 'privilege'
    
    def etat_compte_display(self, obj):
        color = {
            'A': 'green',   # Actif
            'D': 'red',     # Désactivé
        }.get(obj.etatCompte, 'gray')
        
        badge_color = {
            'A': '#28a745',   # Vert
            'D': '#dc3545',   # Rouge
        }.get(obj.etatCompte, '#6c757d')
        
        return format_html(
            '''
            <span style="
                color: {color};
                background-color: {bg_color};
                padding: 3px 8px;
                border-radius: 12px;
                font-weight: bold;
                font-size: 12px;
            ">
                {text}
            </span>
            ''',
            color='white',
            bg_color=badge_color,
            text=obj.get_etatCompte_display()
        )
    etat_compte_display.short_description = 'État du compte'
    etat_compte_display.admin_order_field = 'etatCompte'
    
    def date_creation_format(self, obj):
        if obj.DateCreation:
            return obj.DateCreation.strftime('%d/%m/%Y %H:%M')
        return "N/A"
    date_creation_format.short_description = 'Date de création'
    date_creation_format.admin_order_field = 'DateCreation'
    
    def heure_derniere_modification_format(self, obj):
        if obj.heure_derniere_modification:
            return obj.heure_derniere_modification.strftime('%d/%m/%Y %H:%M')
        return "Jamais modifié"
    heure_derniere_modification_format.short_description = 'Dernière modification'
    heure_derniere_modification_format.admin_order_field = 'heure_derniere_modification'
    
    # Méthodes d'action personnalisées
    actions = ['activer_comptes', 'desactiver_comptes', 'promouvoir_administrateurs', 'retrograder_clients']
    
    def activer_comptes(self, request, queryset):
        updated = queryset.update(etatCompte='A')
        self.message_user(request, f"{updated} compte(s) activé(s) avec succès.")
    activer_comptes.short_description = "Activer les comptes sélectionnés"
    
    def desactiver_comptes(self, request, queryset):
        updated = queryset.update(etatCompte='D')
        self.message_user(request, f"{updated} compte(s) désactivé(s) avec succès.")
    desactiver_comptes.short_description = "Désactiver les comptes sélectionnés"
    
    def promouvoir_administrateurs(self, request, queryset):
        updated = queryset.update(privilege='AD')
        self.message_user(request, f"{updated} utilisateur(s) promu(s) administrateur.")
    promouvoir_administrateurs.short_description = "Promouvoir en administrateur"
    
    def retrograder_clients(self, request, queryset):
        updated = queryset.update(privilege='C')
        self.message_user(request, f"{updated} administrateur(s) rétrogradé(s) client.")
    retrograder_clients.short_description = "Rétrograder en client"
    
    # Surcharge de la méthode save pour mettre à jour les champs de modification
    def save_model(self, request, obj, form, change):
        if change:
            obj.derniere_modification = request.user.email
            obj.heure_derniere_modification = timezone.now()
        super().save_model(request, obj, form, change)
    
    # Configuration des permissions d'affichage
    def has_delete_permission(self, request, obj=None):
        # Empêcher la suppression des superutilisateurs par des non-superutilisateurs
        if obj and obj.is_superuser:
            return request.user.is_superuser
        return super().has_delete_permission(request, obj)
    
    # Filtrage personnalisé selon les privilèges
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Les non-superutilisateurs ne voient que leur propre compte
        if not request.user.is_superuser:
            return qs.filter(id=request.user.id)
        return qs

# Enregistrement du modèle avec l'admin personnalisé
admin.site.register(Utilisateur, UtilisateurAdmin)