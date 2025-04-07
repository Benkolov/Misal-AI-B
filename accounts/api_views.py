from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout, authenticate, login
from .token_utils import TokenManager

from accounts.models import CustomUser
from accounts.serializers import UserSerializer, UserRegistrationSerializer


@method_decorator(csrf_exempt, name='dispatch')
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({
                'error': 'Моля, въведете email и парола.'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)
        
        if user:
            # Използваме TokenManager за създаване/опресняване на токен
            token = TokenManager.create_or_refresh_token(user)
            login(request, user)
            
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'email': user.email,
                'is_staff': user.is_staff
            })
        
        return Response({
            'error': 'Невалидни credentials.'
        }, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CustomUser.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            token = TokenManager.create_or_refresh_token(user)
            
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Не сте влезли в системата'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            TokenManager.invalidate_user_tokens(request.user)
            logout(request)
            
            return Response({'message': 'Успешно излизане от системата'})
        except Exception as e:
            return Response(
                {'error': 'Грешка при излизане от системата'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            # Проверка дали email се променя
            if 'email' in serializer.validated_data and serializer.validated_data['email'] != user.email:
                return Response(
                    {'error': 'Email адресът не може да бъде променян'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'])
    def delete_account(self, request):
        user = request.user
        try:
            TokenManager.invalidate_user_tokens(user)
            user.delete()
            return Response({'message': 'Акаунтът е изтрит успешно'})
        except Exception as e:
            return Response(
                {'error': 'Грешка при изтриване на акаунта'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
