"""
Telegram login response verification functionality.
"""
import hashlib
import hmac
import time

from tg_authorization.errors import (NotTrustedTelegramData,
                                     OutdatedTelegramResponse)

ONE_DAY_IN_SECONDS = 86400


def verify_telegram_response(bot_token, response_tg_data):
    """
    Check if received data from Telegram is real.

    Based on SHA and HMAC algothims.
    Instructions - https://core.telegram.org/widgets/login#checking-authorization
    """

    response_tg_data = response_tg_data.copy()

    received_hash = response_tg_data['hash']
    auth_date = response_tg_data['auth_date']

    response_tg_data.pop('hash', None)
    request_data_alphabetical_order = sorted(response_tg_data.items(), key=lambda x: x[0])

    data_check_string = []

    for data_pair in request_data_alphabetical_order:
        key, value = data_pair[0], data_pair[1]
        data_check_string.append(key + '=' + value)

    data_check_string = '\n'.join(data_check_string)

    secret_key = hashlib.sha256(bot_token.encode()).digest()
    _hash = hmac.new(secret_key, msg=data_check_string.encode(), digestmod=hashlib.sha256).hexdigest()

    unix_time_now = int(time.time())
    unix_time_auth_date = int(auth_date)

    if unix_time_now - unix_time_auth_date > ONE_DAY_IN_SECONDS:
        raise OutdatedTelegramResponse(
            'Authentication data is outdated. Authentication was received more than day ago.'
        )

    if _hash != received_hash:
        raise NotTrustedTelegramData(
            'This is not a Telegram data. Hash from recieved authentication data does not match'
            'with calculated hash based on bot token.'
        )

    return response_tg_data
