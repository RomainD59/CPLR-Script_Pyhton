import csv
import requests
import argparse
import os
import json
from datetime import datetime

CONFIG_FILE = 'web_services.csv'

def create_config_file():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Name', 'URL', 'Webhook'])

def read_config_file():
    with open(CONFIG_FILE, 'r') as file:
        reader = csv.DictReader(file)
        return list(reader)

def add_site(name, url, webhook=""):
    with open(CONFIG_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name, url, webhook])
    print(f"Ajouté : {name} -> {url} (Webhook: {webhook if webhook else 'Aucun'})")

def remove_site(name):
    sites = read_config_file()
    with open(CONFIG_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'URL', 'Webhook'])
        for site in sites:
            if site['Name'] != name:
                writer.writerow([site['Name'], site['URL'], site.get('Webhook', '')])
    print(f"Supprimé : {name}")

def list_sites():
    sites = read_config_file()
    if not sites:
        print("Aucun site configuré.")
    for site in sites:
        print(f"{site['Name']} -> {site['URL']}")

def send_discord_notification(webhook_url, message):
    try:
        requests.post(webhook_url, json={"content": message})
    except Exception as e:
        print(f"Erreur lors de l'envoi Discord : {e}")

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
            writer.writerow(["Date/Heure", "Nom", "URL", "Code HTTP", "Erreur", "Statut"])

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

            writer.writerow([now, site['Name'], site['URL'], status_code, error, status])
            current_status[site['Name']] = status

            if discord_enabled and 'Webhook' in site and site['Webhook']:
                previous = previous_status.get(site['Name'])
                if previous != status:
                    emoji = "🟢" if status == "UP" else "🔴"
                    message = f"{emoji} **{site['Name']}** est **{status}** (était {previous})\n{site['URL']}"
                    send_discord_notification(site['Webhook'], message)

    with open(status_file, 'w') as f:
        json.dump(current_status, f, indent=2)

    print(f"\n✅ Fichier de log généré : {log_file}")

def main():
    parser = argparse.ArgumentParser(description="Surveillance de services web")
    parser.add_argument('--add', nargs='+', help="Ajouter un site (optionnel : webhook)")
    parser.add_argument('--remove', metavar='NOM', help="Supprimer un site")
    parser.add_argument('--list', action='store_true', help="Lister les sites")
    parser.add_argument('--check', action='store_true', help="Vérifier les sites")
    parser.add_argument('--discord', action='store_true', help="Envoyer les changements d'état sur Discord")

    args = parser.parse_args()
    create_config_file()

    if args.add:
        if len(args.add) < 2:
            print("Erreur : vous devez fournir au moins un nom et une URL.")
        else:
            name = args.add[0]
            url = args.add[1]
            webhook = args.add[2] if len(args.add) > 2 else ""
            add_site(name, url, webhook)
    elif args.remove:
        remove_site(args.remove)
    elif args.list:
        list_sites()
    elif args.check:
        check_sites(discord_enabled=args.discord)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

import csv
import requests
import argparse
import os
import json
from datetime import datetime

CONFIG_FILE = 'web_services.csv'

def create_config_file():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Name', 'URL', 'Webhook'])

def read_config_file():
    with open(CONFIG_FILE, 'r') as file:
        reader = csv.DictReader(file)
        return list(reader)

def add_site(name, url, webhook=""):
    with open(CONFIG_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name, url, webhook])
    print(f"Ajouté : {name} -> {url} (Webhook: {webhook if webhook else 'Aucun'})")

def remove_site(name):
    sites = read_config_file()
    with open(CONFIG_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'URL', 'Webhook'])
        for site in sites:
            if site['Name'] != name:
                writer.writerow([site['Name'], site['URL'], site.get('Webhook', '')])
    print(f"Supprimé : {name}")

def list_sites():
    sites = read_config_file()
    if not sites:
        print("Aucun site configuré.")
    for site in sites:
        print(f"{site['Name']} -> {site['URL']}")

def send_discord_notification(webhook_url, message):
    try:
        requests.post(webhook_url, json={"content": message})
    except Exception as e:
        print(f"Erreur lors de l'envoi Discord : {e}")

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
            writer.writerow(["Date/Heure", "Nom", "URL", "Code HTTP", "Erreur", "Statut"])

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

            writer.writerow([now, site['Name'], site['URL'], status_code, error, status])
            current_status[site['Name']] = status

            if discord_enabled and 'Webhook' in site and site['Webhook']:
                previous = previous_status.get(site['Name'])
                if previous != status:
                    emoji = "🟢" if status == "UP" else "🔴"
                    message = f"{emoji} **{site['Name']}** est **{status}** (était {previous})\n{site['URL']}"
                    send_discord_notification(site['Webhook'], message)

    with open(status_file, 'w') as f:
        json.dump(current_status, f, indent=2)

    print(f"\n✅ Fichier de log généré : {log_file}")

def main():
    parser = argparse.ArgumentParser(description="Surveillance de services web")
    parser.add_argument('--add', nargs='+', help="Ajouter un site (optionnel : webhook)")
    parser.add_argument('--remove', metavar='NOM', help="Supprimer un site")
    parser.add_argument('--list', action='store_true', help="Lister les sites")
    parser.add_argument('--check', action='store_true', help="Vérifier les sites")
    parser.add_argument('--discord', action='store_true', help="Envoyer les changements d'état sur Discord")

    args = parser.parse_args()
    create_config_file()

    if args.add:
        if len(args.add) < 2:
            print("Erreur : vous devez fournir au moins un nom et une URL.")
        else:
            name = args.add[0]
            url = args.add[1]
            webhook = args.add[2] if len(args.add) > 2 else ""
            add_site(name, url, webhook)
    elif args.remove:
        remove_site(args.remove)
    elif args.list:
        list_sites()
    elif args.check:
        check_sites(discord_enabled=args.discord)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

