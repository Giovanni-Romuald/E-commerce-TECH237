from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .models import Utilisateur
from django.contrib.auth.hashers import make_password
from datetime import datetime
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Utilisateur

# Create your views here.

def pageLoginUser(request):
    """
    Version simplifiée de la fonction de connexion
    """
    print(f"=== DEBUT pageLoginUser ===")
    print(f"Méthode de requête: {request.method}")
    
    # Si c'est une requête POST (formulaire soumis)
    if request.method == 'POST':
        print("=== TRAITEMENT POST ===")
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember = request.POST.get('remember')  # Case "Se souvenir de moi"
        
        print(f"Email reçu: {email}")
        print(f"Remember me: {remember}")
        
        try:
            # Essayer d'authentifier l'utilisateur
            print("Tentative d'authentification...")
            user = authenticate(request, username=email, password=password)
            print(f"Résultat authenticate: {user}")
            
            if user is not None:
                print("Authentification réussie")
                # Récupérer l'utilisateur
                utilisateur = get_object_or_404(Utilisateur, email=email)
                print(f"Utilisateur trouvé: {utilisateur.email}, privilège: {utilisateur.privilege}")
                
                # Vérifier l'état du compte
                print(f"État du compte: {utilisateur.etatCompte}")
                if utilisateur.etatCompte != "A":
                    print("Compte non actif")
                    messages.error(request, "Compte non actif ou désactivé.")
                    return render(request, "pageAuth/login.html")
                
                # Connecter l'utilisateur
                print("Connexion de l'utilisateur...")
                login(request, utilisateur)
                
                # Sauvegarder quelques infos en session
                request.session["email"] = utilisateur.email
                request.session["privilege"] = utilisateur.privilege
                print(f"Session créée - email: {utilisateur.email}, privilege: {utilisateur.privilege}")
                
                # Gestion "Se souvenir de moi"
                if not remember:
                    print("Session sans 'Se souvenir de moi'")
                    request.session.set_expiry(0)  # Session navigateur
                else:
                    print("Session avec 'Se souvenir de moi' (2 semaines)")
                    request.session.set_expiry(1209600)  # 2 semaines
                
                # Marquer comme en ligne
                print("Sauvegarde de l'utilisateur...")
                utilisateur.save()
                
                print(f"Redirection selon privilège: {utilisateur.privilege}")
                # Redirection selon le privilège
                if utilisateur.privilege == "C":
                    print("Redirection vers pageAccueilSite")
                    messages.success(request, "Connexion réussie ! Bienvenue " + utilisateur.email)
                    return redirect("pageAccueilSite")
                elif utilisateur.privilege == "AD":
                    print("Redirection vers pageSuperAdmin")
                    return HttpResponse("pageSuperAdmin")
                else:
                    print(f"Redirection vers accueil (privilège: {utilisateur.privilege})")
                    return redirect("accueil")  # Page par défaut
                
            else:
                print("Échec d'authentification - utilisateur None")
                messages.error(request, "Email ou mot de passe incorrect.")
                return render(request, "pageAuth/login.html")
                
        except Exception as e:
            print(f"=== ERREUR EXCEPTION ===")
            print(f"Type d'erreur: {type(e).__name__}")
            print(f"Message d'erreur: {e}")
            print(f"Traceback complet:", exc_info=True)
            messages.error(request, "Une erreur est survenue.")
            return render(request, "pageAuth/login.html")
    
    # Si GET ou autre méthode, afficher le formulaire
    print("Affichage du formulaire de login (méthode GET)")
    return render(request, "pageAuth/login.html")


def pageInscription(request):
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        numero_tel = request.POST.get('numero')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        terms = request.POST.get('terms')
        
        # Validation
        errors = []
        
        # Vérifier si l'email existe déjà
        if Utilisateur.objects.filter(email=email).exists():
            errors.append("Cette adresse email est déjà utilisée.")

        if Utilisateur.objects.filter(numero_tel = numero_tel).exists():
            errors.append("ce numero de telephone est déjà utilisée")
        
        # Vérifier la correspondance des mots de passe
        if password != confirm_password:
            errors.append("Les mots de passe ne correspondent pas.")
        
        # Vérifier la longueur du mot de passe
        if len(password) < 8:
            errors.append("Le mot de passe doit contenir au moins 8 caractères.")
        
        # Vérifier les conditions
        if not terms:
            errors.append("Vous devez accepter les conditions d'utilisation.")
        
        # Si pas d'erreurs, créer l'utilisateur
        if not errors:
            try:
                # Créer le nom d'utilisateur combiné
                username = f"{prenom} {nom}"
                
                # Créer l'utilisateur
                utilisateur = Utilisateur.objects.create(
                    username=username,
                    email=email,
                    numero_tel=numero_tel,
                    etatCompte='A',  # Compte actif par défaut
                    privilege='C',   # Client par défaut
                    DateCreation=datetime.now()
                )
                
                # Définir le mot de passe (hashé automatiquement par Django)
                utilisateur.set_password(password)
                utilisateur.save()
                
                # Optionnel : connecter automatiquement l'utilisateur
                # login(request, utilisateur)
                
                messages.success(request, "Inscription réussie ! Vous pouvez maintenant vous connecter.")
                return redirect('loginUser')  # Remplacez par votre vue de connexion
                
            except Exception as e:
                errors.append(f"Une erreur est survenue : {str(e)}")
        
        # S'il y a des erreurs, les afficher
        for error in errors:
            messages.error(request, error)
        
        # Retourner les données pour pré-remplir le formulaire
        context = {
            'nom': nom,
            'prenom': prenom,
            'email': email,
            'numero_tel': numero_tel
        }
        return render(request, 'pageAuth/inscription.html', context)
    
    # GET request : afficher le formulaire vide
    return render(request, 'pageAuth/inscription.html')