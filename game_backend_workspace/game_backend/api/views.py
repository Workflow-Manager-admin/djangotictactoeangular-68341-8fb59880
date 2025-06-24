from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model, login, logout
from django.db.models import Q

from .models import Game
from .serializers import (
    UserRegisterSerializer, UserLoginSerializer,
    GameSerializer, GameCreateSerializer, MoveSerializer
)

User = get_user_model()


@api_view(['GET'])
def health(request):
    return Response({"message": "Server is up!"})


# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    PUBLIC_INTERFACE
    Register a new user.
    """
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    PUBLIC_INTERFACE
    Login a user and create a session.
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        login(request, serializer.validated_data)
        return Response({'message': 'Login successful.'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    PUBLIC_INTERFACE
    Log out the current user.
    """
    logout(request)
    return Response({'message': 'Logged out.'})


# PUBLIC_INTERFACE
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def session_view(request):
    """
    PUBLIC_INTERFACE
    Get the current authenticated user's session info.
    """
    return Response({'username': request.user.username})


# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_game(request):
    """
    PUBLIC_INTERFACE
    Start a new game, optionally inviting another user by username.
    """
    serializer = GameCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    opponent = None
    if 'opponent_username' in serializer.validated_data:
        try:
            opponent = User.objects.get(
                username=serializer.validated_data['opponent_username']
            )
        except User.DoesNotExist:
            return Response({'error': 'Opponent does not exist.'}, status=404)
        if opponent == request.user:
            return Response({'error': 'Cannot play against yourself.'}, status=400)
        game = Game.objects.create(
            player_x=request.user,
            player_o=opponent,
            board=[""] * 9
        )
    else:
        game = Game.objects.create(player_x=request.user, board=[""] * 9)
    return Response(GameSerializer(game).data, status=201)


# PUBLIC_INTERFACE
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_games(request):
    """
    PUBLIC_INTERFACE
    List all games for the current user.
    """
    games = Game.objects.filter(
        Q(player_x=request.user) | Q(player_o=request.user)
    ).order_by('-created')
    return Response(GameSerializer(games, many=True).data)


# PUBLIC_INTERFACE
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def game_state(request, game_id):
    """
    PUBLIC_INTERFACE
    Retrieve the state of a specific game by ID.
    """
    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        return Response({'error': 'Game not found'}, status=404)
    if request.user != game.player_x and request.user != game.player_o:
        return Response({'error': 'Not authorized'}, status=403)
    return Response(GameSerializer(game).data)


# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_move(request, game_id):
    """
    PUBLIC_INTERFACE
    Make a move in a game by game ID.
    Request: {"position": position_integer}
    """
    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        return Response({'error': 'Game not found'}, status=404)
    if request.user != game.player_x and request.user != game.player_o:
        return Response({'error': 'Not authorized'}, status=403)
    serializer = MoveSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    success, message, _ = game.make_move(
        request.user,
        serializer.validated_data["position"]
    )
    state = GameSerializer(game).data
    if not success:
        return Response({'error': message, "game": state}, status=400)
    return Response({'message': message, "game": state})


# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_game(request, game_id):
    """
    PUBLIC_INTERFACE
    Reset a game to start over.
    """
    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        return Response({'error': 'Game not found'}, status=404)
    if request.user != game.player_x:
        return Response({'error': 'Only the creator (X) can reset.'}, status=403)
    game.reset_board()
    return Response({'message': 'Game reset.', "game": GameSerializer(game).data})
