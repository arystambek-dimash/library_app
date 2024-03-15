import re
from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'read_only': True}
        }

    def validate_name(self, value):
        if len(value) < 2:
            raise serializers.ValidationError('The name is too short')
        return value

    def validate_password(self, value):
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$', value):
            raise serializers.ValidationError(
                "Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase "
                "letter, and one digit")
        return value

    def create(self, validated_data):
        validated_data['name'] = self.validate_name(validated_data.get('name'))
        validated_data['password'] = self.validate_password(validated_data.get('password'))
        return User.objects.create_user(**validated_data)
