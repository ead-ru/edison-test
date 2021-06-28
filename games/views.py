from typing import Dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from games import models
from games.master import GameMaster


@csrf_exempt
@require_POST
@login_required
def invite_to_play(request):
    ''' '''
    if request.user.in_game:
        return _return_error('You are already playing')

    user_id = request.POST.get('user_id', None)
    if not user_id:
        return _return_error('Provide user you want to play with')

    User = get_user_model()
    try:
        invited_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return _return_error('User not found')

    master = GameMaster()
    master.create_game(request.user, invited_user)

    return _return_success({})


@require_GET
@login_required
def get_ready_games(request):
    ''' '''
    return _return_success(
        {'games': [
            {'id': game.id, 'user': game.user1.email}
            for game in models.Game.objects.get_ready_games(request.user)
        ]}
    )


@require_GET
@login_required
def get_accepted_game(request):
    ''' '''
    game = models.Game.objects.get_accepted_game(request.user)
    return _return_success({'game_id': game.id} if game else {})


@require_GET
@login_required
def game(request, game_id: int):
    ''' '''
    master = GameMaster()
    game = master.get_check_game(game_id)
    return render(request, 'games/game.html', context={
        'game': game,
        'enemy': game.user1 if game.user2 == request.user else game.user2,
        'move': models.Move.objects.get_last(game, request.user) if game.is_started() else None,
        'moves': models.Move.objects.list_for_game(game) if not game.is_started() else []
    })


@csrf_exempt
@require_POST
@login_required
def decline_to_play(request, game_id: int):
    ''' '''
    master = GameMaster(game_id)
    master.decline_game(request.user)
    return _return_success({})


@csrf_exempt
@require_POST
@login_required
def accept_to_play(request, game_id: int):
    ''' '''
    master = GameMaster(game_id)
    master.accept_game(request.user)
    return _return_success({'game_id': game_id})


@csrf_exempt
@require_POST
@login_required
def move(request, game_id: int, move_id: int):
    ''' '''
    master = GameMaster(game_id)
    chosen = request.POST.get('chosen', None)
    master.make_move(request.user, move_id, chosen)
    return _return_success({
        'game_id': game_id, 'move_id': move_id, 'chosen': chosen
    })


@require_GET
@login_required
def check(request, game_id: int, move_id: int):
    ''' '''
    game = models.Game.objects.get_started_game(game_id, request.user)
    if not game:
        return _return_error('Game not found')

    cur_move = models.Move.objects.one_for_game(game, move_id)
    if not cur_move:
        return _return_error('Move not found')

    ret = {'game_id': game.id, 'move_id': cur_move.id}
    if cur_move.is_finished():
        ret['enemy_move'] = cur_move.another_user_choice(request.user)
        # @todo
        ret['result'] = 0 if cur_move.winner is None else (1 if cur_move.winner == request.user else -1)
    return _return_success(ret)


def _return_success(data: Dict) -> JsonResponse:
    ''' '''
    resp = {'success': True}
    resp.update(data)
    return JsonResponse(resp)


def _return_error(error: str) -> JsonResponse:
    ''' '''
    return JsonResponse({'message': error, 'success': False})
