"""
Telegram login errors.
"""


class NotTrustedTelegramData(Exception):
    """
    The verification algorithm did not authorize Telegram data.
    """
    pass


class OutdatedTelegramResponse(Exception):
    """
    The Telegram data is outdated.
    """
    pass
