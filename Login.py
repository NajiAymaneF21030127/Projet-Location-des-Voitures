import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import mysql.connector
import subprocess
 
# Connexion à la base de données MySQL
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="location_voiture"
)
 
# Créer un objet curseur pour exécuter des requêtes
cursor = db_connection.cursor()
cursor.execute("SELECT username, password FROM `login`")
users = cursor.fetchall()
 
def login():
    username = username_entry.get()
    password = password_entry.get()
 
    if (username, password) in users:
        messagebox.showinfo("Connexion réussie", "Bienvenue, " + username + " !")
        root.destroy()
        subprocess.Popen(['python','acceuil.py'])
        
     
 
    else:
        messagebox.showerror("Échec de la connexion", "Nom d'utilisateur ou mot de passe incorrect")
 
def on_enter(e):
    if username_entry.get() == "Nom d'utilisateur":
        username_entry.delete(0, 'end')
 
def on_leave(e):
    if not username_entry.get():
        username_entry.insert(0, "Nom d'utilisateur")
 
def on_enterp(e):
    if password_entry.get() == "Mot de passe":
        password_entry.delete(0, 'end')
        password_entry.config(show='*')
 
def on_leavep(e):
    if not password_entry.get():
        password_entry.insert(0, "Mot de passe")
        password_entry.config(show='')
 
# Création de la fenêtre principale
root = tk.Tk()
root.title("Connexion")
root.geometry('925x500+300+200')
root.configure(bg="#fff")
root.resizable(False, False)
 
# Cadre pour le côté gauche (logo)
left_frame = tk.Frame(root, width=462, height=500, bg='white')
left_frame.pack(side='left', fill='both', expand=True)
 
# Redimensionner l'image du logo
original_image = Image.open('nono.jpg')
resized_image = original_image.resize((400, 400))
img = ImageTk.PhotoImage(resized_image)
tk.Label(left_frame, image=img, bg='white').pack(expand=True)
 
# Cadre pour le côté droit (formulaire de connexion)
right_frame = tk.Frame(root, width=463, height=500, bg='white')
right_frame.pack(side='right', fill='both', expand=True)
 
heading = tk.Label(right_frame, text='Connexion', fg='#57a1f8', bg='white',
                   font=('Microsoft YaHei UI Light', 23, 'bold'))
heading.place(x=90, y=50)
 
# Étiquette et champ de saisie pour le nom d'utilisateur
label_user = tk.Label(right_frame, text="Nom d'utilisateur", bg='white')
label_user.place(x=30, y=120)
 
username_entry = tk.Entry(right_frame, width=25, fg='black', border=0, bg="white", font=('Microsoft YaHei UI Light', 11))
username_entry.place(x=30, y=150)
username_entry.insert(0, "Nom d'utilisateur")
username_entry.bind('<FocusIn>', on_enter)
username_entry.bind('<FocusOut>', on_leave)
 
tk.Frame(right_frame, width=295, height=2, bg='black').place(x=25, y=177)
 
# Étiquette et champ de saisie pour le mot de passe
label_password = tk.Label(right_frame, text="Mot de passe", bg='white')
label_password.place(x=30, y=200)
 
password_entry = tk.Entry(right_frame, width=25, fg='black', border=0, bg="white", font=('Microsoft YaHei UI Light', 11))
password_entry.place(x=30, y=230)
password_entry.insert(0, "Mot de passe")
password_entry.bind('<FocusIn>', on_enterp)
password_entry.bind('<FocusOut>', on_leavep)
 
tk.Frame(right_frame, width=295, height=2, bg='black').place(x=25, y=257)
 
# Bouton de connexion
tk.Button(right_frame, width=39, pady=7, text='Se connecter', bg='#57a1f8', fg='white', border=0, command=login).place(x=35, y=300)
 
root.mainloop()