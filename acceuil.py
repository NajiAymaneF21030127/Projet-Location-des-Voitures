import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
import re
import mysql.connector

# Configuration de la base de données
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'location_voiture',
}

# Validation des champs de saisie d'employer
def validate_fields():
    if not cin_var.get():
        return "CIN est obligatoire."
    if not points_var.get().isdigit() or int(points_var.get()) <= 0:
        return "Points doivent être un entier positif."
    if not nom_var.get():
        return "Nom est obligatoire."
    if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email_var.get()):
        return "Email est incorrect."
    if not prenom_var.get():
        return "Prenom est obligatoire."
    if not adresse_var.get():
        return "Adresse est obligatoire."
    if not re.match(r"^\d{10}$", telephone_var.get()):
        return "Téléphone doit être un nombre à 10 chiffres."
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_emploi_var.get()):
        return "Date d'emploi doit être au format YYYY-MM-DD."
    if not salaire_var.get().replace('.', '', 1).isdigit() or float(salaire_var.get()) <= 0:
        return "Salaire doit être un nombre positif."
    if genre_var.get() not in ["H", "F"]:
        return "Genre doit être 'H' ou 'F'."
    return None

# Ajout d'un employé dans la base de données
def add_employee():
    error_message = validate_fields()
    if error_message:
        messagebox.showerror("Erreur de validation", error_message)
        return

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO employer (CIN, Prenom, Nom, Email , Points , Adresse, Telephone, Date_emploi, Salaire, Genre)
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                       (cin_var.get(), prenom_var.get(), nom_var.get(), email_var.get(), points_var.get(),
                        adresse_var.get(), telephone_var.get(), date_emploi_var.get(), salaire_var.get(), genre_var.get()))
        conn.commit()
        cursor.close()
        conn.close()
        refresh_treeview_employer()
    except mysql.connector.Error as err:
        messagebox.showerror("Erreur de la base de données", str(err))

# Annulation de l'ajout d'un employé (réinitialisation des champs)
def cancel_employee():
    cin_var.set('')
    points_var.set('')
    nom_var.set('')
    email_var.set('')
    prenom_var.set('')
    adresse_var.set('')
    telephone_var.set('')
    date_emploi_var.set('')
    salaire_var.set('')
    genre_var.set('')

# Rafraîchissement de l'affichage des employés dans le treeview
def refresh_treeview_employer():
    for i in tree.get_children():
        tree.delete(i)
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM employer')
        rows = cursor.fetchall()
        for row in rows:
            tree.insert('', tk.END, values=row)
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Erreur de la base de données", str(err))

# Vérification de l'existence d'un client par son CIN accueil
def check_client_cin(cin):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM client WHERE CIN = %s', (cin,))
        result = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return result > 0
    except mysql.connector.Error as err:
        messagebox.showerror("Erreur de la base de données", str(err))
        return False

# Fonction de réservation
def reserve():
    cin = cin_entry.get()
    nom_conducteur1 = nom_conducteur1_entry.get()
    nom_conducteur2 = nom_conducteur2_entry.get()
    duree = duree_entry.get()
    nom = voiture_selection.get()

    if not cin:
        messagebox.showerror("Erreur", "Le champ CIN est obligatoire")
        return

    if not nom_conducteur1 or not nom_conducteur2 or not duree or not nom:
        messagebox.showerror("Erreur", "Tous les champs sont obligatoires")
        return

    try:
        duree = int(duree)
    except ValueError:
        messagebox.showerror("Erreur", "La durée doit être un nombre entier")
        return

    if check_client_cin(cin):
        messagebox.showinfo("Succès", "Réservation réussie, téléchargez le reçu")
        download_button.configure(state=ctk.NORMAL)
    else:
        messagebox.showwarning("Client non trouvé", "Le CIN n'existe pas. Redirection vers l'ajout de client.")
        show_content("Clients")

# Téléchargement du reçu de réservation
def download_receipt(cin, nom_conducteur1, nom_conducteur2, duree, nom):
    # Connexion à la base de données MySQL
    conn = mysql.connector.connect(
        host='localhost',  # Ex. 'localhost'
        user='root',  # Ex. 'root'
        password='',  # Ex. 'password'
        database='location_voiture'  # Ex. 'location_voitures'
    )
    cursor = conn.cursor()

    # Récupération du cout de la voiture par nom
    cursor.execute("SELECT cout FROM voiture WHERE nom = %s", (nom,))
    voiture = cursor.fetchone()

    if voiture:
        cout_voiture = voiture[0]
        total = duree * cout_voiture
    else:
        messagebox.showerror("Erreur", "Voiture non trouvée dans la base de données")
        cursor.close()
        conn.close()
        return

    # Fermeture de la connexion à la base de données
    cursor.close()
    conn.close()

    # Nom du fichier
    filename = f"receipt_{cin}.txt"

    # Création du contenu du fichier de reçu
    contenu = (
        f"Réservation pour le client avec CIN: {cin}\n"
        f"Nom du conducteur 1: {nom_conducteur1}\n"
        f"Nom du conducteur 2: {nom_conducteur2}\n"
        f"Durée: {duree} jours\n"
        f"Coût de la voiture par jour: {cout_voiture} dirhams\n"
        f"Total: {total} dirhams\n"
    )

    # Enregistrement du fichier de reçu
    with open(filename, 'w') as f:
        f.write(contenu)

    # Affichage d'un message de confirmation
    messagebox.showinfo("Téléchargement", f"Reçu enregistré sous {filename}")

def show_content(texte):
    for widget in cadre_contenu.winfo_children():
        widget.destroy()

    if texte == "Accueil":
        afficher_accueil()
    elif texte == "Clients":
        manage_clients(cadre_contenu, large_font, button_font)
    elif texte == "Employer":
        manage_employer(cadre_contenu, large_font, button_font) 
    elif texte == "Voitures":
        add_car_form(cadre_contenu, large_font, button_font, cadre_principal)
    elif texte == "Rapport":
        afficher_rapport()

# Fonction pour afficher la page d'accueil
def afficher_accueil():
    global cin_entry, duree_entry, nom_conducteur1_entry, nom_conducteur2_entry, voiture_selection, download_button
    
    champs = ["CIN:", "Durée:", "Nom du conducteur 1:", "Nom du conducteur 2:", "Voiture:"]
    cin_entry = ctk.CTkEntry(cadre_contenu, font=large_font, height=30)
    
    for i, champ in enumerate(champs):
        etiquette = ctk.CTkLabel(cadre_contenu, text=champ, font=large_font, height=30)
        etiquette.place(relx=0.05, rely=0.1 + i*0.15, relwidth=0.4)
        
        if champ == "CIN:":
            cin_entry.place(relx=0.5, rely=0.1 + i*0.15, relwidth=0.45)
            
        elif champ == "Voiture:":
            available_cars = get_available_cars()
            voiture_selection = ctk.CTkComboBox(cadre_contenu, values=available_cars, font=large_font, height=30)
            voiture_selection.place(relx=0.5, rely=0.1 + i*0.15, relwidth=0.45)
            
        else:
            entree = ctk.CTkEntry(cadre_contenu, font=large_font, height=30)
            entree.place(relx=0.5, rely=0.1 + i*0.15, relwidth=0.45)
            if champ == "Durée:":
                duree_entry = entree
            elif champ == "Nom du conducteur 1:":
                nom_conducteur1_entry = entree
            elif champ == "Nom du conducteur 2:":
                nom_conducteur2_entry = entree

    bouton_reserver = ctk.CTkButton(cadre_contenu, text="Réserver", font=button_font, height=40, command=reserve)
    bouton_reserver.place(relx=0.05, rely=0.85, relwidth=0.4)

    download_button = ctk.CTkButton(cadre_contenu, text="Télécharger", font=button_font, height=40, command=lambda: download_receipt(cin_entry.get(), nom_conducteur1_entry.get(), nom_conducteur2_entry.get(), int(duree_entry.get()), voiture_selection.get()), state=ctk.DISABLED)
    download_button.place(relx=0.55, rely=0.85, relwidth=0.4)

# Obtention de la liste des voitures disponibles
def get_available_cars():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT nom FROM voiture WHERE etat = 'disponible'")
        rows = cursor.fetchall()
        available_cars = [row[0] for row in rows]
        cursor.close()
        conn.close()
        return available_cars
    except mysql.connector.Error as err:
        messagebox.showerror("Erreur de la base de données", str(err))
        return []

# Formulaire d'ajout de voiture
def add_car_form(cadre_contenu, large_font, button_font, cadre_principal):
    global matricule_var, nom_var, couleur_var, puissance_var, carburant_var, modele_var, annee_modele_var, cout_var, etat_var, tree, combo

    matricule_var = tk.StringVar()
    nom_var = tk.StringVar()
    couleur_var = tk.StringVar()
    puissance_var = tk.StringVar()
    carburant_var = tk.StringVar()
    modele_var = tk.StringVar()
    annee_modele_var = tk.StringVar()
    cout_var = tk.StringVar()
    etat_var = tk.StringVar()

    champs = [
        ("Matricule:", matricule_var, "Puissance:", puissance_var),
        ("Nom:", nom_var, "Année du modèle:", annee_modele_var),
        ("Couleur:", couleur_var, "Carburant:", carburant_var),
        ("Modèle:", modele_var, "Coût par jour:", cout_var),
        ("État:", etat_var, "", None)
    ]
    for i, (champ_gauche, var_gauche, champ_droite, var_droite) in enumerate(champs):
        etiquette_gauche = ctk.CTkLabel(cadre_contenu, text=champ_gauche, font=large_font, height=30)
        etiquette_gauche.place(relx=0.05, rely=0.05 + i*0.12, relwidth=0.2)
        entree_gauche = ctk.CTkEntry(cadre_contenu, textvariable=var_gauche, font=large_font, height=30)
        entree_gauche.place(relx=0.25, rely=0.05 + i*0.12, relwidth=0.2)

        if champ_droite and var_droite is not None:
            etiquette_droite = ctk.CTkLabel(cadre_contenu, text=champ_droite, font=large_font, height=30)
            etiquette_droite.place(relx=0.55, rely=0.05 + i*0.12, relwidth=0.2)

            if champ_droite == "Carburant:":
                carburants = ["Essence", "Diesel", "Électrique", "Hybride"]
                carburant_var.set(carburants[0])
                combo = ctk.CTkComboBox(cadre_contenu, values=carburants, font=large_font, height=30)
                combo.place(relx=0.75, rely=0.05 + i*0.12, relwidth=0.2)
                combo.bind("<<ComboboxSelected>>", lambda event, var=carburant_var: var.set(combo.get()))

            else:
                entree_droite = ctk.CTkEntry(cadre_contenu, textvariable=var_droite, font=large_font, height=30)
                entree_droite.place(relx=0.75, rely=0.05 + i*0.12, relwidth=0.2)

    bouton_ajouter = ctk.CTkButton(cadre_contenu, text="Ajouter", font=button_font, height=40, command=add_voiture)
    bouton_ajouter.place(relx=0.55, rely=0.50, relwidth=0.15)

    bouton_annuler = ctk.CTkButton(cadre_contenu, text="Annuler", font=button_font, height=40, command=cancel_voiture)
    bouton_annuler.place(relx=0.75, rely=0.50, relwidth=0.15)

    table_frame = ctk.CTkFrame(cadre_contenu)
    table_frame.place(relx=0, rely=0.60, relwidth=1, relheight=0.30)

    columns = ["matricule", "nom", "couleur", "puissance", "carburant", "modele", "anneem", "cout", "etat"]
    tree = ttk.Treeview(table_frame, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=80, anchor='center')
    tree.pack(fill=tk.BOTH, expand=True)

    refresh_treeview_voiture()

# Ajout d'une voiture dans la base de données
def add_voiture():
    if not matricule_var.get() or not nom_var.get() or not couleur_var.get() or not puissance_var.get() or not combo.get() or not modele_var.get() or not annee_modele_var.get() or not cout_var.get() or not etat_var.get():
        messagebox.showerror("Erreur", "Tous les champs sont obligatoires")
        return

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO voiture (matricule, nom, couleur, puissance, carburant, modele, anneem, cout, etat)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                    (matricule_var.get(), nom_var.get(), couleur_var.get(), puissance_var.get(), combo.get(),
                        modele_var.get(), annee_modele_var.get(), cout_var.get(), etat_var.get()))
        conn.commit()
        cursor.close()
        conn.close()
        refresh_treeview_voiture()
    except mysql.connector.Error as err:
        messagebox.showerror("Erreur de la base de données", str(err))

# Annulation de l'ajout d'une voiture (réinitialisation des champs)
def cancel_voiture():
    matricule_var.set('')
    nom_var.set('')
    couleur_var.set('')
    puissance_var.set('')
    carburant_var.set('')
    modele_var.set('')
    annee_modele_var.set('')
    cout_var.set('')
    etat_var.set('')

# Rafraîchissement de l'affichage des voitures dans le treeview
def refresh_treeview_voiture():
    for i in tree.get_children():
        tree.delete(i)
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM voiture')
        rows = cursor.fetchall()
        for row in rows:
            tree.insert('', tk.END, values=row)
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Erreur de la base de données", str(err))

# Gestion des clients
def manage_clients(cadre_contenu, large_font, button_font):
    global cin_var, nom_var, prenom_var, genre_var, permit_var, email_var, adresse_var, telephone_var, tree

    cin_var = tk.StringVar()
    nom_var = tk.StringVar()
    prenom_var = tk.StringVar()
    genre_var = tk.StringVar()
    permit_var = tk.StringVar()
    email_var = tk.StringVar()
    adresse_var = tk.StringVar()
    telephone_var = tk.StringVar()

    champs = [
        ("CIN:", cin_var, "Permit:", permit_var),
        ("Nom:", nom_var, "Email:", email_var),
        ("Prenom:", prenom_var, "Adresse:", adresse_var),
        ("Telephone:", telephone_var, "", None),
    ]

    for i, (champ_gauche, var_gauche, champ_droite, var_droite) in enumerate(champs):
        etiquette_gauche = ctk.CTkLabel(cadre_contenu, text=champ_gauche, font=large_font, height=30)
        etiquette_gauche.place(relx=0.05, rely=0.05 + i*0.12, relwidth=0.2)
        entree_gauche = ctk.CTkEntry(cadre_contenu, textvariable=var_gauche, font=large_font, height=30)
        entree_gauche.place(relx=0.25, rely=0.05 + i*0.12, relwidth=0.2)

        if champ_droite and var_droite is not None:
            etiquette_droite = ctk.CTkLabel(cadre_contenu, text=champ_droite, font=large_font, height=30)
            etiquette_droite.place(relx=0.55, rely=0.05 + i*0.12, relwidth=0.2)
            entree_droite = ctk.CTkEntry(cadre_contenu, textvariable=var_droite, font=large_font, height=30)
            entree_droite.place(relx=0.75, rely=0.05 + i*0.12, relwidth=0.2)

    etiquette_genre = ctk.CTkLabel(cadre_contenu, text="Genre:", font=large_font, height=30)
    etiquette_genre.place(relx=0.05, rely=0.65, relwidth=0.2)
    bouton_genre_h = ctk.CTkRadioButton(cadre_contenu, text="H", variable=genre_var, value="H", font=large_font, height=30, width=30)
    bouton_genre_h.place(relx=0.25, rely=0.65, relwidth=0.05)
    bouton_genre_f = ctk.CTkRadioButton(cadre_contenu, text="F", variable=genre_var, value="F", font=large_font, height=30, width=30)
    bouton_genre_f.place(relx=0.35, rely=0.65, relwidth=0.05)

    bouton_ajouter = ctk.CTkButton(cadre_contenu, text="Ajouter", font=button_font, height=40, command=add_client)
    bouton_ajouter.place(relx=0.60, rely=0.65, relwidth=0.15)

    bouton_annuler = ctk.CTkButton(cadre_contenu, text="Annuler", font=button_font, height=40, command=cancel_client)
    bouton_annuler.place(relx=0.80, rely=0.65, relwidth=0.15)

    table_frame = ctk.CTkFrame(cadre_contenu)
    table_frame.place(relx=0, rely=0.75, relwidth=1, relheight=0.30)

    columns = ["CIN", "nom", "prenom", "genre", "permit", "email", "adresse", "telephone"]
    tree = ttk.Treeview(table_frame, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=80, anchor='center')
    tree.pack(fill=tk.BOTH, expand=True)

    refresh_treeview_client()

# Validation de l'email
def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

# Validation du numéro de téléphone
def is_valid_phone(phone):
    pattern = r"^\d{10}$"
    return re.match(pattern, phone) is not None

# Ajout d'un client dans la base de données
def add_client():
    if not cin_var.get() or not nom_var.get() or not prenom_var.get() or not genre_var.get() or not permit_var.get() or not email_var.get() or not adresse_var.get() or not telephone_var.get():
        messagebox.showerror("Erreur", "Tous les champs sont obligatoires")
        return

    if not is_valid_email(email_var.get()):
        messagebox.showerror("Erreur", "Le format de l'email est incorrect")
        return

    if not is_valid_phone(telephone_var.get()):
        messagebox.showerror("Erreur", "Le format du téléphone est incorrect (10 chiffres requis)")
        return

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO client (CIN, nom, prenom, genre, permit, email, adresse, telephone)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                    (cin_var.get(), nom_var.get(), prenom_var.get(), genre_var.get(), permit_var.get(),
                        email_var.get(), adresse_var.get(), telephone_var.get()))
        conn.commit()
        cursor.close()
        conn.close()
        refresh_treeview_client()
    except mysql.connector.Error as err:
        messagebox.showerror("Erreur de la base de données", str(err))

# Annulation de l'ajout d'un client (réinitialisation des champs)
def cancel_client():
    cin_var.set('')
    nom_var.set('')
    prenom_var.set('')
    genre_var.set('')
    permit_var.set('')
    email_var.set('')
    adresse_var.set('')
    telephone_var.set('')

# Rafraîchissement de l'affichage des clients dans le treeview
def refresh_treeview_client():
    for i in tree.get_children():
        tree.delete(i)
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM client')
        rows = cursor.fetchall()
        for row in rows:
            tree.insert('', tk.END, values=row)
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Erreur de la base de données", str(err))

# Gestion des employés
def manage_employer(cadre_contenu, large_font, button_font):
    global cin_var, nom_var, points_var, email_var, prenom_var, adresse_var, telephone_var, date_emploi_var, salaire_var, genre_var, tree

    cin_var = tk.StringVar()
    points_var = tk.StringVar()
    nom_var = tk.StringVar()
    email_var = tk.StringVar()
    prenom_var = tk.StringVar()
    adresse_var = tk.StringVar()
    telephone_var = tk.StringVar()
    date_emploi_var = tk.StringVar()
    salaire_var = tk.StringVar()
    genre_var = tk.StringVar()

    champs = [
        ("CIN:", cin_var, "Points:", points_var),
        ("Nom:", nom_var, "Email:", email_var),
        ("Prenom:", prenom_var, "Adresse:", adresse_var),
        ("Date d'emploi:", date_emploi_var, "Telephone:", telephone_var),
        ("Salaire:", salaire_var, "Genre:", genre_var)
    ]
    genres = [("H", "H"), ("F", "F")]

    for i, (champ_gauche, var_gauche, champ_droite, var_droite) in enumerate(champs):
        etiquette_gauche = ctk.CTkLabel(cadre_contenu, text=champ_gauche, font=large_font, height=30)
        etiquette_gauche.place(relx=0.05, rely=0.05 + i*0.12, relwidth=0.2)
        entree_gauche = ctk.CTkEntry(cadre_contenu, textvariable=var_gauche, font=large_font, height=30)
        entree_gauche.place(relx=0.25, rely=0.05 + i*0.12, relwidth=0.2)

        etiquette_droite = ctk.CTkLabel(cadre_contenu, text=champ_droite, font=large_font, height=30)
        etiquette_droite.place(relx=0.55, rely=0.05 + i*0.12, relwidth=0.2)
        if champ_droite == "Genre:":
            for j, (genre_text, genre_value) in enumerate(genres):
                bouton_genre = ctk.CTkRadioButton(cadre_contenu, text=genre_text, variable=genre_var, value=genre_value, font=large_font, height=30, width=30)
                bouton_genre.place(relx=0.75 + j*0.1, rely=0.05 + i*0.12, relwidth=0.05)
        else:
            entree_droite = ctk.CTkEntry(cadre_contenu, textvariable=var_droite, font=large_font, height=30)
            entree_droite.place(relx=0.75, rely=0.05 + i*0.12, relwidth=0.2)

    bouton_ajouter = ctk.CTkButton(cadre_contenu, text="Ajouter", font=button_font, height=40, command=add_employee)
    bouton_ajouter.place(relx=0.55, rely=0.65, relwidth=0.15)

    bouton_annuler = ctk.CTkButton(cadre_contenu, text="Annuler", font=button_font, height=40, command=cancel_employee)
    bouton_annuler.place(relx=0.75, rely=0.65, relwidth=0.15)

    table_frame = ctk.CTkFrame(cadre_contenu)
    table_frame.place(relx=0, rely=0.75, relwidth=1, relheight=0.3)

    columns = ["cin", "nom", "prenom", "points", "genre", "telephone", "email", "date d'emploi", "salaire", "adresse"]
    tree = ttk.Treeview(table_frame, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=80, anchor='center')
    tree.pack(fill=tk.BOTH, expand=True)

    refresh_treeview_employer()

# Fonction pour afficher la section rapport
import mysql.connector
from datetime import datetime
import customtkinter as ctk
from tkinter import ttk

import mysql.connector
from datetime import datetime
import customtkinter as ctk
from tkinter import ttk
from decimal import Decimal
import os

def calculer_total_vente(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT SUM(cout) FROM voiture
        WHERE MONTH(NOW()) = MONTH(NOW())
    """)
    return float(cur.fetchone()[0] or 0)

def calculer_total_tax(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT (50 * (SELECT COUNT(*) FROM voiture WHERE etat='disponible')) +
               (70 * (SELECT COUNT(*) FROM voiture WHERE etat='maintenance'))
    """)
    return float(cur.fetchone()[0] or 0)

def calculer_total_salaire(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT SUM(Salaire) FROM employer
    """)
    return float(cur.fetchone()[0] or 0)

def telecharger_rapport(mois, total_vente, total_salaire, total_tax, total_profits):
    # Nom du fichier
    fichier_nom = f"rapport_{mois}.txt"
    
    # Contenu du fichier
    contenu = (
        f"Mois: {mois}\n"
        f"Total vente: {total_vente}\n"
        f"Total salaire: {total_salaire}\n"
        f"Total tax: {total_tax}\n"
        f"Total profits: {total_profits}\n"
    )
    
    # Écrire le contenu dans le fichier
    with open(fichier_nom, 'w') as fichier:
        fichier.write(contenu)
    
    print(f"Le rapport a été téléchargé sous le nom {fichier_nom}")
    messagebox.showinfo("","rapport a été téléchargé ")
def afficher_rapport():
    table_frame = ctk.CTkFrame(cadre_contenu)
    table_frame.place(relx=0, rely=0, relwidth=0.95, relheight=0.8)

    columns = ["Mois", "Total vente", "Total salaire", "Total tax", "Total profits"]
    tree = ttk.Treeview(table_frame, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150, anchor='center')
    tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

    # Connexion à la base de données
    conn = mysql.connector.connect(
        host='localhost',  # Remplacez par le nom ou l'adresse IP de votre serveur MySQL
        user='root',       # Remplacez par votre nom d'utilisateur MySQL
        password='',  # Remplacez par votre mot de passe MySQL
        database='location_voiture'  # Remplacez par le nom de votre base de données
    )

    total_vente = calculer_total_vente(conn)
    total_salaire = calculer_total_salaire(conn)
    total_tax = calculer_total_tax(conn)
    total_profits = total_vente - (total_tax + total_salaire)
    mois_actuel = datetime.now().strftime('%B')

    tree.insert('', 'end', values=(mois_actuel, total_vente, total_salaire, total_tax, total_profits))

    conn.close()

    # Fonction pour télécharger le rapport
    def bouton_telecharger_action():
        telecharger_rapport(mois_actuel, total_vente, total_salaire, total_tax, total_profits)
    
    bouton_telecharger = ctk.CTkButton(cadre_contenu, text="Télécharger", font=button_font, height=40, command=bouton_telecharger_action)
    bouton_telecharger.place(relx=0.80, rely=0.82, relwidth=0.15)

    etiquette_date_heure = ctk.CTkLabel(cadre_contenu, text="Date et heure actuelle", font=large_font)
    etiquette_date_heure.place(relx=0.95, rely=0.95, anchor='se')

# Assurez-vous d'avoir les bonnes configurations pour ctk, ttk, et les widgets de votre interface graphique.

# Fonction principale
def main():
    global cadre_contenu, cadre_principal, large_font, button_font
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Location de voiture")
    root.geometry("800x600")

    large_font = ("Helvetica", 16)
    button_font = ("Helvetica", 14, "bold")
    header_font = ("Helvetica", 20, "bold")

    cadre_principal = ctk.CTkFrame(root)
    cadre_principal.place(relwidth=1, relheight=1)

    header_frame = ctk.CTkFrame(cadre_principal, height=100)
    header_frame.place(relx=0, rely=0, relwidth=1)

    titre_label = ctk.CTkLabel(header_frame, text="Location de voiture", font=header_font)
    titre_label.place(relx=0.15, rely=0.1, relwidth=0.7)

    cadre_menu = ctk.CTkFrame(cadre_principal, width=200)
    cadre_menu.place(relx=0, rely=0.15, relheight=0.85)

    boutons = ["Accueil", "Clients", "Employer", "Rapport", "Voitures"]
    for i, texte in enumerate(boutons):
        bouton = ctk.CTkButton(cadre_menu, text=texte, font=button_font, height=40, command=lambda texte=texte: show_content(texte))
        bouton.place(relx=0.1, rely=0.05 + i*0.15, relwidth=0.8)

    cadre_contenu = ctk.CTkFrame(cadre_principal)
    cadre_contenu.place(relx=0.25, rely=0.2, relwidth=0.7, relheight=0.75)

    show_content("Accueil")
    
    root.mainloop()

if __name__ == "__main__":
    main()