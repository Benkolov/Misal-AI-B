from rest_framework.authtoken.models import Token
from django.utils import timezone
from datetime import timedelta

class TokenManager:
    @staticmethod
    def create_or_refresh_token(user):
        token, created = Token.objects.get_or_create(user=user)

        if not created and token.created < timezone.now() - timedelta(hours=24):
            token.delete()
            token = Token.objects.create(user=user)
            
        return token

    @staticmethod
    def invalidate_user_tokens(user):
        Token.objects.filter(user=user).delete()

    @staticmethod
    def is_token_valid(token_key):
        try:
            token = Token.objects.get(key=token_key)
            return token.created > timezone.now() - timedelta(hours=24)
        except Token.DoesNotExist:
            return False
