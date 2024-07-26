import logging
from decimal import Decimal

import requests
from django.conf import settings


class PayStack:
    PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
    base_url = "https://api.paystack.co"

    def verify_payment(self, ref, *args, **kwargs):
        path = f"/transaction/verify/{ref}"

        headers = {
            "Authorization": f"Bearer {self.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        url = self.base_url + path
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            return response_data["status"], response_data["data"]
        response_data = response.json()
        return response_data["status"], response_data["message"]


class NowPayment:
    NOWPAYMENTS_API_KEY = settings.NOWPAYMENTS_API_KEY
    NOWPAYMENTS_API_URL = "https://api.nowpayments.io/v1/"

    def create_payment(self, amount, currency, order_id, description):
        url = f"{self.NOWPAYMENTS_API_URL}invoice"

        headers = {
            "x-api-key": self.NOWPAYMENTS_API_KEY,
            "Content-Type": "application/json",
        }

        data = {
            "price_amount": amount,
            "price_currency": currency,
            "order_id": order_id,
            "order_description": description,
            "ipn_callback_url": "your_ipn_callback_url",
            "success_url": "http://acctmarket.com/ecommerce/payment-complete",
            "cancel_url": "http://acctmarket.com/ecommerce/payment-failed",
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()


logger = logging.getLogger(__name__)


def get_exchange_rate(target_currency="NGN"):
    url = f"{settings.EXCHANGE_RATE_API_URL}"
    headers = {
        "apikey": settings.EXCHANGE_RATE_API_KEY
    }
    response = requests.get(url, headers=headers)
    data = response.json()

    if response.status_code == 200 and "conversion_rates" in data:
        rate = data["conversion_rates"].get(target_currency)
        if rate:
            return Decimal(rate)
        else:
            logger.error(
                f"Target currency {target_currency} not found in response data"               # noqa
            )
            raise Exception(
                f"Target currency {target_currency} not found in response data"                 # noqa
            )
    else:
        logger.error(f"Error fetching exchange rate: {data}")
        raise Exception("Error fetching exchange rate")


def convert_to_naira(amount, exchange_rate):
    return amount * exchange_rate
