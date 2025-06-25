import csv
import requests
import argparse
import os

CONFIG_FILE = 'web_services.csv'

def create_config_file():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Name', 'URL'])

def read_config_file():
    with open(CONFIG_FILE, 'r') as file:
        reader = csv.DictReader(file)
        return list(reader)

def add_site(name, url):
    with open(CONFIG_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name, url])
    print(f"Ajouté : {name} -> {url}")

def remove_site(name):
    sites = read_config_file()
    with open(CONFIG_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'URL'])
        for site in sites:
            if site['Name'] != name:
                writer.writerow([site['Name'], site['URL']])
    print(f"Supprimé : {name}")

def list_sites():
    sites = read_config_file()
    if not sites:
        print("Aucun site configuré.")
    for site in sites:
        print(f"{site['Name']} -> {site['URL']}")

def check_sites():
    sites = read_config_file()
    for site in sites:
        try:
            response = requests.get(site['URL'], timeout=5)
            if 200 <= response.status_code <= 299:
                print(f"[OK] {site['Name']} est en ligne.")
            else:
                print(f"[ERREUR] {site['Name']} retourne le code {response.status_code}.")
        except Exception as e:
            print(f"[HORS LIGNE] {site['Name']} : {e}")

def main():
    parser = argparse.ArgumentParser(description="Surveillance de services web")
    parser.add_argument('--add', nargs=2, metavar=('NOM', 'URL'), help="Ajouter un site")
    parser.add_argument('--remove', metavar='NOM', help="Supprimer un site")
    parser.add_argument('--list', action='store_true', help="Lister les sites")
    parser.add_argument('--check', action='store_true', help="Vérifier les sites")

    args = parser.parse_args()
    create_config_file()

    if args.add:
        add_site(*args.add)
    elif args.remove:
        remove_site(args.remove)
    elif args.list:
        list_sites()
    elif args.check:
        check_sites()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

