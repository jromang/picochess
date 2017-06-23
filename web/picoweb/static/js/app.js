NAG_NULL = 0;
var NAG_GOOD_MOVE = 1;
//"""A good move. Can also be indicated by ``!`` in PGN notation."""
var NAG_MISTAKE = 2;
//"""A mistake. Can also be indicated by ``?`` in PGN notation."""
var NAG_BRILLIANT_MOVE = 3;
//"""A brilliant move. Can also be indicated by ``!!`` in PGN notation."""
var NAG_BLUNDER = 4;
//"""A blunder. Can also be indicated by ``??`` in PGN notation."""
var NAG_SPECULATIVE_MOVE = 5;
//"""A speculative move. Can also be indicated by ``!?`` in PGN notation."""
var NAG_DUBIOUS_MOVE = 6;
//"""A dubious move. Can also be indicated by ``?!`` in PGN notation."""

simple_nags = {'1': '!', '2': '?', '3': '!!', '4': '??', '5': '!?', '6': '?!', '7': '&#9633', '8': '&#9632','11' : '=', '13': '&infin;', '14': '&#10866', '15': '&#10865', '16': '&plusmn;', '17': '&#8723', '18': '&#43; &minus;', '19': '&minus; &#43;', '36': '&rarr;','142': '&#8979','146': 'N'};


NAG_FORCED_MOVE = 7;
NAG_SINGULAR_MOVE = 8;
NAG_WORST_MOVE = 9;
NAG_DRAWISH_POSITION = 10;
NAG_QUIET_POSITION = 11;
NAG_ACTIVE_POSITION = 12;
NAG_UNCLEAR_POSITION = 13;
NAG_WHITE_SLIGHT_ADVANTAGE = 14;
NAG_BLACK_SLIGHT_ADVANTAGE = 15;

//# TODO: Add more constants for example from
//# https://en.wikipedia.org/wiki/Numeric_Annotation_Glyphs

NAG_WHITE_MODERATE_COUNTERPLAY = 132;
NAG_BLACK_MODERATE_COUNTERPLAY = 133;
NAG_WHITE_DECISIVE_COUNTERPLAY = 134;
NAG_BLACK_DECISIVE_COUNTERPLAY = 135;
NAG_WHITE_MODERATE_TIME_PRESSURE = 136;
NAG_BLACK_MODERATE_TIME_PRESSURE = 137;
NAG_WHITE_SEVERE_TIME_PRESSURE = 138;
NAG_BLACK_SEVERE_TIME_PRESSURE = 139;

const START_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';

var boardStatusEl = $('#BoardStatus'),
    dgtClockStatusEl = $('#DGTClockStatus'),
    dgtClockTextEl = $('#DGTClockText'),
    pgnEl = $('#pgn');

var gameHistory, fenHash, currentPosition;
var backend_server_prefix = 'http://drshivaji.com:3334';
//var backend_server_prefix = "http://localhost:7777";

fenHash = {};

currentPosition = {};
currentPosition.fen = START_FEN;

gameHistory = currentPosition;
gameHistory.gameHeader = '';
gameHistory.result = '';
gameHistory.variations = [];

var setupBoardFen = START_FEN;
var DataTableFen = START_FEN;

function updateDGTPosition(data) {
    if (!goToPosition(data.fen) || data.play === 'reload') {
        loadGame(data['pgn'].split("\n"));
        goToPosition(data.fen);
    }
}

function load_nacl_stockfish() {
    var listener = document.getElementById('listener');
    listener.addEventListener('load', stockfishPNACLModuleDidLoad, true);
    listener.addEventListener('message', handleMessage, true);
    listener.addEventListener('crash', handleCrash, true);
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

function setTitle(data) {
    window.ip_info = data;
    var ip = '';
    if (window.ip_info.ext_ip) {
        ip += ' IP: ' + window.ip_info.ext_ip
    }
    var version = '';
    if (window.ip_info.version) {
        version = window.ip_info.version
    } else if (window.system_info.version) {
        version = window.system_info.version
    }
    document.title = 'Webserver Picochess ' + version + ip
}

// copied from loadGame()
function setHeaders(data) {
    gameHistory.gameHeader = getWebGameHeader(data);
    gameHistory.result = data.Result;
    gameHistory.originalHeader = data;
    var exporter = new WebExporter();
    export_game(gameHistory, exporter, true, true, undefined, false);
    writeVariationTree(pgnEl, exporter.toString(), gameHistory);
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

function updateChessGround() {
    var tmp_game = create_game_pointer();

    chessground_1.set({
        fen: currentPosition.fen,
        turnColor: toColor(tmp_game),
        movable: {
            color: toColor(tmp_game),
            dests: toDests(tmp_game)
        }
    });
}

var BookDataTable = $("#BookTable").DataTable( {
    "processing": true,
    "paging": false,
    "info": false,
    "searching": false,
    "order": [[2, "desc"]],
    "select": {
        "style": "os",
        "selector": "td:not(.control)"
    },
    "responsive": {
        "details": {
           "type": "column",
           "target": 0
        }
      },
      "columnDefs": [
         {
           "data": null,
           "defaultContent": "",
           "className": "control",
           "orderable": false,
           "targets": 0
         }
      ],
    "ajax": {
        "url": backend_server_prefix + "/query",
        "dataSrc": "records",
        "dataType": "jsonp",
        "data": function ( d ) {
            d.action = "get_book_moves";
            d.fen = DataTableFen;
            d.db = "#ref";
        }
    },
    "columns": [
        {data: null},
        {data: "move", render: function ( data, type, row ) { return figurinize_move(data) } },
        {data: "freq", render: $.fn.dataTable.render.intlNumber()},
        {data: "pct", render: $.fn.dataTable.render.number( ",", ".", 2, "", "%" )},
        {data: "draws", render: $.fn.dataTable.render.intlNumber()},
        {data: "wins", render: $.fn.dataTable.render.intlNumber()},
        {data: "losses", render: $.fn.dataTable.render.intlNumber()}
    ]
});
BookDataTable.on('select', function( e, dt, type, indexes ) {
    if( type === 'row') {
        var data = BookDataTable.rows(indexes).data().pluck('move')[0];
        stop_analysis();
        var tmp_game = create_game_pointer();
        var move = tmp_game.move(data);
        updateCurrentPosition(move, tmp_game);
        updateChessGround();
        updateStatus();
        remove_highlights();
    }
});

var GameDataTable = $("#GameTable").DataTable( {
    "processing": true,
    "serverSide": true,
    "paging": true,
    "info": true,
    "searching": true,
    "order": [[1, "desc"]],
    "select": {
        "style": "os",
        "selector": "td:not(.control)"
    },
    "responsive": {
        "details": {
           "type": "column",
           "target": 0
        }
      },
      "columnDefs": [
          {
              "data": null,
              "defaultContent": "",
              "className": "control",
              "orderable": false,
              "targets": 0
          },
          {
              "targets": [1],
              "visible": false
          }
      ],
    "ajax": {
        "url": backend_server_prefix + "/query",
        "dataSrc": "records",
        "dataType": "jsonp",
        "data": function ( d ) {
            d.action = "get_games";
            d.fen = DataTableFen;
            d.db = "#ref";
        },
        "error": function (xhr, error, thrown) {
            console.warn(xhr);
        }
    },
    "initComplete": function() {
        var searchInput = $('div.dataTables_filter input');
        searchInput.unbind();
        searchInput.bind('keyup', function(e) {
            if(this.value.length > 2) {
                GameDataTable.search( this.value ).draw();
            }
            if(this.value === '') {
                GameDataTable.search('').draw();
            }
        });
    },
    "columns": [
        {data: null},
        {data: 'id'},
        {data: "white"},
        {data: "white_elo"},
        {data: "black"},
        {data: "black_elo"},
        {data: "result"},
        {data: "date"},
        {data: "event"},
        {data: "site"},
        {data: "eco"}
    ]
});
GameDataTable.on('xhr.dt', function( e, settings, json, xhr) {
    if(json) {
        json['recordsTotal'] = json['totalRecordCount'];
        json['recordsFiltered'] = json['queryRecordCount'];
        delete json['totalRecordCount'];
        delete json['queryRecordCount'];
    }
});
GameDataTable.on('select', function( e, dt, type, indexes ) {
    if( type === 'row') {
        var data = GameDataTable.rows(indexes).data().pluck('id')[0];
        $.ajax({
            dataType: 'jsonp',
            url: backend_server_prefix + '/query?callback=game_callback',
            data: {
                action: 'get_game_content',
                game_num: data,
                db: '#ref'
            }
        }).done(function(data) {
            loadGame(data['pgn']);
            updateStatus();
            remove_highlights();
        });
    }
});

$(function() {
    getAllInfo();

    $('a[data-toggle="tab"]').on('shown.bs.tab', function(e) {
        updateStatus();
    });
    window.engine_lines = {};
    window.multipv = 1;

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
                        remove_highlights();
                    }
                    if(data.play === 'user') {
                        highlightBoard(data.move, 'user');
                    }
                    if(data.play === 'review') {
                        highlightBoard(data.move, 'review');
                    }
                    break;
                case 'Game':
                    newBoard(data.fen);
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
                    remove_highlights();
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
        load_nacl_stockfish();
    }

    $.fn.dataTable.ext.errMode = 'throw';

    $('[data-toggle="tooltip"]').tooltip();
});

function highlightBoard(uci_move, play) {
    //remove_highlights();
    var move = uci_move.match(/.{2}/g);
    var brush = 'green';
    if( play === 'computer') {
        brush = 'yellow'
    }
    if( play === 'review') {
        brush = 'blue';
    }
    var shapes = {orig: move[0], dest: move[1], brush: brush};
    chessground_1.setShapes([shapes]);
}

function remove_highlights() {
    chessground_1.setShapes([]);
}

// do not pick up pieces if the game is over
// only pick up pieces for the side to move
function create_game_pointer() {
    var tmp_game;

    if (currentPosition && currentPosition.fen) {
        tmp_game = new Chess(currentPosition.fen);
    }
    else {
        tmp_game = new Chess(setupBoardFen);
    }
    return tmp_game;
}

function strip_fen(fen) {
    var stripped_fen = fen.replace(/\//g, "");
    stripped_fen = stripped_fen.replace(/ /g, "");
    return stripped_fen;
}

function figurinize_move(move) {
    if (!move) return;
    move = move.replace("N", "&#9816;");
    move = move.replace("B", "&#9815;");
    move = move.replace("R", "&#9814;");
    move = move.replace("K", "&#9812;");
    move = move.replace("Q", "&#9813;");
    move = move.replace("X", "&#9888;"); // error code
    return move;
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
        this.write_token("<span class='gameVariation'> [ ");
    };

    this.end_variation = function() {
        this.write_token(" ] </span>");
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
        if (simple_nags[int_nag]) {
            this.write_token(" " + simple_nags[int_nag] + " ");
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
        var tmp_board = new Chess(old_fen);
        var out_move = tmp_board.move(m);
        var fen = tmp_board.fen();
        var stripped_fen = strip_fen(fen);
        if (!out_move) {
            console.warn('put_move error');
            console.log(tmp_board.ascii());
            console.log(m);
            out_move = {'san': 'X' + m.from + m.to};
        }
        this.write_token('<span class="gameMove' + (board.fullmove_number) + '"><a href="#" class="fen" data-fen="' + fen + '" id="' + stripped_fen + '"> ' + figurinize_move(out_move.san) + ' </a></span>');
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
        var tmp_board = new Chess(board.fen());
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

function export_game(root_node, exporter, include_comments, include_variations, _board, _after_variation) {
    if (_board === undefined) {
        _board = new Chess(root_node.fen);
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
            export_game(variation, exporter, include_comments, include_variations, _board, false);
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
        export_game(main_variation, exporter, include_comments, include_variations, _board, _after_variation);
        _board.undo();
    }
}

// update the board position after the piece snap
// for castling, en passant, pawn promotion
function updateCurrentPosition(move, tmp_game) {
    var found_move = false;
    if (currentPosition && currentPosition.variations) {
        for (var i = 0; i < currentPosition.variations.length; i++) {
            if (move.san === currentPosition.variations[i].move.san) {
                currentPosition = currentPosition.variations[i];
                found_move = true;
            }
        }
    }
    if (!found_move) {
        var __ret = addNewMove({'move': move}, currentPosition, tmp_game.fen());
        currentPosition = __ret.node;
        var exporter = new WebExporter();
        export_game(gameHistory, exporter, true, true, undefined, false);
        writeVariationTree(pgnEl, exporter.toString(), gameHistory);
    }
}

var onSnapEnd = function(source, target) {
    stop_analysis();
    var tmp_game = create_game_pointer();

    if(!currentPosition) {
        currentPosition = {};
        currentPosition.fen = tmp_game.fen();
        gameHistory = currentPosition;
        gameHistory.gameHeader = '<h4>Player (-) vs Player (-)</h4><h5>Board game</h5>';
        gameHistory.result = '*';
    }

    var move = tmp_game.move({
        from: source,
        to: target,
        promotion: 'q' // NOTE: always promote to a pawn for example simplicity
    });

    updateCurrentPosition(move, tmp_game);
    updateChessGround();
    updateStatus();
    $.post('/channel', {action: 'move', fen: currentPosition.fen, source: source, target: target}, function(data) {
    });
};

var updateStatus = function() {
    var status = '';
    $('.fen').unbind('click', goToGameFen).one('click', goToGameFen);

    var moveColor = 'White';
    var tmp_game = create_game_pointer();
    var fen = tmp_game.fen();

    var stripped_fen = strip_fen(fen);

    if (tmp_game.turn() === 'b') {
        moveColor = 'Black';
        $('#sidetomove').html("<i class=\"fa fa-square fa-lg \"></i>");
    }
    else {
        $('#sidetomove').html("<i class=\"fa fa-square-o fa-lg \"></i>");
    }

    // checkmate?
    if (tmp_game.in_checkmate() === true) {
        status = moveColor + ' is in checkmate';
    }
    // draw?
    else if (tmp_game.in_draw() === true) {
        status = 'Drawn position';
    }
    // game still on
    else {
        status = moveColor + ' to move';
        // check?
        if (tmp_game.in_check() === true) {
            status += ' (in check)';
        }
    }

    boardStatusEl.html(status);
    if (window.analysis) {
        analyze(true);
    }

    DataTableFen = fen;
    BookDataTable.ajax.reload();
    GameDataTable.ajax.reload();

    $(".highlight").removeClass('highlight');

    if ($('#' + stripped_fen).position()) {
        pgnEl.scrollTop(0);
        var y_position = $('#' + stripped_fen).position().top;
        pgnEl.scrollTop(y_position);
    }
    $('#' + stripped_fen).addClass('highlight');
};

var cfg3 = {
            movable: {
                color: 'white',
                free: false,
                dests: toDests(Chess())
            }
        };

var chessground_1 = new Chessground(document.getElementById('board'), cfg3 );

chessground_1.set({
    movable: { events: { after: playOtherSide() } }
});


$(window).resize(function() {
    chessground_1.redrawAll();
});

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

function playOtherSide() {
    return onSnapEnd;
}

$('#flipOrientationBtn').on('click', boardFlip);
$('#backBtn').on('click', goBack);
$('#fwdBtn').on('click', goForward);
$('#startBtn').on('click', goToStart);
$('#endBtn').on('click', goToEnd);

$('#DgtSyncBtn').on('click', goToDGTFen);
$('#downloadBtn').on('click', download);
$('#broadcastBtn').on('click', broadcastPosition);

$('#analyzeBtn').on('click', analyze_pressed);

$('#analyzePlus').on('click', multipv_increase);
$('#analyzeMinus').on('click', multipv_decrease);

$('#ClockBtn0').on('click', clockButton0);
$('#ClockBtn1').on('click', clockButton1);
$('#ClockBtn2').on('click', clockButton2);
$('#ClockBtn3').on('click', clockButton3);
$('#ClockBtn4').on('click', clockButton4);
$('#ClockLeverBtn').on('click', toggleLeverButton);

$('#consoleBtn').on('click', toggleConsoleButton);
$('#getFenToConsoleBtn').on('click', getFenToConsole);

$("#inputConsole").keyup(function(event) {
    if(event.keyCode === 13) {
        sendConsoleCommand();
        $(this).val('');
    }
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

    var tmp_game;
    if ('FEN' in game_headers && 'SetUp' in game_headers) {
        tmp_game = new Chess(game_headers['FEN']);
        setupBoardFen = game_headers['FEN'];
    }
    else {
        tmp_game = new Chess();
        setupBoardFen = START_FEN;
    }

    var board_stack = [tmp_game];
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
    fenHash['last'] = fenHash[tmp_game.fen()];

    if (curr_fen === undefined) {
        currentPosition = fenHash['first'];
    }
    else {
        currentPosition = fenHash[curr_fen];
    }
    setHeaders(game_headers);
    $('.fen').unbind('click', goToGameFen).one('click', goToGameFen);
}

function get_full_game() {
    var game_header = getPgnGameHeader(gameHistory.originalHeader);
    if (game_header.length <= 1) {
        gameHistory.originalHeader = {
            'White': '*',
            'Black': '*',
            'Event': '?',
            'Site': '?',
            'Date': '?',
            'Round': '?',
            'Result': '*',
            'BlackElo' : '-',
            'WhiteElo' : '-'
        };
        game_header = getPgnGameHeader(gameHistory.originalHeader);
    }

    var exporter = new PgnExporter();
    export_game(gameHistory, exporter, true, true, undefined, false);
    var exporter_content = exporter.toString();
    return game_header + exporter_content;
}

function writeVariationTree(dom, gameMoves, gameHistoryEl) {
    $(dom).html(gameHistoryEl.gameHeader + '<div class="gameMoves">' + gameMoves + ' <span class="gameResult">' + gameHistoryEl.result + '</span></div>');
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
    var content = get_full_game();
    var dl = document.createElement('a');
    dl.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(content));
    dl.setAttribute('download', 'game.pgn');
    document.body.appendChild(dl);
    dl.click();
}

function newBoard(fen) {
    stop_analysis();

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
        var content = get_full_game();
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
    $('#consoleTextarea').append(cmd + '&#13;');
    $.post('/channel', {action: 'command', command: cmd}, function (data) {
    });
}

function getFenToConsole() {
    var tmp_game = create_game_pointer();
    $('#inputConsole').val(tmp_game.fen());
}

function toggleConsoleButton() {
    $('#Console').toggle();
    $('#Database').toggle();
}

function goToGameFen() {
    var fen = $(this).attr('data-fen');
    goToPosition(fen);
    remove_highlights();
}

function goToPosition(fen) {
    stop_analysis();
    currentPosition = fenHash[fen];
    if (!currentPosition) {
        return false;
    }
    updateChessGround();
    updateStatus();
    return true;
}

function goToStart() {
    stop_analysis();
    currentPosition = gameHistory;
    updateChessGround();
    updateStatus();
}

function goToEnd() {
    stop_analysis();
    if (fenHash.last) {
        currentPosition = fenHash.last;
        updateChessGround();
    }
    updateStatus();
}

function goForward() {
    stop_analysis();
    if (currentPosition && currentPosition.variations[0]) {
        currentPosition = currentPosition.variations[0];
        if (currentPosition) {
            updateChessGround();
        }
    }
    updateStatus();
}

function goBack() {
    stop_analysis();
    if (currentPosition && currentPosition.previous) {
        currentPosition = currentPosition.previous;
        updateChessGround();
    }
    updateStatus();
}

function boardFlip() {
    chessground_1.toggleOrientation();
}

function formatEngineOutput(line) {
    if (line.search('depth') > 0 && line.search('currmove') < 0) {
        var analysis_game = new Chess();
        var start_move_num = 1;
        if (currentPosition && currentPosition.fen) {
            analysis_game.load(currentPosition.fen);
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

        output = '<div class="list-group-item"><div class="row-picture" style="padding-right: 0.2vw;">' +
            '<button id="import_pv_' + multipv + '" class="importPVBtn btn btn-default btn-xs"><i class="fa fa-paste"></i></button>' +
            '</div><div class="row-content">';

        if (score !== null) {
            output += '<div class="least-content">' +
                '<i class="fa fa-paste"></i></div>';
            output += '<h4 class="list-group-item-heading" id="pv_' + multipv + '_score">' +
                '<span style="color:blue">' + score + '/' + depth + '</span></h4>';
        }
        output += '<p class="list-group-item-text">' + turn_sep;
        for (i = 0; i < history.length; ++i) {
            if ((start_move_num + i) % 2 === 1) {
                output += Math.floor((start_move_num + i + 1) / 2) + ". ";
            }
            if (history[i]) {
                output += figurinize_move(history[i]) + " ";
            }
        }
        output += '</p></div></div><div class="list-group-separator"></div>';

        analysis_game = null;
        return {line: output, pv_index: multipv};
    }
    else if (line.search('currmove') < 0 && line.search('time') < 0) {
        return line;
    }
}

function multipv_increase() {
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

        var new_div_str = "<div id=\"pv_" + window.multipv + "\"></div>";
        $("#pv_output").append(new_div_str);

        if (!window.StockfishModule) {
            // Need to restart web worker as its not Chrome
            stop_analysis();
            analyze(true);
        }
    }
}

function multipv_decrease() {
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
            stop_analysis();
            analyze(true);
        }
    }
}

function import_pv(e) {
    stop_analysis();
    var tmp_game = create_game_pointer();
    for (var i = 0; i < window.engine_lines[$(this).context.id].line.length; ++i) {
        var text_move = window.engine_lines[$(this).context.id].line[i];
        var move = tmp_game.move(text_move);
        updateCurrentPosition(move, tmp_game);
    }
    updateChessGround();
    updateStatus();
}

function analyze_pressed() {
    analyze(false);
}

function stockfishPNACLModuleDidLoad() {
    window.StockfishModule = document.getElementById('stockfish_module');
    window.StockfishModule.postMessage('uci');
    $('#analyzeBtn').prop('disabled', false);
}

function handleCrash(event) {
    console.warn('Nacl Module crash handler method..');
    load_nacl_stockfish();
}

function handleMessage(event) {
    var output = formatEngineOutput(event.data);
    if (output && output.pv_index && output.pv_index > 0) {
        $('#pv_' + output.pv_index).html(output.line);
    }
    $('#engineMultiPVStatus').html(window.multipv + " line(s)");
    $('.importPVBtn').on('click', import_pv);
}

function stop_analysis() {
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
            stop_analysis();
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
