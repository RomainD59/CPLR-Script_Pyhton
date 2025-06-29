# ============================================
# Commentaires générés par Copilot
# Script de surveillance de services web
# ============================================

import csv
import requests
import argparse
import os
import json
import ssl
import socket
from datetime import datetime, timedelta

# Fichier de configuration contenant les services à surveiller
CONFIG_FILE = 'web_services.csv'

# Crée le fichier de configuration s'il n'existe pas
def create_config_file():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Name', 'URL', 'Webhook', 'SSL_Expiry_Threshold'])

# Lit le fichier de configuration et retourne la liste des services
def read_config_file():
    with open(CONFIG_FILE, 'r') as file:
        reader = csv.DictReader(file)
        return list(reader)

# Ajoute un nouveau site au fichier de configuration
def add_site(name, url, webhook="", ssl_expiry_threshold=30):
    with open(CONFIG_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name, url, webhook, ssl_expiry_threshold])
    print(f"Ajouté : {name} -> {url} (Webhook: {webhook if webhook else 'Aucun'}, SSL Expiry Threshold: {ssl_expiry_threshold} jours)")

# Supprime un site du fichier de configuration
def remove_site(name):
    sites = read_config_file()
    with open(CONFIG_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'URL', 'Webhook', 'SSL_Expiry_Threshold'])
        for site in sites:
            if site['Name'] != name:
                writer.writerow([site['Name'], site['URL'], site.get('Webhook', ''), site.get('SSL_Expiry_Threshold', 30)])
    print(f"Supprimé : {name}")

# Affiche la liste des sites configurés
def list_sites():
    sites = read_config_file()
    if not sites:
        print("Aucun site configuré.")
    for site in sites:
        print(f"{site['Name']} -> {site['URL']} (Webhook: {site.get('Webhook', 'Aucun')}, SSL Expiry Threshold: {site.get('SSL_Expiry_Threshold', 30)} jours)")

# ============================================
# Webhook Discord
# Aide de l'IA
# ============================================

# Envoie une notification à un webhook Discord
def send_discord_notification(webhook_url, message):
    try:
        requests.post(webhook_url, json={"content": message})
    except Exception as e:
        print(f"Erreur lors de l'envoi Discord : {e}")

# Vérifie la date d'expiration du certificat SSL
def check_ssl_expiry(hostname, threshold_days):
    context = ssl.create_default_context()
    with socket.create_connection((hostname, 443)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()
            expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            days_to_expiry = (expiry_date - datetime.utcnow()).days
            if days_to_expiry < threshold_days:
                return True, expiry_date
            else:
                return False, expiry_date

# ============================================
# Logs et Status.json
# Aide de l'IA
# ============================================

# Vérifie l'état des sites et enregistre les résultats
def check_sites(discord_enabled=False):
    sites = read_config_file()

    log_dir = "log"
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H_%M_%S')
    log_file = os.path.join(log_dir, f"log_{timestamp}.csv")
    file_exists = os.path.isfile(log_file)

    status_file = "status.json"
    if os.path.exists(status_file):
        with open(status_file, 'r') as f:
            previous_status = json.load(f)
    else:
        previous_status = {}

    current_status = {}

    with open(log_file, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Date/Heure", "Nom", "URL", "Code HTTP", "Erreur", "Statut", "SSL Expiry Date"])

        for site in sites:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                response = requests.get(site['URL'], timeout=5)
                status_code = response.status_code
                status = "UP" if 200 <= status_code < 300 else "DOWN"
                error = ""
                print(f"[OK] {site['Name']} est en ligne.")
            except Exception as e:
                status_code = "N/A"
                status = "DOWN"
                error = str(e)
                print(f"[HORS LIGNE] {site['Name']} : {e}")

            ssl_warning = False
            ssl_expiry_date = ""
            if status == "UP":
                hostname = site['URL'].split("//")[-1].split("/")[0]
                threshold_days = int(site.get('SSL_Expiry_Threshold', 30))
                ssl_warning, ssl_expiry_date = check_ssl_expiry(hostname, threshold_days)
                if ssl_warning:
                    status = "WARNING_SSL"
                    print(f"[WARNING_SSL] {site['Name']} : Le certificat SSL expire bientôt.")

            writer.writerow([now, site['Name'], site['URL'], status_code, error, status, ssl_expiry_date])
            current_status[site['Name']] = status

            if discord_enabled and 'Webhook' in site and site['Webhook']:
                previous = previous_status.get(site['Name'])
                if previous != status:
                    emoji = "🟢" if status == "UP" else "🔴" if status == "DOWN" else "⚠️"
                    message = f"{emoji} **{site['Name']}** est **{status}** (était {previous})\n{site['URL']}"
                    if status == "WARNING_SSL":
                        message += f"\nLe certificat SSL expire le {ssl_expiry_date}."
                    send_discord_notification(site['Webhook'], message)

    with open(status_file, 'w') as f:
        json.dump(current_status, f, indent=2)

    print(f"\n✅ Fichier de log généré : {log_file}")

# Exporte l'historique des vérifications pour un ou plusieurs sites
def export_site_history(site_names):
    log_dir = "log"
    export_dir = "export"
    os.makedirs(export_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H_%M_%S')
    export_file = os.path.join(export_dir, f"export_{timestamp}.csv")

    with open(export_file, 'w', newline='', encoding='utf-8') as export:
        writer = csv.writer(export)
        writer.writerow(["Date/Heure", "Nom", "URL", "Code HTTP", "Erreur", "Statut", "SSL Expiry Date"])

        for log_file in os.listdir(log_dir):
            if log_file.endswith(".csv"):
                with open(os.path.join(log_dir, log_file), 'r', encoding='utf-8') as log:
                    reader = csv.DictReader(log)
                    for row in reader:
                        if row['Nom'] in site_names:
                            writer.writerow([row["Date/Heure"], row["Nom"], row["URL"], row["Code HTTP"], row["Erreur"], row["Statut"], row["SSL Expiry Date"]])

    print(f"\n✅ Rapport exporté : {export_file}")

# Point d'entrée principal du script
def main():
    parser = argparse.ArgumentParser(description="Surveillance de services web")
    parser.add_argument('--add', nargs='+', help="Ajouter un site (optionnel : webhook, SSL expiry threshold)")
    parser.add_argument('--remove', metavar='NOM', help="Supprimer un site")
    parser.add_argument('--list', action='store_true', help="Lister les sites")
    parser.add_argument('--check', action='store_true', help="Vérifier les sites")
    parser.add_argument('--discord', action='store_true', help="Envoyer les changements d'état sur Discord")
    parser.add_argument('--export', nargs='+', metavar='NOM', help="Exporter l'historique des vérifications pour un ou plusieurs sites")

    args = parser.parse_args()
    create_config_file()

    if args.add:
        if len(args.add) < 2:
            print("Erreur : vous devez fournir au moins un nom et une URL.")
        else:
            name = args.add[0]
            url = args.add[1]
            webhook = args.add[2] if len(args.add) > 2 else ""
            ssl_expiry_threshold = args.add[3] if len(args.add) > 3 else 30
            add_site(name, url, webhook, ssl_expiry_threshold)
    elif args.remove:
        remove_site(args.remove)
    elif args.list:
        list_sites()
    elif args.check:
        check_sites(discord_enabled=args.discord)
    elif args.export:
        export_site_history(args.export)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
