import csv

def parse_amount(amount_str):
    """Convertit '0.59 EUR' -> 0.59 (float)"""
    try:
        return float(amount_str.replace('EUR', '').replace(',', '.').strip())
    except:
        return None

def check_regle_1(csv_file_path):
    """
    Règle 1 :
    "Total saisissable" doit être < "Solde bancaire insaisissable à retenir"
    """
    montant_saisissable = None
    montant_insaisissable = None

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) < 2:
                continue
            label = row[0].strip().lower()
            montant = parse_amount(row[1])

            if montant is None:
                continue

            if "total saisissable" in label:
                montant_saisissable = montant
            elif "insaisissable" in label:
                montant_insaisissable = montant

    print(f"🔍 Vérification de la règle 1 pour {csv_file_path}")
    if montant_saisissable is not None and montant_insaisissable is not None:
        print(f"   🧮 Insaisissable : {montant_insaisissable} | Saisissable : {montant_saisissable}")
        if montant_saisissable < montant_insaisissable:
            print("   ✅ Règle 1 OK : Total saisissable < montant insaisissable")
            return True
        else:
            print("   ❌ Règle 1 VIOLÉE : Total saisissable >= montant insaisissable")
            return False
    else:
        print("   ⚠️ Données insuffisantes pour vérifier la règle 1.")
        return False
