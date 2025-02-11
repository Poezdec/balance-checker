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
        "eth": 2600,
        "pol": 0.3
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
    for i, address in enumerate(addresses):
        if address.strip():
            print(f"Проверяем {address}...")
            row = [address]
            
            if CONFIG["enabled_networks"].get("base", False):
                base_balance = get_balance(address, "base", CONFIG["api_keys"]["base"])
                row.extend([base_balance, base_balance * CONFIG["prices"]["eth"]])
            else:
                row.extend([None, None])
            
            if CONFIG["enabled_networks"].get("optimism", False):
                optimism_balance = get_balance(address, "optimism", CONFIG["api_keys"]["optimism"])
                row.extend([optimism_balance, optimism_balance * CONFIG["prices"]["eth"]])
            else:
                row.extend([None, None])
            
            if CONFIG["enabled_networks"].get("arbitrum", False):
                arbitrum_balance = get_balance(address, "arbitrum", CONFIG["api_keys"]["arbitrum"])
                row.extend([arbitrum_balance, arbitrum_balance * CONFIG["prices"]["eth"]])
            else:
                row.extend([None, None])
            
            if CONFIG["enabled_networks"].get("polygon", False):
                polygon_balance = get_balance(address, "polygon", CONFIG["api_keys"]["polygon"])
                row.extend([polygon_balance, polygon_balance * CONFIG["prices"]["pol"]])
            else:
                row.extend([None, None])
            
            results.append(row)
            
            if (i + 1) % 3 == 0:
                print("Делаем паузу 1 сек... (лимит 3 запроса в секунду)")
                time.sleep(1)
    
    columns = ["Address"]
    if CONFIG["enabled_networks"].get("base", False):
        columns.extend(["Base ETH", "Base $"])
    if CONFIG["enabled_networks"].get("optimism", False):
        columns.extend(["Optimism ETH", "Optimism $"])
    if CONFIG["enabled_networks"].get("arbitrum", False):
        columns.extend(["Arbitrum ETH", "Arbitrum $"])
    if CONFIG["enabled_networks"].get("polygon", False):
        columns.extend(["Polygon POL", "Polygon $"])
    
    df = pd.DataFrame(results, columns=columns)
    df.to_csv("balances.csv", index=False)
    print("Результаты сохранены в balances.csv")
    print("\nТаблица результатов:\n")
    print(df.to_string(index=False))

if __name__ == "__main__":
    main()
