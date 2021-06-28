var moveOver = false;
function redraw_users(data) {
    const table = $('#users');
    table.empty();
    table.append(
        `<tr>
        <th>User</th>
        <th>Status</th>
        <th>&nbsp;</th>
        </tr>`
    );
    data.users.forEach(function(user){
        table.append(
            `<tr>
             <td>${user.email}</td>
             <td>${user.status}</td>
             <td><a href="#" onclick="invite(${user.id})">Invite</a></td>
             </tr>`
        );
    });
    setTimeout(update_users, 10000);
}
function update_users() {
    do_request('GET', '/users/ready', null, redraw_users);
}
function redraw_invites(data) {
    const table = $('#invites');
    table.empty();
    table.append(
        `<tr>
        <th>User</th>
        <th>&nbsp;</th>
        <th>&nbsp;</th>
        </tr>`
    );
    data.games.forEach(function(game){
        table.append(
            `<tr>
             <td>${game.user}</td>
             <td><a href="#" onclick="accept(${game.id})">Accept</a></td>
             <td><a href="#" onclick="decline(${game.id})">Decline</a></td>
             </tr>`
        );
    });
    setTimeout(update_invites, 5000);
}
function update_invites() {
    do_request('GET', '/games/invited', null, redraw_invites);
}
function check_accepted() {
    do_request('GET', '/games/accepted', null, start_game);
}
function decline(gameId) {
    do_request('POST', '/games/' + gameId + '/decline');
}
function invite(userId) {
    do_request('POST', '/games/invite', {user_id: userId});
    setTimeout(check_accepted, 2000);
    return false;
}
function accept(gameId) {
    do_request('POST', '/games/' + gameId + '/accept', null, start_game);
    return false;
}
function start_game(data) {
    if (data.game_id) {
        location = '/games/' + data.game_id;
    }
    else {
        setTimeout(check_accepted, 2000);
    }
}
function move(gameId, moveId, chosen) {
    if (moveOver) {
        return;
    }
    do_request('POST', '/games/' + gameId + '/' + moveId + '/move', {chosen: chosen}, draw_your_move);
    watch_move(gameId, moveId);
    return false;
}
function draw_your_move(data) {
    moveOver = true;
    $('#yours').html('<h3>Your move: ' + data.chosen + '</h3>');
}
function check_move(data) {
    if (data.enemy_move) {
        const res = data.result == 0 ? 'stalemate' : (data.result == 1 ? 'you won' : 'you lose');
        $('#enemy').html('<h3>Enemy move: ' + data.enemy_move + '</h3>');
        $('#victor').html('<h3>' + res + '</h3>');
        setTimeout(function(){location.reload();}, 5000);
    }
    else {
        setTimeout(watch_move, 2000, data.game_id, data.move_id);
    }
}
function watch_move(gameId, moveId) {
    do_request('GET', '/games/' + gameId + '/' + moveId + '/check', null, check_move);
}
function do_request(method, url, data, func) {
    $.ajax({
        type: method,
        url: url,
        dataType: 'json',
        data: data
    })
    .done(function(data) {
        if (data.success) {
            if (func) {
                func(data);
            }
        }
        else {
             alert(data.message ? data.message : 'Error from server');
        }
    })
    .fail(function() {
        alert('Error connecting server');
    });
}