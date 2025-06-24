from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Game


# PUBLIC_INTERFACE
class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer for registering a new user."""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password')

    def create(self, validated_data):
        user = User(username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        return user


# PUBLIC_INTERFACE
class UserLoginSerializer(serializers.Serializer):
    """Serializer for authenticating a user and returning login details."""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid credentials.")


# PUBLIC_INTERFACE
class GameSerializer(serializers.ModelSerializer):
    """Serializer for Game state (read only)."""
    player_x = serializers.CharField(source='player_x.username', read_only=True)
    player_o = serializers.CharField(source='player_o.username', default=None, read_only=True)
    winner = serializers.CharField(default=None, read_only=True)
    is_draw = serializers.BooleanField(read_only=True)

    class Meta:
        model = Game
        fields = [
            'id', 'player_x', 'player_o', 'board', 'current_turn', 'winner',
            'is_draw', 'is_finished', 'created', 'updated'
        ]


# PUBLIC_INTERFACE
class GameCreateSerializer(serializers.Serializer):
    """Serializer for creating a new game."""
    opponent_username = serializers.CharField(required=False)

    def validate(self, attrs):
        # Additional validation can be added if needed
        return attrs


# PUBLIC_INTERFACE
class MoveSerializer(serializers.Serializer):
    """Serializer for making a move in the game."""
    position = serializers.IntegerField(min_value=0, max_value=8)
