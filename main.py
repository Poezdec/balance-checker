import time
import requests
import pandas as pd
from pathlib import Path

# Файл с адресами кошельков
ADDRESS_FILE = "address.txt"

# Настройки (конфигурация внутри кода)
CONFIG = {
    "enabled_networks": {
        "base": True,
        "optimism": True,
        "arbitrum": True,
        "polygon": True
    },
    "api_keys": {
        "base": "YOUR_BASESCAN_API_KEY",
        "optimism": "YOUR_OPTIMISM_API_KEY",
        "arbitrum": "YOUR_ARBITRUM_API_KEY",
        "polygon": "YOUR_POLYGONSCAN_API_KEY"
    },
    "prices": {
        "eth": 3000.0,
        "pol": 1.5
    }
}

def get_balance(address, network, api_key):
    """Получает баланс в указанной сети."""
    api_urls = {
        "base": "https://api.basescan.org/api",
        "optimism": "https://api-optimistic.etherscan.io/api",
        "arbitrum": "https://api.arbiscan.io/api",
        "polygon": "https://api.polygonscan.com/api"
    }
    url = api_urls[network]
    params = {
        "module": "account",
        "action": "balance",
        "address": address,
        "tag": "latest",
        "apikey": api_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "1":
            return int(data["result"]) / 10**18  # Конвертация в ETH или POL
    return 0.0

def main():
    addresses = Path(ADDRESS_FILE).read_text().splitlines()
    
    results = []
    max_columns = ["Address"]
    for network in CONFIG["enabled_networks"]:
        if CONFIG["enabled_networks"][network]:
            if network == "polygon":
                max_columns.extend(["Polygon POL", "Polygon $"])
            else:
                max_columns.extend([f"{network.capitalize()} ETH", f"{network.capitalize()} $"])
    
    for i, address in enumerate(addresses):
        if address.strip():
            print(f"Проверяем {address}...")
            row = [address]
            
            for network in CONFIG["enabled_networks"]:
                if CONFIG["enabled_networks"][network]:
                    balance = get_balance(address, network, CONFIG["api_keys"][network])
                    price = CONFIG["prices"]["pol"] if network == "polygon" else CONFIG["prices"]["eth"]
                    row.extend([balance, balance * price])
                else:
                    row.extend([None, None])
            
            results.append(row)
            
            if (i + 1) % 3 == 0:
                print("Делаем паузу 1 сек... (лимит 3 запроса в секунду)")
                time.sleep(1)
    
    df = pd.DataFrame(results, columns=max_columns)
    df.to_csv("balances.csv", index=False)
    print("Результаты сохранены в balances.csv")
    print("\nТаблица результатов:\n")
    print(df.to_string(index=False))

if __name__ == "__main__":
    main()
