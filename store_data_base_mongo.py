import pymongo

"""
    Projekt zaliczeniowy: Sklep Internetowy (MongoDB)
    Pełna wersja na ocenę 5.0 z rozbudowanymi testami.
"""


def connect(host, port, timeout):
    try:
        client = pymongo.MongoClient(host, port, serverSelectionTimeoutMS=timeout)
        client.server_info()
        return client
    except Exception as e:
        print(f"Error: {e}")
        return None


def create_database(client):
    db = client["online_store"]
    products_collection = db["products"]
    customers_collection = db["customers"]
    orders_collection = db["orders"]
    return db, products_collection, customers_collection, orders_collection


# --- WALIDATORY (4 i 4+) ---

def is_not_empty_str(value):
    """[4] Sprawdza, czy string nie jest pusty/same spacje."""
    if isinstance(value, str):
        if not value.strip():
            return False
    return True


def validate_email(email):
    """[4+] Walidacja: zawiera @, niepuste części, kropka w domenie."""
    if not isinstance(email, str): return False
    if "@" not in email: return False

    parts = email.split("@")
    if len(parts) != 2: return False
    username, domain = parts

    if not username or not domain: return False
    if "." not in domain: return False
    if domain.startswith(".") or domain.endswith("."): return False

    # Sprawdzenie czy nie ma pustych sekcji (np. a..pl)
    if any(not part for part in domain.split(".")):
        return False
    return True


def validate_phone(phone):
    """[4+] Walidacja: min 7 cyfr, dozwolone: cyfry, spacje, -, ()."""
    if not isinstance(phone, (str, int)): return False
    phone_str = str(phone)
    allowed = set("0123456789 -()")

    for char in phone_str:
        if char not in allowed: return False

    digits = sum(c.isdigit() for c in phone_str)
    return digits >= 7


# --- PRODUKTY ---

def add_product(products_collection, product_id, name, price, stock, category):
    if products_collection.find_one({"product_id": product_id}):
        print(f"BŁĄD: Produkt {product_id} już istnieje!")
        return None

    fields = {"product_id": str, "name": str, "price": (int, float), "stock": int, "category": str}
    values = {"product_id": product_id, "name": name, "price": price, "stock": stock, "category": category}

    for k, expected in fields.items():
        val = values[k]
        if not isinstance(val, expected):
            print(f"BŁĄD: Pole {k} powinno być typu {expected}")
            return None
        # [4] Puste stringi
        if isinstance(val, str) and not is_not_empty_str(val):
            print(f"BŁĄD: Pole {k} nie może być puste.")
            return None

    print(f"SUKCES: Dodano produkt '{name}' (ID: {product_id}) | Cena: {price} | Stan: {stock}")
    return products_collection.insert_one(values)


def update_product(products_collection, product_id, **updates):
    if not products_collection.find_one({"product_id": product_id}):
        print(f"BŁĄD: Brak produktu {product_id}")
        return None

    fields = {"name": str, "price": (int, float), "stock": int, "category": str}

    for k, val in updates.items():
        if k not in fields:
            print(f"BŁĄD: Nieznane pole {k}")
            return None
        expected = fields[k]
        if not isinstance(expected, tuple): expected = (expected,)

        if not isinstance(val, expected):
            print(f"BŁĄD: Zły typ danych dla {k}")
            return None
        # [4] Puste stringi
        if isinstance(val, str) and not is_not_empty_str(val):
            print(f"BŁĄD: Pole {k} nie może być puste.")
            return None

    result = products_collection.update_one({"product_id": product_id}, {"$set": updates})
    if result.modified_count:
        print(f"SUKCES: Zaktualizowano produkt {product_id}: {updates}")
    else:
        print(f"INFO: Brak zmian dla produktu {product_id}")
    return result


def view_all_products(products_collection):
    print("\n--- Lista Produktów ---")
    for p in products_collection.find():
        print(f"[{p['product_id']}] {p['name']:<20} Cena: {p['price']:>7} | Ilość: {p['stock']}")


# --- KLIENCI ---

def add_customer(customers_collection, customer_id, name, email, phone, address):
    if customers_collection.find_one({"customer_id": customer_id}):
        print(f"BŁĄD: Klient {customer_id} już istnieje!")
        return None

    # [4] Puste stringi
    if not is_not_empty_str(name) or not is_not_empty_str(address):
        print(f"BŁĄD (Walidacja): Imię i Adres nie mogą być puste. (Próba dla ID: {customer_id})")
        return None

    # [4+] Walidacja Email
    if not validate_email(email):
        print(f"BŁĄD (Walidacja): Niepoprawny email '{email}'.")
        return None

    # [4+] Walidacja Telefonu
    if not validate_phone(phone):
        print(f"BŁĄD (Walidacja): Niepoprawny telefon '{phone}'.")
        return None

    values = {
        "customer_id": customer_id, "name": name,
        "email": email, "phone": str(phone), "address": address
    }

    if not isinstance(customer_id, str):
        print("BŁĄD: customer_id musi być stringiem")
        return None

    print(f"SUKCES: Zarejestrowano klienta {name} (ID: {customer_id})")
    return customers_collection.insert_one(values)


def update_customer(customers_collection, customer_id, **updates):
    if not customers_collection.find_one({"customer_id": customer_id}):
        print(f"BŁĄD: Brak klienta {customer_id}")
        return None

    valid_fields = ["name", "email", "phone", "address"]
    for k, val in updates.items():
        if k not in valid_fields:
            print(f"BŁĄD: Niepoprawne pole {k}")
            return None

        if isinstance(val, str) and not is_not_empty_str(val):
            print(f"BŁĄD: Pole {k} nie może być puste.")
            return None

        if k == "email" and not validate_email(val):
            print(f"BŁĄD: Niepoprawny format email '{val}'")
            return None
        if k == "phone" and not validate_phone(val):
            print(f"BŁĄD: Niepoprawny format telefonu '{val}'")
            return None

    result = customers_collection.update_one({"customer_id": customer_id}, {"$set": updates})
    if result.modified_count:
        print(f"SUKCES: Zaktualizowano dane klienta {customer_id}")
    else:
        print(f"INFO: Brak zmian dla klienta {customer_id}")
    return result


def view_all_customers(customers_collection):
    print("\n--- Lista Klientów ---")
    for c in customers_collection.find():
        print(f"[{c['customer_id']}] {c['name']:<20} Email: {c['email']}")


# --- ZAMÓWIENIA ---

def add_order(orders_collection, customers_collection, product_collection, order_id, customer_id, items):
    # [4] Walidacja pustych ID
    if not is_not_empty_str(order_id) or not is_not_empty_str(customer_id):
        print("BŁĄD: ID zamówienia i klienta nie mogą być puste.")
        return None

    if orders_collection.find_one({"order_id": order_id}):
        print(f"BŁĄD: Zamówienie {order_id} już istnieje")
        return None
    if not customers_collection.find_one({"customer_id": customer_id}):
        print(f"BŁĄD: Klient {customer_id} nie istnieje")
        return None
    if not items:
        print("BŁĄD: Lista przedmiotów jest pusta")
        return None

    order_items = []
    total_price = 0.0

    for item in items:
        pid = item.get("product_id")
        qty = item.get("quantity")

        # [4] Walidacja produktu
        if not is_not_empty_str(pid):
            print("BŁĄD: ID produktu puste")
            return None

        prod = product_collection.find_one({"product_id": pid})
        if not prod:
            print(f"BŁĄD: Produkt {pid} nie istnieje")
            return None
        if prod["stock"] < qty:
            print(f"BŁĄD: Za mało sztuk produktu {prod['name']} (Dostępne: {prod['stock']}, Chcesz: {qty})")
            return None

        price = float(prod["price"])
        total_price += price * qty
        order_items.append({"product_id": pid, "quantity": qty, "price": price})

    # Aktualizacja stanu magazynowego
    for item in order_items:
        product_collection.update_one(
            {"product_id": item["product_id"]},
            {"$inc": {"stock": -item["quantity"]}}
        )

    order = {
        "order_id": order_id,
        "customer_id": customer_id,
        "items": order_items,
        "total_price": total_price
    }
    print(f"SUKCES: Złożono zamówienie {order_id} dla klienta {customer_id}. Kwota: {total_price:.2f} PLN")
    return orders_collection.insert_one(order)


def view_orders_by_customer(orders_collection, customer_id):
    """[4] Wyświetla zamówienia danego klienta."""
    print(f"\n--- Historria zamówień klienta: {customer_id} ---")
    orders = list(orders_collection.find({"customer_id": customer_id}))
    if not orders:
        print(" > Brak zamówień.")
        return

    for o in orders:
        print(f" > Zamówienie {o['order_id']} | Kwota: {o['total_price']:.2f} | Pozycje: {len(o['items'])}")
        for item in o['items']:
            print(f"     - Produkt: {item['product_id']} x{item['quantity']}")


# --- AGREGACJE (OCENA 5) ---

def count_orders_per_customer(orders_collection):
    print("\n[5] STATYSTYKA: Liczba zamówień na klienta")
    print("-" * 40)
    pipeline = [
        {"$group": {"_id": "$customer_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    results = list(orders_collection.aggregate(pipeline))
    if not results: print("Brak danych."); return

    for res in results:
        print(f"Klient: {res['_id']:<10} | Liczba zamówień: {res['count']}")


def total_spent_per_customer(orders_collection):
    print("\n[5] STATYSTYKA: Ranking wydatków klientów")
    print("-" * 40)
    pipeline = [
        {"$group": {"_id": "$customer_id", "total": {"$sum": "$total_price"}}},
        {"$sort": {"total": -1}}
    ]
    results = list(orders_collection.aggregate(pipeline))
    if not results: print("Brak danych."); return

    for res in results:
        print(f"Klient: {res['_id']:<10} | Wydano łącznie: {res['total']:>10.2f} PLN")


# ==========================================
# GŁÓWNA PĘTLA TESTOWA
# ==========================================

def main():
    print("Łączenie z bazą...")
    client = connect("localhost", 27017, 1000)
    if not client: return
    db, prod_col, cust_col, ord_col = create_database(client)

    # Czyszczenie bazy na start
    prod_col.delete_many({})
    cust_col.delete_many({})
    ord_col.delete_many({})
    print("Baza wyczyszczona. Rozpoczynam scenariusz testowy.\n")

    # ---------------------------------------------------------
    print("=== KROK 1: ZATOWAROWANIE SKLEPU ===")
    add_product(prod_col, "P001", "Laptop Gamingowy", 4500.00, 5, "Elektronika")
    add_product(prod_col, "P002", "Myszka Bezprzewodowa", 150.00, 20, "Akcesoria")
    add_product(prod_col, "P003", "Klawiatura Mech.", 300.00, 10, "Akcesoria")
    add_product(prod_col, "P004", "Monitor 27cali", 1200.00, 3, "Elektronika")

    # Test walidacji produktu
    print("\n[TEST WALIDACJI PRODUKTU]")
    add_product(prod_col, "P_BAD", "", 100, 10, "Test")  # Pusta nazwa

    view_all_products(prod_col)

    # ---------------------------------------------------------
    print("\n=== KROK 2: REJESTRACJA KLIENTÓW ===")
    add_customer(cust_col, "C001", "Jan Kowalski", "jan.kowalski@gmail.com", "500-100-200", "Warszawa, Złota 44")
    add_customer(cust_col, "C002", "Anna Nowak", "anna.nowak@firma.pl", "(48) 123 456 789", "Kraków, Rynek 1")
    add_customer(cust_col, "C003", "Piotr Wiśniewski", "piotr@tech.com", "600 700 800", "Gdańsk, Długa 5")

    # Testy walidacji klientów (Hakerzy)
    print("\n[TESTY WALIDACJI KLIENTÓW - ODRZUCANIE BŁĘDNYCH DANYCH]")
    add_customer(cust_col, "C_BAD1", "Haker Pusty", "", "123456789", "Adres")  # Pusty email
    add_customer(cust_col, "C_BAD2", "Haker BezAdresu", "ok@ok.pl", "123456789", "   ")  # Pusty adres (spacje)
    add_customer(cust_col, "C_BAD3", "Zły Email", "jan@domena", "123456789", "Adres")  # Brak kropki w domenie
    add_customer(cust_col, "C_BAD4", "Zły Telefon", "jan@ok.pl", "123", "Adres")  # Za krótki telefon
    add_customer(cust_col, "C_BAD5", "Zły Znak", "jan@ok.pl", "123-abc-456", "Adres")  # Litery w telefonie

    # ---------------------------------------------------------
    print("\n=== KROK 3: SKŁADANIE ZAMÓWIEŃ ===")

    # Jan kupuje laptopa i myszkę
    add_order(ord_col, cust_col, prod_col, "ORD_001", "C001", [
        {"product_id": "P001", "quantity": 1},
        {"product_id": "P002", "quantity": 1}
    ])

    # Anna kupuje monitor
    add_order(ord_col, cust_col, prod_col, "ORD_002", "C002", [
        {"product_id": "P004", "quantity": 1}
    ])

    # Piotr kupuje dużo sprzętu
    add_order(ord_col, cust_col, prod_col, "ORD_003", "C003", [
        {"product_id": "P003", "quantity": 2},  # 2 klawiatury
        {"product_id": "P002", "quantity": 5}  # 5 myszek
    ])

    # Jan wraca po monitor (Drugie zamówienie Jana)
    add_order(ord_col, cust_col, prod_col, "ORD_004", "C001", [
        {"product_id": "P004", "quantity": 1}
    ])

    # Testy błędów zamówień
    print("\n[TESTY BŁĘDÓW ZAMÓWIEŃ]")
    # Próba kupna towaru, którego jest za mało (było 3 monitory, Jan i Anna kupili po 1, zostało 1. Ktoś chce 2)
    add_order(ord_col, cust_col, prod_col, "ORD_FAIL1", "C003", [
        {"product_id": "P004", "quantity": 2}
    ])
    # Próba kupna przez nieistniejącego klienta
    add_order(ord_col, cust_col, prod_col, "ORD_FAIL2", "C_GHOST", [
        {"product_id": "P002", "quantity": 1}
    ])

    # ---------------------------------------------------------
    print("\n=== KROK 4: RAPORTY I WERYFIKACJA (To co widzi admin) ===")

    # Sprawdzenie stanów magazynowych po zakupach
    view_all_products(prod_col)

    # Historia zakupów Jana (powinien mieć 2 zamówienia)
    view_orders_by_customer(ord_col, "C001")

    # Agregacje - Statystyki (Grade 5)
    print("\n" + "=" * 50)
    print("PODSUMOWANIE ANALITYCZNE (AGREGACJE)")
    print("=" * 50)

    count_orders_per_customer(ord_col)
    # Oczekiwane: C001: 2, C003: 1, C002: 1

    total_spent_per_customer(ord_col)
    # Oczekiwane:
    # C001 wydał najwięcej (Laptop 4500 + Mysz 150 + Monitor 1200 = 5850 PLN)
    # C002 wydała (Monitor 1200 PLN)
    # C003 wydał (2*Klawiatura 600 + 5*Mysz 750 = 1350 PLN)

    client.close()
    print("\n--- KONIEC TESTU ---")


if __name__ == '__main__':
    main()
