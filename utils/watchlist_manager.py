import json
import os

WATCHLIST_FILE = "data/watchlist.json"

def load_watchlist():
    if not os.path.exists(WATCHLIST_FILE):
        os.makedirs(os.path.dirname(WATCHLIST_FILE), exist_ok=True)
        with open(WATCHLIST_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(WATCHLIST_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_watchlist(data):
    with open(WATCHLIST_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_coin_to_watchlist(user_id, coin):
    data = load_watchlist()
    user_id = str(user_id)
    coin = coin.upper()

    if user_id not in data:
        data[user_id] = []

    if coin not in data[user_id]:
        data[user_id].append(coin)
        save_watchlist(data)
        return True
    return False

def remove_coin_from_watchlist(user_id, coin):
    data = load_watchlist()
    user_id = str(user_id)
    coin = coin.upper()

    if user_id in data and coin in data[user_id]:
        data[user_id].remove(coin)
        save_watchlist(data)
        return True
    return False

def get_user_watchlist(user_id):
    data = load_watchlist()
    return data.get(str(user_id), [])
