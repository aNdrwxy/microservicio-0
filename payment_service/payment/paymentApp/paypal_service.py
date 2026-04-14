import requests
from requests.auth import HTTPBasicAuth


BASE_URL = "https://api-m.sandbox.paypal.com"

PAYPAL_CLIENT_ID = "AbkKq9zWsxfOautNVaG37FUL9C2886TtNbwCKMQYaGIiF4VQ6w9hJqpucxvm8D87NUFxSANFfQZZ8UYj"
PAYPAL_CLIENT_SECRET = "EEmMcIyArsJ1bTdu2OkGjxLLP5xUisnXRcORbDLoCnQ99o51zeErpcbM9h529uFZ2Yedc_rRkPY9sqcu"


def get_access_token():
    url = f"{BASE_URL}/v1/oauth2/token"

    response = requests.post(
        url,
        auth=HTTPBasicAuth(
            PAYPAL_CLIENT_ID,
            PAYPAL_CLIENT_SECRET
        ),
        data={"grant_type": "client_credentials"}
    )

    response.raise_for_status()

    return response.json()["access_token"]


def create_paypal_order(amount):

    access_token = get_access_token()

    url = f"{BASE_URL}/v2/checkout/orders"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    body = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {
                    "currency_code": "USD",
                    "value": str(amount)
                }
            }
        ]
    }

    response = requests.post(url, json=body, headers=headers)
    response.raise_for_status()

    return response.json()

def capture_paypal_order(paypal_order_id):
    """Captura el pago después de que el usuario aprueba en PayPal."""
    access_token = get_access_token()
    url = f"{BASE_URL}/v2/checkout/orders/{paypal_order_id}/capture"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response