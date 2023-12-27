import tkinter as tk
from tkinter import font as tkFont
from PIL import Image, ImageTk
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time


def read_config(file_path):
    """Lire le fichier de configuration et retourner les informations."""
    with open(file_path, 'r') as file:
        lines = file.readlines()
        config = {}
        for line in lines:
            key, value = line.strip().split(':')
            config[key] = value
        return config

# Lire les informations de configuration
config = read_config('e9pro.cfg')
username = config.get('username', 'root')
password = config.get('password', 'root')
ip = config.get('ip', '192.168.1.50')

# Fonction pour extraire les données
def extract_data():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ajouter l'option headless

    #username = "root"
    #password = "root"
    #url = f"http://{username}:{password}@192.168.1.50"
    url = f"http://{username}:{password}@{ip}"

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        time.sleep(5)  # Attendre que JavaScript soit chargé
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')

        # Récupérer et retourner les données
        mnr_title = soup.find('h3', {'id': 'mnrTitle'}).get_text().strip() if soup.find('h3', {'id': 'mnrTitle'}) else "Titre du mineur non trouvé"
        real_time_hashrate = 'RealTime: ' + soup.find('span', {'class': 'clr-4682FF num'}).get_text().strip() + " MH/s" if soup.find('span', {'class': 'clr-4682FF num'}) else "Real Time Hashrate non trouvé"
        avg_total_hashrate = 'Avg Total: ' + soup.find('span', {'class': 'clr-1C1C1C num'}).get_text().strip() + " MH/s" if soup.find('span', {'class': 'clr-1C1C1C num'}) else "Average Total Hashrate non trouvé"
        uptime_elements = soup.select('span.clr-1C1C1C i.num')
        uptime = 'Uptime: ' + 'd '.join([elem.get_text() for elem in uptime_elements[:1]]) + 'd ' + 'h '.join([elem.get_text() for elem in uptime_elements[1:2]]) + 'h ' + 'm '.join([elem.get_text() for elem in uptime_elements[2:3]]) + 'm ' + 'sec '.join([elem.get_text() for elem in uptime_elements[3:]]) + 'sec' if uptime_elements and len(uptime_elements) == 4 else "Uptime non trouvé"

        return mnr_title, real_time_hashrate, avg_total_hashrate, uptime

    finally:
        driver.quit()

# Fonction pour mettre à jour les labels
def update_labels():
    data = extract_data()  # Extraire les nouvelles données
    for i, (label, text) in enumerate(zip(labels, data)):
        label.config(text=text)  # Mettre à jour le texte du label
    app.after(60000, update_labels)  # Planifier la prochaine mise à jour

# Créer une application Tkinter
app = tk.Tk()
app.geometry("500x200")
app.resizable(False, False)  # Empêcher le redimensionnement

# Définir le titre de la fenêtre
app.title("E9Pro Monitor by @sulfuroid")

# Définir l'icône de la fenêtre (remplacez 'chemin_vers_icon.ico' par le chemin de votre fichier d'icône)
app.iconbitmap('best.ico')  # Par exemple, 'e9pro_icon.ico'


# Charger l'image de fond
bg_image = Image.open('e9.jpg')  # Assurez-vous que le chemin est correct
bg_photo = ImageTk.PhotoImage(bg_image)

# Créer un label pour l'image de fond
bg_label = tk.Label(app, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Extraire les données initiales
data = extract_data()

# Coordonnées de départ pour le texte
x, y = 250, 50
line_height = 25  # Hauteur de ligne pour positionner le texte suivant

# Couleur de fond pour les labels
bg_color = "#0e4c0c"

# Police en gras pour mnr_title
bold_font = tkFont.Font(weight="bold")

# Créer et positionner les labels
labels = []
for i, text in enumerate(data):
    if i == 0:  # Appliquer la police en gras uniquement pour mnr_title
        label = tk.Label(app, text=text, fg='white', bg=bg_color, anchor='w', font=bold_font)
    else:
        label = tk.Label(app, text=text, fg='white', bg=bg_color, anchor='w')
    label.place(x=x, y=y + i * line_height)
    labels.append(label)

# Planifier la première mise à jour
app.after(60000, update_labels)

app.mainloop()
