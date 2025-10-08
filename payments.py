import requests

CRYPTO_PAY_BOT_TOKEN = '470214:AAtsGnRZSFgSV3t0yqvHfoepEW37pAcm5Ao'
API_URL = 'https://pay.crypt.bot/api/'

def create_invoice(amount, currency, description, payload):
    """
    Создает счет для оплаты.
    """
    url = f"{API_URL}createInvoice"
    headers = {
        'Crypto-Pay-API-Token': CRYPTO_PAY_BOT_TOKEN
    }
    data = {
        'asset': currency,
        'amount': amount,
        'description': description,
        'payload': payload,
        'allow_anonymous': False
    }
    
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()  # Вызовет исключение для ошибок HTTP
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при создании счета: {e}")
        return None

def check_invoice_status(invoice_id):
    """
    Проверяет статус счета по его ID.
    """
    url = f"{API_URL}getInvoices"
    headers = {
        'Crypto-Pay-API-Token': CRYPTO_PAY_BOT_TOKEN
    }
    params = {
        'invoice_ids': invoice_id
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        invoices = response.json().get('result', {}).get('items', [])
        if invoices:
            return invoices[0].get('status')
        return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при проверке статуса счета: {e}")
        return None

