from django.core.exceptions import ValidationError
from django.db.transaction import atomic
from games import models


class GameMaster():
    ''' '''

    def create_game(self, started_user, invited_user):
        ''' '''
        game = models.Game()
        game.set_invited(started_user, invited_user)
        mov = models.Move(game=game)
        with atomic():
            game.save()
            mov.save()

    def accept_game(self, game_id: int, user):
        ''' '''
        game = self._get_game(game_id)
        if self._game.user2 != user:
            raise ValidationError('Game not found')
        game.set_started()
        game.save()

    def decline_game(self, game_id: int, user):
        ''' '''
        game = self._get_game(game_id)
        if self._game.user2 != user:
            raise ValidationError('Game not found')
        game.set_declined()
        game.save()

    def make_move(self, game_id: int, user, move_id, figure):
        ''' '''
        game = self._get_game(game_id)
        move = models.Move.objects.one_for_game(game, move_id)
        if not move:
            raise ValidationError('Move not found')
        move.chose_figure(user, figure)
        move.save()

    def get_check_game(self, game_id: int) -> models.Game:
        ''' '''
        game = self._get_game(game_id)
        if game.is_started() and game.is_enough():
            game.set_finished()
            game.save()
        return game

    def _get_game(self, game_id: int):
        ''' '''
        try:
            return models.Game.objects.get(pk=game_id)
        except models.Game.DoesNotExist:
            raise ValidationError('Game not found')
