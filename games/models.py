from django.db import models
from django.conf import settings


class GameManager(models.Manager):
    ''' '''

    def get_ready_games(self, user):
        ''' '''
        return self.filter(user2=user, status=Game.STATUS_INVITED)

    def get_accepted_game(self, user):
        ''' '''
        return self.filter(user1=user, status=Game.STATUS_STARTED).first()

    def get_game_to_play(self, game_id: int, user):
        ''' '''
        return self.filter(id=game_id, user2=user).first()

    def get_started_game(self, game_id: int, user):
        ''' '''
        return self._filter_for_user(user).filter(
            status=Game.STATUS_STARTED, id=game_id
        ).first()

    def _filter_for_user(self, user):
        ''' '''
        return self.filter(models.Q(user1=user) | models.Q(user2=user))


class Game(models.Model):
    ''' '''

    STATUS_INVITED = 'invited'
    STATUS_DECLINED = 'declined'
    STATUS_STARTED = 'started'
    STATUS_FINISHED = 'finished'
    STATUSES = (
        (STATUS_INVITED, STATUS_INVITED), (STATUS_DECLINED, STATUS_DECLINED),
        (STATUS_STARTED, STATUS_STARTED), (STATUS_FINISHED, STATUS_FINISHED)
    )

    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='games_started')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='games_joined')
    status = models.CharField(max_length=15, choices=STATUSES)
    winner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='winned_games', blank=True, null=True)

    objects = GameManager()

    def is_started(self) -> bool:
        ''' '''
        return self.status == self.STATUS_STARTED

    def set_invited(self, user1, user2):
        ''' '''
        self.user1 = user1
        self.user2 = user2
        self.status = self.STATUS_INVITED

    def set_declined(self):
        ''' '''
        self.status = self.STATUS_DECLINED

    def set_started(self):
        ''' '''
        self.status = self.STATUS_STARTED

    def get_most_winner(self):
        ''' '''
        return self.moves.filter(
            winner__isnull=False
        ).values('winner').annotate(
            num_wins=models.Count('winner')
        ).order_by('-num_wins').first()

    def set_finished(self):
        ''' '''
        self.status = self.STATUS_FINISHED
        winner = self.get_most_winner()
        if not winner:
            # @todo
            raise Exception('Game is not finished')
        self.winner_id = winner['winner']

    def is_enough(self):
        ''' '''
        winner = self.get_most_winner()
        if not winner:
            return False
        return False if winner['num_wins'] < settings.GAMES_MAX_WINS else True

    def winner_title(self) -> str:
        ''' '''
        return self.winner.email if self.winner else ''


class MoveManager(models.Manager):
    ''' '''

    def get_last(self, game: Game, user):
        ''' '''
        if game.user1 == user:
            qs = self.filter(figure1__isnull=True)
        else:
            qs = self.filter(figure2__isnull=True)
        move = qs.filter(game=game).order_by('-id').first()
        if not move:
            move = Move(game=game)
            move.save()
        return move

    def list_for_game(self, game: Game):
        ''' '''
        return self.filter(game=game).order_by('id')

    def one_for_game(self, game: Game, move_id: int):
        ''' '''
        return self.filter(game=game, id=move_id).first()


class Move(models.Model):
    ''' '''

    FIGURE_STONE = 'stone'
    FIGURE_SCISSORS = 'scissors'
    FIGURE_PAPER = 'paper'
    FIGURE_LIZARD = 'lizard'
    FIGURE_SPOK = 'spok'
    FIGURES = (
        (FIGURE_STONE, FIGURE_STONE), (FIGURE_SCISSORS, FIGURE_SCISSORS),
        (FIGURE_PAPER, FIGURE_PAPER), (FIGURE_LIZARD, FIGURE_LIZARD),
        (FIGURE_SPOK, FIGURE_SPOK)
    )
    RESULTS = {
        FIGURE_STONE: {'wins': (FIGURE_SCISSORS, FIGURE_LIZARD), 'loses': (FIGURE_PAPER, FIGURE_SPOK)},
        FIGURE_SCISSORS: {'wins': (FIGURE_PAPER, FIGURE_LIZARD), 'loses': (FIGURE_STONE, FIGURE_SPOK)},
        FIGURE_PAPER: {'wins': (FIGURE_STONE, FIGURE_SPOK), 'loses': (FIGURE_SCISSORS, FIGURE_LIZARD)},
        FIGURE_LIZARD: {'wins': (FIGURE_PAPER, FIGURE_SPOK), 'loses': (FIGURE_STONE, FIGURE_SCISSORS)},
        FIGURE_SPOK: {'wins': (FIGURE_STONE, FIGURE_SCISSORS), 'loses': (FIGURE_PAPER, FIGURE_LIZARD)},
    }

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='moves')
    figure1 = models.CharField(max_length=12, choices=FIGURES, blank=True, null=True)
    figure2 = models.CharField(max_length=12, choices=FIGURES, blank=True, null=True)
    winner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='winned_moves', blank=True, null=True)

    objects = MoveManager()

    @classmethod
    def figure_valid(cls, figure) -> bool:
        ''' @todo '''
        for fig in cls.FIGURES:
            if fig[0] == figure:
                return True
        return False

    def is_finished(self) -> bool:
        ''' '''
        return False if self.figure1 is None or self.figure2 is None else True

    def chose_figure(self, user, figure: str):
        ''' '''
        if user == self.game.user1:
            self.figure1 = figure
        else:
            self.figure2 = figure
        if self.is_finished():
            if self.figure1 == self.figure2:
                self.winner = None
            elif self.figure2 in self.RESULTS[self.figure1]['wins']:
                self.winner = self.game.user1
            elif self.figure2 in self.RESULTS[self.figure1]['loses']:
                self.winner = self.game.user2

    def another_user_choice(self, user):
        '''
        if user has set figure then he is allowed to see another user's figure
        '''
        if self.game.user1 == user:
            return None if self.figure1 is None else self.figure2
        else:
            return None if self.figure2 is None else self.figure1

    def winner_title(self) -> str:
        ''' '''
        return self.winner.email if self.winner else 'stalemate'
