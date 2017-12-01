const NAG_NULL = 0;
const NAG_GOOD_MOVE = 1;
//"""A good move. Can also be indicated by ``!`` in PGN notation."""
const NAG_MISTAKE = 2;
//"""A mistake. Can also be indicated by ``?`` in PGN notation."""
const NAG_BRILLIANT_MOVE = 3;
//"""A brilliant move. Can also be indicated by ``!!`` in PGN notation."""
const NAG_BLUNDER = 4;
//"""A blunder. Can also be indicated by ``??`` in PGN notation."""
const NAG_SPECULATIVE_MOVE = 5;
//"""A speculative move. Can also be indicated by ``!?`` in PGN notation."""
const NAG_DUBIOUS_MOVE = 6;
//"""A dubious move. Can also be indicated by ``?!`` in PGN notation."""

var simpleNags = {'1': '!', '2': '?', '3': '!!', '4': '??', '5': '!?', '6': '?!', '7': '&#9633', '8': '&#9632',
    '11': '=', '13': '&infin;', '14': '&#10866', '15': '&#10865', '16': '&plusmn;', '17': '&#8723',
    '18': '&#43; &minus;', '19': '&minus; &#43;', '36': '&rarr;','142': '&#8979','146': 'N'};


const NAG_FORCED_MOVE = 7;
const NAG_SINGULAR_MOVE = 8;
const NAG_WORST_MOVE = 9;
const NAG_DRAWISH_POSITION = 10;
const NAG_QUIET_POSITION = 11;
const NAG_ACTIVE_POSITION = 12;
const NAG_UNCLEAR_POSITION = 13;
const NAG_WHITE_SLIGHT_ADVANTAGE = 14;
const NAG_BLACK_SLIGHT_ADVANTAGE = 15;

//# TODO: Add more constants for example from
//# https://en.wikipedia.org/wiki/Numeric_Annotation_Glyphs

const NAG_WHITE_MODERATE_COUNTERPLAY = 132;
const NAG_BLACK_MODERATE_COUNTERPLAY = 133;
const NAG_WHITE_DECISIVE_COUNTERPLAY = 134;
const NAG_BLACK_DECISIVE_COUNTERPLAY = 135;
const NAG_WHITE_MODERATE_TIME_PRESSURE = 136;
const NAG_BLACK_MODERATE_TIME_PRESSURE = 137;
const NAG_WHITE_SEVERE_TIME_PRESSURE = 138;
const NAG_BLACK_SEVERE_TIME_PRESSURE = 139;

const START_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';

var boardStatusEl = $('#BoardStatus'),
    dgtClockStatusEl = $('#DGTClockStatus'),
    dgtClockTextEl = $('#DGTClockText'),
    pgnEl = $('#pgn');

var gameHistory, fenHash, currentPosition;
const BACKEND_SERVER_PREFIX = 'http://drshivaji.com:3334';
//const BACKEND_SERVER_PREFIX = "http://localhost:7777";

// remote begin
var remote_server_prefix = "drshivaji.com:9876";
//var remote_server_prefix = "localhost:7766";
var remote_ws = null;
// remote end

fenHash = {};

currentPosition = {};
currentPosition.fen = START_FEN;

gameHistory = currentPosition;
gameHistory.gameHeader = '';
gameHistory.result = '';
gameHistory.variations = [];

var setupBoardFen = START_FEN;
var dataTableFen = START_FEN;
var chessGameType = 0; // 0=Standard ; 1=Chess960


function removeHighlights() {
    chessground1.setShapes([]);
}

function highlightBoard(ucimove, play) {
    //removeHighlights();
    var move = ucimove.match(/.{2}/g);
    var brush = 'green';
    if( play === 'computer') {
        brush = 'yellow';
    }
    if( play === 'review') {
        brush = 'blue';
    }
    var shapes = {orig: move[0], dest: move[1], brush: brush};
    chessground1.setShapes([shapes]);
}

function figurinizeMove(move) {
    if (!move) { return; }
    move = move.replace('N', '&#9816;');
    move = move.replace('B', '&#9815;');
    move = move.replace('R', '&#9814;');
    move = move.replace('K', '&#9812;');
    move = move.replace('Q', '&#9813;');
    move = move.replace('X', '&#9888;'); // error code
    return move;
}

var bookDataTable = $('#BookTable').DataTable( {
    'processing': true,
    'paging': false,
    'info': false,
    'searching': false,
    'order': [[2, 'desc']],
    'select': {
        'style': 'os',
        'selector': 'td:not(.control)'
    },
    'responsive': {
        'details': {
           'type': 'column',
           'target': 0
        }
      },
      'columnDefs': [
         {
           'data': null,
           'defaultContent': '',
           'className': 'control',
           'orderable': false,
           'targets': 0
         }
      ],
    'ajax': {
        'url': BACKEND_SERVER_PREFIX + '/query',
        'dataSrc': 'records',
        'dataType': 'jsonp',
        'data': function ( d ) {
            d.action = 'get_book_moves';
            d.fen = dataTableFen;
            d.db = '#ref';
        }
    },
    'columns': [
        {data: null},
        {data: 'move', render: function ( data, type, row ) { return figurinizeMove(data); } },
        {data: 'freq', render: $.fn.dataTable.render.intlNumber()},
        {data: 'pct', render: $.fn.dataTable.render.number( ',', '.', 2, '', '%' )},
        {data: 'draws', render: $.fn.dataTable.render.intlNumber()},
        {data: 'wins', render: $.fn.dataTable.render.intlNumber()},
        {data: 'losses', render: $.fn.dataTable.render.intlNumber()}
    ]
});
bookDataTable.on('select', function(e, dt, type, indexes ) {
    if( type === 'row') {
        var data = bookDataTable.rows(indexes).data().pluck('move')[0];
        stopAnalysis();
        var tmpGame = createGamePointer();
        var move = tmpGame.move(data);
        updateCurrentPosition(move, tmpGame);
        updateChessGround();
        updateStatus();
        removeHighlights();
    }
});

var gameDataTable = $('#GameTable').DataTable( {
    'processing': true,
    'serverSide': true,
    'paging': true,
    'info': true,
    'searching': true,
    'order': [[1, 'desc']],
    'select': {
        'style': 'os',
        'selector': 'td:not(.control)'
    },
    'responsive': {
        'details': {
           'type': 'column',
           'target': 0
        }
      },
      'columnDefs': [
          {
              'data': null,
              'defaultContent': '',
              'className': 'control',
              'orderable': false,
              'targets': 0
          },
          {
              'targets': [1],
              'visible': false
          }
      ],
    'ajax': {
        'url': BACKEND_SERVER_PREFIX + '/query',
        'dataSrc': 'records',
        'dataType': 'jsonp',
        'data': function ( d ) {
            d.action = 'get_games';
            d.fen = dataTableFen;
            d.db = '#ref';
        },
        'error': function (xhr, error, thrown) {
            console.warn(xhr);
        }
    },
    'initComplete': function() {
        var searchInput = $('div.dataTables_filter input');
        searchInput.unbind();
        searchInput.bind('keyup', function(e) {
            if(this.value.length > 2) {
                gameDataTable.search( this.value ).draw();
            }
            if(this.value === '') {
                gameDataTable.search('').draw();
            }
        });
    },
    'columns': [
        {data: null},
        {data: 'id'},
        {data: 'white'},
        {data: 'white_elo'},
        {data: 'black'},
        {data: 'black_elo'},
        {data: 'result'},
        {data: 'date'},
        {data: 'event'},
        {data: 'site'},
        {data: 'eco'}
    ]
});
gameDataTable.on('xhr.dt', function(e, settings, json, xhr) {
    if(json) {
        json['recordsTotal'] = json['totalRecordCount'];
        json['recordsFiltered'] = json['queryRecordCount'];
        delete json['totalRecordCount'];
        delete json['queryRecordCount'];
    }
});
gameDataTable.on('select', function(e, dt, type, indexes ) {
    if( type === 'row') {
        var data = gameDataTable.rows(indexes).data().pluck('id')[0];
        $.ajax({
            dataType: 'jsonp',
            url: BACKEND_SERVER_PREFIX + '/query?callback=game_callback',
            data: {
                action: 'get_game_content',
                game_num: data,
                db: '#ref'
            }
        }).done(function(data) {
            loadGame(data['pgn']);
            updateStatus();
            removeHighlights();
        });
    }
});

// do not pick up pieces if the game is over
// only pick up pieces for the side to move
function createGamePointer() {
    var tmpGame;

    if (currentPosition && currentPosition.fen) {
        tmpGame = new Chess(currentPosition.fen, chessGameType);
    }
    else {
        tmpGame = new Chess(setupBoardFen, chessGameType);
    }
    return tmpGame;
}

function stripFen(fen) {
    var strippedFen = fen.replace(/\//g, '');
    strippedFen = strippedFen.replace(/ /g, '');
    return strippedFen;
}

String.prototype.trim = function() {
    return this.replace(/\s*$/g, '');
};

function WebExporter(columns) {
    this.lines = [];
    this.columns = columns;
    this.current_line = '';
    this.flush_current_line = function() {
        if (this.current_line) {
            this.lines.append(this.current_line.trim());
            this.current_line = '';
        }
    };

    this.write_token = function(token) {
        if (this.columns && this.columns - this.current_line.length < token.length) {
            this.flush_current_line();
        }
        this.current_line += token;
    };

    this.write_line = function(line) {
        this.flush_current_line();
        this.lines.push(line.trim());
    };

    this.start_game = function() {
    };

    this.end_game = function() {
        this.write_line();
    };

    this.start_headers = function() {
    };

    this.end_headers = function() {
        this.write_line();
    };

    this.start_variation = function() {
        this.write_token('<span class="gameVariation"> [ ');
    };

    this.end_variation = function() {
        this.write_token(' ] </span>');
    };

    this.put_starting_comment = function(comment) {
        this.put_comment(comment);
    };

    this.put_comment = function(comment) {
        this.write_token('<span class="gameComment"><a href="#" class="comment"> ' + comment + ' </a></span>');
    };

    this.put_nags = function(nags) {
        if (nags) {
            nags = nags.sort();

            for (var i = 0; i < nags.length; i++) {
                this.put_nag(nags[i]);
            }
        }
    };

    this.put_nag = function(nag) {
        var int_nag = parseInt(nag);
        if (simpleNags[int_nag]) {
            this.write_token(" " + simpleNags[int_nag] + " ");
        }
        else {
            this.write_token("$" + String(nag) + " ");
        }
    };

    this.put_fullmove_number = function(turn, fullmove_number, variation_start) {
        if (turn === 'w') {
            this.write_token(String(fullmove_number) + ". ");
        }
        else if (variation_start) {
            this.write_token(String(fullmove_number) + "... ");
        }
    };

    this.put_move = function(board, m) {
        var old_fen = board.fen();
        var tmp_board = new Chess(old_fen, chessGameType);
        var out_move = tmp_board.move(m);
        var fen = tmp_board.fen();
        var stripped_fen = stripFen(fen);
        if (!out_move) {
            console.warn('put_move error');
            console.log(board.ascii());
            console.log(board.moves());
            console.log(tmp_board.ascii());
            console.log(m);
            out_move = {'san': 'X' + m.from + m.to};
        }
        this.write_token('<span class="gameMove' + (board.fullmove_number) + '"><a href="#" class="fen" data-fen="' + fen + '" id="' + stripped_fen + '"> ' + figurinizeMove(out_move.san) + ' </a></span>');
    };

    this.put_result = function(result) {
        this.write_token(result + " ");
    };

    // toString override added to prototype of Foo class
    this.toString = function() {
        if (this.current_line) {
            var tmp_lines = this.lines.slice(0);
            tmp_lines.push(this.current_line.trim());

            return tmp_lines.join("\n").trim();
        }
        else {
            return this.lines.join("\n").trim();
        }
    };
}

function PgnExporter(columns) {
    this.lines = [];
    this.columns = columns;
    this.current_line = "";
    this.flush_current_line = function() {
        if (this.current_line) {
            this.lines.append(this.current_line.trim());
            this.current_line = "";
        }
    };

    this.write_token = function(token) {
        if (this.columns && this.columns - this.current_line.length < token.length) {
            this.flush_current_line();
        }
        this.current_line += token;
    };

    this.write_line = function(line) {
        this.flush_current_line();
        this.lines.push(line.trim());
    };

    this.start_game = function() {
    };

    this.end_game = function() {
        this.write_line();
    };

    this.start_headers = function() {
    };

    this.put_header = function(tagname, tagvalue) {
        this.write_line("[{0} \"{1}\"]".format(tagname, tagvalue));
    };

    this.end_headers = function() {
        this.write_line();
    };

    this.start_variation = function() {
        this.write_token("( ");
    };

    this.end_variation = function() {
        this.write_token(") ");
    };

    this.put_starting_comment = function(comment) {
        this.put_comment(comment);
    };

    this.put_comment = function(comment) {
        this.write_token("{ " + comment.replace("}", "").trim() + " } ");
    };

    this.put_nags = function(nags) {
        if (nags) {
            nags = nags.sort();

            for (var i = 0; i < nags.length; i++) {
                this.put_nag(nags[i]);
            }
        }
    };

    this.put_nag = function(nag) {
        this.write_token("$" + String(nag) + " ");
    };

    this.put_fullmove_number = function(turn, fullmove_number, variation_start) {
        if (turn === 'w') {
            this.write_token(String(fullmove_number) + ". ");
        }
        else if (variation_start) {
            this.write_token(String(fullmove_number) + "... ");
        }
    };

    this.put_move = function(board, m) {
        var tmp_board = new Chess(board.fen(), chessGameType);
        var out_move = tmp_board.move(m);
        if (!out_move) {
            console.warn('put_move error');
            console.log(tmp_board.ascii());
            console.log(m);
            out_move = {'san': 'X' + m.from + m.to};
        }
        this.write_token(out_move.san + " ");
    };

    this.put_result = function(result) {
        this.write_token(result + " ");
    };

    // toString override added to prototype of Foo class
    this.toString = function() {
        if (this.current_line) {
            var tmp_lines = this.lines.slice(0);
            tmp_lines.push(this.current_line.trim());

            return tmp_lines.join("\n").trim();
        }
        else {
            return this.lines.join("\n").trim();
        }
    };
}

function exportGame(root_node, exporter, include_comments, include_variations, _board, _after_variation) {
    if (_board === undefined) {
        _board = new Chess(root_node.fen, chessGameType);
    }

    // append fullmove number
    if (root_node.variations && root_node.variations.length > 0) {
        _board.fullmove_number = Math.ceil(root_node.variations[0].half_move_num / 2);

        var main_variation = root_node.variations[0];
        exporter.put_fullmove_number(_board.turn(), _board.fullmove_number, _after_variation);
        exporter.put_move(_board, main_variation.move);
        if (include_comments) {
            exporter.put_nags(main_variation.nags);
            // append comment
            if (main_variation.comment) {
                exporter.put_comment(main_variation.comment);
            }
        }
    }

    // Then export sidelines.
    if (include_variations && root_node.variations) {
        for (var j = 1; j < root_node.variations.length; j++) {
            var variation = root_node.variations[j];
            exporter.start_variation();

            if (include_comments && variation.starting_comment) {
                exporter.put_starting_comment(variation.starting_comment);
            }
            exporter.put_fullmove_number(_board.turn(), _board.fullmove_number, true);

            exporter.put_move(_board, variation.move);

            if (include_comments) {
                // Append NAGs.
                exporter.put_nags(variation.nags);

                // Append the comment.
                if (variation.comment) {
                    exporter.put_comment(variation.comment);
                }
            }
            // Recursively append the next moves.
            _board.move(variation.move);
            exportGame(variation, exporter, include_comments, include_variations, _board, false);
            _board.undo();

            // End variation.
            exporter.end_variation();
        }
    }

    // The mainline is continued last.
    if (root_node.variations && root_node.variations.length > 0) {
        main_variation = root_node.variations[0];

        // Recursively append the next moves.
        _board.move(main_variation.move);
        _after_variation = (include_variations && (root_node.variations.length > 1));
        exportGame(main_variation, exporter, include_comments, include_variations, _board, _after_variation);
        _board.undo();
    }
}

function writeVariationTree(dom, gameMoves, gameHistoryEl) {
    $(dom).html(gameHistoryEl.gameHeader + '<div class="gameMoves">' + gameMoves + ' <span class="gameResult">' + gameHistoryEl.result + '</span></div>');
}

// update the board position after the piece snap
// for castling, en passant, pawn promotion
function updateCurrentPosition(move, tmpGame) {
    var foundMove = false;
    if (currentPosition && currentPosition.variations) {
        for (var i = 0; i < currentPosition.variations.length; i++) {
            if (move.san === currentPosition.variations[i].move.san) {
                currentPosition = currentPosition.variations[i];
                foundMove = true;
            }
        }
    }
    if (!foundMove) {
        var __ret = addNewMove({'move': move}, currentPosition, tmpGame.fen());
        currentPosition = __ret.node;
        var exporter = new WebExporter();
        exportGame(gameHistory, exporter, true, true, undefined, false);
        writeVariationTree(pgnEl, exporter.toString(), gameHistory);
    }
}

var updateStatus = function() {
    var status = '';
    $('.fen').unbind('click', goToGameFen).one('click', goToGameFen);

    var moveColor = 'White';
    var tmpGame = createGamePointer();
    var fen = tmpGame.fen();

    var strippedFen = stripFen(fen);

    if (tmpGame.turn() === 'b') {
        moveColor = 'Black';
        $('#sidetomove').html("<i class=\"fa fa-square fa-lg \"></i>");
    }
    else {
        $('#sidetomove').html("<i class=\"fa fa-square-o fa-lg \"></i>");
    }

    // checkmate?
    if (tmpGame.in_checkmate() === true) {
        status = moveColor + ' is in checkmate';
    }
    // draw?
    else if (tmpGame.in_draw() === true) {
        status = 'Drawn position';
    }
    // game still on
    else {
        status = moveColor + ' to move';
        // check?
        if (tmpGame.in_check() === true) {
            status += ' (in check)';
        }
    }

    boardStatusEl.html(status);
    if (window.analysis) {
        analyze(true);
    }

    dataTableFen = fen;
    bookDataTable.ajax.reload();
    gameDataTable.ajax.reload();

    if ($('#' + strippedFen).position()) {
        pgnEl.scrollTop(0);
        var y_position = $('#' + strippedFen).position().top;
        pgnEl.scrollTop(y_position);
    }
};

function toDests(chess) {
    var dests = {};
    chess.SQUARES.forEach(function (s) {
        var ms = chess.moves({ square: s, verbose: true });
        if (ms.length)
            dests[s] = ms.map(function (m) { return m.to; });
    });
    return dests;
}

function toColor(chess) {
    return (chess.turn() === 'w') ? 'white' : 'black';
}

var onSnapEnd = function(source, target) {
    stopAnalysis();
    var tmpGame = createGamePointer();

    if(!currentPosition) {
        currentPosition = {};
        currentPosition.fen = tmpGame.fen();
        gameHistory = currentPosition;
        gameHistory.gameHeader = '<h4>Player (-) vs Player (-)</h4><h5>Board game</h5>';
        gameHistory.result = '*';
    }

    var move = tmpGame.move({
        from: source,
        to: target,
        promotion: 'q' // NOTE: always promote to a pawn for example simplicity
    });
    updateCurrentPosition(move, tmpGame);
    updateChessGround();
    updateStatus();
    $.post('/channel', {action: 'move', fen: currentPosition.fen, source: source, target: target}, function(data) {
    });
};

function updateChessGround() {
    var tmpGame = createGamePointer();

    chessground1.set({
        fen: currentPosition.fen,
        turnColor: toColor(tmpGame),
        movable: {
            color: toColor(tmpGame),
            dests: toDests(tmpGame)
        }
    });
}

function playOtherSide() {
    return onSnapEnd;
}

var cfg3 = {
            movable: {
                color: 'white',
                free: false,
                dests: toDests(Chess())
            }
        };

var chessground1 = new Chessground(document.getElementById('board'), cfg3 );

chessground1.set({
    movable: { events: { after: playOtherSide() } }
});

$(window).resize(function() {
    chessground1.redrawAll();
});

function addNewMove(m, current_position, fen, props) {
    var node = {};
    node.variations = [];

    node.move = m.move;
    node.previous = current_position;
    node.nags = [];
    if (props) {
        if (props.comment) {
            node.comment = props.comment;
        }
        if (props.starting_comment) {
            node.starting_comment = props.starting_comment;
        }
    }

    if (current_position && current_position.previous) {
        node.half_move_num = node.previous.half_move_num + 1;
    }
    else {
        node.half_move_num = 1;
    }
    node.fen = fen;
    if ($.isEmptyObject(fenHash)) {
        fenHash['first'] = node.previous;
        node.previous.fen = setupBoardFen;
    }
    fenHash[node.fen] = node;
    if (current_position) {
        if (!current_position.variations) {
            current_position.variations = [];
        }
        current_position.variations.push(node);
    }
    return {node: node, position: current_position};
}

function loadGame(pgn_lines) {
    fenHash = {};

    var curr_fen;
    if (currentPosition) {
        curr_fen = currentPosition.fen;
    }
    else {
        curr_fen = START_FEN;
    }

    gameHistory.previous = null;
    currentPosition = {};
    var current_position = currentPosition;
    gameHistory = current_position;

    var game_body_regex = /(%.*?[\n\r])|(\{[\s\S]*?\})|(\$[0-9]+)|(\()|(\))|(\*|1-0|0-1|1\/2-1\/2)|([NBKRQ]?[a-h]?[1-8]?[\-x]?[a-h][1-8](?:=?[nbrqNBRQ])?[\+]?|--|O-O(?:-O)?|0-0(?:-0)?)|([\?!]{1,2})/g;
    var game_header_regex = /\[([A-Za-z0-9]+)\s+\"(.*)\"\]/;

    var line;
    var parsed_headers = false;
    var game_headers = {};
    var game_body = '';
    for (var j = 0; j < pgn_lines.length; j++) {
        line = pgn_lines[j];
        // Parse headers first, then game body
        if (!parsed_headers) {
            if ((result = game_header_regex.exec(line)) !== null) {
                game_headers[result[1]] = result[2];
            }
            else {
                parsed_headers = true;
            }
        }
        if (parsed_headers) {
            game_body += line + "\n";
        }
    }

    var tmpGame;
    if ('FEN' in game_headers && 'SetUp' in game_headers) {
        if ('Variant' in game_headers && 'Chess960' === game_headers['Variant']) {
            chessGameType = 1; // values from chess960.js
        } else {
            chessGameType = 0;
        }
        tmpGame = new Chess(game_headers['FEN'], chessGameType);
        setupBoardFen = game_headers['FEN'];
    }
    else {
        tmpGame = new Chess();
        setupBoardFen = START_FEN;
        chessGameType = 0;
    }

    var board_stack = [tmpGame];
    var variation_stack = [current_position];
    var last_board_stack_index;
    var last_variation_stack_index;

    var in_variation = false;
    var starting_comment = '';

    var result;
    while ((result = game_body_regex.exec(game_body)) !== null) {

        var token = result[0];
        var comment;

        if (token === '1-0' || token === '0-1' || token === '1/2-1/2' || token === '*') {
            game_headers['Result'] = token;
        }
        else if (token[0] === '{') {
            last_variation_stack_index = variation_stack.length - 1;

            comment = token.substring(1, token.length - 1);
            comment = comment.replace(/\n|\r/g, " ");

            if (in_variation || !variation_stack[last_variation_stack_index].previous) {
                if (variation_stack[last_variation_stack_index].comment) {
                    variation_stack[last_variation_stack_index].comment = variation_stack[last_variation_stack_index].comment + " " + comment;
                }
                else {
                    variation_stack[last_variation_stack_index].comment = comment;
                }
                comment = undefined;
            }
            else {
                if (starting_comment.length > 0) {
                    comment = starting_comment + " " + comment;
                }
                starting_comment = comment;
                comment = undefined;
            }
        }
        else if (token === '(') {
            last_board_stack_index = board_stack.length - 1;
            last_variation_stack_index = variation_stack.length - 1;

            if (variation_stack[last_variation_stack_index].previous) {
                variation_stack.push(variation_stack[last_variation_stack_index].previous);
                last_variation_stack_index += 1;
                board_stack.push(Chess(variation_stack[last_variation_stack_index].fen));
                in_variation = false;
            }
        }
        else if (token === ')') {
            if (variation_stack.length > 1) {
                variation_stack.pop();
                board_stack.pop();
            }
        }
        else if (token[0] === '$') {
            variation_stack[variation_stack.length - 1].nags.push(token.slice(1));
        }
        else if (token === '?') {
            variation_stack[variation_stack.length - 1].nags.push(NAG_MISTAKE);
        }
        else if (token === '??') {
            variation_stack[variation_stack.length - 1].nags.push(NAG_BLUNDER);
        }
        else if (token === '!') {
            variation_stack[variation_stack.length - 1].nags.push(NAG_GOOD_MOVE);
        }
        else if (token === '!!') {
            variation_stack[variation_stack.length - 1].nags.push(NAG_BRILLIANT_MOVE);
        }
        else if (token === '!?') {
            variation_stack[variation_stack.length - 1].nags.push(NAG_SPECULATIVE_MOVE);
        }
        else if (token === '?!') {
            variation_stack[variation_stack.length - 1].nags.push(NAG_DUBIOUS_MOVE);
        }
        else {
            last_board_stack_index = board_stack.length - 1;
            last_variation_stack_index = variation_stack.length - 1;

            var preparsed_move = token;
            var move = board_stack[last_board_stack_index].move(preparsed_move, {sloppy: true});
            in_variation = true;
            if (move === null) {
                console.log('Unparsed move:');
                console.log(preparsed_move);
                console.log('Fen: ' + board_stack[last_board_stack_index].fen());
                console.log('faulty line: ' + line);
                console.log('Chess960: ' + chessGameType)
            }

            var props = {};
            if (comment) {
                props.comment = comment;
                comment = undefined;
            }
            if (starting_comment) {
                props.starting_comment = starting_comment;
                starting_comment = '';
            }

            var __ret = addNewMove({'move': move}, variation_stack[last_variation_stack_index], board_stack[last_board_stack_index].fen(), props);
            variation_stack[last_variation_stack_index] = __ret.node;
        }
    }
    fenHash['last'] = fenHash[tmpGame.fen()];

    if (curr_fen === undefined) {
        currentPosition = fenHash['first'];
    }
    else {
        currentPosition = fenHash[curr_fen];
    }
    setHeaders(game_headers);
    $('.fen').unbind('click', goToGameFen).one('click', goToGameFen);
}

function getFullGame() {
    var gameHeader = getPgnGameHeader(gameHistory.originalHeader);
    if (gameHeader.length <= 1) {
        gameHistory.originalHeader = {
            'White': '*',
            'Black': '*',
            'Event': '?',
            'Site': '?',
            'Date': '?',
            'Round': '?',
            'Result': '*',
            'BlackElo' : '-',
            'WhiteElo' : '-',
            'Time' : '00:00:00'
        };
        gameHeader = getPgnGameHeader(gameHistory.originalHeader);
    }

    var exporter = new PgnExporter();
    exportGame(gameHistory, exporter, true, true, undefined, false);
    var exporterContent = exporter.toString();
    return gameHeader + exporterContent;
}

function getPgnGameHeader(h) {
    var gameHeaderText = '';
    for (var key in h) {
        // hasOwnProperty ensures that inherited properties are not included
        if (h.hasOwnProperty(key)) {
            var value = h[key];
            gameHeaderText += "[" + key + " \"" + value + "\"]\n";
        }
    }
    gameHeaderText += "\n";
    return gameHeaderText;
}

function getWebGameHeader(h) {
    var gameHeaderText = '';
    gameHeaderText += '<h4>' + h.White + ' (' + h.WhiteElo + ') vs ' + h.Black + ' (' + h.BlackElo + ')</h4>';
    gameHeaderText += '<h5>' + h.Event + ', ' + h.Site + ' ' + h.Date + '</h5>';
    return gameHeaderText;
}

function download() {
    var content = getFullGame();
    var dl = document.createElement('a');
    dl.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(content));
    dl.setAttribute('download', 'game.pgn');
    document.body.appendChild(dl);
    dl.click();
}

function newBoard(fen) {
    stopAnalysis();

    currentPosition = {};
    currentPosition.fen = fen;

    setupBoardFen = fen;
    gameHistory = currentPosition;
    gameHistory.gameHeader = '';
    gameHistory.result = '';
    gameHistory.variations = [];

    updateChessGround();
    updateStatus();
}

function broadcastPosition() {
    if (currentPosition) {
        var content = getFullGame();
        $.post('/channel', {action: 'broadcast', fen: currentPosition.fen, pgn: content}, function (data) {
        });
    }
}

function clockButton0() {
    $.post('/channel', {action: 'clockbutton', button: 0}, function (data) {
    });
}

function clockButton1() {
    $.post('/channel', {action: 'clockbutton', button: 1}, function (data) {
    });
}

function clockButton2() {
    $.post('/channel', {action: 'clockbutton', button: 2}, function (data) {
    });
}

function clockButton3() {
    $.post('/channel', {action: 'clockbutton', button: 3}, function (data) {
    });
}

function clockButton4() {
    $.post('/channel', {action: 'clockbutton', button: 4}, function (data) {
    });
}

function toggleLeverButton() {
    $('#leverDown').toggle();
    $('#leverUp').toggle();
    var button = 0x40;
    if($('#leverDown').is(':hidden')) {
        button = -0x40;
    }
    $.post('/channel', {action: 'clockbutton', button: button}, function (data) {
    });
}

function clockButtonPower() {
    $.post('/channel', {action: 'clockbutton', button: 0x11}, function (data) {
    });
}

function sendConsoleCommand() {
    var cmd = $('#inputConsole').val();
    $('#consoleLogArea').append('<li>' + cmd + '</li>');
    $.post('/channel', {action: 'command', command: cmd}, function (data) {
    });
}

function getFenToConsole() {
    var tmpGame = createGamePointer();
    $('#inputConsole').val(tmpGame.fen());
}

function toggleConsoleButton() {
    $('#Console').toggle();
    $('#Database').toggle();
}

function goToPosition(fen) {
    stopAnalysis();
    currentPosition = fenHash[fen];
    if (!currentPosition) {
        return false;
    }
    updateChessGround();
    updateStatus();
    return true;
}

function goToGameFen() {
    var fen = $(this).attr('data-fen');
    goToPosition(fen);
    removeHighlights();
}

function goToStart() {
    stopAnalysis();
    currentPosition = gameHistory;
    updateChessGround();
    updateStatus();
}

function goToEnd() {
    stopAnalysis();
    if (fenHash.last) {
        currentPosition = fenHash.last;
        updateChessGround();
    }
    updateStatus();
}

function goForward() {
    stopAnalysis();
    if (currentPosition && currentPosition.variations[0]) {
        currentPosition = currentPosition.variations[0];
        if (currentPosition) {
            updateChessGround();
        }
    }
    updateStatus();
}

function goBack() {
    stopAnalysis();
    if (currentPosition && currentPosition.previous) {
        currentPosition = currentPosition.previous;
        updateChessGround();
    }
    updateStatus();
}

function boardFlip() {
    chessground1.toggleOrientation();
}

// remote begin
function sendRemoteMsg() {
    if(remote_ws) {
        var text_msg_obj = {"event": "text", "payload": $('#remoteText').val()};
        $("#remoteText").val("");
        $("#remoteText").focus();
        var jmsg = JSON.stringify(text_msg_obj);
        remote_ws.send(jmsg);
    } else {
        console.log('cant send message cause of closed connection!');
    }
}

function sendRemoteFen(data) {
    if(remote_ws) {
        var text_msg_obj = {"event": "Fen", "move": data.move, "fen": data.fen, "play": data.play};
        var jmsg = JSON.stringify(text_msg_obj);
        remote_ws.send(jmsg);
    } else {
        console.log('cant send message cause of closed connection!');
    }
}

function sendRemoteGame(fen) {
    if(remote_ws) {
        var text_msg_obj = {"event": "Game", "fen": fen};
        var jmsg = JSON.stringify(text_msg_obj);
        remote_ws.send(jmsg);
    } else {
        console.log('cant send message cause of closed connection!');
    }
}

function setInsideRoom() {
    $('#leaveRoomBtn').removeAttr('disabled').show();
    $('#SendTextRemoteBtn').removeAttr('disabled');
    $('#enterRoomBtn').attr('disabled', 'disabled').hide();
    $('#RemoteRoom').attr('disabled', 'disabled');
    $('#RemoteNick').attr('disabled', 'disabled');
    $('#broadcastBtn').removeAttr('disabled');

    $.post('/channel', {action: 'room', room: 'inside'}, function (data) {
    });
}

function setOutsideRoom() {
    $('#leaveRoomBtn').attr('disabled', 'disabled').hide();
    $('#SendTextRemoteBtn').attr('disabled', 'disabled');
    $('#enterRoomBtn').removeAttr('disabled').show();
    $('#RemoteRoom').removeAttr('disabled');
    $('#RemoteNick').removeAttr('disabled');
    $('#broadcastBtn').attr('disabled', 'disabled');

    $.post('/channel', {action: 'room', room: 'outside'}, function (data) {
    });
}

function leaveRoom() {
    setOutsideRoom();
    if(remote_ws) {
        remote_ws.close();
    }
}

function enterRoom() {
    $.ajax({
        dataType: 'jsonp',
        url: 'http://' + remote_server_prefix,
        data: {
            room: $('#RemoteRoom').val(),
            nick: $('#RemoteNick').val()
        }
    }).done(function(data) {
        console.log(data);
        if(data.result === 'OK') {
            setInsideRoom();

            remote_ws = new WebSocket("ws://" + remote_server_prefix + "/ws/" + data.client_id);

            remote_ws.onopen = function (event) {
                console.log("RemoteChessServerSocket opened");
            };

            remote_ws.onclose = function () {
                console.log("RemoteChessServerSocket closed");
                setOutsideRoom();
            };

            remote_ws.onerror = function (event) {
                console.warn("RemoteChessServerSocket error");
                dgtClockStatusEl.html(event.data);
            };

            remote_ws.onmessage = receive_message;
        }

    }).fail(function(jqXHR, textStatus) {
        console.warn('Failed ajax request');
        console.log(jqXHR);
        dgtClockStatusEl.html(textStatus);
    });
}

function format_username(username) {
    if(username === $('#RemoteNick').val()) {
        return '<span style="color: green;">' + username + '</span>';
    } else {
        return '<span style="color: red;">' + username + '</span>';
    }
}

function receive_message(wsevent) {
    console.log("received message: " + wsevent.data);
    var msg_obj = $.parseJSON(wsevent.data);
    var logging = $('#consoleLogArea');
    var username = format_username(msg_obj.username);
    switch (msg_obj.event) {
        case "join":
            logging.append('<li>' + username + ' => Joined room ' + msg_obj.payload + '</li>');
            break;
        case "leave":
            logging.append('<li>' + username + ' => Left room ' + msg_obj.payload + '</li>');
            break;
        case "nick_list":
            logging.append('<li>' + username + ' => Current users: ' + msg_obj.payload.toString() + '</li>');
            break;
        case "text":
            logging.append('<li>' + username + ' => ' +  msg_obj.payload + '</li>');
            break;
        // picochess events!
        case 'Clock':
            logging.append('<li>' + username + ' => Clock: ' + msg_obj.msg + '</li>');
            break;
        case 'Light':
            logging.append('<li>' + username + ' => Light: ' + msg_obj.move + '</li>');
            break;
        case 'Clear':
            logging.append('<li>' + username + ' => Clear' + '</li>');
            break;
        case 'Fen':
            logging.append('<li>' + username + ' => Fen: ' + msg_obj.fen + ' move: ' + msg_obj.move + ' play: ' + msg_obj.play + '</li>');
            break;
        case 'Game':
            logging.append('<li>' + username + ' => NewGame: ' + msg_obj.fen + '</li>');
            break;
        case 'Message':
            logging.append('<li>' + username + ' => Message: ' + msg_obj.msg + '</li>');
            break;
        case 'Status':
            logging.append('<li>' + username + ' => ClockStatus: ' + msg_obj.msg + '</li>');
            break;
        case 'Header':
            logging.append('<li>' + username + ' => Header: ' + msg_obj.headers.toString() + '</li>');
            break;
        case 'Title':
            logging.append('<li>' + username + ' => Title: ' + msg_obj.ip_info.toString() + '</li>');
            break;
        case 'Broadcast':
            logging.append('<li>' + username + ' => Broadcast: ' + msg_obj.msg + 'fen: ' + msg_obj.fen + '</li>');
            break;
        default:
            console.log(msg_obj.event);
            console.log(msg_obj);
            console.log(' ');
    }
}
// remote end

function formatEngineOutput(line) {
    if (line.search('depth') > 0 && line.search('currmove') < 0) {
        var analysis_game = new Chess();
        var start_move_num = 1;
        if (currentPosition && currentPosition.fen) {
            analysis_game.load(currentPosition.fen, chessGameType);
            start_move_num = getCountPrevMoves(currentPosition) + 1;
        }

        var output = '';
        var tokens = line.split(" ");
        var depth_index = tokens.indexOf('depth') + 1;
        var depth = tokens[depth_index];
        var score_index = tokens.indexOf('score') + 1;

        var multipv_index = tokens.indexOf('multipv');
        var multipv = 0;
        if (multipv_index > -1) {
            multipv = Number(tokens[multipv_index + 1]);
        }

        var token = tokens[score_index];
        var score = '?';
        if (token === 'mate') {
            score = '#' + token + tokens[score_index + 1];
        }
        else {
            score = (tokens[score_index + 1] / 100.0).toFixed(2);
            if (analysis_game.turn() === 'b') {
                score *= -1;
            }
            if (token === 'lowerbound') {
                score = '>' + score;
            }
            if (token === 'upperbound') {
                score = '<' + score;
            }
        }

        var pv_index = tokens.indexOf('pv') + 1;

        var pv_out = tokens.slice(pv_index);
        var first_move = pv_out[0];
        for (var i = 0; i < pv_out.length; i++) {
            var from = pv_out[i].slice(0, 2);
            var to = pv_out[i].slice(2, 4);
            var promotion = '';
            if (pv_out[i].length === 5) {
                promotion = pv_out[i][4];
            }
            if (promotion) {
                var mv = analysis_game.move(({from: from, to: to, promotion: promotion}));
            } else {
                analysis_game.move(({from: from, to: to}));
            }
        }

        var history = analysis_game.history();
        window.engine_lines['import_pv_' + multipv] = {score: score, depth: depth, line: history};

        var turn_sep = '';
        if (start_move_num % 2 === 0) {
            turn_sep = '..';
        }

        output = '<div class="list-group-item">';
        if (score !== null) {
            output += '<h4 class="list-group-item-heading" id="pv_' + multipv + '_score">';
            output += '<button id="import_pv_' + multipv + '" style="margin-top: 0px;" class="importPVBtn btn btn-raised btn-info btn-xs" onclick="importPv(multipv)" data-placement="auto" data-toggle="tooltip" title="copy to game record"><i class="fa fa-copy"></i><span>&nbsp;Copy</span></button>';
            output += '<span style="color:blue; font-size: 1.8vw; margin-left: 1vw;">' + score + '/' + depth + '</span>';
            output += '</h4>';
        }
        output += '<p class="list-group-item-text">' + turn_sep;
        for (i = 0; i < history.length; ++i) {
            if ((start_move_num + i) % 2 === 1) {
                output += Math.floor((start_move_num + i + 1) / 2) + ". ";
            }
            if (history[i]) {
                output += figurinizeMove(history[i]) + " ";
            }
        }
        output += '</p></div>';

        analysis_game = null;
        return {line: output, pv_index: multipv};
    }
    else if (line.search('currmove') < 0 && line.search('time') < 0) {
        return line;
    }
}

function multiPvIncrease() {
    if (window.stockfish) {
        window.multipv += 1;

        if (window.stockfish) {
            window.stockfish.postMessage('setoption name multipv value ' + window.multipv);
            if (window.analysis) {
                window.stockfish.postMessage('stop');
                window.stockfish.postMessage('go infinite');
            }
            else {
                $('#engineMultiPVStatus').html(window.multipv + " line(s)");
            }
        }

        var new_div_str = "<div id=\"pv_" + window.multipv + "\"  style=\"margin-bottom: 3vh;\"></div>";
        $("#pv_output").append(new_div_str);

        if (!window.StockfishModule) {
            // Need to restart web worker as its not Chrome
            stopAnalysis();
            analyze(true);
        }
    }
}

function multiPvDecrease() {
    if (window.multipv > 1) {
        $('#pv_' + window.multipv).remove();

        window.multipv -= 1;
        if (window.stockfish) {
            window.stockfish.postMessage('setoption name multipv value ' + window.multipv);
            if (window.analysis) {
                window.stockfish.postMessage('stop');
                window.stockfish.postMessage('go infinite');
            }
            else {
                $('#engineMultiPVStatus').html(window.multipv + " line(s)");
            }
        }

        if (!window.StockfishModule) {
            // Need to restart web worker as its not Chrome
            stopAnalysis();
            analyze(true);
        }
    }
}

function importPv(multipv) {
    stopAnalysis();
    var tmpGame = createGamePointer();
    var line = window.engine_lines['import_pv_' + multipv].line;
    for (var i = 0; i < line.length; ++i) {
        var text_move = line[i];
        var move = tmpGame.move(text_move);
        if(move) {
            updateCurrentPosition(move, tmpGame);
        } else {
            console.warn('import_pv error');
            console.log(tmpGame.ascii());
            console.log(text_move);
            break;
        }
    }
    updateChessGround();
    updateStatus();
}

function analyzePressed() {
    analyze(false);
}

function stockfishPNACLModuleDidLoad() {
    window.StockfishModule = document.getElementById('stockfish_module');
    window.StockfishModule.postMessage('uci');
    $('#analyzeBtn').prop('disabled', false);
}

function handleCrash(event) {
    console.warn('Nacl Module crash handler method');
    console.warn(event);
    loadNaclStockfish();
}

function handleMessage(event) {
    var output = formatEngineOutput(event.data);
    if (output && output.pv_index && output.pv_index > 0) {
        $('#pv_' + output.pv_index).html(output.line);
    }
    $('#engineMultiPVStatus').html(window.multipv + " line(s)");
}

function loadNaclStockfish() {
    var listener = document.getElementById('listener');
    listener.addEventListener('load', stockfishPNACLModuleDidLoad, true);
    listener.addEventListener('message', handleMessage, true);
    listener.addEventListener('crash', handleCrash, true);
}

function stopAnalysis() {
    if (!window.StockfishModule) {
        if (window.stockfish) {
            window.stockfish.terminate();
        }
    } else {
        try {
            window.StockfishModule.postMessage('stop');
        }
        catch (err) {
            console.warn(err);
        }
    }
}

function getCountPrevMoves(node) {
    if (node.previous) {
        return getCountPrevMoves(node.previous) + 1;
    } else {
        return 0;
    }
}

function getPreviousMoves(node, format) {
    format = format || 'raw';

    if (node.previous) {
        var san = '';
        if (format === 'san') {
            if (node.half_move_num % 2 === 1) {
                san += Math.floor((node.half_move_num + 1) / 2) + ". "
            }
            san += node.move.san;
        }
        else {
            san += node.move.from + node.move.to + (node.move.promotion ? node.move.promotion : '');
        }
        return getPreviousMoves(node.previous, format) + ' ' + san;
    } else {
        return '';
    }
}

function analyze(position_update) {
    if (!position_update) {
        if ($('#AnalyzeText').text() === 'Analyze') {
            window.analysis = true;
            $('#AnalyzeText').text('Stop');
        }
        else {
            $('#AnalyzeText').text('Analyze');
            stopAnalysis();
            window.analysis = false;
            $('#engineStatus').html('');
            return;
        }
    }
    var moves;
    if (currentPosition === undefined) {
        moves = '';
    }
    else {
        moves = getPreviousMoves(currentPosition);
    }
    if (!window.StockfishModule) {
        window.stockfish = new Worker('/static/js/stockfish.js');
        window.stockfish.onmessage = function(event) {
            handleMessage(event);
        };
    }
    else {
        if (!window.stockfish) {
            window.stockfish = StockfishModule;
        }
    }

    var startpos = 'startpos';
    if (setupBoardFen !== START_FEN) {
        startpos = 'fen ' + setupBoardFen;
    }
    window.stockfish.postMessage('position ' + startpos + ' moves ' + moves);
    window.stockfish.postMessage('setoption name multipv value ' + window.multipv);
    window.stockfish.postMessage('go infinite');
}

function updateDGTPosition(data) {
    if (!goToPosition(data.fen) || data.play === 'reload') {
        loadGame(data['pgn'].split("\n"));
        goToPosition(data.fen);
    }
}

function goToDGTFen() {
    $.get('/dgt', {action: 'get_last_move'}, function(data) {
        if (data) {
            updateDGTPosition(data);
            highlightBoard(data.move, data.play);
        }
    }).fail(function(jqXHR, textStatus) {
        dgtClockStatusEl.html(textStatus);
    });
}

function setTitle(data) {
    window.ip_info = data;
    var ip = '';
    if (window.ip_info.ext_ip) {
        ip += ' IP: ' + window.ip_info.ext_ip;
    }
    var version = '';
    if (window.ip_info.version) {
        version = window.ip_info.version;
    } else if (window.system_info.version) {
        version = window.system_info.version;
    }
    document.title = 'Webserver Picochess ' + version + ip;
}

// copied from loadGame()
function setHeaders(data) {
    if ('FEN' in data && 'SetUp' in data) {
        if ('Variant' in data && 'Chess960' === data['Variant']) {
            chessGameType = 1; // values from chess960.js
        } else {
            chessGameType = 0;
        }
    }
    gameHistory.gameHeader = getWebGameHeader(data);
    gameHistory.result = data.Result;
    gameHistory.originalHeader = data;
    var exporter = new WebExporter();
    exportGame(gameHistory, exporter, true, true, undefined, false);
    writeVariationTree(pgnEl, exporter.toString(), gameHistory);
}

function getAllInfo() {
    $.get('/info', {action: 'get_system_info'}, function(data) {
        window.system_info = data;
    }).fail(function(jqXHR, textStatus) {
        dgtClockStatusEl.html(textStatus);
    });
    $.get('/info', {action: 'get_ip_info'}, function(data) {
        setTitle(data);
    }).fail(function(jqXHR, textStatus) {
        dgtClockStatusEl.html(textStatus);
    });
    $.get('/info', {action: 'get_headers'}, function(data) {
        setHeaders(data);
    }).fail(function(jqXHR, textStatus) {
        dgtClockStatusEl.html(textStatus);
    });
    $.get('/info', {action: 'get_clock_text'}, function(data) {
        dgtClockTextEl.html(data);
    }).fail(function(jqXHR, textStatus) {
        console.warn(textStatus);
        dgtClockStatusEl.html(textStatus);
    });
}

$('#flipOrientationBtn').on('click', boardFlip);
$('#backBtn').on('click', goBack);
$('#fwdBtn').on('click', goForward);
$('#startBtn').on('click', goToStart);
$('#endBtn').on('click', goToEnd);

$('#DgtSyncBtn').on('click', goToDGTFen);
$('#downloadBtn').on('click', download);
$('#broadcastBtn').on('click', broadcastPosition);

$('#analyzeBtn').on('click', analyzePressed);

$('#analyzePlus').on('click', multiPvIncrease);
$('#analyzeMinus').on('click', multiPvDecrease);

$('#ClockBtn0').on('click', clockButton0);
$('#ClockBtn1').on('click', clockButton1);
$('#ClockBtn2').on('click', clockButton2);
$('#ClockBtn3').on('click', clockButton3);
$('#ClockBtn4').on('click', clockButton4);
$('#ClockLeverBtn').on('click', toggleLeverButton);

$('#consoleBtn').on('click', toggleConsoleButton);
$('#getFenToConsoleBtn').on('click', getFenToConsole);

// remote begin
$('#enterRoomBtn').on('click', enterRoom);
$('#leaveRoomBtn').on('click', leaveRoom);
$('#SendTextRemoteBtn').on('click', sendRemoteMsg);
// remote end

$("#inputConsole").keyup(function(event) {
    if(event.keyCode === 13) {
        sendConsoleCommand();
        $(this).val('');
    }
});

$(function() {
    getAllInfo();

    $('a[data-toggle="tab"]').on('shown.bs.tab', function(e) {
        updateStatus();
    });
    window.engine_lines = {};
    window.multipv = 1;

// remote begin
    setOutsideRoom();
    $("#RemoteRoom").keyup(function(event) { remote_send(); } );
    $("#RemoteNick").keyup(function(event) { remote_send(); } );

    function remote_send() {
        if ( $("#RemoteRoom").val() !== "" && $("#RemoteNick").val() !== "") {
            $("#enterRoomBtn").removeAttr("disabled");
        } else {
            $("#enterRoomBtn").attr("disabled", "disabled");
        }
    }
// remote end

    $(document).keydown(function(e) {
        if (e.keyCode === 39) { //right arrow
            if (e.ctrlKey) {
                $('#endBtn').click();
            } else {
                $('#fwdBtn').click();
            }
            return true;
        }
    });

    $(document).keydown(function(e) {
        if (e.keyCode === 37) { //left arrow
            if (e.ctrlKey) {
                $('#startBtn').click();
            } else {
                $('#backBtn').click();
            }
        }
        return true;
    });
    updateStatus();

    window.WebSocket = window.WebSocket || window.MozWebSocket || false;
    if (!window.WebSocket) {
        alert('No WebSocket Support');
    }
    else {
        var ws = new WebSocket('ws://' + location.host + '/event');
        // Process messages from picochess
        ws.onmessage = function(e) {
            var data = JSON.parse(e.data);
            switch (data.event) {
                case 'Fen':
                    updateDGTPosition(data);
                    updateStatus();
                    if(data.play === 'reload') {
                        removeHighlights();
                    }
                    if(data.play === 'user') {
                        highlightBoard(data.move, 'user');
                    }
                    if(data.play === 'review') {
                        highlightBoard(data.move, 'review');
                    }
                    //sendRemoteFen(data);
                    break;
                case 'Game':
                    newBoard(data.fen);
                    //sendRemoteGame(data.fen);
                    break;
                case 'Message':
                    boardStatusEl.html(data.msg);
                    break;
                case 'Clock':
                    dgtClockTextEl.html(data.msg);
                    break;
                case 'Status':
                    dgtClockStatusEl.html(data.msg);
                    break;
                case 'Light':
                    highlightBoard(data.move, 'computer');
                    break;
                case 'Clear':
                    removeHighlights();
                    break;
                case 'Header':
                    setHeaders(data['headers']);
                    break;
                case 'Title':
                    setTitle(data['ip_info']);
                    break;
                case 'Broadcast':
                    boardStatusEl.html(data.msg);
                    break;
                default:
                    console.warn(data);
            }
        };
        ws.onclose = function() {
            dgtClockStatusEl.html('closed');
        };
    }

    if (navigator.mimeTypes['application/x-pnacl'] !== undefined) {
        $('#analyzeBtn').prop('disabled', true);
        loadNaclStockfish();
    }

    $.fn.dataTable.ext.errMode = 'throw';

    $('[data-toggle="tooltip"]').tooltip();
});