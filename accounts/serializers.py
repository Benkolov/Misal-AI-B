from rest_framework import serializers
from .models import CustomUser
from rest_framework.authtoken.models import Token

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)  # Email не може да се променя
    
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 
                 'profile_picture', 'is_staff', 'date_joined']
        read_only_fields = ['email', 'is_staff', 'date_joined']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'password2', 'profile_picture']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Паролите не съвпадат")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        email = validated_data.get('email')
        
        # Generate username from email if not provided
        validated_data['username'] = email.split('@')[0]
            
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        
        return user