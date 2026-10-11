from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User, Address
import re

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password2', 'phone_number', 'is_seller')

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Email already registered')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                'password2': 'Passwords do not match'
            })

        attrs.pop('password2')
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'is_seller'
            )
        read_only_fields = ('id', 'username', 'is_seller')

    def validate_email(self, value):
        qs = User.objects.filter(email__iexact=value).exclude(pk=self.instance.pk)
        if value and qs.exists():
            raise serializers.ValidationError('Email already registered')
        return value

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate_old_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError('Old password is not correct')
        return value

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError('Password must be at least 8 characters')
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        return user

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id',
            'title',
            'reverse_name',
            'phone_number',
            'city',
            'postal_code',
            'full_address',
            'is_default',
        ]
        read_only_fields = ['id']

    def validate_postal_code(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError(
                'Postal code must contain exactly 10 digits.'
            )
        return value

    def validate_phone_number(self, value):
        if not re.fullmatch(r'^\+?\d{7,15}$', value):
            raise serializers.ValidationError('Enter a valid phone number')
        return value











