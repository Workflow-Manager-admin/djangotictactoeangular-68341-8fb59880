from django.urls import path
from .views import (
    health, register, login_view, logout_view, session_view, start_game,
    make_move, game_state, reset_game, my_games
)

urlpatterns = [
    path('health/', health, name='Health'),

    # User endpoints
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('session/', session_view, name='session'),

    # Game endpoints
    # GET: List user's games
    path('games/', my_games, name='my_games'),
    # POST: Start new game
    path('games/start/', start_game, name='start_game'),
    # GET: Get state of a game
    path('games/<int:game_id>/', game_state, name='game_state'),
    # POST: Make a move
    path('games/<int:game_id>/move/', make_move, name='make_move'),
    # POST: Reset game
    path('games/<int:game_id>/reset/', reset_game, name='reset_game'),
]
