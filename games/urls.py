from django.urls import path
from games import views


app_name = 'games'
urlpatterns = [
    path('invite', views.invite_to_play, name='invite'),
    path('invited', views.get_invited_games, name='invited'),
    path('accepted', views.get_accepted_game, name='accepted'),
    path('<int:game_id>/accept', views.accept_to_play, name='accept'),
    path('<int:game_id>/decline', views.decline_to_play, name='decline'),
    path('<int:game_id>', views.game, name='game'),
    path('<int:game_id>/<int:move_id>/move', views.move, name='move'),
    path('<int:game_id>/<int:move_id>/check', views.check, name='check'),
]
