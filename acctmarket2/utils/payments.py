import logging
from decimal import Decimal

import requests
from django.conf import settings
# from django.contrib import messages
from django.urls import reverse

logger = logging.getLogger(__name__)


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
    # Set the API key and URL based on the environment
    NOWPAYMENTS_API_KEY = settings.NOWPAYMENTS_API_KEY
    # Use sandbox URL for testing
    # Uncomment the production URL for live use
    NOWPAYMENTS_API_URL = "https://api-sandbox.nowpayments.io/v1/"
    # NOWPAYMENTS_API_URL = "https://api.nowpayments.io/v1/"

    def create_payment(self, amount, currency, order_id, description, request):
        """
        Creates a payment invoice using the NOWPayments API.

        Args:
            amount (float): The amount of the payment.
            currency (str): The currency of the payment.
            order_id (int): The ID of the order associated with the payment.
            description (str): The description of the payment.
            request (HttpRequest): The request object for making the API call.

        Returns:
            dict: The response from the API call.
            Includes status and data or message.
        """
        url = f"{self.NOWPAYMENTS_API_URL}invoice"
        headers = {
            "x-api-key": self.NOWPAYMENTS_API_KEY,
            "Content-Type": "application/json",
        }
        data = {
            "price_amount": amount,
            "price_currency": currency,
            "order_id": str(order_id),
            "order_description": description,
            "ipn_callback_url": request.build_absolute_uri(
                reverse("ecommerce:ipn")
            ),
            "success_url": request.build_absolute_uri(
                reverse("ecommerce:payment_complete")
            ),
            "cancel_url": request.build_absolute_uri(
                reverse("ecommerce:payment_failed")
            ),
        }
        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        if response.status_code == 200:
            if "id" in result:  # "id" is the correct field to check
                return {"status": True, "data": result}
            else:
                return {
                    "status": False,
                    "message": "Payment ID missing in response"
                }
        else:
            # Handle error appropriately
            return {"status": False, "message": result.get(
                "message", "Unknown error"
            )}

    def verify_payment(self, payment_id):
        """
        Verify the payment using the NOWPayments API.

        Args:
            payment_id (str): The ID of the payment to be verified.

        Returns:
            tuple: A tuple with a boolean
            indicating success and the response data or None.
        """
        headers = {
            "x-api-key": self.NOWPAYMENTS_API_KEY,
        }
        url = f"{self.NOWPAYMENTS_API_URL}payment/{payment_id}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return True, response.json()

        error_message = f"Failed to verify payment: {response.status_code}, {response.text}"   # noqa
        return False, error_message


def get_exchange_rate(target_currency="NGN"):
    """
    Retrieves the exchange rate for a given target
    currency from an external API.

    Args:
        target_currency (str, optional):
        The currency for which to retrieve the exchange rate.
        Defaults to "NGN".

    Returns:
        Decimal: The exchange rate for the target currency.

    Raises:
        Exception: If the exchange rate cannot be retrieved
        or the target currency is not found in the response data.

    """
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
