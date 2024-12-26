from django.utils.translation import get_language_from_request, activate


class LocaleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Set the language from the session or use default
        language = request.session.get('language', 'en')
        activate(language)

        # Set the currency from the session or use default
        currency = request.session.get('currency', 'GBP')
        currency_symbols = {
            'GBP': '£',
            'USD': '$',
            'EUR': '€',
            'JPY': '¥',
            'AUD': 'A$',
            'CAD': 'C$',
            'CNY': '¥',
        }
        request.currency_symbol = currency_symbols.get(currency, '£')

        # Define exchange rates (simplified example)
        exchange_rates = {
            'GBP': 1.0,
            'USD': 1.25,
            'EUR': 1.15,
            'JPY': 140.0,
            'AUD': 1.85,
            'CAD': 1.70,
            'CNY': 8.5,
        }
        request.exchange_rate = exchange_rates.get(currency, 1.0)

        response = self.get_response(request)
        return response
