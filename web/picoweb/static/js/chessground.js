(function(f){if(typeof exports==="object"&&typeof module!=="undefined"){module.exports=f()}else if(typeof define==="function"&&define.amd){define([],f)}else{var g;if(typeof window!=="undefined"){g=window}else if(typeof global!=="undefined"){g=global}else if(typeof self!=="undefined"){g=self}else{g=this}g.Chessground = f()}})(function(){var define,module,exports;return (function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
"use strict";
var __assign = (this && this.__assign) || Object.assign || function(t) {
    for (var s, i = 1, n = arguments.length; i < n; i++) {
        s = arguments[i];
        for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
            t[p] = s[p];
    }
    return t;
};
Object.defineProperty(exports, "__esModule", { value: true });
var util = require("./util");
function anim(mutation, state) {
    return state.animation.enabled ? animate(mutation, state) : render(mutation, state);
}
exports.anim = anim;
function render(mutation, state) {
    var result = mutation(state);
    state.dom.redraw();
    return result;
}
exports.render = render;
function makePiece(key, piece) {
    return {
        key: key,
        pos: util.key2pos(key),
        piece: piece
    };
}
function closer(piece, pieces) {
    return pieces.sort(function (p1, p2) {
        return util.distanceSq(piece.pos, p1.pos) - util.distanceSq(piece.pos, p2.pos);
    })[0];
}
function computePlan(prevPieces, current) {
    var bounds = current.dom.bounds(), width = bounds.width / 8, height = bounds.height / 8, anims = {}, animedOrigs = [], fadings = {}, missings = [], news = [], prePieces = {}, white = current.orientation === 'white';
    var curP, preP, i, orig, dest, vector;
    for (i in prevPieces) {
        prePieces[i] = makePiece(i, prevPieces[i]);
    }
    for (var _i = 0, _a = util.allKeys; _i < _a.length; _i++) {
        var key = _a[_i];
        curP = current.pieces[key];
        preP = prePieces[key];
        if (curP) {
            if (preP) {
                if (!util.samePiece(curP, preP.piece)) {
                    missings.push(preP);
                    news.push(makePiece(key, curP));
                }
            }
            else
                news.push(makePiece(key, curP));
        }
        else if (preP)
            missings.push(preP);
    }
    news.forEach(function (newP) {
        preP = closer(newP, missings.filter(function (p) { return util.samePiece(newP.piece, p.piece); }));
        if (preP) {
            orig = white ? preP.pos : newP.pos;
            dest = white ? newP.pos : preP.pos;
            vector = [(orig[0] - dest[0]) * width, (dest[1] - orig[1]) * height];
            anims[newP.key] = [vector, vector];
            animedOrigs.push(preP.key);
        }
    });
    missings.forEach(function (p) {
        if (!util.containsX(animedOrigs, p.key) &&
            !(current.items ? current.items(p.pos, p.key) : false))
            fadings[p.key] = p.piece;
    });
    return {
        anims: anims,
        fadings: fadings
    };
}
function step(state) {
    var cur = state.animation.current;
    if (!cur) {
        if (!state.dom.destroyed)
            state.dom.redrawNow();
        return;
    }
    var rest = 1 - (new Date().getTime() - cur.start) / cur.duration;
    if (rest <= 0) {
        state.animation.current = undefined;
        state.dom.redrawNow();
    }
    else {
        var ease = easing(rest);
        for (var i in cur.plan.anims) {
            var cfg = cur.plan.anims[i];
            cfg[1] = [roundBy(cfg[0][0] * ease, 10), roundBy(cfg[0][1] * ease, 10)];
        }
        state.dom.redrawNow(true);
        util.raf(function () { return step(state); });
    }
}
function animate(mutation, state) {
    var prevPieces = __assign({}, state.pieces);
    var result = mutation(state);
    var plan = computePlan(prevPieces, state);
    if (!isObjectEmpty(plan.anims) || !isObjectEmpty(plan.fadings)) {
        var alreadyRunning = state.animation.current && state.animation.current.start;
        state.animation.current = {
            start: new Date().getTime(),
            duration: state.animation.duration,
            plan: plan
        };
        if (!alreadyRunning)
            step(state);
    }
    else {
        state.dom.redraw();
    }
    return result;
}
function isObjectEmpty(o) {
    for (var _ in o)
        return false;
    return true;
}
function easing(t) {
    return t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1;
}
function roundBy(n, by) {
    return Math.round(n * by) / by;
}

},{"./util":17}],2:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var board = require("./board");
var fen_1 = require("./fen");
var config_1 = require("./config");
var anim_1 = require("./anim");
var drag_1 = require("./drag");
var explosion_1 = require("./explosion");
function start(state, redrawAll) {
    function toggleOrientation() {
        board.toggleOrientation(state);
        redrawAll();
    }
    ;
    return {
        set: function (config) {
            if (config.orientation && config.orientation !== state.orientation)
                toggleOrientation();
            (config.fen ? anim_1.anim : anim_1.render)(function (state) { return config_1.configure(state, config); }, state);
        },
        state: state,
        getFen: function () { return fen_1.write(state.pieces); },
        toggleOrientation: toggleOrientation,
        setPieces: function (pieces) {
            anim_1.anim(function (state) { return board.setPieces(state, pieces); }, state);
        },
        selectSquare: function (key, force) {
            if (key || state.selected)
                anim_1.anim(function (state) { return board.selectSquare(state, key, force); }, state);
        },
        move: function (orig, dest) {
            anim_1.anim(function (state) { return board.baseMove(state, orig, dest); }, state);
        },
        newPiece: function (piece, key) {
            anim_1.anim(function (state) { return board.baseNewPiece(state, piece, key); }, state);
        },
        playPremove: function () {
            if (state.premovable.current) {
                if (anim_1.anim(board.playPremove, state))
                    return true;
                state.dom.redraw();
            }
            return false;
        },
        playPredrop: function (validate) {
            if (state.predroppable.current) {
                var result = board.playPredrop(state, validate);
                state.dom.redraw();
                return result;
            }
            return false;
        },
        cancelPremove: function () {
            anim_1.render(board.unsetPremove, state);
        },
        cancelPredrop: function () {
            anim_1.render(board.unsetPredrop, state);
        },
        cancelMove: function () {
            anim_1.render(function (state) { board.cancelMove(state); drag_1.cancel(state); }, state);
        },
        stop: function () {
            anim_1.render(function (state) { board.stop(state); drag_1.cancel(state); }, state);
        },
        explode: function (keys) {
            explosion_1.default(state, keys);
        },
        setAutoShapes: function (shapes) {
            anim_1.render(function (state) { return state.drawable.autoShapes = shapes; }, state);
        },
        setShapes: function (shapes) {
            anim_1.render(function (state) { return state.drawable.shapes = shapes; }, state);
        },
        getKeyAtDomPos: function (pos) {
            return board.getKeyAtDomPos(pos, state.orientation === 'white', state.dom.bounds());
        },
        redrawAll: redrawAll,
        dragNewPiece: function (piece, event, force) {
            drag_1.dragNewPiece(state, piece, event, force);
        },
        destroy: function () {
            board.stop(state);
            state.dom.unbind && state.dom.unbind();
            state.dom.destroyed = true;
        }
    };
}
exports.start = start;

},{"./anim":1,"./board":3,"./config":5,"./drag":6,"./explosion":9,"./fen":10}],3:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var util_1 = require("./util");
var premove_1 = require("./premove");
function callUserFunction(f) {
    var args = [];
    for (var _i = 1; _i < arguments.length; _i++) {
        args[_i - 1] = arguments[_i];
    }
    if (f)
        setTimeout(function () { return f.apply(void 0, args); }, 1);
}
exports.callUserFunction = callUserFunction;
function toggleOrientation(state) {
    state.orientation = util_1.opposite(state.orientation);
    state.animation.current =
        state.draggable.current =
            state.selected = undefined;
}
exports.toggleOrientation = toggleOrientation;
function reset(state) {
    state.lastMove = undefined;
    unselect(state);
    unsetPremove(state);
    unsetPredrop(state);
}
exports.reset = reset;
function setPieces(state, pieces) {
    for (var key in pieces) {
        var piece = pieces[key];
        if (piece)
            state.pieces[key] = piece;
        else
            delete state.pieces[key];
    }
}
exports.setPieces = setPieces;
function setCheck(state, color) {
    if (color === true)
        color = state.turnColor;
    if (!color)
        state.check = undefined;
    else
        for (var k in state.pieces) {
            if (state.pieces[k].role === 'king' && state.pieces[k].color === color) {
                state.check = k;
            }
        }
}
exports.setCheck = setCheck;
function setPremove(state, orig, dest, meta) {
    unsetPredrop(state);
    state.premovable.current = [orig, dest];
    callUserFunction(state.premovable.events.set, orig, dest, meta);
}
function unsetPremove(state) {
    if (state.premovable.current) {
        state.premovable.current = undefined;
        callUserFunction(state.premovable.events.unset);
    }
}
exports.unsetPremove = unsetPremove;
function setPredrop(state, role, key) {
    unsetPremove(state);
    state.predroppable.current = {
        role: role,
        key: key
    };
    callUserFunction(state.predroppable.events.set, role, key);
}
function unsetPredrop(state) {
    var pd = state.predroppable;
    if (pd.current) {
        pd.current = undefined;
        callUserFunction(pd.events.unset);
    }
}
exports.unsetPredrop = unsetPredrop;
function tryAutoCastle(state, orig, dest) {
    if (!state.autoCastle)
        return false;
    var king = state.pieces[orig];
    if (king.role !== 'king')
        return false;
    var origPos = util_1.key2pos(orig);
    if (origPos[0] !== 5)
        return false;
    if (origPos[1] !== 1 && origPos[1] !== 8)
        return false;
    var destPos = util_1.key2pos(dest);
    var oldRookPos, newRookPos, newKingPos;
    if (destPos[0] === 7 || destPos[0] === 8) {
        oldRookPos = util_1.pos2key([8, origPos[1]]);
        newRookPos = util_1.pos2key([6, origPos[1]]);
        newKingPos = util_1.pos2key([7, origPos[1]]);
    }
    else if (destPos[0] === 3 || destPos[0] === 1) {
        oldRookPos = util_1.pos2key([1, origPos[1]]);
        newRookPos = util_1.pos2key([4, origPos[1]]);
        newKingPos = util_1.pos2key([3, origPos[1]]);
    }
    else
        return false;
    var rook = state.pieces[oldRookPos];
    if (rook.role !== 'rook')
        return false;
    delete state.pieces[orig];
    delete state.pieces[oldRookPos];
    state.pieces[newKingPos] = king;
    state.pieces[newRookPos] = rook;
    return true;
}
function baseMove(state, orig, dest) {
    if (orig === dest || !state.pieces[orig])
        return false;
    var captured = (state.pieces[dest] &&
        state.pieces[dest].color !== state.pieces[orig].color) ? state.pieces[dest] : undefined;
    if (dest == state.selected)
        unselect(state);
    callUserFunction(state.events.move, orig, dest, captured);
    if (!tryAutoCastle(state, orig, dest)) {
        state.pieces[dest] = state.pieces[orig];
        delete state.pieces[orig];
    }
    state.lastMove = [orig, dest];
    state.check = undefined;
    callUserFunction(state.events.change);
    return captured || true;
}
exports.baseMove = baseMove;
function baseNewPiece(state, piece, key, force) {
    if (state.pieces[key]) {
        if (force)
            delete state.pieces[key];
        else
            return false;
    }
    callUserFunction(state.events.dropNewPiece, piece, key);
    state.pieces[key] = piece;
    state.lastMove = [key];
    state.check = undefined;
    callUserFunction(state.events.change);
    state.movable.dests = undefined;
    state.turnColor = util_1.opposite(state.turnColor);
    return true;
}
exports.baseNewPiece = baseNewPiece;
function baseUserMove(state, orig, dest) {
    var result = baseMove(state, orig, dest);
    if (result) {
        state.movable.dests = undefined;
        state.turnColor = util_1.opposite(state.turnColor);
        state.animation.current = undefined;
    }
    return result;
}
function userMove(state, orig, dest) {
    if (canMove(state, orig, dest)) {
        var result = baseUserMove(state, orig, dest);
        if (result) {
            var holdTime = state.hold.stop();
            unselect(state);
            var metadata = {
                premove: false,
                ctrlKey: state.stats.ctrlKey,
                holdTime: holdTime
            };
            if (result !== true)
                metadata.captured = result;
            callUserFunction(state.movable.events.after, orig, dest, metadata);
            return true;
        }
    }
    else if (canPremove(state, orig, dest)) {
        setPremove(state, orig, dest, {
            ctrlKey: state.stats.ctrlKey
        });
        unselect(state);
    }
    else if (isMovable(state, dest) || isPremovable(state, dest)) {
        setSelected(state, dest);
        state.hold.start();
    }
    else
        unselect(state);
    return false;
}
exports.userMove = userMove;
function dropNewPiece(state, orig, dest, force) {
    if (canDrop(state, orig, dest) || force) {
        var piece = state.pieces[orig];
        delete state.pieces[orig];
        baseNewPiece(state, piece, dest, force);
        callUserFunction(state.movable.events.afterNewPiece, piece.role, dest, {
            predrop: false
        });
    }
    else if (canPredrop(state, orig, dest)) {
        setPredrop(state, state.pieces[orig].role, dest);
    }
    else {
        unsetPremove(state);
        unsetPredrop(state);
    }
    delete state.pieces[orig];
    unselect(state);
}
exports.dropNewPiece = dropNewPiece;
function selectSquare(state, key, force) {
    if (state.selected) {
        if (state.selected === key && !state.draggable.enabled) {
            unselect(state);
            state.hold.cancel();
        }
        else if ((state.selectable.enabled || force) && state.selected !== key) {
            if (userMove(state, state.selected, key))
                state.stats.dragged = false;
        }
        else
            state.hold.start();
    }
    else if (isMovable(state, key) || isPremovable(state, key)) {
        setSelected(state, key);
        state.hold.start();
    }
    if (key)
        callUserFunction(state.events.select, key);
}
exports.selectSquare = selectSquare;
function setSelected(state, key) {
    state.selected = key;
    if (isPremovable(state, key)) {
        state.premovable.dests = premove_1.default(state.pieces, key, state.premovable.castle);
    }
    else
        state.premovable.dests = undefined;
}
exports.setSelected = setSelected;
function unselect(state) {
    state.selected = undefined;
    state.premovable.dests = undefined;
    state.hold.cancel();
}
exports.unselect = unselect;
function isMovable(state, orig) {
    var piece = state.pieces[orig];
    return piece && (state.movable.color === 'both' || (state.movable.color === piece.color &&
        state.turnColor === piece.color));
}
function canMove(state, orig, dest) {
    return orig !== dest && isMovable(state, orig) && (state.movable.free || (!!state.movable.dests && util_1.containsX(state.movable.dests[orig], dest)));
}
exports.canMove = canMove;
function canDrop(state, orig, dest) {
    var piece = state.pieces[orig];
    return piece && dest && (orig === dest || !state.pieces[dest]) && (state.movable.color === 'both' || (state.movable.color === piece.color &&
        state.turnColor === piece.color));
}
function isPremovable(state, orig) {
    var piece = state.pieces[orig];
    return piece && state.premovable.enabled &&
        state.movable.color === piece.color &&
        state.turnColor !== piece.color;
}
function canPremove(state, orig, dest) {
    return orig !== dest &&
        isPremovable(state, orig) &&
        util_1.containsX(premove_1.default(state.pieces, orig, state.premovable.castle), dest);
}
function canPredrop(state, orig, dest) {
    var piece = state.pieces[orig];
    return piece && dest &&
        (!state.pieces[dest] || state.pieces[dest].color !== state.movable.color) &&
        state.predroppable.enabled &&
        (piece.role !== 'pawn' || (dest[1] !== '1' && dest[1] !== '8')) &&
        state.movable.color === piece.color &&
        state.turnColor !== piece.color;
}
function isDraggable(state, orig) {
    var piece = state.pieces[orig];
    return piece && state.draggable.enabled && (state.movable.color === 'both' || (state.movable.color === piece.color && (state.turnColor === piece.color || state.premovable.enabled)));
}
exports.isDraggable = isDraggable;
function playPremove(state) {
    var move = state.premovable.current;
    if (!move)
        return false;
    var orig = move[0], dest = move[1];
    var success = false;
    if (canMove(state, orig, dest)) {
        var result = baseUserMove(state, orig, dest);
        if (result) {
            var metadata = { premove: true };
            if (result !== true)
                metadata.captured = result;
            callUserFunction(state.movable.events.after, orig, dest, metadata);
            success = true;
        }
    }
    unsetPremove(state);
    return success;
}
exports.playPremove = playPremove;
function playPredrop(state, validate) {
    var drop = state.predroppable.current, success = false;
    if (!drop)
        return false;
    if (validate(drop)) {
        var piece = {
            role: drop.role,
            color: state.movable.color
        };
        if (baseNewPiece(state, piece, drop.key)) {
            callUserFunction(state.movable.events.afterNewPiece, drop.role, drop.key, {
                predrop: true
            });
            success = true;
        }
    }
    unsetPredrop(state);
    return success;
}
exports.playPredrop = playPredrop;
function cancelMove(state) {
    unsetPremove(state);
    unsetPredrop(state);
    unselect(state);
}
exports.cancelMove = cancelMove;
function stop(state) {
    state.movable.color =
        state.movable.dests =
            state.animation.current = undefined;
    cancelMove(state);
}
exports.stop = stop;
function getKeyAtDomPos(pos, asWhite, bounds) {
    var file = Math.ceil(8 * ((pos[0] - bounds.left) / bounds.width));
    if (!asWhite)
        file = 9 - file;
    var rank = Math.ceil(8 - (8 * ((pos[1] - bounds.top) / bounds.height)));
    if (!asWhite)
        rank = 9 - rank;
    return (file > 0 && file < 9 && rank > 0 && rank < 9) ? util_1.pos2key([file, rank]) : undefined;
}
exports.getKeyAtDomPos = getKeyAtDomPos;

},{"./premove":12,"./util":17}],4:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var api_1 = require("./api");
var config_1 = require("./config");
var state_1 = require("./state");
var wrap_1 = require("./wrap");
var events = require("./events");
var render_1 = require("./render");
var svg = require("./svg");
var util = require("./util");
function Chessground(element, config) {
    var state = state_1.defaults();
    config_1.configure(state, config || {});
    state.browser = {
        transform: util.transformFunction()
    };
    function redrawAll() {
        var prevUnbind = state.dom && state.dom.unbind;
        element.classList.add('cg-board-wrap');
        var bounds = util.memo(function () { return element.getBoundingClientRect(); });
        var elements = wrap_1.default(element, state, bounds());
        var redrawNow = function (skipSvg) {
            render_1.default(state);
            if (!skipSvg && elements.svg)
                svg.renderSvg(state, elements.svg);
        };
        state.dom = {
            elements: elements,
            bounds: bounds,
            redraw: debounceRedraw(redrawNow),
            redrawNow: redrawNow,
            unbind: prevUnbind
        };
        svg.clearCache();
        redrawNow(false);
        events.bindBoard(state);
        if (!prevUnbind)
            state.dom.unbind = events.bindDocument(state, redrawAll);
    }
    redrawAll();
    var api = api_1.start(state, redrawAll);
    return api;
}
exports.Chessground = Chessground;
;
function debounceRedraw(redrawNow) {
    var redrawing = false;
    return function () {
        if (redrawing)
            return;
        redrawing = true;
        util.raf(function () {
            redrawNow();
            redrawing = false;
        });
    };
}

},{"./api":2,"./config":5,"./events":8,"./render":13,"./state":14,"./svg":15,"./util":17,"./wrap":18}],5:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var board_1 = require("./board");
var fen_1 = require("./fen");
function configure(state, config) {
    if (config.movable && config.movable.dests)
        state.movable.dests = undefined;
    merge(state, config);
    if (config.fen) {
        state.pieces = fen_1.read(config.fen);
        state.drawable.shapes = [];
    }
    if (config.hasOwnProperty('check'))
        board_1.setCheck(state, config.check || false);
    if (config.hasOwnProperty('lastMove') && !config.lastMove)
        state.lastMove = undefined;
    else if (config.lastMove)
        state.lastMove = config.lastMove;
    if (state.selected)
        board_1.setSelected(state, state.selected);
    if (!state.animation.duration || state.animation.duration < 100)
        state.animation.enabled = false;
    if (!state.movable.rookCastle && state.movable.dests) {
        var rank_1 = state.movable.color === 'white' ? 1 : 8;
        var kingStartPos = 'e' + rank_1;
        var dests_1 = state.movable.dests[kingStartPos];
        if (!dests_1 || state.pieces[kingStartPos].role !== 'king')
            return;
        state.movable.dests[kingStartPos] = dests_1.filter(function (d) {
            if ((d === 'a' + rank_1) && dests_1.indexOf('c' + rank_1) !== -1)
                return false;
            if ((d === 'h' + rank_1) && dests_1.indexOf('g' + rank_1) !== -1)
                return false;
            return true;
        });
    }
}
exports.configure = configure;
;
function merge(base, extend) {
    for (var key in extend) {
        if (isObject(base[key]) && isObject(extend[key]))
            merge(base[key], extend[key]);
        else
            base[key] = extend[key];
    }
}
function isObject(o) {
    return typeof o === 'object';
}

},{"./board":3,"./fen":10}],6:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var board = require("./board");
var util = require("./util");
var draw_1 = require("./draw");
var anim_1 = require("./anim");
function start(s, e) {
    if (e.button !== undefined && e.button !== 0)
        return;
    if (e.touches && e.touches.length > 1)
        return;
    e.preventDefault();
    var asWhite = s.orientation === 'white', bounds = s.dom.bounds(), position = util.eventPosition(e), orig = board.getKeyAtDomPos(position, asWhite, bounds);
    if (!orig)
        return;
    var piece = s.pieces[orig];
    var previouslySelected = s.selected;
    if (!previouslySelected && (s.drawable.eraseOnClick || (!piece || piece.color !== s.turnColor)))
        draw_1.clear(s);
    if (s.viewOnly)
        return;
    var hadPremove = !!s.premovable.current;
    var hadPredrop = !!s.predroppable.current;
    s.stats.ctrlKey = e.ctrlKey;
    if (s.selected && board.canMove(s, s.selected, orig)) {
        anim_1.anim(function (state) { return board.selectSquare(state, orig); }, s);
    }
    else {
        board.selectSquare(s, orig);
    }
    var stillSelected = s.selected === orig;
    var element = pieceElementByKey(s, orig);
    if (piece && element && stillSelected && board.isDraggable(s, orig)) {
        var squareBounds = computeSquareBounds(orig, asWhite, bounds);
        s.draggable.current = {
            orig: orig,
            origPos: util.key2pos(orig),
            piece: piece,
            rel: position,
            epos: position,
            pos: [0, 0],
            dec: s.draggable.centerPiece ? [
                position[0] - (squareBounds.left + squareBounds.width / 2),
                position[1] - (squareBounds.top + squareBounds.height / 2)
            ] : [0, 0],
            started: s.draggable.autoDistance && s.stats.dragged,
            element: element,
            previouslySelected: previouslySelected,
            originTarget: e.target
        };
        element.cgDragging = true;
        element.classList.add('dragging');
        var ghost = s.dom.elements.ghost;
        if (ghost) {
            ghost.className = "ghost " + piece.color + " " + piece.role;
            var translation = util.posToTranslate(util.key2pos(orig), asWhite, bounds);
            s.browser.transform(ghost, util.translate(translation));
        }
        processDrag(s);
    }
    else {
        if (hadPremove)
            board.unsetPremove(s);
        if (hadPredrop)
            board.unsetPredrop(s);
    }
    s.dom.redraw();
}
exports.start = start;
function dragNewPiece(s, piece, e, force) {
    var key = 'a0';
    s.pieces[key] = piece;
    s.dom.redraw();
    var position = util.eventPosition(e), asWhite = s.orientation === 'white', bounds = s.dom.bounds(), squareBounds = computeSquareBounds(key, asWhite, bounds);
    var rel = [
        (asWhite ? 0 : 7) * squareBounds.width + bounds.left,
        (asWhite ? 8 : -1) * squareBounds.height + bounds.top
    ];
    s.draggable.current = {
        orig: key,
        origPos: util.key2pos(key),
        piece: piece,
        rel: rel,
        epos: position,
        pos: [position[0] - rel[0], position[1] - rel[1]],
        dec: [-squareBounds.width / 2, -squareBounds.height / 2],
        started: true,
        element: function () { return pieceElementByKey(s, key); },
        originTarget: e.target,
        newPiece: true,
        force: force || false
    };
    processDrag(s);
}
exports.dragNewPiece = dragNewPiece;
function processDrag(s) {
    util.raf(function () {
        var cur = s.draggable.current;
        if (!cur)
            return;
        if (s.animation.current && s.animation.current.plan.anims[cur.orig])
            s.animation.current = undefined;
        var origPiece = s.pieces[cur.orig];
        if (!origPiece || !util.samePiece(origPiece, cur.piece))
            cancel(s);
        else {
            if (!cur.started && util.distanceSq(cur.epos, cur.rel) >= Math.pow(s.draggable.distance, 2))
                cur.started = true;
            if (cur.started) {
                if (typeof cur.element === 'function') {
                    var found = cur.element();
                    if (!found)
                        return;
                    cur.element = found;
                    cur.element.cgDragging = true;
                    cur.element.classList.add('dragging');
                }
                var asWhite = s.orientation === 'white', bounds = s.dom.bounds();
                cur.pos = [
                    cur.epos[0] - cur.rel[0],
                    cur.epos[1] - cur.rel[1]
                ];
                cur.over = board.getKeyAtDomPos(cur.epos, asWhite, bounds);
                var translation = util.posToTranslate(cur.origPos, asWhite, bounds);
                translation[0] += cur.pos[0] + cur.dec[0];
                translation[1] += cur.pos[1] + cur.dec[1];
                s.browser.transform(cur.element, util.translate(translation));
                var overEl = s.dom.elements.over;
                if (overEl && cur.over && cur.over !== cur.overPrev) {
                    var dests = s.movable.dests;
                    if (s.movable.free ||
                        util.containsX(dests && dests[cur.orig], cur.over) ||
                        util.containsX(s.premovable.dests, cur.over)) {
                        var pos = util.key2pos(cur.over), vector = [
                            (asWhite ? pos[0] - 1 : 8 - pos[0]) * bounds.width / 8,
                            (asWhite ? 8 - pos[1] : pos[1] - 1) * bounds.height / 8
                        ];
                        s.browser.transform(overEl, util.translate(vector));
                    }
                    else {
                        s.browser.transform(overEl, util.translateAway);
                    }
                    cur.overPrev = cur.over;
                }
            }
        }
        processDrag(s);
    });
}
function move(s, e) {
    if (s.draggable.current && (!e.touches || e.touches.length < 2)) {
        s.draggable.current.epos = util.eventPosition(e);
    }
}
exports.move = move;
function end(s, e) {
    var cur = s.draggable.current;
    if (!cur)
        return;
    if (e.type === 'touchend' && cur && cur.originTarget !== e.target && !cur.newPiece) {
        s.draggable.current = undefined;
        return;
    }
    board.unsetPremove(s);
    board.unsetPredrop(s);
    var eventPos = util.eventPosition(e) || cur.epos;
    var dest = board.getKeyAtDomPos(eventPos, s.orientation === 'white', s.dom.bounds());
    if (dest && cur.started) {
        if (cur.newPiece)
            board.dropNewPiece(s, cur.orig, dest, cur.force);
        else {
            s.stats.ctrlKey = e.ctrlKey;
            if (board.userMove(s, cur.orig, dest))
                s.stats.dragged = true;
        }
    }
    else if (cur.newPiece) {
        delete s.pieces[cur.orig];
    }
    else if (s.draggable.deleteOnDropOff) {
        delete s.pieces[cur.orig];
        board.callUserFunction(s.events.change);
    }
    if (cur && cur.orig === cur.previouslySelected && (cur.orig === dest || !dest))
        board.unselect(s);
    else if (!s.selectable.enabled)
        board.unselect(s);
    removeDragElements(s);
    s.draggable.current = undefined;
    s.dom.redraw();
}
exports.end = end;
function cancel(s) {
    var cur = s.draggable.current;
    if (cur) {
        if (cur.newPiece)
            delete s.pieces[cur.orig];
        s.draggable.current = undefined;
        board.unselect(s);
        removeDragElements(s);
        s.dom.redraw();
    }
}
exports.cancel = cancel;
function removeDragElements(s) {
    var e = s.dom.elements;
    if (e.over)
        s.browser.transform(e.over, util.translateAway);
    if (e.ghost)
        s.browser.transform(e.ghost, util.translateAway);
}
function computeSquareBounds(key, asWhite, bounds) {
    var pos = util.key2pos(key);
    if (!asWhite) {
        pos[0] = 9 - pos[0];
        pos[1] = 9 - pos[1];
    }
    return {
        left: bounds.left + bounds.width * (pos[0] - 1) / 8,
        top: bounds.top + bounds.height * (8 - pos[1]) / 8,
        width: bounds.width / 8,
        height: bounds.height / 8
    };
}
function pieceElementByKey(s, key) {
    var el = s.dom.elements.board.firstChild;
    while (el) {
        if (el.cgKey === key && el.tagName === 'PIECE')
            return el;
        el = el.nextSibling;
    }
    return undefined;
}

},{"./anim":1,"./board":3,"./draw":7,"./util":17}],7:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var board_1 = require("./board");
var util_1 = require("./util");
var brushes = ['green', 'red', 'blue', 'yellow'];
function start(state, e) {
    if (e.touches && e.touches.length > 1)
        return;
    e.stopPropagation();
    e.preventDefault();
    board_1.cancelMove(state);
    var position = util_1.eventPosition(e);
    var orig = board_1.getKeyAtDomPos(position, state.orientation === 'white', state.dom.bounds());
    if (!orig)
        return;
    state.drawable.current = {
        orig: orig,
        dest: orig,
        pos: position,
        brush: eventBrush(e)
    };
    processDraw(state);
}
exports.start = start;
function processDraw(state) {
    util_1.raf(function () {
        var cur = state.drawable.current;
        if (cur) {
            var dest = board_1.getKeyAtDomPos(cur.pos, state.orientation === 'white', state.dom.bounds());
            var newDest = (cur.orig === dest) ? undefined : dest;
            if (newDest !== cur.dest) {
                cur.dest = newDest;
                state.dom.redrawNow();
            }
            processDraw(state);
        }
    });
}
exports.processDraw = processDraw;
function move(state, e) {
    if (state.drawable.current)
        state.drawable.current.pos = util_1.eventPosition(e);
}
exports.move = move;
function end(state) {
    var cur = state.drawable.current;
    if (!cur)
        return;
    if (cur.dest && cur.dest !== cur.orig)
        addLine(state.drawable, cur, cur.dest);
    else
        addCircle(state.drawable, cur);
    cancel(state);
}
exports.end = end;
function cancel(state) {
    if (state.drawable.current) {
        state.drawable.current = undefined;
        state.dom.redraw();
    }
}
exports.cancel = cancel;
function clear(state) {
    if (state.drawable.shapes.length) {
        state.drawable.shapes = [];
        state.dom.redraw();
        onChange(state.drawable);
    }
}
exports.clear = clear;
function eventBrush(e) {
    var a = e.shiftKey && util_1.isRightButton(e) ? 1 : 0;
    var b = e.altKey ? 2 : 0;
    return brushes[a + b];
}
function not(f) {
    return function (x) { return !f(x); };
}
function addCircle(drawable, cur) {
    var orig = cur.orig;
    var sameCircle = function (s) { return s.orig === orig && !s.dest; };
    var similar = drawable.shapes.filter(sameCircle)[0];
    if (similar)
        drawable.shapes = drawable.shapes.filter(not(sameCircle));
    if (!similar || similar.brush !== cur.brush)
        drawable.shapes.push({
            brush: cur.brush,
            orig: orig
        });
    onChange(drawable);
}
function addLine(drawable, cur, dest) {
    var orig = cur.orig;
    var sameLine = function (s) {
        return !!s.dest && ((s.orig === orig && s.dest === dest) || (s.dest === orig && s.orig === dest));
    };
    var exists = drawable.shapes.filter(sameLine).length > 0;
    if (exists)
        drawable.shapes = drawable.shapes.filter(not(sameLine));
    else
        drawable.shapes.push({
            brush: cur.brush,
            orig: orig,
            dest: dest
        });
    onChange(drawable);
}
function onChange(drawable) {
    if (drawable.onChange)
        drawable.onChange(drawable.shapes);
}

},{"./board":3,"./util":17}],8:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var drag = require("./drag");
var draw = require("./draw");
var util_1 = require("./util");
function bindBoard(s) {
    var boardEl = s.dom.elements.board;
    if (!s.viewOnly) {
        ['touchstart', 'mousedown'].forEach(function (ev) { return boardEl.addEventListener(ev, startDragOrDraw(s)); });
    }
    if (s.disableContextMenu || s.drawable.enabled) {
        boardEl.addEventListener('contextmenu', function (e) {
            e.preventDefault();
            return false;
        });
    }
}
exports.bindBoard = bindBoard;
function bindDocument(s, redrawAll) {
    var onmove = dragOrDraw(s, drag.move, draw.move);
    var onend = dragOrDraw(s, drag.end, draw.end);
    var unbinds = [];
    if (!s.viewOnly) {
        ['touchmove', 'mousemove'].forEach(function (ev) { return unbinds.push(unbindable(document, ev, onmove)); });
        ['touchend', 'mouseup'].forEach(function (ev) { return unbinds.push(unbindable(document, ev, onend)); });
    }
    var onResize = function () {
        s.dom.bounds.clear();
        util_1.raf(redrawAll);
    };
    if (s.resizable)
        unbinds.push(unbindable(document.body, 'chessground.resize', onResize));
    var onScroll = function () { return s.dom.bounds.clear(); };
    unbinds.push(unbindable(window, 'scroll', onScroll, { passive: true }));
    unbinds.push(unbindable(window, 'resize', onScroll, { passive: true }));
    return function () { return unbinds.forEach(function (f) { return f(); }); };
}
exports.bindDocument = bindDocument;
function unbindable(el, eventName, callback, options) {
    el.addEventListener(eventName, callback, options);
    return function () { return el.removeEventListener(eventName, callback); };
}
function startDragOrDraw(s) {
    return function (e) {
        if (s.draggable.current)
            drag.cancel(s);
        else if (s.drawable.current)
            draw.cancel(s);
        else if (e.shiftKey || util_1.isRightButton(e)) {
            if (s.drawable.enabled)
                draw.start(s, e);
        }
        else if (!s.viewOnly)
            drag.start(s, e);
    };
}
function dragOrDraw(s, withDrag, withDraw) {
    return function (e) {
        if (e.shiftKey || util_1.isRightButton(e)) {
            if (s.drawable.enabled)
                withDraw(s, e);
        }
        else if (!s.viewOnly)
            withDrag(s, e);
    };
}

},{"./drag":6,"./draw":7,"./util":17}],9:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
function explosion(state, keys) {
    state.exploding = {
        stage: 1,
        keys: keys
    };
    state.dom.redraw();
    setTimeout(function () {
        setStage(state, 2);
        setTimeout(function () { return setStage(state, undefined); }, 120);
    }, 120);
}
exports.default = explosion;
function setStage(state, stage) {
    if (state.exploding) {
        if (stage)
            state.exploding.stage = stage;
        else
            state.exploding = undefined;
        state.dom.redraw();
    }
}

},{}],10:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var util_1 = require("./util");
var cg = require("./types");
exports.initial = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR';
var roles = { p: 'pawn', r: 'rook', n: 'knight', b: 'bishop', q: 'queen', k: 'king' };
var letters = { pawn: 'p', rook: 'r', knight: 'n', bishop: 'b', queen: 'q', king: 'k' };
function read(fen) {
    if (fen === 'start')
        fen = exports.initial;
    var pieces = {};
    var row = 8;
    var col = 0;
    for (var _i = 0, fen_1 = fen; _i < fen_1.length; _i++) {
        var c = fen_1[_i];
        switch (c) {
            case ' ': return pieces;
            case '/':
                --row;
                if (row === 0)
                    return pieces;
                col = 0;
                break;
            case '~':
                pieces[util_1.pos2key([col, row])].promoted = true;
                break;
            default:
                var nb = c.charCodeAt(0);
                if (nb < 57)
                    col += nb - 48;
                else {
                    ++col;
                    var role = c.toLowerCase();
                    pieces[util_1.pos2key([col, row])] = {
                        role: roles[role],
                        color: (c === role ? 'black' : 'white')
                    };
                }
        }
    }
    return pieces;
}
exports.read = read;
function write(pieces) {
    var piece, letter;
    return util_1.invRanks.map(function (y) { return cg.ranks.map(function (x) {
        piece = pieces[util_1.pos2key([x, y])];
        if (piece) {
            letter = letters[piece.role];
            return piece.color === 'white' ? letter.toUpperCase() : letter;
        }
        else
            return '1';
    }).join(''); }).join('/').replace(/1{2,}/g, function (s) { return s.length.toString(); });
}
exports.write = write;

},{"./types":16,"./util":17}],11:[function(require,module,exports){
module.exports = require("./chessground").Chessground;

},{"./chessground":4}],12:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var util = require("./util");
function diff(a, b) {
    return Math.abs(a - b);
}
function pawn(color) {
    return function (x1, y1, x2, y2) { return diff(x1, x2) < 2 && (color === 'white' ? (y2 === y1 + 1 || (y1 <= 2 && y2 === (y1 + 2) && x1 === x2)) : (y2 === y1 - 1 || (y1 >= 7 && y2 === (y1 - 2) && x1 === x2))); };
}
var knight = function (x1, y1, x2, y2) {
    var xd = diff(x1, x2);
    var yd = diff(y1, y2);
    return (xd === 1 && yd === 2) || (xd === 2 && yd === 1);
};
var bishop = function (x1, y1, x2, y2) {
    return diff(x1, x2) === diff(y1, y2);
};
var rook = function (x1, y1, x2, y2) {
    return x1 === x2 || y1 === y2;
};
var queen = function (x1, y1, x2, y2) {
    return bishop(x1, y1, x2, y2) || rook(x1, y1, x2, y2);
};
function king(color, rookFiles, canCastle) {
    return function (x1, y1, x2, y2) { return (diff(x1, x2) < 2 && diff(y1, y2) < 2) || (canCastle && y1 === y2 && y1 === (color === 'white' ? 1 : 8) && ((x1 === 5 && (x2 === 3 || x2 === 7)) || util.containsX(rookFiles, x2))); };
}
function rookFilesOf(pieces, color) {
    var piece;
    return Object.keys(pieces).filter(function (key) {
        piece = pieces[key];
        return piece && piece.color === color && piece.role === 'rook';
    }).map(function (key) { return util.key2pos(key)[0]; });
}
function premove(pieces, key, canCastle) {
    var piece = pieces[key], pos = util.key2pos(key);
    var mobility;
    switch (piece.role) {
        case 'pawn':
            mobility = pawn(piece.color);
            break;
        case 'knight':
            mobility = knight;
            break;
        case 'bishop':
            mobility = bishop;
            break;
        case 'rook':
            mobility = rook;
            break;
        case 'queen':
            mobility = queen;
            break;
        case 'king':
            mobility = king(piece.color, rookFilesOf(pieces, piece.color), canCastle);
            break;
    }
    return util.allKeys.map(util.key2pos).filter(function (pos2) {
        return (pos[0] !== pos2[0] || pos[1] !== pos2[1]) && mobility(pos[0], pos[1], pos2[0], pos2[1]);
    }).map(util.pos2key);
}
exports.default = premove;
;

},{"./util":17}],13:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var util_1 = require("./util");
function render(s) {
    var asWhite = s.orientation === 'white', bounds = s.dom.bounds(), boardEl = s.dom.elements.board, pieces = s.pieces, curAnim = s.animation.current, anims = curAnim ? curAnim.plan.anims : {}, fadings = curAnim ? curAnim.plan.fadings : {}, curDrag = s.draggable.current, squares = computeSquareClasses(s), samePieces = {}, sameSquares = {}, movedPieces = {}, movedSquares = {}, piecesKeys = Object.keys(pieces), transform = s.browser.transform;
    var k, p, el, pieceAtKey, elPieceName, translation, anim, fading, pMvdset, pMvd, sMvdset, sMvd;
    el = boardEl.firstChild;
    while (el) {
        k = el.cgKey;
        if (isPieceNode(el)) {
            pieceAtKey = pieces[k];
            anim = anims[k];
            fading = fadings[k];
            elPieceName = el.cgPiece;
            if (el.cgDragging && (!curDrag || curDrag.orig !== k)) {
                el.classList.remove('dragging');
                transform(el, util_1.translate(util_1.posToTranslate(util_1.key2pos(k), asWhite, bounds)));
                el.cgDragging = false;
            }
            if (!fading && el.cgFading) {
                el.cgFading = false;
                el.classList.remove('fading');
            }
            if (pieceAtKey) {
                if (anim && el.cgAnimating && elPieceName === pieceNameOf(pieceAtKey)) {
                    translation = util_1.posToTranslate(util_1.key2pos(k), asWhite, bounds);
                    translation[0] += anim[1][0];
                    translation[1] += anim[1][1];
                    transform(el, util_1.translate(translation));
                    el.classList.add('anim');
                }
                else if (el.cgAnimating) {
                    translation = util_1.posToTranslate(util_1.key2pos(k), asWhite, bounds);
                    transform(el, util_1.translate(translation));
                    el.cgAnimating = false;
                    el.classList.remove('anim');
                }
                if (elPieceName === pieceNameOf(pieceAtKey) && (!fading || !el.cgFading)) {
                    samePieces[k] = true;
                }
                else {
                    if (fading && elPieceName === pieceNameOf(fading)) {
                        el.classList.add('fading');
                        el.cgFading = true;
                    }
                    else {
                        if (movedPieces[elPieceName])
                            movedPieces[elPieceName].push(el);
                        else
                            movedPieces[elPieceName] = [el];
                    }
                }
            }
            else {
                if (movedPieces[elPieceName])
                    movedPieces[elPieceName].push(el);
                else
                    movedPieces[elPieceName] = [el];
            }
        }
        else if (isSquareNode(el)) {
            var cn = el.className;
            if (squares[k] === cn)
                sameSquares[k] = true;
            else if (movedSquares[cn])
                movedSquares[cn].push(el);
            else
                movedSquares[cn] = [el];
        }
        el = el.nextSibling;
    }
    for (var sk in squares) {
        if (!sameSquares[sk]) {
            sMvdset = movedSquares[squares[sk]];
            sMvd = sMvdset && sMvdset.pop();
            translation = util_1.posToTranslate(util_1.key2pos(sk), asWhite, bounds);
            if (sMvd) {
                sMvd.cgKey = sk;
                transform(sMvd, util_1.translate(translation));
            }
            else {
                boardEl.insertBefore(renderSquareDom(sk, squares[sk], translation, transform), boardEl.firstChild);
            }
        }
    }
    for (var j in piecesKeys) {
        k = piecesKeys[j];
        p = pieces[k];
        anim = anims[k];
        if (!samePieces[k]) {
            pMvdset = movedPieces[pieceNameOf(p)];
            pMvd = pMvdset && pMvdset.pop();
            if (pMvd) {
                pMvd.cgKey = k;
                if (pMvd.cgFading) {
                    pMvd.classList.remove('fading');
                    pMvd.cgFading = false;
                }
                var pos = util_1.key2pos(k);
                if (s.addPieceZIndex)
                    pMvd.style.zIndex = posZIndex(pos, asWhite);
                translation = util_1.posToTranslate(pos, asWhite, bounds);
                if (anim) {
                    pMvd.cgAnimating = true;
                    pMvd.classList.add('anim');
                    translation[0] += anim[1][0];
                    translation[1] += anim[1][1];
                }
                transform(pMvd, util_1.translate(translation));
            }
            else {
                boardEl.appendChild(renderPieceDom(s, p, k, asWhite, anim, bounds));
            }
        }
    }
    for (var i in movedPieces)
        removeNodes(s, movedPieces[i]);
    for (var i in movedSquares)
        removeNodes(s, movedSquares[i]);
}
exports.default = render;
function isPieceNode(el) {
    return el.tagName === 'PIECE';
}
function isSquareNode(el) {
    return el.tagName === 'SQUARE';
}
function removeNodes(s, nodes) {
    for (var i in nodes)
        s.dom.elements.board.removeChild(nodes[i]);
}
function renderSquareDom(key, className, translation, transform) {
    var s = util_1.createEl('square', className);
    s.cgKey = key;
    transform(s, util_1.translate(translation));
    return s;
}
function renderPieceDom(s, piece, key, asWhite, anim, bounds) {
    var pieceName = pieceNameOf(piece), p = util_1.createEl('piece', pieceName), pos = util_1.key2pos(key);
    p.cgPiece = pieceName;
    p.cgKey = key;
    var translation = util_1.posToTranslate(pos, asWhite, bounds);
    if (anim) {
        p.cgAnimating = true;
        translation[0] += anim[1][0];
        translation[1] += anim[1][1];
    }
    s.browser.transform(p, util_1.translate(translation));
    if (s.addPieceZIndex)
        p.style.zIndex = posZIndex(pos, asWhite);
    return p;
}
function posZIndex(pos, asWhite) {
    var z = 2 + (pos[1] - 1) * 8 + (8 - pos[0]);
    if (asWhite)
        z = 67 - z;
    return z + '';
}
function pieceNameOf(piece) {
    return piece.color + " " + piece.role;
}
function computeSquareClasses(s) {
    var squares = {};
    var i, k;
    if (s.lastMove && s.highlight.lastMove)
        for (i in s.lastMove) {
            addSquare(squares, s.lastMove[i], 'last-move');
        }
    if (s.check && s.highlight.check)
        addSquare(squares, s.check, 'check');
    if (s.selected) {
        addSquare(squares, s.selected, 'selected');
        if (s.movable.showDests) {
            var dests = s.movable.dests && s.movable.dests[s.selected];
            if (dests)
                for (i in dests) {
                    k = dests[i];
                    addSquare(squares, k, 'move-dest' + (s.pieces[k] ? ' oc' : ''));
                }
            var pDests = s.premovable.dests;
            if (pDests)
                for (i in pDests) {
                    k = pDests[i];
                    addSquare(squares, k, 'premove-dest' + (s.pieces[k] ? ' oc' : ''));
                }
        }
    }
    var premove = s.premovable.current;
    if (premove)
        for (i in premove)
            addSquare(squares, premove[i], 'current-premove');
    else if (s.predroppable.current)
        addSquare(squares, s.predroppable.current.key, 'current-premove');
    var o = s.exploding;
    if (o)
        for (i in o.keys)
            addSquare(squares, o.keys[i], 'exploding' + o.stage);
    return squares;
}
function addSquare(squares, key, klass) {
    if (squares[key])
        squares[key] += ' ' + klass;
    else
        squares[key] = klass;
}

},{"./util":17}],14:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var fen = require("./fen");
var util_1 = require("./util");
function defaults() {
    return {
        pieces: fen.read(fen.initial),
        orientation: 'white',
        turnColor: 'white',
        coordinates: true,
        autoCastle: true,
        viewOnly: false,
        disableContextMenu: false,
        resizable: true,
        addPieceZIndex: false,
        pieceKey: false,
        highlight: {
            lastMove: true,
            check: true
        },
        animation: {
            enabled: true,
            duration: 200
        },
        movable: {
            free: true,
            color: 'both',
            showDests: true,
            events: {},
            rookCastle: true
        },
        premovable: {
            enabled: true,
            showDests: true,
            castle: true,
            events: {}
        },
        predroppable: {
            enabled: false,
            events: {}
        },
        draggable: {
            enabled: true,
            distance: 3,
            autoDistance: true,
            centerPiece: true,
            showGhost: true,
            deleteOnDropOff: false
        },
        selectable: {
            enabled: true
        },
        stats: {
            dragged: !('ontouchstart' in window)
        },
        events: {},
        drawable: {
            enabled: true,
            eraseOnClick: true,
            shapes: [],
            autoShapes: [],
            brushes: {
                green: { key: 'g', color: '#15781B', opacity: 1, lineWidth: 10 },
                red: { key: 'r', color: '#882020', opacity: 1, lineWidth: 10 },
                blue: { key: 'b', color: '#003088', opacity: 1, lineWidth: 10 },
                yellow: { key: 'y', color: '#e68f00', opacity: 1, lineWidth: 10 },
                paleBlue: { key: 'pb', color: '#003088', opacity: 0.4, lineWidth: 15 },
                paleGreen: { key: 'pg', color: '#15781B', opacity: 0.4, lineWidth: 15 },
                paleRed: { key: 'pr', color: '#882020', opacity: 0.4, lineWidth: 15 },
                paleGrey: { key: 'pgr', color: '#4a4a4a', opacity: 0.35, lineWidth: 15 }
            },
            pieces: {
                baseUrl: 'https://lichess1.org/assets/piece/cburnett/'
            }
        },
        hold: util_1.timer()
    };
}
exports.defaults = defaults;

},{"./fen":10,"./util":17}],15:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var util_1 = require("./util");
function createElement(tagName) {
    return document.createElementNS('http://www.w3.org/2000/svg', tagName);
}
exports.createElement = createElement;
var isTrident;
var fullHashPrev = '';
function clearCache() {
    fullHashPrev = '';
}
exports.clearCache = clearCache;
function renderSvg(state, root) {
    var d = state.drawable, shapes = d.shapes.concat(d.autoShapes).map(function (s) {
        return {
            shape: s,
            current: false,
            hash: shapeHash(s, false)
        };
    });
    if (d.current)
        shapes.push({
            shape: d.current,
            current: true,
            hash: shapeHash(d.current, true)
        });
    var fullHash = shapes.map(function (sc) { return sc.hash; }).join('');
    if (fullHash === fullHashPrev)
        return;
    fullHashPrev = fullHash;
    var defsEl = root.firstChild;
    syncDefs(d, shapes, defsEl);
    syncShapes(state, shapes, d.brushes, root, defsEl);
}
exports.renderSvg = renderSvg;
function syncDefs(d, shapes, defsEl) {
    var brushes = {};
    var brush;
    shapes.forEach(function (s) {
        if (s.shape.dest) {
            brush = d.brushes[s.shape.brush];
            if (s.shape.modifiers)
                brush = makeCustomBrush(brush, s.shape.modifiers);
            brushes[brush.key] = brush;
        }
    });
    var keysInDom = {};
    var el = defsEl.firstChild;
    while (el) {
        keysInDom[el.getAttribute('cgKey')] = true;
        el = el.nextSibling;
    }
    for (var key in brushes) {
        if (!keysInDom[key])
            defsEl.appendChild(renderMarker(brushes[key]));
    }
}
function syncShapes(state, shapes, brushes, root, defsEl) {
    if (isTrident === undefined)
        isTrident = util_1.computeIsTrident();
    var bounds = state.dom.bounds(), hashesInDom = {}, toRemove = [];
    shapes.forEach(function (sc) { hashesInDom[sc.hash] = false; });
    var el = defsEl.nextSibling, elHash;
    while (el) {
        elHash = el.getAttribute('cgHash');
        if (hashesInDom.hasOwnProperty(elHash))
            hashesInDom[elHash] = true;
        else
            toRemove.push(el);
        el = el.nextSibling;
    }
    toRemove.forEach(function (el) { return root.removeChild(el); });
    shapes.forEach(function (sc) {
        if (!hashesInDom[sc.hash])
            root.appendChild(renderShape(state, sc, brushes, bounds));
    });
}
function shapeHash(_a, current) {
    var orig = _a.orig, dest = _a.dest, brush = _a.brush, piece = _a.piece, modifiers = _a.modifiers;
    return [current, orig, dest, brush,
        piece && pieceHash(piece),
        modifiers && modifiersHash(modifiers)
    ].filter(function (x) { return x; }).join('');
}
function pieceHash(piece) {
    return [piece.color, piece.role, piece.scale].filter(function (x) { return x; }).join('');
}
function modifiersHash(m) {
    return '' + (m.lineWidth || '');
}
function renderShape(state, _a, brushes, bounds) {
    var shape = _a.shape, current = _a.current, hash = _a.hash;
    var el;
    if (shape.piece)
        el = renderPiece(state.drawable.pieces.baseUrl, orient(util_1.key2pos(shape.orig), state.orientation), shape.piece, bounds);
    else {
        var orig = orient(util_1.key2pos(shape.orig), state.orientation);
        if (shape.orig && shape.dest) {
            var brush = brushes[shape.brush];
            if (shape.modifiers)
                brush = makeCustomBrush(brush, shape.modifiers);
            el = renderArrow(brush, orig, orient(util_1.key2pos(shape.dest), state.orientation), current, bounds);
        }
        else
            el = renderCircle(brushes[shape.brush], orig, current, bounds);
    }
    el.setAttribute('cgHash', hash);
    return el;
}
function renderCircle(brush, pos, current, bounds) {
    var o = pos2px(pos, bounds), width = circleWidth(current, bounds), radius = (bounds.width + bounds.height) / 32;
    return setAttributes(createElement('circle'), {
        stroke: brush.color,
        'stroke-width': width,
        fill: 'none',
        opacity: opacity(brush, current),
        cx: o[0],
        cy: o[1],
        r: radius - width / 2
    });
}
function renderArrow(brush, orig, dest, current, bounds) {
    var m = arrowMargin(bounds, current), a = pos2px(orig, bounds), b = pos2px(dest, bounds), dx = b[0] - a[0], dy = b[1] - a[1], angle = Math.atan2(dy, dx), xo = Math.cos(angle) * m, yo = Math.sin(angle) * m;
    return setAttributes(createElement('line'), {
        stroke: brush.color,
        'stroke-width': lineWidth(brush, current, bounds),
        'stroke-linecap': 'round',
        'marker-end': isTrident ? undefined : 'url(#arrowhead-' + brush.key + ')',
        opacity: opacity(brush, current),
        x1: a[0],
        y1: a[1],
        x2: b[0] - xo,
        y2: b[1] - yo
    });
}
function renderPiece(baseUrl, pos, piece, bounds) {
    var o = pos2px(pos, bounds), size = bounds.width / 8 * (piece.scale || 1), name = piece.color[0] + (piece.role === 'knight' ? 'n' : piece.role[0]).toUpperCase();
    return setAttributes(createElement('image'), {
        className: piece.role + " " + piece.color,
        x: o[0] - size / 2,
        y: o[1] - size / 2,
        width: size,
        height: size,
        href: baseUrl + name + '.svg'
    });
}
function renderMarker(brush) {
    var marker = setAttributes(createElement('marker'), {
        id: 'arrowhead-' + brush.key,
        orient: 'auto',
        markerWidth: 4,
        markerHeight: 8,
        refX: 2.05,
        refY: 2.01
    });
    marker.appendChild(setAttributes(createElement('path'), {
        d: 'M0,0 V4 L3,2 Z',
        fill: brush.color
    }));
    marker.setAttribute('cgKey', brush.key);
    return marker;
}
function setAttributes(el, attrs) {
    for (var key in attrs)
        el.setAttribute(key, attrs[key]);
    return el;
}
function orient(pos, color) {
    return color === 'white' ? pos : [9 - pos[0], 9 - pos[1]];
}
function makeCustomBrush(base, modifiers) {
    var brush = {
        color: base.color,
        opacity: Math.round(base.opacity * 10) / 10,
        lineWidth: Math.round(modifiers.lineWidth || base.lineWidth)
    };
    brush.key = [base.key, modifiers.lineWidth].filter(function (x) { return x; }).join('');
    return brush;
}
function circleWidth(current, bounds) {
    return (current ? 3 : 4) / 512 * bounds.width;
}
function lineWidth(brush, current, bounds) {
    return (brush.lineWidth || 10) * (current ? 0.85 : 1) / 512 * bounds.width;
}
function opacity(brush, current) {
    return (brush.opacity || 1) * (current ? 0.9 : 1);
}
function arrowMargin(bounds, current) {
    return isTrident ? 0 : ((current ? 10 : 20) / 512 * bounds.width);
}
function pos2px(pos, bounds) {
    return [(pos[0] - 0.5) * bounds.width / 8, (8.5 - pos[1]) * bounds.height / 8];
}

},{"./util":17}],16:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
exports.ranks = [1, 2, 3, 4, 5, 6, 7, 8];

},{}],17:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var cg = require("./types");
exports.colors = ['white', 'black'];
exports.invRanks = [8, 7, 6, 5, 4, 3, 2, 1];
exports.allKeys = (_a = Array.prototype).concat.apply(_a, cg.files.map(function (c) { return cg.ranks.map(function (r) { return c + r; }); }));
exports.pos2key = function (pos) { return exports.allKeys[8 * pos[0] + pos[1] - 9]; };
exports.key2pos = function (k) { return [k.charCodeAt(0) - 96, k.charCodeAt(1) - 48]; };
function memo(f) {
    var v;
    var ret = function () {
        if (v === undefined)
            v = f();
        return v;
    };
    ret.clear = function () { v = undefined; };
    return ret;
}
exports.memo = memo;
exports.timer = function () {
    var startAt;
    return {
        start: function () { startAt = new Date(); },
        cancel: function () { startAt = undefined; },
        stop: function () {
            if (!startAt)
                return 0;
            var time = new Date().getTime() - startAt.getTime();
            startAt = undefined;
            return time;
        }
    };
};
exports.opposite = function (c) { return c === 'white' ? 'black' : 'white'; };
function containsX(xs, x) {
    return xs ? xs.indexOf(x) !== -1 : false;
}
exports.containsX = containsX;
exports.distanceSq = function (pos1, pos2) {
    return Math.pow(pos1[0] - pos2[0], 2) + Math.pow(pos1[1] - pos2[1], 2);
};
exports.samePiece = function (p1, p2) {
    return p1.role === p2.role && p1.color === p2.color;
};
exports.transformFunction = function () {
    var s = document.body.style;
    var prop = 'transform' in s ?
        'transform' : 'webkitTransform' in s ?
        'webkitTransform' : 'mozTransform' in s ?
        'mozTransform' : 'oTransform' in s ?
        'oTransform' : 'msTransform';
    return function (el, value) {
        el.style[prop] = value;
    };
};
exports.computeIsTrident = function () { return window.navigator.userAgent.indexOf('Trident/') > -1; };
exports.posToTranslate = function (pos, asWhite, bounds) {
    return [
        (asWhite ? pos[0] - 1 : 8 - pos[0]) * bounds.width / 8,
        (asWhite ? 8 - pos[1] : pos[1] - 1) * bounds.height / 8
    ];
};
exports.translate = function (pos) { return 'translate(' + pos[0] + 'px,' + pos[1] + 'px)'; };
exports.translateAway = exports.translate([-99999, -99999]);
exports.eventPosition = function (e) {
    if (e.clientX || e.clientX === 0)
        return [e.clientX, e.clientY];
    if (e.touches && e.targetTouches[0])
        return [e.targetTouches[0].clientX, e.targetTouches[0].clientY];
    return undefined;
};
exports.isRightButton = function (e) { return e.buttons === 2 || e.button === 2; };
exports.createEl = function (tagName, className) {
    var el = document.createElement(tagName);
    if (className)
        el.className = className;
    return el;
};
exports.raf = (window.requestAnimationFrame || window.setTimeout).bind(window);
var _a;

},{"./types":16}],18:[function(require,module,exports){
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var util_1 = require("./util");
var types_1 = require("./types");
var svg_1 = require("./svg");
function wrap(element, s, bounds) {
    element.innerHTML = '';
    element.classList.add('cg-board-wrap');
    util_1.colors.forEach(function (c) {
        element.classList.toggle('orientation-' + c, s.orientation === c);
    });
    element.classList.toggle('manipulable', !s.viewOnly);
    var board = util_1.createEl('div', 'cg-board');
    element.appendChild(board);
    var svg;
    if (s.drawable.enabled) {
        svg = svg_1.createElement('svg');
        svg.appendChild(svg_1.createElement('defs'));
        element.appendChild(svg);
    }
    if (s.coordinates) {
        var orientClass = s.orientation === 'black' ? ' black' : '';
        element.appendChild(renderCoords(types_1.ranks, 'ranks' + orientClass));
        element.appendChild(renderCoords(types_1.files, 'files' + orientClass));
    }
    var over;
    if (!s.viewOnly && (s.movable.showDests || s.premovable.showDests)) {
        over = util_1.createEl('div', 'over');
        s.browser.transform(over, util_1.translateAway);
        over.style.width = (bounds.width / 8) + 'px';
        over.style.height = (bounds.height / 8) + 'px';
        element.appendChild(over);
    }
    var ghost;
    if (!s.viewOnly && s.draggable.showGhost) {
        ghost = util_1.createEl('piece', 'ghost');
        s.browser.transform(ghost, util_1.translateAway);
        element.appendChild(ghost);
    }
    return {
        board: board,
        over: over,
        ghost: ghost,
        svg: svg
    };
}
exports.default = wrap;
function renderCoords(elems, className) {
    var el = util_1.createEl('coords', className);
    var f;
    for (var i in elems) {
        f = util_1.createEl('coord');
        f.textContent = elems[i];
        el.appendChild(f);
    }
    return el;
}

},{"./svg":15,"./types":16,"./util":17}]},{},[11])(11)
});
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCJzcmMvYW5pbS50cyIsInNyYy9hcGkudHMiLCJzcmMvYm9hcmQudHMiLCJzcmMvY2hlc3Nncm91bmQudHMiLCJzcmMvY29uZmlnLnRzIiwic3JjL2RyYWcudHMiLCJzcmMvZHJhdy50cyIsInNyYy9ldmVudHMudHMiLCJzcmMvZXhwbG9zaW9uLnRzIiwic3JjL2Zlbi50cyIsInNyYy9pbmRleC5qcyIsInNyYy9wcmVtb3ZlLnRzIiwic3JjL3JlbmRlci50cyIsInNyYy9zdGF0ZS50cyIsInNyYy9zdmcudHMiLCJzcmMvdHlwZXMudHMiLCJzcmMvdXRpbC50cyIsInNyYy93cmFwLnRzIl0sIm5hbWVzIjpbXSwibWFwcGluZ3MiOiJBQUFBOzs7Ozs7Ozs7OztBQ0NBLDZCQUE4QjtBQWdDOUIsY0FBd0IsUUFBcUIsRUFBRSxLQUFZO0lBQ3pELE1BQU0sQ0FBQyxLQUFLLENBQUMsU0FBUyxDQUFDLE9BQU8sR0FBRyxPQUFPLENBQUMsUUFBUSxFQUFFLEtBQUssQ0FBQyxHQUFHLE1BQU0sQ0FBQyxRQUFRLEVBQUUsS0FBSyxDQUFDLENBQUM7QUFDdEYsQ0FBQztBQUZELG9CQUVDO0FBRUQsZ0JBQTBCLFFBQXFCLEVBQUUsS0FBWTtJQUMzRCxJQUFNLE1BQU0sR0FBRyxRQUFRLENBQUMsS0FBSyxDQUFDLENBQUM7SUFDL0IsS0FBSyxDQUFDLEdBQUcsQ0FBQyxNQUFNLEVBQUUsQ0FBQztJQUNuQixNQUFNLENBQUMsTUFBTSxDQUFDO0FBQ2hCLENBQUM7QUFKRCx3QkFJQztBQVdELG1CQUFtQixHQUFXLEVBQUUsS0FBZTtJQUM3QyxNQUFNLENBQUM7UUFDTCxHQUFHLEVBQUUsR0FBRztRQUNSLEdBQUcsRUFBRSxJQUFJLENBQUMsT0FBTyxDQUFDLEdBQUcsQ0FBQztRQUN0QixLQUFLLEVBQUUsS0FBSztLQUNiLENBQUM7QUFDSixDQUFDO0FBRUQsZ0JBQWdCLEtBQWdCLEVBQUUsTUFBbUI7SUFDbkQsTUFBTSxDQUFDLE1BQU0sQ0FBQyxJQUFJLENBQUMsVUFBQyxFQUFFLEVBQUUsRUFBRTtRQUN4QixNQUFNLENBQUMsSUFBSSxDQUFDLFVBQVUsQ0FBQyxLQUFLLENBQUMsR0FBRyxFQUFFLEVBQUUsQ0FBQyxHQUFHLENBQUMsR0FBRyxJQUFJLENBQUMsVUFBVSxDQUFDLEtBQUssQ0FBQyxHQUFHLEVBQUUsRUFBRSxDQUFDLEdBQUcsQ0FBQyxDQUFDO0lBQ2pGLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDO0FBQ1IsQ0FBQztBQUVELHFCQUFxQixVQUFxQixFQUFFLE9BQWM7SUFDeEQsSUFBTSxNQUFNLEdBQUcsT0FBTyxDQUFDLEdBQUcsQ0FBQyxNQUFNLEVBQUUsRUFDbkMsS0FBSyxHQUFHLE1BQU0sQ0FBQyxLQUFLLEdBQUcsQ0FBQyxFQUN4QixNQUFNLEdBQUcsTUFBTSxDQUFDLE1BQU0sR0FBRyxDQUFDLEVBQzFCLEtBQUssR0FBZ0IsRUFBRSxFQUN2QixXQUFXLEdBQWEsRUFBRSxFQUMxQixPQUFPLEdBQWdCLEVBQUUsRUFDekIsUUFBUSxHQUFnQixFQUFFLEVBQzFCLElBQUksR0FBZ0IsRUFBRSxFQUN0QixTQUFTLEdBQWUsRUFBRSxFQUMxQixLQUFLLEdBQUcsT0FBTyxDQUFDLFdBQVcsS0FBSyxPQUFPLENBQUM7SUFDeEMsSUFBSSxJQUFjLEVBQUUsSUFBZSxFQUFFLENBQU0sRUFBRSxJQUFZLEVBQUUsSUFBWSxFQUFFLE1BQXFCLENBQUM7SUFDL0YsR0FBRyxDQUFDLENBQUMsQ0FBQyxJQUFJLFVBQVUsQ0FBQyxDQUFDLENBQUM7UUFDckIsU0FBUyxDQUFDLENBQUMsQ0FBQyxHQUFHLFNBQVMsQ0FBQyxDQUFXLEVBQUUsVUFBVSxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUM7SUFDdkQsQ0FBQztJQUNELEdBQUcsQ0FBQyxDQUFjLFVBQVksRUFBWixLQUFBLElBQUksQ0FBQyxPQUFPLEVBQVosY0FBWSxFQUFaLElBQVk7UUFBekIsSUFBTSxHQUFHLFNBQUE7UUFDWixJQUFJLEdBQUcsT0FBTyxDQUFDLE1BQU0sQ0FBQyxHQUFHLENBQUMsQ0FBQztRQUMzQixJQUFJLEdBQUcsU0FBUyxDQUFDLEdBQUcsQ0FBQyxDQUFDO1FBQ3RCLEVBQUUsQ0FBQyxDQUFDLElBQUksQ0FBQyxDQUFDLENBQUM7WUFDVCxFQUFFLENBQUMsQ0FBQyxJQUFJLENBQUMsQ0FBQyxDQUFDO2dCQUNULEVBQUUsQ0FBQyxDQUFDLENBQUMsSUFBSSxDQUFDLFNBQVMsQ0FBQyxJQUFJLEVBQUUsSUFBSSxDQUFDLEtBQUssQ0FBQyxDQUFDLENBQUMsQ0FBQztvQkFDdEMsUUFBUSxDQUFDLElBQUksQ0FBQyxJQUFJLENBQUMsQ0FBQztvQkFDcEIsSUFBSSxDQUFDLElBQUksQ0FBQyxTQUFTLENBQUMsR0FBRyxFQUFFLElBQUksQ0FBQyxDQUFDLENBQUM7Z0JBQ2xDLENBQUM7WUFDSCxDQUFDO1lBQUMsSUFBSTtnQkFBQyxJQUFJLENBQUMsSUFBSSxDQUFDLFNBQVMsQ0FBQyxHQUFHLEVBQUUsSUFBSSxDQUFDLENBQUMsQ0FBQztRQUN6QyxDQUFDO1FBQUMsSUFBSSxDQUFDLEVBQUUsQ0FBQyxDQUFDLElBQUksQ0FBQztZQUFDLFFBQVEsQ0FBQyxJQUFJLENBQUMsSUFBSSxDQUFDLENBQUM7S0FDdEM7SUFDRCxJQUFJLENBQUMsT0FBTyxDQUFDLFVBQUEsSUFBSTtRQUNmLElBQUksR0FBRyxNQUFNLENBQUMsSUFBSSxFQUFFLFFBQVEsQ0FBQyxNQUFNLENBQUMsVUFBQSxDQUFDLElBQUksT0FBQSxJQUFJLENBQUMsU0FBUyxDQUFDLElBQUksQ0FBQyxLQUFLLEVBQUUsQ0FBQyxDQUFDLEtBQUssQ0FBQyxFQUFuQyxDQUFtQyxDQUFDLENBQUMsQ0FBQztRQUMvRSxFQUFFLENBQUMsQ0FBQyxJQUFJLENBQUMsQ0FBQyxDQUFDO1lBQ1QsSUFBSSxHQUFHLEtBQUssR0FBRyxJQUFJLENBQUMsR0FBRyxHQUFHLElBQUksQ0FBQyxHQUFHLENBQUM7WUFDbkMsSUFBSSxHQUFHLEtBQUssR0FBRyxJQUFJLENBQUMsR0FBRyxHQUFHLElBQUksQ0FBQyxHQUFHLENBQUM7WUFDbkMsTUFBTSxHQUFHLENBQUMsQ0FBQyxJQUFJLENBQUMsQ0FBQyxDQUFDLEdBQUcsSUFBSSxDQUFDLENBQUMsQ0FBQyxDQUFDLEdBQUcsS0FBSyxFQUFFLENBQUMsSUFBSSxDQUFDLENBQUMsQ0FBQyxHQUFHLElBQUksQ0FBQyxDQUFDLENBQUMsQ0FBQyxHQUFHLE1BQU0sQ0FBQyxDQUFDO1lBQ3JFLEtBQUssQ0FBQyxJQUFJLENBQUMsR0FBRyxDQUFDLEdBQUcsQ0FBQyxNQUFNLEVBQUUsTUFBTSxDQUFDLENBQUM7WUFDbkMsV0FBVyxDQUFDLElBQUksQ0FBQyxJQUFJLENBQUMsR0FBRyxDQUFDLENBQUM7UUFDN0IsQ0FBQztJQUNILENBQUMsQ0FBQyxDQUFDO0lBQ0gsUUFBUSxDQUFDLE9BQU8sQ0FBQyxVQUFBLENBQUM7UUFDaEIsRUFBRSxDQUFDLENBQ0QsQ0FBQyxJQUFJLENBQUMsU0FBUyxDQUFDLFdBQVcsRUFBRSxDQUFDLENBQUMsR0FBRyxDQUFDO1lBQ25DLENBQUMsQ0FBQyxPQUFPLENBQUMsS0FBSyxHQUFHLE9BQU8sQ0FBQyxLQUFLLENBQUMsQ0FBQyxDQUFDLEdBQUcsRUFBRSxDQUFDLENBQUMsR0FBRyxDQUFDLEdBQUcsS0FBSyxDQUN2RCxDQUFDO1lBQ0QsT0FBTyxDQUFDLENBQUMsQ0FBQyxHQUFHLENBQUMsR0FBRyxDQUFDLENBQUMsS0FBSyxDQUFDO0lBQzNCLENBQUMsQ0FBQyxDQUFDO0lBRUgsTUFBTSxDQUFDO1FBQ0wsS0FBSyxFQUFFLEtBQUs7UUFDWixPQUFPLEVBQUUsT0FBTztLQUNqQixDQUFDO0FBQ0osQ0FBQztBQUVELGNBQWMsS0FBWTtJQUN4QixJQUFNLEdBQUcsR0FBRyxLQUFLLENBQUMsU0FBUyxDQUFDLE9BQU8sQ0FBQztJQUNwQyxFQUFFLENBQUMsQ0FBQyxDQUFDLEdBQUcsQ0FBQyxDQUFDLENBQUM7UUFDVCxFQUFFLENBQUMsQ0FBQyxDQUFDLEtBQUssQ0FBQyxHQUFHLENBQUMsU0FBUyxDQUFDO1lBQUMsS0FBSyxDQUFDLEdBQUcsQ0FBQyxTQUFTLEVBQUUsQ0FBQztRQUNoRCxNQUFNLENBQUM7SUFDVCxDQUFDO0lBQ0QsSUFBTSxJQUFJLEdBQUcsQ0FBQyxHQUFHLENBQUMsSUFBSSxJQUFJLEVBQUUsQ0FBQyxPQUFPLEVBQUUsR0FBRyxHQUFHLENBQUMsS0FBSyxDQUFDLEdBQUcsR0FBRyxDQUFDLFFBQVEsQ0FBQztJQUNuRSxFQUFFLENBQUMsQ0FBQyxJQUFJLElBQUksQ0FBQyxDQUFDLENBQUMsQ0FBQztRQUNkLEtBQUssQ0FBQyxTQUFTLENBQUMsT0FBTyxHQUFHLFNBQVMsQ0FBQztRQUNwQyxLQUFLLENBQUMsR0FBRyxDQUFDLFNBQVMsRUFBRSxDQUFDO0lBQ3hCLENBQUM7SUFBQyxJQUFJLENBQUMsQ0FBQztRQUNOLElBQU0sSUFBSSxHQUFHLE1BQU0sQ0FBQyxJQUFJLENBQUMsQ0FBQztRQUMxQixHQUFHLENBQUMsQ0FBQyxJQUFJLENBQUMsSUFBSSxHQUFHLENBQUMsSUFBSSxDQUFDLEtBQUssQ0FBQyxDQUFDLENBQUM7WUFDN0IsSUFBTSxHQUFHLEdBQUcsR0FBRyxDQUFDLElBQUksQ0FBQyxLQUFLLENBQUMsQ0FBQyxDQUFDLENBQUM7WUFDOUIsR0FBRyxDQUFDLENBQUMsQ0FBQyxHQUFHLENBQUMsT0FBTyxDQUFDLEdBQUcsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsR0FBRyxJQUFJLEVBQUUsRUFBRSxDQUFDLEVBQUUsT0FBTyxDQUFDLEdBQUcsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsR0FBRyxJQUFJLEVBQUUsRUFBRSxDQUFDLENBQUMsQ0FBQztRQUMxRSxDQUFDO1FBQ0QsS0FBSyxDQUFDLEdBQUcsQ0FBQyxTQUFTLENBQUMsSUFBSSxDQUFDLENBQUM7UUFDMUIsSUFBSSxDQUFDLEdBQUcsQ0FBQyxjQUFNLE9BQUEsSUFBSSxDQUFDLEtBQUssQ0FBQyxFQUFYLENBQVcsQ0FBQyxDQUFDO0lBQzlCLENBQUM7QUFDSCxDQUFDO0FBRUQsaUJBQW9CLFFBQXFCLEVBQUUsS0FBWTtJQUVyRCxJQUFNLFVBQVUsZ0JBQWtCLEtBQUssQ0FBQyxNQUFNLENBQUMsQ0FBQztJQUVoRCxJQUFNLE1BQU0sR0FBRyxRQUFRLENBQUMsS0FBSyxDQUFDLENBQUM7SUFDL0IsSUFBTSxJQUFJLEdBQUcsV0FBVyxDQUFDLFVBQVUsRUFBRSxLQUFLLENBQUMsQ0FBQztJQUM1QyxFQUFFLENBQUMsQ0FBQyxDQUFDLGFBQWEsQ0FBQyxJQUFJLENBQUMsS0FBSyxDQUFDLElBQUksQ0FBQyxhQUFhLENBQUMsSUFBSSxDQUFDLE9BQU8sQ0FBQyxDQUFDLENBQUMsQ0FBQztRQUMvRCxJQUFNLGNBQWMsR0FBRyxLQUFLLENBQUMsU0FBUyxDQUFDLE9BQU8sSUFBSSxLQUFLLENBQUMsU0FBUyxDQUFDLE9BQU8sQ0FBQyxLQUFLLENBQUM7UUFDaEYsS0FBSyxDQUFDLFNBQVMsQ0FBQyxPQUFPLEdBQUc7WUFDeEIsS0FBSyxFQUFFLElBQUksSUFBSSxFQUFFLENBQUMsT0FBTyxFQUFFO1lBQzNCLFFBQVEsRUFBRSxLQUFLLENBQUMsU0FBUyxDQUFDLFFBQVE7WUFDbEMsSUFBSSxFQUFFLElBQUk7U0FDWCxDQUFDO1FBQ0YsRUFBRSxDQUFDLENBQUMsQ0FBQyxjQUFjLENBQUM7WUFBQyxJQUFJLENBQUMsS0FBSyxDQUFDLENBQUM7SUFDbkMsQ0FBQztJQUFDLElBQUksQ0FBQyxDQUFDO1FBRU4sS0FBSyxDQUFDLEdBQUcsQ0FBQyxNQUFNLEVBQUUsQ0FBQztJQUNyQixDQUFDO0lBQ0QsTUFBTSxDQUFDLE1BQU0sQ0FBQztBQUNoQixDQUFDO0FBRUQsdUJBQXVCLENBQU07SUFDM0IsR0FBRyxDQUFDLENBQUMsSUFBSSxDQUFDLElBQUksQ0FBQyxDQUFDO1FBQUMsTUFBTSxDQUFDLEtBQUssQ0FBQztJQUM5QixNQUFNLENBQUMsSUFBSSxDQUFDO0FBQ2QsQ0FBQztBQUVELGdCQUFnQixDQUFTO0lBQ3ZCLE1BQU0sQ0FBQyxDQUFDLEdBQUcsR0FBRyxHQUFHLENBQUMsR0FBRyxDQUFDLEdBQUcsQ0FBQyxHQUFHLENBQUMsR0FBRyxDQUFDLENBQUMsR0FBRyxDQUFDLENBQUMsR0FBRyxDQUFDLENBQUMsR0FBRyxDQUFDLEdBQUcsQ0FBQyxDQUFDLEdBQUcsQ0FBQyxDQUFDLEdBQUcsQ0FBQyxHQUFHLENBQUMsQ0FBQyxHQUFHLENBQUMsQ0FBQztBQUMzRSxDQUFDO0FBQ0QsaUJBQWlCLENBQVMsRUFBRSxFQUFVO0lBQ3BDLE1BQU0sQ0FBQyxJQUFJLENBQUMsS0FBSyxDQUFDLENBQUMsR0FBRyxFQUFFLENBQUMsR0FBRyxFQUFFLENBQUM7QUFDakMsQ0FBQzs7Ozs7QUN4S0QsK0JBQWdDO0FBQ2hDLDZCQUF5QztBQUN6QyxtQ0FBNEM7QUFDNUMsK0JBQXFDO0FBQ3JDLCtCQUEyRDtBQUUzRCx5Q0FBbUM7QUF5RW5DLGVBQXNCLEtBQVksRUFBRSxTQUFvQjtJQUV0RDtRQUNFLEtBQUssQ0FBQyxpQkFBaUIsQ0FBQyxLQUFLLENBQUMsQ0FBQztRQUMvQixTQUFTLEVBQUUsQ0FBQztJQUNkLENBQUM7SUFBQSxDQUFDO0lBRUYsTUFBTSxDQUFDO1FBRUwsR0FBRyxZQUFDLE1BQU07WUFDUixFQUFFLENBQUMsQ0FBQyxNQUFNLENBQUMsV0FBVyxJQUFJLE1BQU0sQ0FBQyxXQUFXLEtBQUssS0FBSyxDQUFDLFdBQVcsQ0FBQztnQkFBQyxpQkFBaUIsRUFBRSxDQUFDO1lBQ3hGLENBQUMsTUFBTSxDQUFDLEdBQUcsR0FBRyxXQUFJLEdBQUcsYUFBTSxDQUFDLENBQUMsVUFBQSxLQUFLLElBQUksT0FBQSxrQkFBUyxDQUFDLEtBQUssRUFBRSxNQUFNLENBQUMsRUFBeEIsQ0FBd0IsRUFBRSxLQUFLLENBQUMsQ0FBQztRQUN6RSxDQUFDO1FBRUQsS0FBSyxPQUFBO1FBRUwsTUFBTSxFQUFFLGNBQU0sT0FBQSxXQUFRLENBQUMsS0FBSyxDQUFDLE1BQU0sQ0FBQyxFQUF0QixDQUFzQjtRQUVwQyxpQkFBaUIsbUJBQUE7UUFFakIsU0FBUyxZQUFDLE1BQU07WUFDZCxXQUFJLENBQUMsVUFBQSxLQUFLLElBQUksT0FBQSxLQUFLLENBQUMsU0FBUyxDQUFDLEtBQUssRUFBRSxNQUFNLENBQUMsRUFBOUIsQ0FBOEIsRUFBRSxLQUFLLENBQUMsQ0FBQztRQUN2RCxDQUFDO1FBRUQsWUFBWSxZQUFDLEdBQUcsRUFBRSxLQUFLO1lBQ3JCLEVBQUUsQ0FBQyxDQUFDLEdBQUcsSUFBSSxLQUFLLENBQUMsUUFBUSxDQUFDO2dCQUFDLFdBQUksQ0FBQyxVQUFBLEtBQUssSUFBSSxPQUFBLEtBQUssQ0FBQyxZQUFZLENBQUMsS0FBSyxFQUFFLEdBQUcsRUFBRSxLQUFLLENBQUMsRUFBckMsQ0FBcUMsRUFBRSxLQUFLLENBQUMsQ0FBQztRQUN6RixDQUFDO1FBRUQsSUFBSSxZQUFDLElBQUksRUFBRSxJQUFJO1lBQ2IsV0FBSSxDQUFDLFVBQUEsS0FBSyxJQUFJLE9BQUEsS0FBSyxDQUFDLFFBQVEsQ0FBQyxLQUFLLEVBQUUsSUFBSSxFQUFFLElBQUksQ0FBQyxFQUFqQyxDQUFpQyxFQUFFLEtBQUssQ0FBQyxDQUFDO1FBQzFELENBQUM7UUFFRCxRQUFRLFlBQUMsS0FBSyxFQUFFLEdBQUc7WUFDakIsV0FBSSxDQUFDLFVBQUEsS0FBSyxJQUFJLE9BQUEsS0FBSyxDQUFDLFlBQVksQ0FBQyxLQUFLLEVBQUUsS0FBSyxFQUFFLEdBQUcsQ0FBQyxFQUFyQyxDQUFxQyxFQUFFLEtBQUssQ0FBQyxDQUFDO1FBQzlELENBQUM7UUFFRCxXQUFXO1lBQ1QsRUFBRSxDQUFDLENBQUMsS0FBSyxDQUFDLFVBQVUsQ0FBQyxPQUFPLENBQUMsQ0FBQyxDQUFDO2dCQUM3QixFQUFFLENBQUMsQ0FBQyxXQUFJLENBQUMsS0FBSyxDQUFDLFdBQVcsRUFBRSxLQUFLLENBQUMsQ0FBQztvQkFBQyxNQUFNLENBQUMsSUFBSSxDQUFDO2dCQUVoRCxLQUFLLENBQUMsR0FBRyxDQUFDLE1BQU0sRUFBRSxDQUFDO1lBQ3JCLENBQUM7WUFDRCxNQUFNLENBQUMsS0FBSyxDQUFDO1FBQ2YsQ0FBQztRQUVELFdBQVcsWUFBQyxRQUFRO1lBQ2xCLEVBQUUsQ0FBQyxDQUFDLEtBQUssQ0FBQyxZQUFZLENBQUMsT0FBTyxDQUFDLENBQUMsQ0FBQztnQkFDL0IsSUFBTSxNQUFNLEdBQUcsS0FBSyxDQUFDLFdBQVcsQ0FBQyxLQUFLLEVBQUUsUUFBUSxDQUFDLENBQUM7Z0JBQ2xELEtBQUssQ0FBQyxHQUFHLENBQUMsTUFBTSxFQUFFLENBQUM7Z0JBQ25CLE1BQU0sQ0FBQyxNQUFNLENBQUM7WUFDaEIsQ0FBQztZQUNELE1BQU0sQ0FBQyxLQUFLLENBQUM7UUFDZixDQUFDO1FBRUQsYUFBYTtZQUNYLGFBQU0sQ0FBQyxLQUFLLENBQUMsWUFBWSxFQUFFLEtBQUssQ0FBQyxDQUFDO1FBQ3BDLENBQUM7UUFFRCxhQUFhO1lBQ1gsYUFBTSxDQUFDLEtBQUssQ0FBQyxZQUFZLEVBQUUsS0FBSyxDQUFDLENBQUM7UUFDcEMsQ0FBQztRQUVELFVBQVU7WUFDUixhQUFNLENBQUMsVUFBQSxLQUFLLElBQU0sS0FBSyxDQUFDLFVBQVUsQ0FBQyxLQUFLLENBQUMsQ0FBQyxDQUFDLGFBQVUsQ0FBQyxLQUFLLENBQUMsQ0FBQyxDQUFDLENBQUMsRUFBRSxLQUFLLENBQUMsQ0FBQztRQUMxRSxDQUFDO1FBRUQsSUFBSTtZQUNGLGFBQU0sQ0FBQyxVQUFBLEtBQUssSUFBTSxLQUFLLENBQUMsSUFBSSxDQUFDLEtBQUssQ0FBQyxDQUFDLENBQUMsYUFBVSxDQUFDLEtBQUssQ0FBQyxDQUFDLENBQUMsQ0FBQyxFQUFFLEtBQUssQ0FBQyxDQUFDO1FBQ3BFLENBQUM7UUFFRCxPQUFPLFlBQUMsSUFBYztZQUNwQixtQkFBUyxDQUFDLEtBQUssRUFBRSxJQUFJLENBQUMsQ0FBQztRQUN6QixDQUFDO1FBRUQsYUFBYSxZQUFDLE1BQW1CO1lBQy9CLGFBQU0sQ0FBQyxVQUFBLEtBQUssSUFBSSxPQUFBLEtBQUssQ0FBQyxRQUFRLENBQUMsVUFBVSxHQUFHLE1BQU0sRUFBbEMsQ0FBa0MsRUFBRSxLQUFLLENBQUMsQ0FBQztRQUM3RCxDQUFDO1FBRUQsU0FBUyxZQUFDLE1BQW1CO1lBQzNCLGFBQU0sQ0FBQyxVQUFBLEtBQUssSUFBSSxPQUFBLEtBQUssQ0FBQyxRQUFRLENBQUMsTUFBTSxHQUFHLE1BQU0sRUFBOUIsQ0FBOEIsRUFBRSxLQUFLLENBQUMsQ0FBQztRQUN6RCxDQUFDO1FBRUQsY0FBYyxZQUFDLEdBQUc7WUFDaEIsTUFBTSxDQUFDLEtBQUssQ0FBQyxjQUFjLENBQUMsR0FBRyxFQUFFLEtBQUssQ0FBQyxXQUFXLEtBQUssT0FBTyxFQUFFLEtBQUssQ0FBQyxHQUFHLENBQUMsTUFBTSxFQUFFLENBQUMsQ0FBQztRQUN0RixDQUFDO1FBRUQsU0FBUyxXQUFBO1FBRVQsWUFBWSxZQUFDLEtBQUssRUFBRSxLQUFLLEVBQUUsS0FBSztZQUM5QixtQkFBWSxDQUFDLEtBQUssRUFBRSxLQUFLLEVBQUUsS0FBSyxFQUFFLEtBQUssQ0FBQyxDQUFBO1FBQzFDLENBQUM7UUFFRCxPQUFPO1lBQ0wsS0FBSyxDQUFDLElBQUksQ0FBQyxLQUFLLENBQUMsQ0FBQztZQUNsQixLQUFLLENBQUMsR0FBRyxDQUFDLE1BQU0sSUFBSSxLQUFLLENBQUMsR0FBRyxDQUFDLE1BQU0sRUFBRSxDQUFDO1lBQ3ZDLEtBQUssQ0FBQyxHQUFHLENBQUMsU0FBUyxHQUFHLElBQUksQ0FBQztRQUM3QixDQUFDO0tBQ0YsQ0FBQztBQUNKLENBQUM7QUFsR0Qsc0JBa0dDOzs7OztBQ2pMRCwrQkFBOEQ7QUFDOUQscUNBQStCO0FBSy9CLDBCQUFpQyxDQUF1QjtJQUFFLGNBQWM7U0FBZCxVQUFjLEVBQWQscUJBQWMsRUFBZCxJQUFjO1FBQWQsNkJBQWM7O0lBQ3RFLEVBQUUsQ0FBQyxDQUFDLENBQUMsQ0FBQztRQUFDLFVBQVUsQ0FBQyxjQUFNLE9BQUEsQ0FBQyxlQUFJLElBQUksR0FBVCxDQUFVLEVBQUUsQ0FBQyxDQUFDLENBQUM7QUFDekMsQ0FBQztBQUZELDRDQUVDO0FBRUQsMkJBQWtDLEtBQVk7SUFDNUMsS0FBSyxDQUFDLFdBQVcsR0FBRyxlQUFRLENBQUMsS0FBSyxDQUFDLFdBQVcsQ0FBQyxDQUFDO0lBQ2hELEtBQUssQ0FBQyxTQUFTLENBQUMsT0FBTztRQUN2QixLQUFLLENBQUMsU0FBUyxDQUFDLE9BQU87WUFDdkIsS0FBSyxDQUFDLFFBQVEsR0FBRyxTQUFTLENBQUM7QUFDN0IsQ0FBQztBQUxELDhDQUtDO0FBRUQsZUFBc0IsS0FBWTtJQUNoQyxLQUFLLENBQUMsUUFBUSxHQUFHLFNBQVMsQ0FBQztJQUMzQixRQUFRLENBQUMsS0FBSyxDQUFDLENBQUM7SUFDaEIsWUFBWSxDQUFDLEtBQUssQ0FBQyxDQUFDO0lBQ3BCLFlBQVksQ0FBQyxLQUFLLENBQUMsQ0FBQztBQUN0QixDQUFDO0FBTEQsc0JBS0M7QUFFRCxtQkFBMEIsS0FBWSxFQUFFLE1BQXFCO0lBQzNELEdBQUcsQ0FBQyxDQUFDLElBQUksR0FBRyxJQUFJLE1BQU0sQ0FBQyxDQUFDLENBQUM7UUFDdkIsSUFBTSxLQUFLLEdBQUcsTUFBTSxDQUFDLEdBQUcsQ0FBQyxDQUFDO1FBQzFCLEVBQUUsQ0FBQyxDQUFDLEtBQUssQ0FBQztZQUFDLEtBQUssQ0FBQyxNQUFNLENBQUMsR0FBRyxDQUFDLEdBQUcsS0FBSyxDQUFDO1FBQ3JDLElBQUk7WUFBQyxPQUFPLEtBQUssQ0FBQyxNQUFNLENBQUMsR0FBRyxDQUFDLENBQUM7SUFDaEMsQ0FBQztBQUNILENBQUM7QUFORCw4QkFNQztBQUVELGtCQUF5QixLQUFZLEVBQUUsS0FBeUI7SUFDOUQsRUFBRSxDQUFDLENBQUMsS0FBSyxLQUFLLElBQUksQ0FBQztRQUFDLEtBQUssR0FBRyxLQUFLLENBQUMsU0FBUyxDQUFDO0lBQzVDLEVBQUUsQ0FBQyxDQUFDLENBQUMsS0FBSyxDQUFDO1FBQUMsS0FBSyxDQUFDLEtBQUssR0FBRyxTQUFTLENBQUM7SUFDcEMsSUFBSTtRQUFDLEdBQUcsQ0FBQyxDQUFDLElBQUksQ0FBQyxJQUFJLEtBQUssQ0FBQyxNQUFNLENBQUMsQ0FBQyxDQUFDO1lBQ2hDLEVBQUUsQ0FBQyxDQUFDLEtBQUssQ0FBQyxNQUFNLENBQUMsQ0FBQyxDQUFDLENBQUMsSUFBSSxLQUFLLE1BQU0sSUFBSSxLQUFLLENBQUMsTUFBTSxDQUFDLENBQUMsQ0FBQyxDQUFDLEtBQUssS0FBSyxLQUFLLENBQUMsQ0FBQyxDQUFDO2dCQUN2RSxLQUFLLENBQUMsS0FBSyxHQUFHLENBQVcsQ0FBQztZQUM1QixDQUFDO1FBQ0gsQ0FBQztBQUNILENBQUM7QUFSRCw0QkFRQztBQUVELG9CQUFvQixLQUFZLEVBQUUsSUFBWSxFQUFFLElBQVksRUFBRSxJQUEyQjtJQUN2RixZQUFZLENBQUMsS0FBSyxDQUFDLENBQUM7SUFDcEIsS0FBSyxDQUFDLFVBQVUsQ0FBQyxPQUFPLEdBQUcsQ0FBQyxJQUFJLEVBQUUsSUFBSSxDQUFDLENBQUM7SUFDeEMsZ0JBQWdCLENBQUMsS0FBSyxDQUFDLFVBQVUsQ0FBQyxNQUFNLENBQUMsR0FBRyxFQUFFLElBQUksRUFBRSxJQUFJLEVBQUUsSUFBSSxDQUFDLENBQUM7QUFDbEUsQ0FBQztBQUVELHNCQUE2QixLQUFZO0lBQ3ZDLEVBQUUsQ0FBQyxDQUFDLEtBQUssQ0FBQyxVQUFVLENBQUMsT0FBTyxDQUFDLENBQUMsQ0FBQztRQUM3QixLQUFLLENBQUMsVUFBVSxDQUFDLE9BQU8sR0FBRyxTQUFTLENBQUM7UUFDckMsZ0JBQWdCLENBQUMsS0FBSyxDQUFDLFVBQVUsQ0FBQyxNQUFNLENBQUMsS0FBSyxDQUFDLENBQUM7SUFDbEQsQ0FBQztBQUNILENBQUM7QUFMRCxvQ0FLQztBQUVELG9CQUFvQixLQUFZLEVBQUUsSUFBYSxFQUFFLEdBQVc7SUFDMUQsWUFBWSxDQUFDLEtBQUssQ0FBQyxDQUFDO0lBQ3BCLEtBQUssQ0FBQyxZQUFZLENBQUMsT0FBTyxHQUFHO1FBQzNCLElBQUksRUFBRSxJQUFJO1FBQ1YsR0FBRyxFQUFFLEdBQUc7S0FDVCxDQUFDO0lBQ0YsZ0JBQWdCLENBQUMsS0FBSyxDQUFDLFlBQVksQ0FBQyxNQUFNLENBQUMsR0FBRyxFQUFFLElBQUksRUFBRSxHQUFHLENBQUMsQ0FBQztBQUM3RCxDQUFDO0FBRUQsc0JBQTZCLEtBQVk7SUFDdkMsSUFBTSxFQUFFLEdBQUcsS0FBSyxDQUFDLFlBQVksQ0FBQztJQUM5QixFQUFFLENBQUMsQ0FBQyxFQUFFLENBQUMsT0FBTyxDQUFDLENBQUMsQ0FBQztRQUNmLEVBQUUsQ0FBQyxPQUFPLEdBQUcsU0FBUyxDQUFDO1FBQ3ZCLGdCQUFnQixDQUFDLEVBQUUsQ0FBQyxNQUFNLENBQUMsS0FBSyxDQUFDLENBQUM7SUFDcEMsQ0FBQztBQUNILENBQUM7QUFORCxvQ0FNQztBQUVELHVCQUF1QixLQUFZLEVBQUUsSUFBWSxFQUFFLElBQVk7SUFDN0QsRUFBRSxDQUFDLENBQUMsQ0FBQyxLQUFLLENBQUMsVUFBVSxDQUFDO1FBQUMsTUFBTSxDQUFDLEtBQUssQ0FBQztJQUNwQyxJQUFNLElBQUksR0FBRyxLQUFLLENBQUMsTUFBTSxDQUFDLElBQUksQ0FBQyxDQUFDO0lBQ2hDLEVBQUUsQ0FBQyxDQUFDLElBQUksQ0FBQyxJQUFJLEtBQUssTUFBTSxDQUFDO1FBQUMsTUFBTSxDQUFDLEtBQUssQ0FBQztJQUN2QyxJQUFNLE9BQU8sR0FBRyxjQUFPLENBQUMsSUFBSSxDQUFDLENBQUM7SUFDOUIsRUFBRSxDQUFDLENBQUMsT0FBTyxDQUFDLENBQUMsQ0FBQyxLQUFLLENBQUMsQ0FBQztRQUFDLE1BQU0sQ0FBQyxLQUFLLENBQUM7SUFDbkMsRUFBRSxDQUFDLENBQUMsT0FBTyxDQUFDLENBQUMsQ0FBQyxLQUFLLENBQUMsSUFBSSxPQUFPLENBQUMsQ0FBQyxDQUFDLEtBQUssQ0FBQyxDQUFDO1FBQUMsTUFBTSxDQUFDLEtBQUssQ0FBQztJQUN2RCxJQUFNLE9BQU8sR0FBRyxjQUFPLENBQUMsSUFBSSxDQUFDLENBQUM7SUFDOUIsSUFBSSxVQUFVLEVBQUUsVUFBVSxFQUFFLFVBQVUsQ0FBQztJQUN2QyxFQUFFLENBQUMsQ0FBQyxPQUFPLENBQUMsQ0FBQyxDQUFDLEtBQUssQ0FBQyxJQUFJLE9BQU8sQ0FBQyxDQUFDLENBQUMsS0FBSyxDQUFDLENBQUMsQ0FBQyxDQUFDO1FBQ3pDLFVBQVUsR0FBRyxjQUFPLENBQUMsQ0FBQyxDQUFDLEVBQUUsT0FBTyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQztRQUN0QyxVQUFVLEdBQUcsY0FBTyxDQUFDLENBQUMsQ0FBQyxFQUFFLE9BQU8sQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUM7UUFDdEMsVUFBVSxHQUFHLGNBQU8sQ0FBQyxDQUFDLENBQUMsRUFBRSxPQUFPLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDO0lBQ3hDLENBQUM7SUFBQyxJQUFJLENBQUMsRUFBRSxDQUFDLENBQUMsT0FBTyxDQUFDLENBQUMsQ0FBQyxLQUFLLENBQUMsSUFBSSxPQUFPLENBQUMsQ0FBQyxDQUFDLEtBQUssQ0FBQyxDQUFDLENBQUMsQ0FBQztRQUNoRCxVQUFVLEdBQUcsY0FBTyxDQUFDLENBQUMsQ0FBQyxFQUFFLE9BQU8sQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUM7UUFDdEMsVUFBVSxHQUFHLGNBQU8sQ0FBQyxDQUFDLENBQUMsRUFBRSxPQUFPLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDO1FBQ3RDLFVBQVUsR0FBRyxjQUFPLENBQUMsQ0FBQyxDQUFDLEVBQUUsT0FBTyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQztJQUN4QyxDQUFDO0lBQUMsSUFBSTtRQUFDLE1BQU0sQ0FBQyxLQUFLLENBQUM7SUFFcEIsSUFBTSxJQUFJLEdBQUcsS0FBSyxDQUFDLE1BQU0sQ0FBQyxVQUFVLENBQUMsQ0FBQztJQUN0QyxFQUFFLENBQUMsQ0FBQyxJQUFJLENBQUMsSUFBSSxLQUFLLE1BQU0sQ0FBQztRQUFDLE1BQU0sQ0FBQyxLQUFLLENBQUM7SUFFdkMsT0FBTyxLQUFLLENBQUMsTUFBTSxDQUFDLElBQUksQ0FBQyxDQUFDO0lBQzFCLE9BQU8sS0FBSyxDQUFDLE1BQU0sQ0FBQyxVQUFVLENBQUMsQ0FBQztJQUVoQyxLQUFLLENBQUMsTUFBTSxDQUFDLFVBQVUsQ0FBQyxHQUFHLElBQUksQ0FBQTtJQUMvQixLQUFLLENBQUMsTUFBTSxDQUFDLFVBQVUsQ0FBQyxHQUFHLElBQUksQ0FBQztJQUNoQyxNQUFNLENBQUMsSUFBSSxDQUFDO0FBQ2QsQ0FBQztBQUVELGtCQUF5QixLQUFZLEVBQUUsSUFBWSxFQUFFLElBQVk7SUFDL0QsRUFBRSxDQUFDLENBQUMsSUFBSSxLQUFLLElBQUksSUFBSSxDQUFDLEtBQUssQ0FBQyxNQUFNLENBQUMsSUFBSSxDQUFDLENBQUM7UUFBQyxNQUFNLENBQUMsS0FBSyxDQUFDO0lBQ3ZELElBQU0sUUFBUSxHQUF5QixDQUNyQyxLQUFLLENBQUMsTUFBTSxDQUFDLElBQUksQ0FBQztRQUNsQixLQUFLLENBQUMsTUFBTSxDQUFDLElBQUksQ0FBQyxDQUFDLEtBQUssS0FBSyxLQUFLLENBQUMsTUFBTSxDQUFDLElBQUksQ0FBQyxDQUFDLEtBQUssQ0FDdEQsR0FBRyxLQUFLLENBQUMsTUFBTSxDQUFDLElBQUksQ0FBQyxHQUFHLFNBQVMsQ0FBQztJQUNuQyxFQUFFLENBQUMsQ0FBQyxJQUFJLElBQUksS0FBSyxDQUFDLFFBQVEsQ0FBQztRQUFDLFFBQVEsQ0FBQyxLQUFLLENBQUMsQ0FBQztJQUM1QyxnQkFBZ0IsQ0FBQyxLQUFLLENBQUMsTUFBTSxDQUFDLElBQUksRUFBRSxJQUFJLEVBQUUsSUFBSSxFQUFFLFFBQVEsQ0FBQyxDQUFDO0lBQzFELEVBQUUsQ0FBQyxDQUFDLENBQUMsYUFBYSxDQUFDLEtBQUssRUFBRSxJQUFJLEVBQUUsSUFBSSxDQUFDLENBQUMsQ0FBQyxDQUFDO1FBQ3RDLEtBQUssQ0FBQyxNQUFNLENBQUMsSUFBSSxDQUFDLEdBQUcsS0FBSyxDQUFDLE1BQU0sQ0FBQyxJQUFJLENBQUMsQ0FBQztRQUN4QyxPQUFPLEtBQUssQ0FBQyxNQUFNLENBQUMsSUFBSSxDQUFDLENBQUM7SUFDNUIsQ0FBQztJQUNELEtBQUssQ0FBQyxRQUFRLEdBQUcsQ0FBQyxJQUFJLEVBQUUsSUFBSSxDQUFDLENBQUM7SUFDOUIsS0FBSyxDQUFDLEtBQUssR0FBRyxTQUFTLENBQUM7SUFDeEIsZ0JBQWdCLENBQUMsS0FBSyxDQUFDLE1BQU0sQ0FBQyxNQUFNLENBQUMsQ0FBQztJQUN0QyxNQUFNLENBQUMsUUFBUSxJQUFJLElBQUksQ0FBQztBQUMxQixDQUFDO0FBaEJELDRCQWdCQztBQUVELHNCQUE2QixLQUFZLEVBQUUsS0FBZSxFQUFFLEdBQVcsRUFBRSxLQUFlO0lBQ3RGLEVBQUUsQ0FBQyxDQUFDLEtBQUssQ0FBQyxNQUFNLENBQUMsR0FBRyxDQUFDLENBQUMsQ0FBQyxDQUFDO1FBQ3RCLEVBQUUsQ0FBQyxDQUFDLEtBQUssQ0FBQztZQUFDLE9BQU8sS0FBSyxDQUFDLE1BQU0sQ0FBQyxHQUFHLENBQUMsQ0FBQztRQUNwQyxJQUFJO1lBQUMsTUFBTSxDQUFDLEtBQUssQ0FBQztJQUNwQixDQUFDO0lBQ0QsZ0JBQWdCLENBQUMsS0FBSyxDQUFDLE1BQU0sQ0FBQyxZQUFZLEVBQUUsS0FBSyxFQUFFLEdBQUcsQ0FBQyxDQUFDO0lBQ3hELEtBQUssQ0FBQyxNQUFNLENBQUMsR0FBRyxDQUFDLEdBQUcsS0FBSyxDQUFDO0lBQzFCLEtBQUssQ0FBQyxRQUFRLEdBQUcsQ0FBQyxHQUFHLENBQUMsQ0FBQztJQUN2QixLQUFLLENBQUMsS0FBSyxHQUFHLFNBQVMsQ0FBQztJQUN4QixnQkFBZ0IsQ0FBQyxLQUFLLENBQUMsTUFBTSxDQUFDLE1BQU0sQ0FBQyxDQUFDO0lBQ3RDLEtBQUssQ0FBQyxPQUFPLENBQUMsS0FBSyxHQUFHLFNBQVMsQ0FBQztJQUNoQyxLQUFLLENBQUMsU0FBUyxHQUFHLGVBQVEsQ0FBQyxLQUFLLENBQUMsU0FBUyxDQUFDLENBQUM7SUFDNUMsTUFBTSxDQUFDLElBQUksQ0FBQztBQUNkLENBQUM7QUFiRCxvQ0FhQztBQUVELHNCQUFzQixLQUFZLEVBQUUsSUFBWSxFQUFFLElBQVk7SUFDNUQsSUFBTSxNQUFNLEdBQUcsUUFBUSxDQUFDLEtBQUssRUFBRSxJQUFJLEVBQUUsSUFBSSxDQUFDLENBQUM7SUFDM0MsRUFBRSxDQUFDLENBQUMsTUFBTSxDQUFDLENBQUMsQ0FBQztRQUNYLEtBQUssQ0FBQyxPQUFPLENBQUMsS0FBSyxHQUFHLFNBQVMsQ0FBQztRQUNoQyxLQUFLLENBQUMsU0FBUyxHQUFHLGVBQVEsQ0FBQyxLQUFLLENBQUMsU0FBUyxDQUFDLENBQUM7UUFDNUMsS0FBSyxDQUFDLFNBQVMsQ0FBQyxPQUFPLEdBQUcsU0FBUyxDQUFDO0lBQ3RDLENBQUM7SUFDRCxNQUFNLENBQUMsTUFBTSxDQUFDO0FBQ2hCLENBQUM7QUFFRCxrQkFBeUIsS0FBWSxFQUFFLElBQVksRUFBRSxJQUFZO0lBQy9ELEVBQUUsQ0FBQyxDQUFDLE9BQU8sQ0FBQyxLQUFLLEVBQUUsSUFBSSxFQUFFLElBQUksQ0FBQyxDQUFDLENBQUMsQ0FBQztRQUMvQixJQUFNLE1BQU0sR0FBRyxZQUFZLENBQUMsS0FBSyxFQUFFLElBQUksRUFBRSxJQUFJLENBQUMsQ0FBQztRQUMvQyxFQUFFLENBQUMsQ0FBQyxNQUFNLENBQUMsQ0FBQyxDQUFDO1lBQ1gsSUFBTSxRQUFRLEdBQUcsS0FBSyxDQUFDLElBQUksQ0FBQyxJQUFJLEVBQUUsQ0FBQztZQUNuQyxRQUFRLENBQUMsS0FBSyxDQUFDLENBQUM7WUFDaEIsSUFBTSxRQUFRLEdBQW9CO2dCQUNoQyxPQUFPLEVBQUUsS0FBSztnQkFDZCxPQUFPLEVBQUUsS0FBSyxDQUFDLEtBQUssQ0FBQyxPQUFPO2dCQUM1QixRQUFRLEVBQUUsUUFBUTthQUNuQixDQUFDO1lBQ0YsRUFBRSxDQUFDLENBQUMsTUFBTSxLQUFLLElBQUksQ0FBQztnQkFBQyxRQUFRLENBQUMsUUFBUSxHQUFHLE1BQU0sQ0FBQztZQUNoRCxnQkFBZ0IsQ0FBQyxLQUFLLENBQUMsT0FBTyxDQUFDLE1BQU0sQ0FBQyxLQUFLLEVBQUUsSUFBSSxFQUFFLElBQUksRUFBRSxRQUFRLENBQUMsQ0FBQztZQUNuRSxNQUFNLENBQUMsSUFBSSxDQUFDO1FBQ2QsQ0FBQztJQUNILENBQUM7SUFBQyxJQUFJLENBQUMsRUFBRSxDQUFDLENBQUMsVUFBVSxDQUFDLEtBQUssRUFBRSxJQUFJLEVBQUUsSUFBSSxDQUFDLENBQUMsQ0FBQyxDQUFDO1FBQ3pDLFVBQVUsQ0FBQyxLQUFLLEVBQUUsSUFBSSxFQUFFLElBQUksRUFBRTtZQUM1QixPQUFPLEVBQUUsS0FBSyxDQUFDLEtBQUssQ0FBQyxPQUFPO1NBQzdCLENBQUMsQ0FBQztRQUNILFFBQVEsQ0FBQyxLQUFLLENBQUMsQ0FBQztJQUNsQixDQUFDO0lBQUMsSUFBSSxDQUFDLEVBQUUsQ0FBQyxDQUFDLFNBQVMsQ0FBQyxLQUFLLEVBQUUsSUFBSSxDQUFDLElBQUksWUFBWSxDQUFDLEtBQUssRUFBRSxJQUFJLENBQUMsQ0FBQyxDQUFDLENBQUM7UUFDL0QsV0FBVyxDQUFDLEtBQUssRUFBRSxJQUFJLENBQUMsQ0FBQztRQUN6QixLQUFLLENBQUMsSUFBSSxDQUFDLEtBQUssRUFBRSxDQUFDO0lBQ3JCLENBQUM7SUFBQyxJQUFJO1FBQUMsUUFBUSxDQUFDLEtBQUssQ0FBQyxDQUFDO0lBQ3ZCLE1BQU0sQ0FBQyxLQUFLLENBQUM7QUFDZixDQUFDO0FBekJELDRCQXlCQztBQUVELHNCQUE2QixLQUFZLEVBQUUsSUFBWSxFQUFFLElBQVksRUFBRSxLQUFlO0lBQ3BGLEVBQUUsQ0FBQyxDQUFDLE9BQU8sQ0FBQyxLQUFLLEVBQUUsSUFBSSxFQUFFLElBQUksQ0FBQyxJQUFJLEtBQUssQ0FBQyxDQUFDLENBQUM7UUFDeEMsSUFBTSxLQUFLLEdBQUcsS0FBSyxDQUFDLE1BQU0sQ0FBQyxJQUFJLENBQUMsQ0FBQztRQUNqQyxPQUFPLEtBQUssQ0FBQyxNQUFNLENBQUMsSUFBSSxDQUFDLENBQUM7UUFDMUIsWUFBWSxDQUFDLEtBQUssRUFBRSxLQUFLLEVBQUUsSUFBSSxFQUFFLEtBQUssQ0FBQyxDQUFDO1FBQ3hDLGdCQUFnQixDQUFDLEtBQUssQ0FBQyxPQUFPLENBQUMsTUFBTSxDQUFDLGFBQWEsRUFBRSxLQUFLLENBQUMsSUFBSSxFQUFFLElBQUksRUFBRTtZQUNyRSxPQUFPLEVBQUUsS0FBSztTQUNmLENBQUMsQ0FBQztJQUNMLENBQUM7SUFBQyxJQUFJLENBQUMsRUFBRSxDQUFDLENBQUMsVUFBVSxDQUFDLEtBQUssRUFBRSxJQUFJLEVBQUUsSUFBSSxDQUFDLENBQUMsQ0FBQyxDQUFDO1FBQ3pDLFVBQVUsQ0FBQyxLQUFLLEVBQUUsS0FBSyxDQUFDLE1BQU0sQ0FBQyxJQUFJLENBQUMsQ0FBQyxJQUFJLEVBQUUsSUFBSSxDQUFDLENBQUM7SUFDbkQsQ0FBQztJQUFDLElBQUksQ0FBQyxDQUFDO1FBQ04sWUFBWSxDQUFDLEtBQUssQ0FBQyxDQUFDO1FBQ3BCLFlBQVksQ0FBQyxLQUFLLENBQUMsQ0FBQztJQUN0QixDQUFDO0lBQ0QsT0FBTyxLQUFLLENBQUMsTUFBTSxDQUFDLElBQUksQ0FBQyxDQUFDO0lBQzFCLFFBQVEsQ0FBQyxLQUFLLENBQUMsQ0FBQztBQUNsQixDQUFDO0FBaEJELG9DQWdCQztBQUVELHNCQUE2QixLQUFZLEVBQUUsR0FBVyxFQUFFLEtBQWU7SUFDckUsRUFBRSxDQUFDLENBQUMsS0FBSyxDQUFDLFFBQVEsQ0FBQyxDQUFDLENBQUM7UUFDbkIsRUFBRSxDQUFDLENBQUMsS0FBSyxDQUFDLFFBQVEsS0FBSyxHQUFHLElBQUksQ0FBQyxLQUFLLENBQUMsU0FBUyxDQUFDLE9BQU8sQ0FBQyxDQUFDLENBQUM7WUFDdkQsUUFBUSxDQUFDLEtBQUssQ0FBQyxDQUFDO1lBQ2hCLEtBQUssQ0FBQyxJQUFJLENBQUMsTUFBTSxFQUFFLENBQUM7UUFDdEIsQ0FBQztRQUFDLElBQUksQ0FBQyxFQUFFLENBQUMsQ0FBQyxDQUFDLEtBQUssQ0FBQyxVQUFVLENBQUMsT0FBTyxJQUFJLEtBQUssQ0FBQyxJQUFJLEtBQUssQ0FBQyxRQUFRLEtBQUssR0FBRyxDQUFDLENBQUMsQ0FBQztZQUN6RSxFQUFFLENBQUMsQ0FBQyxRQUFRLENBQUMsS0FBSyxFQUFFLEtBQUssQ0FBQyxRQUFRLEVBQUUsR0FBRyxDQUFDLENBQUM7Z0JBQUMsS0FBSyxDQUFDLEtBQUssQ0FBQyxPQUFPLEdBQUcsS0FBSyxDQUFDO1FBQ3hFLENBQUM7UUFBQyxJQUFJO1lBQUMsS0FBSyxDQUFDLElBQUksQ0FBQyxLQUFLLEVBQUUsQ0FBQztJQUM1QixDQUFDO0lBQUMsSUFBSSxDQUFDLEVBQUUsQ0FBQyxDQUFDLFNBQVMsQ0FBQyxLQUFLLEVBQUUsR0FBRyxDQUFDLElBQUksWUFBWSxDQUFDLEtBQUssRUFBRSxHQUFHLENBQUMsQ0FBQyxDQUFDLENBQUM7UUFDN0QsV0FBVyxDQUFDLEtBQUssRUFBRSxHQUFHLENBQUMsQ0FBQztRQUN4QixLQUFLLENBQUMsSUFBSSxDQUFDLEtBQUssRUFBRSxDQUFDO0lBQ3JCLENBQUM7SUFDRCxFQUFFLENBQUMsQ0FBQyxHQUFHLENBQUM7UUFBQyxnQkFBZ0IsQ0FBQyxLQUFLLENBQUMsTUFBTSxDQUFDLE1BQU0sRUFBRSxHQUFHLENBQUMsQ0FBQztBQUN0RCxDQUFDO0FBYkQsb0NBYUM7QUFFRCxxQkFBNEIsS0FBWSxFQUFFLEdBQVc7SUFDbkQsS0FBSyxDQUFDLFFBQVEsR0FBRyxHQUFHLENBQUM7SUFDckIsRUFBRSxDQUFDLENBQUMsWUFBWSxDQUFDLEtBQUssRUFBRSxHQUFHLENBQUMsQ0FBQyxDQUFDLENBQUM7UUFDN0IsS0FBSyxDQUFDLFVBQVUsQ0FBQyxLQUFLLEdBQUcsaUJBQU8sQ0FBQyxLQUFLLENBQUMsTUFBTSxFQUFFLEdBQUcsRUFBRSxLQUFLLENBQUMsVUFBVSxDQUFDLE1BQU0sQ0FBQyxDQUFDO0lBQy9FLENBQUM7SUFDRCxJQUFJO1FBQUMsS0FBSyxDQUFDLFVBQVUsQ0FBQyxLQUFLLEdBQUcsU0FBUyxDQUFDO0FBQzFDLENBQUM7QUFORCxrQ0FNQztBQUVELGtCQUF5QixLQUFZO0lBQ25DLEtBQUssQ0FBQyxRQUFRLEdBQUcsU0FBUyxDQUFDO0lBQzNCLEtBQUssQ0FBQyxVQUFVLENBQUMsS0FBSyxHQUFHLFNBQVMsQ0FBQztJQUNuQyxLQUFLLENBQUMsSUFBSSxDQUFDLE1BQU0sRUFBRSxDQUFDO0FBQ3RCLENBQUM7QUFKRCw0QkFJQztBQUVELG1CQUFtQixLQUFZLEVBQUUsSUFBWTtJQUMzQyxJQUFNLEtBQUssR0FBRyxLQUFLLENBQUMsTUFBTSxDQUFDLElBQUksQ0FBQyxDQUFDO0lBQ2pDLE1BQU0sQ0FBQyxLQUFLLElBQUksQ0FDZCxLQUFLLENBQUMsT0FBTyxDQUFDLEtBQUssS0FBSyxNQUFNLElBQUksQ0FDaEMsS0FBSyxDQUFDLE9BQU8sQ0FBQyxLQUFLLEtBQUssS0FBSyxDQUFDLEtBQUs7UUFDakMsS0FBSyxDQUFDLFNBQVMsS0FBSyxLQUFLLENBQUMsS0FBSyxDQUNsQyxDQUFDLENBQUM7QUFDUCxDQUFDO0FBRUQsaUJBQXdCLEtBQVksRUFBRSxJQUFZLEVBQUUsSUFBWTtJQUM5RCxNQUFNLENBQUMsSUFBSSxLQUFLLElBQUksSUFBSSxTQUFTLENBQUMsS0FBSyxFQUFFLElBQUksQ0FBQyxJQUFJLENBQ2hELEtBQUssQ0FBQyxPQUFPLENBQUMsSUFBSSxJQUFJLENBQUMsQ0FBQyxDQUFDLEtBQUssQ0FBQyxPQUFPLENBQUMsS0FBSyxJQUFJLGdCQUFTLENBQUMsS0FBSyxDQUFDLE9BQU8sQ0FBQyxLQUFLLENBQUMsSUFBSSxDQUFDLEVBQUUsSUFBSSxDQUFDLENBQUMsQ0FDNUYsQ0FBQztBQUNKLENBQUM7QUFKRCwwQkFJQztBQUVELGlCQUFpQixLQUFZLEVBQUUsSUFBWSxFQUFFLElBQVk7SUFDdkQsSUFBTSxLQUFLLEdBQUcsS0FBSyxDQUFDLE1BQU0sQ0FBQyxJQUFJLENBQUMsQ0FBQztJQUNqQyxNQUFNLENBQUMsS0FBSyxJQUFJLElBQUksSUFBSSxDQUFDLElBQUksS0FBSyxJQUFJLElBQUksQ0FBQyxLQUFLLENBQUMsTUFBTSxDQUFDLElBQUksQ0FBQyxDQUFDLElBQUksQ0FDaEUsS0FBSyxDQUFDLE9BQU8sQ0FBQyxLQUFLLEtBQUssTUFBTSxJQUFJLENBQ2hDLEtBQUssQ0FBQyxPQUFPLENBQUMsS0FBSyxLQUFLLEtBQUssQ0FBQyxLQUFLO1FBQ2pDLEtBQUssQ0FBQyxTQUFTLEtBQUssS0FBSyxDQUFDLEtBQUssQ0FDbEMsQ0FBQyxDQUFDO0FBQ1AsQ0FBQztBQUdELHNCQUFzQixLQUFZLEVBQUUsSUFBWTtJQUM5QyxJQUFNLEtBQUssR0FBRyxLQUFLLENBQUMsTUFBTSxDQUFDLElBQUksQ0FBQyxDQUFDO0lBQ2pDLE1BQU0sQ0FBQyxLQUFLLElBQUksS0FBSyxDQUFDLFVBQVUsQ0FBQyxPQUFPO1FBQ3hDLEtBQUssQ0FBQyxPQUFPLENBQUMsS0FBSyxLQUFLLEtBQUssQ0FBQyxLQUFLO1FBQ2pDLEtBQUssQ0FBQyxTQUFTLEtBQUssS0FBSyxDQUFDLEtBQUssQ0FBQztBQUNwQyxDQUFDO0FBRUQsb0JBQW9CLEtBQVksRUFBRSxJQUFZLEVBQUUsSUFBWTtJQUMxRCxNQUFNLENBQUMsSUFBSSxLQUFLLElBQUk7UUFDcEIsWUFBWSxDQUFDLEtBQUssRUFBRSxJQUFJLENBQUM7UUFDekIsZ0JBQVMsQ0FBQyxpQkFBTyxDQUFDLEtBQUssQ0FBQyxNQUFNLEVBQUUsSUFBSSxFQUFFLEtBQUssQ0FBQyxVQUFVLENBQUMsTUFBTSxDQUFDLEVBQUUsSUFBSSxDQUFDLENBQUM7QUFDeEUsQ0FBQztBQUVELG9CQUFvQixLQUFZLEVBQUUsSUFBWSxFQUFFLElBQVk7SUFDMUQsSUFBTSxLQUFLLEdBQUcsS0FBSyxDQUFDLE1BQU0sQ0FBQyxJQUFJLENBQUMsQ0FBQztJQUNqQyxNQUFNLENBQUMsS0FBSyxJQUFJLElBQUk7UUFDcEIsQ0FBQyxDQUFDLEtBQUssQ0FBQyxNQUFNLENBQUMsSUFBSSxDQUFDLElBQUksS0FBSyxDQUFDLE1BQU0sQ0FBQyxJQUFJLENBQUMsQ0FBQyxLQUFLLEtBQUssS0FBSyxDQUFDLE9BQU8sQ0FBQyxLQUFLLENBQUM7UUFDekUsS0FBSyxDQUFDLFlBQVksQ0FBQyxPQUFPO1FBQzFCLENBQUMsS0FBSyxDQUFDLElBQUksS0FBSyxNQUFNLElBQUksQ0FBQyxJQUFJLENBQUMsQ0FBQyxDQUFDLEtBQUssR0FBRyxJQUFJLElBQUksQ0FBQyxDQUFDLENBQUMsS0FBSyxHQUFHLENBQUMsQ0FBQztRQUMvRCxLQUFLLENBQUMsT0FBTyxDQUFDLEtBQUssS0FBSyxLQUFLLENBQUMsS0FBSztRQUNqQyxLQUFLLENBQUMsU0FBUyxLQUFLLEtBQUssQ0FBQyxLQUFLLENBQUM7QUFDcEMsQ0FBQztBQUVELHFCQUE0QixLQUFZLEVBQUUsSUFBWTtJQUNwRCxJQUFNLEtBQUssR0FBRyxLQUFLLENBQUMsTUFBTSxDQUFDLElBQUksQ0FBQyxDQUFDO0lBQ2pDLE1BQU0sQ0FBQyxLQUFLLElBQUksS0FBSyxDQUFDLFNBQVMsQ0FBQyxPQUFPLElBQUksQ0FDekMsS0FBSyxDQUFDLE9BQU8sQ0FBQyxLQUFLLEtBQUssTUFBTSxJQUFJLENBQ2hDLEtBQUssQ0FBQyxPQUFPLENBQUMsS0FBSyxLQUFLLEtBQUssQ0FBQyxLQUFLLElBQUksQ0FDckMsS0FBSyxDQUFDLFNBQVMsS0FBSyxLQUFLLENBQUMsS0FBSyxJQUFJLEtBQUssQ0FBQyxVQUFVLENBQUMsT0FBTyxDQUM1RCxDQUNGLENBQ0YsQ0FBQztBQUNKLENBQUM7QUFURCxrQ0FTQztBQUVELHFCQUE0QixLQUFZO0lBQ3RDLElBQU0sSUFBSSxHQUFHLEtBQUssQ0FBQyxVQUFVLENBQUMsT0FBTyxDQUFDO0lBQ3RDLEVBQUUsQ0FBQyxDQUFDLENBQUMsSUFBSSxDQUFDO1FBQUMsTUFBTSxDQUFDLEtBQUssQ0FBQztJQUN4QixJQUFNLElBQUksR0FBRyxJQUFJLENBQUMsQ0FBQyxDQUFDLEVBQUUsSUFBSSxHQUFHLElBQUksQ0FBQyxDQUFDLENBQUMsQ0FBQztJQUNyQyxJQUFJLE9BQU8sR0FBRyxLQUFLLENBQUM7SUFDcEIsRUFBRSxDQUFDLENBQUMsT0FBTyxDQUFDLEtBQUssRUFBRSxJQUFJLEVBQUUsSUFBSSxDQUFDLENBQUMsQ0FBQyxDQUFDO1FBQy9CLElBQU0sTUFBTSxHQUFHLFlBQVksQ0FBQyxLQUFLLEVBQUUsSUFBSSxFQUFFLElBQUksQ0FBQyxDQUFDO1FBQy9DLEVBQUUsQ0FBQyxDQUFDLE1BQU0sQ0FBQyxDQUFDLENBQUM7WUFDWCxJQUFNLFFBQVEsR0FBb0IsRUFBRSxPQUFPLEVBQUUsSUFBSSxFQUFFLENBQUM7WUFDcEQsRUFBRSxDQUFDLENBQUMsTUFBTSxLQUFLLElBQUksQ0FBQztnQkFBQyxRQUFRLENBQUMsUUFBUSxHQUFHLE1BQU0sQ0FBQztZQUNoRCxnQkFBZ0IsQ0FBQyxLQUFLLENBQUMsT0FBTyxDQUFDLE1BQU0sQ0FBQyxLQUFLLEVBQUUsSUFBSSxFQUFFLElBQUksRUFBRSxRQUFRLENBQUMsQ0FBQztZQUNuRSxPQUFPLEdBQUcsSUFBSSxDQUFDO1FBQ2pCLENBQUM7SUFDSCxDQUFDO0lBQ0QsWUFBWSxDQUFDLEtBQUssQ0FBQyxDQUFDO0lBQ3BCLE1BQU0sQ0FBQyxPQUFPLENBQUM7QUFDakIsQ0FBQztBQWhCRCxrQ0FnQkM7QUFFRCxxQkFBNEIsS0FBWSxFQUFFLFFBQW9DO0lBQzVFLElBQUksSUFBSSxHQUFHLEtBQUssQ0FBQyxZQUFZLENBQUMsT0FBTyxFQUNyQyxPQUFPLEdBQUcsS0FBSyxDQUFDO0lBQ2hCLEVBQUUsQ0FBQyxDQUFDLENBQUMsSUFBSSxDQUFDO1FBQUMsTUFBTSxDQUFDLEtBQUssQ0FBQztJQUN4QixFQUFFLENBQUMsQ0FBQyxRQUFRLENBQUMsSUFBSSxDQUFDLENBQUMsQ0FBQyxDQUFDO1FBQ25CLElBQU0sS0FBSyxHQUFHO1lBQ1osSUFBSSxFQUFFLElBQUksQ0FBQyxJQUFJO1lBQ2YsS0FBSyxFQUFFLEtBQUssQ0FBQyxPQUFPLENBQUMsS0FBSztTQUNmLENBQUM7UUFDZCxFQUFFLENBQUMsQ0FBQyxZQUFZLENBQUMsS0FBSyxFQUFFLEtBQUssRUFBRSxJQUFJLENBQUMsR0FBRyxDQUFDLENBQUMsQ0FBQyxDQUFDO1lBQ3pDLGdCQUFnQixDQUFDLEtBQUssQ0FBQyxPQUFPLENBQUMsTUFBTSxDQUFDLGFBQWEsRUFBRSxJQUFJLENBQUMsSUFBSSxFQUFFLElBQUksQ0FBQyxHQUFHLEVBQUU7Z0JBQ3hFLE9BQU8sRUFBRSxJQUFJO2FBQ2QsQ0FBQyxDQUFDO1lBQ0gsT0FBTyxHQUFHLElBQUksQ0FBQztRQUNqQixDQUFDO0lBQ0gsQ0FBQztJQUNELFlBQVksQ0FBQyxLQUFLLENBQUMsQ0FBQztJQUNwQixNQUFNLENBQUMsT0FBTyxDQUFDO0FBQ2pCLENBQUM7QUFsQkQsa0NBa0JDO0FBRUQsb0JBQTJCLEtBQVk7SUFDckMsWUFBWSxDQUFDLEtBQUssQ0FBQyxDQUFDO0lBQ3BCLFlBQVksQ0FBQyxLQUFLLENBQUMsQ0FBQztJQUNwQixRQUFRLENBQUMsS0FBSyxDQUFDLENBQUM7QUFDbEIsQ0FBQztBQUpELGdDQUlDO0FBRUQsY0FBcUIsS0FBWTtJQUMvQixLQUFLLENBQUMsT0FBTyxDQUFDLEtBQUs7UUFDbkIsS0FBSyxDQUFDLE9BQU8sQ0FBQyxLQUFLO1lBQ25CLEtBQUssQ0FBQyxTQUFTLENBQUMsT0FBTyxHQUFHLFNBQVMsQ0FBQztJQUNwQyxVQUFVLENBQUMsS0FBSyxDQUFDLENBQUM7QUFDcEIsQ0FBQztBQUxELG9CQUtDO0FBRUQsd0JBQStCLEdBQWtCLEVBQUUsT0FBZ0IsRUFBRSxNQUFrQjtJQUNyRixJQUFJLElBQUksR0FBRyxJQUFJLENBQUMsSUFBSSxDQUFDLENBQUMsR0FBRyxDQUFDLENBQUMsR0FBRyxDQUFDLENBQUMsQ0FBQyxHQUFHLE1BQU0sQ0FBQyxJQUFJLENBQUMsR0FBRyxNQUFNLENBQUMsS0FBSyxDQUFDLENBQUMsQ0FBQztJQUNsRSxFQUFFLENBQUMsQ0FBQyxDQUFDLE9BQU8sQ0FBQztRQUFDLElBQUksR0FBRyxDQUFDLEdBQUcsSUFBSSxDQUFDO0lBQzlCLElBQUksSUFBSSxHQUFHLElBQUksQ0FBQyxJQUFJLENBQUMsQ0FBQyxHQUFHLENBQUMsQ0FBQyxHQUFHLENBQUMsQ0FBQyxHQUFHLENBQUMsQ0FBQyxDQUFDLEdBQUcsTUFBTSxDQUFDLEdBQUcsQ0FBQyxHQUFHLE1BQU0sQ0FBQyxNQUFNLENBQUMsQ0FBQyxDQUFDLENBQUM7SUFDeEUsRUFBRSxDQUFDLENBQUMsQ0FBQyxPQUFPLENBQUM7UUFBQyxJQUFJLEdBQUcsQ0FBQyxHQUFHLElBQUksQ0FBQztJQUM5QixNQUFNLENBQUMsQ0FBQyxJQUFJLEdBQUcsQ0FBQyxJQUFJLElBQUksR0FBRyxDQUFDLElBQUksSUFBSSxHQUFHLENBQUMsSUFBSSxJQUFJLEdBQUcsQ0FBQyxDQUFDLEdBQUcsY0FBTyxDQUFDLENBQUMsSUFBSSxFQUFFLElBQUksQ0FBQyxDQUFDLEdBQUcsU0FBUyxDQUFDO0FBQzVGLENBQUM7QUFORCx3Q0FNQzs7Ozs7QUNoVkQsNkJBQWtDO0FBQ2xDLG1DQUE0QztBQUM1QyxpQ0FBeUM7QUFFekMsK0JBQWdDO0FBQ2hDLGlDQUFrQztBQUNsQyxtQ0FBOEI7QUFDOUIsMkJBQTZCO0FBQzdCLDZCQUErQjtBQUUvQixxQkFBNEIsT0FBb0IsRUFBRSxNQUFlO0lBRS9ELElBQU0sS0FBSyxHQUFHLGdCQUFRLEVBQVcsQ0FBQztJQUVsQyxrQkFBUyxDQUFDLEtBQUssRUFBRSxNQUFNLElBQUksRUFBRSxDQUFDLENBQUM7SUFFL0IsS0FBSyxDQUFDLE9BQU8sR0FBRztRQUNkLFNBQVMsRUFBRSxJQUFJLENBQUMsaUJBQWlCLEVBQUU7S0FDcEMsQ0FBQztJQUVGO1FBQ0UsSUFBSSxVQUFVLEdBQUcsS0FBSyxDQUFDLEdBQUcsSUFBSSxLQUFLLENBQUMsR0FBRyxDQUFDLE1BQU0sQ0FBQztRQUsvQyxPQUFPLENBQUMsU0FBUyxDQUFDLEdBQUcsQ0FBQyxlQUFlLENBQUMsQ0FBQztRQUd2QyxJQUFNLE1BQU0sR0FBRyxJQUFJLENBQUMsSUFBSSxDQUFDLGNBQU0sT0FBQSxPQUFPLENBQUMscUJBQXFCLEVBQUUsRUFBL0IsQ0FBK0IsQ0FBQyxDQUFDO1FBQ2hFLElBQU0sUUFBUSxHQUFHLGNBQVUsQ0FBQyxPQUFPLEVBQUUsS0FBSyxFQUFFLE1BQU0sRUFBRSxDQUFDLENBQUM7UUFDdEQsSUFBTSxTQUFTLEdBQUcsVUFBQyxPQUFnQjtZQUNqQyxnQkFBTSxDQUFDLEtBQUssQ0FBQyxDQUFDO1lBQ2QsRUFBRSxDQUFDLENBQUMsQ0FBQyxPQUFPLElBQUksUUFBUSxDQUFDLEdBQUcsQ0FBQztnQkFBQyxHQUFHLENBQUMsU0FBUyxDQUFDLEtBQUssRUFBRSxRQUFRLENBQUMsR0FBRyxDQUFDLENBQUM7UUFDbkUsQ0FBQyxDQUFDO1FBQ0YsS0FBSyxDQUFDLEdBQUcsR0FBRztZQUNWLFFBQVEsRUFBRSxRQUFRO1lBQ2xCLE1BQU0sRUFBRSxNQUFNO1lBQ2QsTUFBTSxFQUFFLGNBQWMsQ0FBQyxTQUFTLENBQUM7WUFDakMsU0FBUyxFQUFFLFNBQVM7WUFDcEIsTUFBTSxFQUFFLFVBQVU7U0FDbkIsQ0FBQztRQUNGLEdBQUcsQ0FBQyxVQUFVLEVBQUUsQ0FBQztRQUNqQixTQUFTLENBQUMsS0FBSyxDQUFDLENBQUM7UUFDakIsTUFBTSxDQUFDLFNBQVMsQ0FBQyxLQUFLLENBQUMsQ0FBQztRQUN4QixFQUFFLENBQUMsQ0FBQyxDQUFDLFVBQVUsQ0FBQztZQUFDLEtBQUssQ0FBQyxHQUFHLENBQUMsTUFBTSxHQUFHLE1BQU0sQ0FBQyxZQUFZLENBQUMsS0FBSyxFQUFFLFNBQVMsQ0FBQyxDQUFDO0lBQzVFLENBQUM7SUFDRCxTQUFTLEVBQUUsQ0FBQztJQUVaLElBQU0sR0FBRyxHQUFHLFdBQUssQ0FBQyxLQUFLLEVBQUUsU0FBUyxDQUFDLENBQUM7SUFFcEMsTUFBTSxDQUFDLEdBQUcsQ0FBQztBQUNiLENBQUM7QUExQ0Qsa0NBMENDO0FBQUEsQ0FBQztBQUVGLHdCQUF3QixTQUFzQztJQUM1RCxJQUFJLFNBQVMsR0FBRyxLQUFLLENBQUM7SUFDdEIsTUFBTSxDQUFDO1FBQ0wsRUFBRSxDQUFDLENBQUMsU0FBUyxDQUFDO1lBQUMsTUFBTSxDQUFDO1FBQ3RCLFNBQVMsR0FBRyxJQUFJLENBQUM7UUFDakIsSUFBSSxDQUFDLEdBQUcsQ0FBQztZQUNQLFNBQVMsRUFBRSxDQUFDO1lBQ1osU0FBUyxHQUFHLEtBQUssQ0FBQztRQUNwQixDQUFDLENBQUMsQ0FBQztJQUNMLENBQUMsQ0FBQztBQUNKLENBQUM7Ozs7O0FDL0RELGlDQUErQztBQUMvQyw2QkFBdUM7QUF5RnZDLG1CQUEwQixLQUFZLEVBQUUsTUFBYztJQUdwRCxFQUFFLENBQUMsQ0FBQyxNQUFNLENBQUMsT0FBTyxJQUFJLE1BQU0sQ0FBQyxPQUFPLENBQUMsS0FBSyxDQUFDO1FBQUMsS0FBSyxDQUFDLE9BQU8sQ0FBQyxLQUFLLEdBQUcsU0FBUyxDQUFDO0lBRTVFLEtBQUssQ0FBQyxLQUFLLEVBQUUsTUFBTSxDQUFDLENBQUM7SUFHckIsRUFBRSxDQUFDLENBQUMsTUFBTSxDQUFDLEdBQUcsQ0FBQyxDQUFDLENBQUM7UUFDZixLQUFLLENBQUMsTUFBTSxHQUFHLFVBQU8sQ0FBQyxNQUFNLENBQUMsR0FBRyxDQUFDLENBQUM7UUFDbkMsS0FBSyxDQUFDLFFBQVEsQ0FBQyxNQUFNLEdBQUcsRUFBRSxDQUFDO0lBQzdCLENBQUM7SUFHRCxFQUFFLENBQUMsQ0FBQyxNQUFNLENBQUMsY0FBYyxDQUFDLE9BQU8sQ0FBQyxDQUFDO1FBQUMsZ0JBQVEsQ0FBQyxLQUFLLEVBQUUsTUFBTSxDQUFDLEtBQUssSUFBSSxLQUFLLENBQUMsQ0FBQztJQUMzRSxFQUFFLENBQUMsQ0FBQyxNQUFNLENBQUMsY0FBYyxDQUFDLFVBQVUsQ0FBQyxJQUFJLENBQUMsTUFBTSxDQUFDLFFBQVEsQ0FBQztRQUFDLEtBQUssQ0FBQyxRQUFRLEdBQUcsU0FBUyxDQUFDO0lBSXRGLElBQUksQ0FBQyxFQUFFLENBQUMsQ0FBQyxNQUFNLENBQUMsUUFBUSxDQUFDO1FBQUMsS0FBSyxDQUFDLFFBQVEsR0FBRyxNQUFNLENBQUMsUUFBUSxDQUFDO0lBRzNELEVBQUUsQ0FBQyxDQUFDLEtBQUssQ0FBQyxRQUFRLENBQUM7UUFBQyxtQkFBVyxDQUFDLEtBQUssRUFBRSxLQUFLLENBQUMsUUFBUSxDQUFDLENBQUM7SUFHdkQsRUFBRSxDQUFDLENBQUMsQ0FBQyxLQUFLLENBQUMsU0FBUyxDQUFDLFFBQVEsSUFBSSxLQUFLLENBQUMsU0FBUyxDQUFDLFFBQVEsR0FBRyxHQUFHLENBQUM7UUFBQyxLQUFLLENBQUMsU0FBUyxDQUFDLE9BQU8sR0FBRyxLQUFLLENBQUM7SUFFakcsRUFBRSxDQUFDLENBQUMsQ0FBQyxLQUFLLENBQUMsT0FBTyxDQUFDLFVBQVUsSUFBSSxLQUFLLENBQUMsT0FBTyxDQUFDLEtBQUssQ0FBQyxDQUFDLENBQUM7UUFDckQsSUFBTSxNQUFJLEdBQUcsS0FBSyxDQUFDLE9BQU8sQ0FBQyxLQUFLLEtBQUssT0FBTyxHQUFHLENBQUMsR0FBRyxDQUFDLENBQUM7UUFDckQsSUFBTSxZQUFZLEdBQUcsR0FBRyxHQUFHLE1BQUksQ0FBQztRQUNoQyxJQUFNLE9BQUssR0FBRyxLQUFLLENBQUMsT0FBTyxDQUFDLEtBQUssQ0FBQyxZQUFZLENBQUMsQ0FBQztRQUNoRCxFQUFFLENBQUMsQ0FBQyxDQUFDLE9BQUssSUFBSSxLQUFLLENBQUMsTUFBTSxDQUFDLFlBQVksQ0FBQyxDQUFDLElBQUksS0FBSyxNQUFNLENBQUM7WUFBQyxNQUFNLENBQUM7UUFDakUsS0FBSyxDQUFDLE9BQU8sQ0FBQyxLQUFLLENBQUMsWUFBWSxDQUFDLEdBQUcsT0FBSyxDQUFDLE1BQU0sQ0FBQyxVQUFBLENBQUM7WUFDaEQsRUFBRSxDQUFDLENBQUMsQ0FBQyxDQUFDLEtBQUssR0FBRyxHQUFHLE1BQUksQ0FBQyxJQUFJLE9BQUssQ0FBQyxPQUFPLENBQUMsR0FBRyxHQUFHLE1BQWMsQ0FBQyxLQUFLLENBQUMsQ0FBQyxDQUFDO2dCQUFDLE1BQU0sQ0FBQyxLQUFLLENBQUM7WUFDbkYsRUFBRSxDQUFDLENBQUMsQ0FBQyxDQUFDLEtBQUssR0FBRyxHQUFHLE1BQUksQ0FBQyxJQUFJLE9BQUssQ0FBQyxPQUFPLENBQUMsR0FBRyxHQUFHLE1BQWMsQ0FBQyxLQUFLLENBQUMsQ0FBQyxDQUFDO2dCQUFDLE1BQU0sQ0FBQyxLQUFLLENBQUM7WUFDbkYsTUFBTSxDQUFDLElBQUksQ0FBQztRQUNkLENBQUMsQ0FBQyxDQUFDO0lBQ0wsQ0FBQztBQUNILENBQUM7QUF0Q0QsOEJBc0NDO0FBQUEsQ0FBQztBQUVGLGVBQWUsSUFBUyxFQUFFLE1BQVc7SUFDbkMsR0FBRyxDQUFDLENBQUMsSUFBSSxHQUFHLElBQUksTUFBTSxDQUFDLENBQUMsQ0FBQztRQUN2QixFQUFFLENBQUMsQ0FBQyxRQUFRLENBQUMsSUFBSSxDQUFDLEdBQUcsQ0FBQyxDQUFDLElBQUksUUFBUSxDQUFDLE1BQU0sQ0FBQyxHQUFHLENBQUMsQ0FBQyxDQUFDO1lBQUMsS0FBSyxDQUFDLElBQUksQ0FBQyxHQUFHLENBQUMsRUFBRSxNQUFNLENBQUMsR0FBRyxDQUFDLENBQUMsQ0FBQztRQUNoRixJQUFJO1lBQUMsSUFBSSxDQUFDLEdBQUcsQ0FBQyxHQUFHLE1BQU0sQ0FBQyxHQUFHLENBQUMsQ0FBQztJQUMvQixDQUFDO0FBQ0gsQ0FBQztBQUVELGtCQUFrQixDQUFNO0lBQ3RCLE1BQU0sQ0FBQyxPQUFPLENBQUMsS0FBSyxRQUFRLENBQUM7QUFDL0IsQ0FBQzs7Ozs7QUMzSUQsK0JBQWdDO0FBQ2hDLDZCQUE4QjtBQUM5QiwrQkFBMkM7QUFFM0MsK0JBQTZCO0FBb0I3QixlQUFzQixDQUFRLEVBQUUsQ0FBZ0I7SUFDOUMsRUFBRSxDQUFDLENBQUMsQ0FBQyxDQUFDLE1BQU0sS0FBSyxTQUFTLElBQUksQ0FBQyxDQUFDLE1BQU0sS0FBSyxDQUFDLENBQUM7UUFBQyxNQUFNLENBQUM7SUFDckQsRUFBRSxDQUFDLENBQUMsQ0FBQyxDQUFDLE9BQU8sSUFBSSxDQUFDLENBQUMsT0FBTyxDQUFDLE1BQU0sR0FBRyxDQUFDLENBQUM7UUFBQyxNQUFNLENBQUM7SUFDOUMsQ0FBQyxDQUFDLGNBQWMsRUFBRSxDQUFDO0lBQ25CLElBQU0sT0FBTyxHQUFHLENBQUMsQ0FBQyxXQUFXLEtBQUssT0FBTyxFQUN6QyxNQUFNLEdBQUcsQ0FBQyxDQUFDLEdBQUcsQ0FBQyxNQUFNLEVBQUUsRUFDdkIsUUFBUSxHQUFHLElBQUksQ0FBQyxhQUFhLENBQUMsQ0FBQyxDQUFrQixFQUNqRCxJQUFJLEdBQUcsS0FBSyxDQUFDLGNBQWMsQ0FBQyxRQUFRLEVBQUUsT0FBTyxFQUFFLE1BQU0sQ0FBQyxDQUFDO0lBQ3ZELEVBQUUsQ0FBQyxDQUFDLENBQUMsSUFBSSxDQUFDO1FBQUMsTUFBTSxDQUFDO0lBQ2xCLElBQU0sS0FBSyxHQUFHLENBQUMsQ0FBQyxNQUFNLENBQUMsSUFBSSxDQUFDLENBQUM7SUFDN0IsSUFBTSxrQkFBa0IsR0FBRyxDQUFDLENBQUMsUUFBUSxDQUFDO0lBQ3RDLEVBQUUsQ0FBQyxDQUFDLENBQUMsa0JBQWtCLElBQUksQ0FDekIsQ0FBQyxDQUFDLFFBQVEsQ0FBQyxZQUFZLElBQUksQ0FBQyxDQUFDLEtBQUssSUFBSSxLQUFLLENBQUMsS0FBSyxLQUFLLENBQUMsQ0FBQyxTQUFTLENBQUMsQ0FDbkUsQ0FBQztRQUFDLFlBQVMsQ0FBQyxDQUFDLENBQUMsQ0FBQztJQUNoQixFQUFFLENBQUMsQ0FBQyxDQUFDLENBQUMsUUFBUSxDQUFDO1FBQUMsTUFBTSxDQUFDO0lBQ3ZCLElBQU0sVUFBVSxHQUFHLENBQUMsQ0FBQyxDQUFDLENBQUMsVUFBVSxDQUFDLE9BQU8sQ0FBQztJQUMxQyxJQUFNLFVBQVUsR0FBRyxDQUFDLENBQUMsQ0FBQyxDQUFDLFlBQVksQ0FBQyxPQUFPLENBQUM7SUFDNUMsQ0FBQyxDQUFDLEtBQUssQ0FBQyxPQUFPLEdBQUcsQ0FBQyxDQUFDLE9BQU8sQ0FBQztJQUM1QixFQUFFLENBQUMsQ0FBQyxDQUFDLENBQUMsUUFBUSxJQUFJLEtBQUssQ0FBQyxPQUFPLENBQUMsQ0FBQyxFQUFFLENBQUMsQ0FBQyxRQUFRLEVBQUUsSUFBSSxDQUFDLENBQUMsQ0FBQyxDQUFDO1FBQ3JELFdBQUksQ0FBQyxVQUFBLEtBQUssSUFBSSxPQUFBLEtBQUssQ0FBQyxZQUFZLENBQUMsS0FBSyxFQUFFLElBQUksQ0FBQyxFQUEvQixDQUErQixFQUFFLENBQUMsQ0FBQyxDQUFDO0lBQ3BELENBQUM7SUFBQyxJQUFJLENBQUMsQ0FBQztRQUNOLEtBQUssQ0FBQyxZQUFZLENBQUMsQ0FBQyxFQUFFLElBQUksQ0FBQyxDQUFDO0lBQzlCLENBQUM7SUFDRCxJQUFNLGFBQWEsR0FBRyxDQUFDLENBQUMsUUFBUSxLQUFLLElBQUksQ0FBQztJQUMxQyxJQUFNLE9BQU8sR0FBRyxpQkFBaUIsQ0FBQyxDQUFDLEVBQUUsSUFBSSxDQUFDLENBQUM7SUFDM0MsRUFBRSxDQUFDLENBQUMsS0FBSyxJQUFJLE9BQU8sSUFBSSxhQUFhLElBQUksS0FBSyxDQUFDLFdBQVcsQ0FBQyxDQUFDLEVBQUUsSUFBSSxDQUFDLENBQUMsQ0FBQyxDQUFDO1FBQ3BFLElBQU0sWUFBWSxHQUFHLG1CQUFtQixDQUFDLElBQUksRUFBRSxPQUFPLEVBQUUsTUFBTSxDQUFDLENBQUM7UUFDaEUsQ0FBQyxDQUFDLFNBQVMsQ0FBQyxPQUFPLEdBQUc7WUFDcEIsSUFBSSxFQUFFLElBQUk7WUFDVixPQUFPLEVBQUUsSUFBSSxDQUFDLE9BQU8sQ0FBQyxJQUFJLENBQUM7WUFDM0IsS0FBSyxFQUFFLEtBQUs7WUFDWixHQUFHLEVBQUUsUUFBUTtZQUNiLElBQUksRUFBRSxRQUFRO1lBQ2QsR0FBRyxFQUFFLENBQUMsQ0FBQyxFQUFFLENBQUMsQ0FBQztZQUNYLEdBQUcsRUFBRSxDQUFDLENBQUMsU0FBUyxDQUFDLFdBQVcsR0FBRztnQkFDN0IsUUFBUSxDQUFDLENBQUMsQ0FBQyxHQUFHLENBQUMsWUFBWSxDQUFDLElBQUksR0FBRyxZQUFZLENBQUMsS0FBSyxHQUFHLENBQUMsQ0FBQztnQkFDMUQsUUFBUSxDQUFDLENBQUMsQ0FBQyxHQUFHLENBQUMsWUFBWSxDQUFDLEdBQUcsR0FBRyxZQUFZLENBQUMsTUFBTSxHQUFHLENBQUMsQ0FBQzthQUMzRCxHQUFHLENBQUMsQ0FBQyxFQUFFLENBQUMsQ0FBQztZQUNWLE9BQU8sRUFBRSxDQUFDLENBQUMsU0FBUyxDQUFDLFlBQVksSUFBSSxDQUFDLENBQUMsS0FBSyxDQUFDLE9BQU87WUFDcEQsT0FBTyxFQUFFLE9BQU87WUFDaEIsa0JBQWtCLEVBQUUsa0JBQWtCO1lBQ3RDLFlBQVksRUFBRSxDQUFDLENBQUMsTUFBTTtTQUN2QixDQUFDO1FBQ0YsT0FBTyxDQUFDLFVBQVUsR0FBRyxJQUFJLENBQUM7UUFDMUIsT0FBTyxDQUFDLFNBQVMsQ0FBQyxHQUFHLENBQUMsVUFBVSxDQUFDLENBQUM7UUFFbEMsSUFBTSxLQUFLLEdBQUcsQ0FBQyxDQUFDLEdBQUcsQ0FBQyxRQUFRLENBQUMsS0FBSyxDQUFDO1FBQ25DLEVBQUUsQ0FBQyxDQUFDLEtBQUssQ0FBQyxDQUFDLENBQUM7WUFDVixLQUFLLENBQUMsU0FBUyxHQUFHLFdBQVMsS0FBSyxDQUFDLEtBQUssU0FBSSxLQUFLLENBQUMsSUFBTSxDQUFDO1lBQ3ZELElBQU0sV0FBVyxHQUFHLElBQUksQ0FBQyxjQUFjLENBQUMsSUFBSSxDQUFDLE9BQU8sQ0FBQyxJQUFJLENBQUMsRUFBRSxPQUFPLEVBQUUsTUFBTSxDQUFDLENBQUM7WUFDN0UsQ0FBQyxDQUFDLE9BQU8sQ0FBQyxTQUFTLENBQUMsS0FBSyxFQUFFLElBQUksQ0FBQyxTQUFTLENBQUMsV0FBVyxDQUFDLENBQUMsQ0FBQztRQUMxRCxDQUFDO1FBQ0QsV0FBVyxDQUFDLENBQUMsQ0FBQyxDQUFDO0lBQ2pCLENBQUM7SUFBQyxJQUFJLENBQUMsQ0FBQztRQUNOLEVBQUUsQ0FBQyxDQUFDLFVBQVUsQ0FBQztZQUFDLEtBQUssQ0FBQyxZQUFZLENBQUMsQ0FBQyxDQUFDLENBQUM7UUFDdEMsRUFBRSxDQUFDLENBQUMsVUFBVSxDQUFDO1lBQUMsS0FBSyxDQUFDLFlBQVksQ0FBQyxDQUFDLENBQUMsQ0FBQztJQUN4QyxDQUFDO0lBQ0QsQ0FBQyxDQUFDLEdBQUcsQ0FBQyxNQUFNLEVBQUUsQ0FBQztBQUNqQixDQUFDO0FBMURELHNCQTBEQztBQUVELHNCQUE2QixDQUFRLEVBQUUsS0FBZSxFQUFFLENBQWdCLEVBQUUsS0FBZTtJQUV2RixJQUFNLEdBQUcsR0FBVyxJQUFJLENBQUM7SUFFekIsQ0FBQyxDQUFDLE1BQU0sQ0FBQyxHQUFHLENBQUMsR0FBRyxLQUFLLENBQUM7SUFFdEIsQ0FBQyxDQUFDLEdBQUcsQ0FBQyxNQUFNLEVBQUUsQ0FBQztJQUVmLElBQU0sUUFBUSxHQUFHLElBQUksQ0FBQyxhQUFhLENBQUMsQ0FBQyxDQUFrQixFQUN2RCxPQUFPLEdBQUcsQ0FBQyxDQUFDLFdBQVcsS0FBSyxPQUFPLEVBQ25DLE1BQU0sR0FBRyxDQUFDLENBQUMsR0FBRyxDQUFDLE1BQU0sRUFBRSxFQUN2QixZQUFZLEdBQUcsbUJBQW1CLENBQUMsR0FBRyxFQUFFLE9BQU8sRUFBRSxNQUFNLENBQUMsQ0FBQztJQUV6RCxJQUFNLEdBQUcsR0FBa0I7UUFDekIsQ0FBQyxPQUFPLEdBQUcsQ0FBQyxHQUFHLENBQUMsQ0FBQyxHQUFHLFlBQVksQ0FBQyxLQUFLLEdBQUcsTUFBTSxDQUFDLElBQUk7UUFDcEQsQ0FBQyxPQUFPLEdBQUcsQ0FBQyxHQUFHLENBQUMsQ0FBQyxDQUFDLEdBQUcsWUFBWSxDQUFDLE1BQU0sR0FBRyxNQUFNLENBQUMsR0FBRztLQUN0RCxDQUFDO0lBRUYsQ0FBQyxDQUFDLFNBQVMsQ0FBQyxPQUFPLEdBQUc7UUFDcEIsSUFBSSxFQUFFLEdBQUc7UUFDVCxPQUFPLEVBQUUsSUFBSSxDQUFDLE9BQU8sQ0FBQyxHQUFHLENBQUM7UUFDMUIsS0FBSyxFQUFFLEtBQUs7UUFDWixHQUFHLEVBQUUsR0FBRztRQUNSLElBQUksRUFBRSxRQUFRO1FBQ2QsR0FBRyxFQUFFLENBQUMsUUFBUSxDQUFDLENBQUMsQ0FBQyxHQUFHLEdBQUcsQ0FBQyxDQUFDLENBQUMsRUFBRSxRQUFRLENBQUMsQ0FBQyxDQUFDLEdBQUcsR0FBRyxDQUFDLENBQUMsQ0FBQyxDQUFDO1FBQ2pELEdBQUcsRUFBRSxDQUFDLENBQUMsWUFBWSxDQUFDLEtBQUssR0FBRyxDQUFDLEVBQUUsQ0FBQyxZQUFZLENBQUMsTUFBTSxHQUFHLENBQUMsQ0FBQztRQUN4RCxPQUFPLEVBQUUsSUFBSTtRQUNiLE9BQU8sRUFBRSxjQUFNLE9BQUEsaUJBQWlCLENBQUMsQ0FBQyxFQUFFLEdBQUcsQ0FBQyxFQUF6QixDQUF5QjtRQUN4QyxZQUFZLEVBQUUsQ0FBQyxDQUFDLE1BQU07UUFDdEIsUUFBUSxFQUFFLElBQUk7UUFDZCxLQUFLLEVBQUUsS0FBSyxJQUFJLEtBQUs7S0FDdEIsQ0FBQztJQUNGLFdBQVcsQ0FBQyxDQUFDLENBQUMsQ0FBQztBQUNqQixDQUFDO0FBakNELG9DQWlDQztBQUVELHFCQUFxQixDQUFRO0lBQzNCLElBQUksQ0FBQyxHQUFHLENBQUM7UUFDUCxJQUFNLEdBQUcsR0FBRyxDQUFDLENBQUMsU0FBUyxDQUFDLE9BQU8sQ0FBQztRQUNoQyxFQUFFLENBQUMsQ0FBQyxDQUFDLEdBQUcsQ0FBQztZQUFDLE1BQU0sQ0FBQztRQUVqQixFQUFFLENBQUMsQ0FBQyxDQUFDLENBQUMsU0FBUyxDQUFDLE9BQU8sSUFBSSxDQUFDLENBQUMsU0FBUyxDQUFDLE9BQU8sQ0FBQyxJQUFJLENBQUMsS0FBSyxDQUFDLEdBQUcsQ0FBQyxJQUFJLENBQUMsQ0FBQztZQUFDLENBQUMsQ0FBQyxTQUFTLENBQUMsT0FBTyxHQUFHLFNBQVMsQ0FBQztRQUVyRyxJQUFNLFNBQVMsR0FBRyxDQUFDLENBQUMsTUFBTSxDQUFDLEdBQUcsQ0FBQyxJQUFJLENBQUMsQ0FBQztRQUNyQyxFQUFFLENBQUMsQ0FBQyxDQUFDLFNBQVMsSUFBSSxDQUFDLElBQUksQ0FBQyxTQUFTLENBQUMsU0FBUyxFQUFFLEdBQUcsQ0FBQyxLQUFLLENBQUMsQ0FBQztZQUFDLE1BQU0sQ0FBQyxDQUFDLENBQUMsQ0FBQztRQUNuRSxJQUFJLENBQUMsQ0FBQztZQUNKLEVBQUUsQ0FBQyxDQUFDLENBQUMsR0FBRyxDQUFDLE9BQU8sSUFBSSxJQUFJLENBQUMsVUFBVSxDQUFDLEdBQUcsQ0FBQyxJQUFJLEVBQUUsR0FBRyxDQUFDLEdBQUcsQ0FBQyxJQUFJLElBQUksQ0FBQyxHQUFHLENBQUMsQ0FBQyxDQUFDLFNBQVMsQ0FBQyxRQUFRLEVBQUUsQ0FBQyxDQUFDLENBQUM7Z0JBQUMsR0FBRyxDQUFDLE9BQU8sR0FBRyxJQUFJLENBQUM7WUFDaEgsRUFBRSxDQUFDLENBQUMsR0FBRyxDQUFDLE9BQU8sQ0FBQyxDQUFDLENBQUM7Z0JBR2hCLEVBQUUsQ0FBQyxDQUFDLE9BQU8sR0FBRyxDQUFDLE9BQU8sS0FBSyxVQUFVLENBQUMsQ0FBQyxDQUFDO29CQUN0QyxJQUFJLEtBQUssR0FBRyxHQUFHLENBQUMsT0FBTyxFQUFFLENBQUM7b0JBQzFCLEVBQUUsQ0FBQyxDQUFDLENBQUMsS0FBSyxDQUFDO3dCQUFDLE1BQU0sQ0FBQztvQkFDbkIsR0FBRyxDQUFDLE9BQU8sR0FBRyxLQUFLLENBQUM7b0JBQ3BCLEdBQUcsQ0FBQyxPQUFPLENBQUMsVUFBVSxHQUFHLElBQUksQ0FBQztvQkFDOUIsR0FBRyxDQUFDLE9BQU8sQ0FBQyxTQUFTLENBQUMsR0FBRyxDQUFDLFVBQVUsQ0FBQyxDQUFDO2dCQUN4QyxDQUFDO2dCQUVELElBQU0sT0FBTyxHQUFHLENBQUMsQ0FBQyxXQUFXLEtBQUssT0FBTyxFQUN6QyxNQUFNLEdBQUcsQ0FBQyxDQUFDLEdBQUcsQ0FBQyxNQUFNLEVBQUUsQ0FBQztnQkFDeEIsR0FBRyxDQUFDLEdBQUcsR0FBRztvQkFDUixHQUFHLENBQUMsSUFBSSxDQUFDLENBQUMsQ0FBQyxHQUFHLEdBQUcsQ0FBQyxHQUFHLENBQUMsQ0FBQyxDQUFDO29CQUN4QixHQUFHLENBQUMsSUFBSSxDQUFDLENBQUMsQ0FBQyxHQUFHLEdBQUcsQ0FBQyxHQUFHLENBQUMsQ0FBQyxDQUFDO2lCQUN6QixDQUFDO2dCQUNGLEdBQUcsQ0FBQyxJQUFJLEdBQUcsS0FBSyxDQUFDLGNBQWMsQ0FBQyxHQUFHLENBQUMsSUFBSSxFQUFFLE9BQU8sRUFBRSxNQUFNLENBQUMsQ0FBQztnQkFHM0QsSUFBTSxXQUFXLEdBQUcsSUFBSSxDQUFDLGNBQWMsQ0FBQyxHQUFHLENBQUMsT0FBTyxFQUFFLE9BQU8sRUFBRSxNQUFNLENBQUMsQ0FBQztnQkFDdEUsV0FBVyxDQUFDLENBQUMsQ0FBQyxJQUFJLEdBQUcsQ0FBQyxHQUFHLENBQUMsQ0FBQyxDQUFDLEdBQUcsR0FBRyxDQUFDLEdBQUcsQ0FBQyxDQUFDLENBQUMsQ0FBQztnQkFDMUMsV0FBVyxDQUFDLENBQUMsQ0FBQyxJQUFJLEdBQUcsQ0FBQyxHQUFHLENBQUMsQ0FBQyxDQUFDLEdBQUcsR0FBRyxDQUFDLEdBQUcsQ0FBQyxDQUFDLENBQUMsQ0FBQztnQkFDMUMsQ0FBQyxDQUFDLE9BQU8sQ0FBQyxTQUFTLENBQUMsR0FBRyxDQUFDLE9BQU8sRUFBRSxJQUFJLENBQUMsU0FBUyxDQUFDLFdBQVcsQ0FBQyxDQUFDLENBQUM7Z0JBRzlELElBQU0sTUFBTSxHQUFHLENBQUMsQ0FBQyxHQUFHLENBQUMsUUFBUSxDQUFDLElBQUksQ0FBQztnQkFDbkMsRUFBRSxDQUFDLENBQUMsTUFBTSxJQUFJLEdBQUcsQ0FBQyxJQUFJLElBQUksR0FBRyxDQUFDLElBQUksS0FBSyxHQUFHLENBQUMsUUFBUSxDQUFDLENBQUMsQ0FBQztvQkFDcEQsSUFBTSxLQUFLLEdBQUcsQ0FBQyxDQUFDLE9BQU8sQ0FBQyxLQUFLLENBQUM7b0JBQzlCLEVBQUUsQ0FBQyxDQUFDLENBQUMsQ0FBQyxPQUFPLENBQUMsSUFBSTt3QkFDaEIsSUFBSSxDQUFDLFNBQVMsQ0FBQyxLQUFLLElBQUksS0FBSyxDQUFDLEdBQUcsQ0FBQyxJQUFJLENBQUMsRUFBRSxHQUFHLENBQUMsSUFBSSxDQUFDO3dCQUNsRCxJQUFJLENBQUMsU0FBUyxDQUFDLENBQUMsQ0FBQyxVQUFVLENBQUMsS0FBSyxFQUFFLEdBQUcsQ0FBQyxJQUFJLENBQUMsQ0FBQyxDQUFDLENBQUM7d0JBQy9DLElBQU0sR0FBRyxHQUFHLElBQUksQ0FBQyxPQUFPLENBQUMsR0FBRyxDQUFDLElBQUksQ0FBQyxFQUNsQyxNQUFNLEdBQWtCOzRCQUN0QixDQUFDLE9BQU8sR0FBRyxHQUFHLENBQUMsQ0FBQyxDQUFDLEdBQUcsQ0FBQyxHQUFHLENBQUMsR0FBRyxHQUFHLENBQUMsQ0FBQyxDQUFDLENBQUMsR0FBRyxNQUFNLENBQUMsS0FBSyxHQUFHLENBQUM7NEJBQ3RELENBQUMsT0FBTyxHQUFHLENBQUMsR0FBRyxHQUFHLENBQUMsQ0FBQyxDQUFDLEdBQUcsR0FBRyxDQUFDLENBQUMsQ0FBQyxHQUFHLENBQUMsQ0FBQyxHQUFHLE1BQU0sQ0FBQyxNQUFNLEdBQUcsQ0FBQzt5QkFDeEQsQ0FBQzt3QkFDRixDQUFDLENBQUMsT0FBTyxDQUFDLFNBQVMsQ0FBQyxNQUFNLEVBQUUsSUFBSSxDQUFDLFNBQVMsQ0FBQyxNQUFNLENBQUMsQ0FBQyxDQUFDO29CQUN0RCxDQUFDO29CQUFDLElBQUksQ0FBQyxDQUFDO3dCQUNOLENBQUMsQ0FBQyxPQUFPLENBQUMsU0FBUyxDQUFDLE1BQU0sRUFBRSxJQUFJLENBQUMsYUFBYSxDQUFDLENBQUM7b0JBQ2xELENBQUM7b0JBQ0QsR0FBRyxDQUFDLFFBQVEsR0FBRyxHQUFHLENBQUMsSUFBSSxDQUFDO2dCQUMxQixDQUFDO1lBQ0gsQ0FBQztRQUNILENBQUM7UUFDRCxXQUFXLENBQUMsQ0FBQyxDQUFDLENBQUM7SUFDakIsQ0FBQyxDQUFDLENBQUM7QUFDTCxDQUFDO0FBRUQsY0FBcUIsQ0FBUSxFQUFFLENBQWdCO0lBRTdDLEVBQUUsQ0FBQyxDQUFDLENBQUMsQ0FBQyxTQUFTLENBQUMsT0FBTyxJQUFJLENBQUMsQ0FBQyxDQUFDLENBQUMsT0FBTyxJQUFJLENBQUMsQ0FBQyxPQUFPLENBQUMsTUFBTSxHQUFHLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQztRQUNoRSxDQUFDLENBQUMsU0FBUyxDQUFDLE9BQU8sQ0FBQyxJQUFJLEdBQUcsSUFBSSxDQUFDLGFBQWEsQ0FBQyxDQUFDLENBQWtCLENBQUM7SUFDcEUsQ0FBQztBQUNILENBQUM7QUFMRCxvQkFLQztBQUVELGFBQW9CLENBQVEsRUFBRSxDQUFnQjtJQUM1QyxJQUFNLEdBQUcsR0FBRyxDQUFDLENBQUMsU0FBUyxDQUFDLE9BQU8sQ0FBQztJQUNoQyxFQUFFLENBQUMsQ0FBQyxDQUFDLEdBQUcsQ0FBQztRQUFDLE1BQU0sQ0FBQztJQUdqQixFQUFFLENBQUMsQ0FBQyxDQUFDLENBQUMsSUFBSSxLQUFLLFVBQVUsSUFBSSxHQUFHLElBQUksR0FBRyxDQUFDLFlBQVksS0FBSyxDQUFDLENBQUMsTUFBTSxJQUFJLENBQUMsR0FBRyxDQUFDLFFBQVEsQ0FBQyxDQUFDLENBQUM7UUFDbkYsQ0FBQyxDQUFDLFNBQVMsQ0FBQyxPQUFPLEdBQUcsU0FBUyxDQUFDO1FBQ2hDLE1BQU0sQ0FBQztJQUNULENBQUM7SUFDRCxLQUFLLENBQUMsWUFBWSxDQUFDLENBQUMsQ0FBQyxDQUFDO0lBQ3RCLEtBQUssQ0FBQyxZQUFZLENBQUMsQ0FBQyxDQUFDLENBQUM7SUFFdEIsSUFBTSxRQUFRLEdBQWtCLElBQUksQ0FBQyxhQUFhLENBQUMsQ0FBQyxDQUFDLElBQUksR0FBRyxDQUFDLElBQUksQ0FBQztJQUNsRSxJQUFNLElBQUksR0FBRyxLQUFLLENBQUMsY0FBYyxDQUFDLFFBQVEsRUFBRSxDQUFDLENBQUMsV0FBVyxLQUFLLE9BQU8sRUFBRSxDQUFDLENBQUMsR0FBRyxDQUFDLE1BQU0sRUFBRSxDQUFDLENBQUM7SUFDdkYsRUFBRSxDQUFDLENBQUMsSUFBSSxJQUFJLEdBQUcsQ0FBQyxPQUFPLENBQUMsQ0FBQyxDQUFDO1FBQ3hCLEVBQUUsQ0FBQyxDQUFDLEdBQUcsQ0FBQyxRQUFRLENBQUM7WUFBQyxLQUFLLENBQUMsWUFBWSxDQUFDLENBQUMsRUFBRSxHQUFHLENBQUMsSUFBSSxFQUFFLElBQUksRUFBRSxHQUFHLENBQUMsS0FBSyxDQUFDLENBQUM7UUFDbkUsSUFBSSxDQUFDLENBQUM7WUFDSixDQUFDLENBQUMsS0FBSyxDQUFDLE9BQU8sR0FBRyxDQUFDLENBQUMsT0FBTyxDQUFDO1lBQzVCLEVBQUUsQ0FBQyxDQUFDLEtBQUssQ0FBQyxRQUFRLENBQUMsQ0FBQyxFQUFFLEdBQUcsQ0FBQyxJQUFJLEVBQUUsSUFBSSxDQUFDLENBQUM7Z0JBQUMsQ0FBQyxDQUFDLEtBQUssQ0FBQyxPQUFPLEdBQUcsSUFBSSxDQUFDO1FBQ2hFLENBQUM7SUFDSCxDQUFDO0lBQUMsSUFBSSxDQUFDLEVBQUUsQ0FBQyxDQUFDLEdBQUcsQ0FBQyxRQUFRLENBQUMsQ0FBQyxDQUFDO1FBQ3hCLE9BQU8sQ0FBQyxDQUFDLE1BQU0sQ0FBQyxHQUFHLENBQUMsSUFBSSxDQUFDLENBQUM7SUFDNUIsQ0FBQztJQUFDLElBQUksQ0FBQyxFQUFFLENBQUMsQ0FBQyxDQUFDLENBQUMsU0FBUyxDQUFDLGVBQWUsQ0FBQyxDQUFDLENBQUM7UUFDdkMsT0FBTyxDQUFDLENBQUMsTUFBTSxDQUFDLEdBQUcsQ0FBQyxJQUFJLENBQUMsQ0FBQztRQUMxQixLQUFLLENBQUMsZ0JBQWdCLENBQUMsQ0FBQyxDQUFDLE1BQU0sQ0FBQyxNQUFNLENBQUMsQ0FBQztJQUMxQyxDQUFDO0lBQ0QsRUFBRSxDQUFDLENBQUMsR0FBRyxJQUFJLEdBQUcsQ0FBQyxJQUFJLEtBQUssR0FBRyxDQUFDLGtCQUFrQixJQUFJLENBQUMsR0FBRyxDQUFDLElBQUksS0FBSyxJQUFJLElBQUksQ0FBQyxJQUFJLENBQUMsQ0FBQztRQUM3RSxLQUFLLENBQUMsUUFBUSxDQUFDLENBQUMsQ0FBQyxDQUFDO0lBQ3BCLElBQUksQ0FBQyxFQUFFLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxVQUFVLENBQUMsT0FBTyxDQUFDO1FBQUMsS0FBSyxDQUFDLFFBQVEsQ0FBQyxDQUFDLENBQUMsQ0FBQztJQUVsRCxrQkFBa0IsQ0FBQyxDQUFDLENBQUMsQ0FBQztJQUV0QixDQUFDLENBQUMsU0FBUyxDQUFDLE9BQU8sR0FBRyxTQUFTLENBQUM7SUFDaEMsQ0FBQyxDQUFDLEdBQUcsQ0FBQyxNQUFNLEVBQUUsQ0FBQztBQUNqQixDQUFDO0FBbENELGtCQWtDQztBQUVELGdCQUF1QixDQUFRO0lBQzdCLElBQU0sR0FBRyxHQUFHLENBQUMsQ0FBQyxTQUFTLENBQUMsT0FBTyxDQUFDO0lBQ2hDLEVBQUUsQ0FBQyxDQUFDLEdBQUcsQ0FBQyxDQUFDLENBQUM7UUFDUixFQUFFLENBQUMsQ0FBQyxHQUFHLENBQUMsUUFBUSxDQUFDO1lBQUMsT0FBTyxDQUFDLENBQUMsTUFBTSxDQUFDLEdBQUcsQ0FBQyxJQUFJLENBQUMsQ0FBQztRQUM1QyxDQUFDLENBQUMsU0FBUyxDQUFDLE9BQU8sR0FBRyxTQUFTLENBQUM7UUFDaEMsS0FBSyxDQUFDLFFBQVEsQ0FBQyxDQUFDLENBQUMsQ0FBQztRQUNsQixrQkFBa0IsQ0FBQyxDQUFDLENBQUMsQ0FBQztRQUN0QixDQUFDLENBQUMsR0FBRyxDQUFDLE1BQU0sRUFBRSxDQUFDO0lBQ2pCLENBQUM7QUFDSCxDQUFDO0FBVEQsd0JBU0M7QUFFRCw0QkFBNEIsQ0FBUTtJQUNsQyxJQUFNLENBQUMsR0FBRyxDQUFDLENBQUMsR0FBRyxDQUFDLFFBQVEsQ0FBQztJQUN6QixFQUFFLENBQUMsQ0FBQyxDQUFDLENBQUMsSUFBSSxDQUFDO1FBQUMsQ0FBQyxDQUFDLE9BQU8sQ0FBQyxTQUFTLENBQUMsQ0FBQyxDQUFDLElBQUksRUFBRSxJQUFJLENBQUMsYUFBYSxDQUFDLENBQUM7SUFDNUQsRUFBRSxDQUFDLENBQUMsQ0FBQyxDQUFDLEtBQUssQ0FBQztRQUFDLENBQUMsQ0FBQyxPQUFPLENBQUMsU0FBUyxDQUFDLENBQUMsQ0FBQyxLQUFLLEVBQUUsSUFBSSxDQUFDLGFBQWEsQ0FBQyxDQUFDO0FBQ2hFLENBQUM7QUFFRCw2QkFBNkIsR0FBVyxFQUFFLE9BQWdCLEVBQUUsTUFBa0I7SUFDNUUsSUFBTSxHQUFHLEdBQUcsSUFBSSxDQUFDLE9BQU8sQ0FBQyxHQUFHLENBQUMsQ0FBQztJQUM5QixFQUFFLENBQUMsQ0FBQyxDQUFDLE9BQU8sQ0FBQyxDQUFDLENBQUM7UUFDYixHQUFHLENBQUMsQ0FBQyxDQUFDLEdBQUcsQ0FBQyxHQUFHLEdBQUcsQ0FBQyxDQUFDLENBQUMsQ0FBQztRQUNwQixHQUFHLENBQUMsQ0FBQyxDQUFDLEdBQUcsQ0FBQyxHQUFHLEdBQUcsQ0FBQyxDQUFDLENBQUMsQ0FBQztJQUN0QixDQUFDO0lBQ0QsTUFBTSxDQUFDO1FBQ0wsSUFBSSxFQUFFLE1BQU0sQ0FBQyxJQUFJLEdBQUcsTUFBTSxDQUFDLEtBQUssR0FBRyxDQUFDLEdBQUcsQ0FBQyxDQUFDLENBQUMsR0FBRyxDQUFDLENBQUMsR0FBRyxDQUFDO1FBQ25ELEdBQUcsRUFBRSxNQUFNLENBQUMsR0FBRyxHQUFHLE1BQU0sQ0FBQyxNQUFNLEdBQUcsQ0FBQyxDQUFDLEdBQUcsR0FBRyxDQUFDLENBQUMsQ0FBQyxDQUFDLEdBQUcsQ0FBQztRQUNsRCxLQUFLLEVBQUUsTUFBTSxDQUFDLEtBQUssR0FBRyxDQUFDO1FBQ3ZCLE1BQU0sRUFBRSxNQUFNLENBQUMsTUFBTSxHQUFHLENBQUM7S0FDMUIsQ0FBQztBQUNKLENBQUM7QUFFRCwyQkFBMkIsQ0FBUSxFQUFFLEdBQVc7SUFDOUMsSUFBSSxFQUFFLEdBQUcsQ0FBQyxDQUFDLEdBQUcsQ0FBQyxRQUFRLENBQUMsS0FBSyxDQUFDLFVBQTBCLENBQUM7SUFDekQsT0FBTyxFQUFFLEVBQUUsQ0FBQztRQUNWLEVBQUUsQ0FBQyxDQUFDLEVBQUUsQ0FBQyxLQUFLLEtBQUssR0FBRyxJQUFJLEVBQUUsQ0FBQyxPQUFPLEtBQUssT0FBTyxDQUFDO1lBQUMsTUFBTSxDQUFDLEVBQUUsQ0FBQztRQUMxRCxFQUFFLEdBQUcsRUFBRSxDQUFDLFdBQTJCLENBQUM7SUFDdEMsQ0FBQztJQUNELE1BQU0sQ0FBQyxTQUFTLENBQUM7QUFDbkIsQ0FBQzs7Ozs7QUNwUUQsaUNBQW9EO0FBQ3BELCtCQUEwRDtBQXNEMUQsSUFBTSxPQUFPLEdBQUcsQ0FBQyxPQUFPLEVBQUUsS0FBSyxFQUFFLE1BQU0sRUFBRSxRQUFRLENBQUMsQ0FBQztBQUVuRCxlQUFzQixLQUFZLEVBQUUsQ0FBZ0I7SUFDbEQsRUFBRSxDQUFDLENBQUMsQ0FBQyxDQUFDLE9BQU8sSUFBSSxDQUFDLENBQUMsT0FBTyxDQUFDLE1BQU0sR0FBRyxDQUFDLENBQUM7UUFBQyxNQUFNLENBQUM7SUFDOUMsQ0FBQyxDQUFDLGVBQWUsRUFBRSxDQUFDO0lBQ3BCLENBQUMsQ0FBQyxjQUFjLEVBQUUsQ0FBQztJQUNuQixrQkFBVSxDQUFDLEtBQUssQ0FBQyxDQUFDO0lBQ2xCLElBQU0sUUFBUSxHQUFHLG9CQUFhLENBQUMsQ0FBQyxDQUFrQixDQUFDO0lBQ25ELElBQU0sSUFBSSxHQUFHLHNCQUFjLENBQUMsUUFBUSxFQUFFLEtBQUssQ0FBQyxXQUFXLEtBQUssT0FBTyxFQUFFLEtBQUssQ0FBQyxHQUFHLENBQUMsTUFBTSxFQUFFLENBQUMsQ0FBQztJQUN6RixFQUFFLENBQUMsQ0FBQyxDQUFDLElBQUksQ0FBQztRQUFDLE1BQU0sQ0FBQztJQUNsQixLQUFLLENBQUMsUUFBUSxDQUFDLE9BQU8sR0FBRztRQUN2QixJQUFJLEVBQUUsSUFBSTtRQUNWLElBQUksRUFBRSxJQUFJO1FBQ1YsR0FBRyxFQUFFLFFBQVE7UUFDYixLQUFLLEVBQUUsVUFBVSxDQUFDLENBQUMsQ0FBQztLQUNyQixDQUFDO0lBQ0YsV0FBVyxDQUFDLEtBQUssQ0FBQyxDQUFDO0FBQ3JCLENBQUM7QUFmRCxzQkFlQztBQUVELHFCQUE0QixLQUFZO0lBQ3RDLFVBQUcsQ0FBQztRQUNGLElBQU0sR0FBRyxHQUFHLEtBQUssQ0FBQyxRQUFRLENBQUMsT0FBTyxDQUFDO1FBQ25DLEVBQUUsQ0FBQyxDQUFDLEdBQUcsQ0FBQyxDQUFDLENBQUM7WUFDUixJQUFNLElBQUksR0FBRyxzQkFBYyxDQUFDLEdBQUcsQ0FBQyxHQUFHLEVBQUUsS0FBSyxDQUFDLFdBQVcsS0FBSyxPQUFPLEVBQUUsS0FBSyxDQUFDLEdBQUcsQ0FBQyxNQUFNLEVBQUUsQ0FBQyxDQUFDO1lBQ3hGLElBQU0sT0FBTyxHQUFHLENBQUMsR0FBRyxDQUFDLElBQUksS0FBSyxJQUFJLENBQUMsR0FBRyxTQUFTLEdBQUcsSUFBSSxDQUFDO1lBQ3ZELEVBQUUsQ0FBQyxDQUFDLE9BQU8sS0FBSyxHQUFHLENBQUMsSUFBSSxDQUFDLENBQUMsQ0FBQztnQkFDekIsR0FBRyxDQUFDLElBQUksR0FBRyxPQUFPLENBQUM7Z0JBQ25CLEtBQUssQ0FBQyxHQUFHLENBQUMsU0FBUyxFQUFFLENBQUM7WUFDeEIsQ0FBQztZQUNELFdBQVcsQ0FBQyxLQUFLLENBQUMsQ0FBQztRQUNyQixDQUFDO0lBQ0gsQ0FBQyxDQUFDLENBQUM7QUFDTCxDQUFDO0FBYkQsa0NBYUM7QUFFRCxjQUFxQixLQUFZLEVBQUUsQ0FBZ0I7SUFDakQsRUFBRSxDQUFDLENBQUMsS0FBSyxDQUFDLFFBQVEsQ0FBQyxPQUFPLENBQUM7UUFBQyxLQUFLLENBQUMsUUFBUSxDQUFDLE9BQU8sQ0FBQyxHQUFHLEdBQUcsb0JBQWEsQ0FBQyxDQUFDLENBQWtCLENBQUM7QUFDN0YsQ0FBQztBQUZELG9CQUVDO0FBRUQsYUFBb0IsS0FBWTtJQUM5QixJQUFNLEdBQUcsR0FBRyxLQUFLLENBQUMsUUFBUSxDQUFDLE9BQU8sQ0FBQztJQUNuQyxFQUFFLENBQUMsQ0FBQyxDQUFDLEdBQUcsQ0FBQztRQUFDLE1BQU0sQ0FBQztJQUNqQixFQUFFLENBQUMsQ0FBQyxHQUFHLENBQUMsSUFBSSxJQUFJLEdBQUcsQ0FBQyxJQUFJLEtBQUssR0FBRyxDQUFDLElBQUksQ0FBQztRQUFDLE9BQU8sQ0FBQyxLQUFLLENBQUMsUUFBUSxFQUFFLEdBQUcsRUFBRSxHQUFHLENBQUMsSUFBSSxDQUFDLENBQUM7SUFDOUUsSUFBSTtRQUFDLFNBQVMsQ0FBQyxLQUFLLENBQUMsUUFBUSxFQUFFLEdBQUcsQ0FBQyxDQUFDO0lBQ3BDLE1BQU0sQ0FBQyxLQUFLLENBQUMsQ0FBQztBQUNoQixDQUFDO0FBTkQsa0JBTUM7QUFFRCxnQkFBdUIsS0FBWTtJQUNqQyxFQUFFLENBQUMsQ0FBQyxLQUFLLENBQUMsUUFBUSxDQUFDLE9BQU8sQ0FBQyxDQUFDLENBQUM7UUFDM0IsS0FBSyxDQUFDLFFBQVEsQ0FBQyxPQUFPLEdBQUcsU0FBUyxDQUFDO1FBQ25DLEtBQUssQ0FBQyxHQUFHLENBQUMsTUFBTSxFQUFFLENBQUM7SUFDckIsQ0FBQztBQUNILENBQUM7QUFMRCx3QkFLQztBQUVELGVBQXNCLEtBQVk7SUFDaEMsRUFBRSxDQUFDLENBQUMsS0FBSyxDQUFDLFFBQVEsQ0FBQyxNQUFNLENBQUMsTUFBTSxDQUFDLENBQUMsQ0FBQztRQUNqQyxLQUFLLENBQUMsUUFBUSxDQUFDLE1BQU0sR0FBRyxFQUFFLENBQUM7UUFDM0IsS0FBSyxDQUFDLEdBQUcsQ0FBQyxNQUFNLEVBQUUsQ0FBQztRQUNuQixRQUFRLENBQUMsS0FBSyxDQUFDLFFBQVEsQ0FBQyxDQUFDO0lBQzNCLENBQUM7QUFDSCxDQUFDO0FBTkQsc0JBTUM7QUFFRCxvQkFBb0IsQ0FBZ0I7SUFDbEMsSUFBTSxDQUFDLEdBQVcsQ0FBQyxDQUFDLFFBQVEsSUFBSSxvQkFBYSxDQUFDLENBQUMsQ0FBQyxHQUFHLENBQUMsR0FBRyxDQUFDLENBQUM7SUFDekQsSUFBTSxDQUFDLEdBQVcsQ0FBQyxDQUFDLE1BQU0sR0FBRyxDQUFDLEdBQUcsQ0FBQyxDQUFDO0lBQ25DLE1BQU0sQ0FBQyxPQUFPLENBQUMsQ0FBQyxHQUFHLENBQUMsQ0FBQyxDQUFDO0FBQ3hCLENBQUM7QUFFRCxhQUFnQixDQUFvQjtJQUNsQyxNQUFNLENBQUMsVUFBQyxDQUFJLElBQUssT0FBQSxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsRUFBTCxDQUFLLENBQUM7QUFDekIsQ0FBQztBQUVELG1CQUFtQixRQUFrQixFQUFFLEdBQWdCO0lBQ3JELElBQU0sSUFBSSxHQUFHLEdBQUcsQ0FBQyxJQUFJLENBQUM7SUFDdEIsSUFBTSxVQUFVLEdBQUcsVUFBQyxDQUFZLElBQUssT0FBQSxDQUFDLENBQUMsSUFBSSxLQUFLLElBQUksSUFBSSxDQUFDLENBQUMsQ0FBQyxJQUFJLEVBQTFCLENBQTBCLENBQUM7SUFDaEUsSUFBTSxPQUFPLEdBQUcsUUFBUSxDQUFDLE1BQU0sQ0FBQyxNQUFNLENBQUMsVUFBVSxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUM7SUFDdEQsRUFBRSxDQUFDLENBQUMsT0FBTyxDQUFDO1FBQUMsUUFBUSxDQUFDLE1BQU0sR0FBRyxRQUFRLENBQUMsTUFBTSxDQUFDLE1BQU0sQ0FBQyxHQUFHLENBQUMsVUFBVSxDQUFDLENBQUMsQ0FBQztJQUN2RSxFQUFFLENBQUMsQ0FBQyxDQUFDLE9BQU8sSUFBSSxPQUFPLENBQUMsS0FBSyxLQUFLLEdBQUcsQ0FBQyxLQUFLLENBQUM7UUFBQyxRQUFRLENBQUMsTUFBTSxDQUFDLElBQUksQ0FBQztZQUNoRSxLQUFLLEVBQUUsR0FBRyxDQUFDLEtBQUs7WUFDaEIsSUFBSSxFQUFFLElBQUk7U0FDWCxDQUFDLENBQUM7SUFDSCxRQUFRLENBQUMsUUFBUSxDQUFDLENBQUM7QUFDckIsQ0FBQztBQUVELGlCQUFpQixRQUFrQixFQUFFLEdBQWdCLEVBQUUsSUFBWTtJQUNqRSxJQUFNLElBQUksR0FBRyxHQUFHLENBQUMsSUFBSSxDQUFDO0lBQ3RCLElBQU0sUUFBUSxHQUFHLFVBQUMsQ0FBWTtRQUM1QixNQUFNLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxJQUFJLElBQUksQ0FBQyxDQUFDLENBQUMsQ0FBQyxJQUFJLEtBQUssSUFBSSxJQUFJLENBQUMsQ0FBQyxJQUFJLEtBQUssSUFBSSxDQUFDLElBQUksQ0FBQyxDQUFDLENBQUMsSUFBSSxLQUFLLElBQUksSUFBSSxDQUFDLENBQUMsSUFBSSxLQUFLLElBQUksQ0FBQyxDQUFDLENBQUM7SUFDcEcsQ0FBQyxDQUFDO0lBQ0YsSUFBTSxNQUFNLEdBQUcsUUFBUSxDQUFDLE1BQU0sQ0FBQyxNQUFNLENBQUMsUUFBUSxDQUFDLENBQUMsTUFBTSxHQUFHLENBQUMsQ0FBQztJQUMzRCxFQUFFLENBQUMsQ0FBQyxNQUFNLENBQUM7UUFBQyxRQUFRLENBQUMsTUFBTSxHQUFHLFFBQVEsQ0FBQyxNQUFNLENBQUMsTUFBTSxDQUFDLEdBQUcsQ0FBQyxRQUFRLENBQUMsQ0FBQyxDQUFDO0lBQ3BFLElBQUk7UUFBQyxRQUFRLENBQUMsTUFBTSxDQUFDLElBQUksQ0FBQztZQUN4QixLQUFLLEVBQUUsR0FBRyxDQUFDLEtBQUs7WUFDaEIsSUFBSSxFQUFFLElBQUk7WUFDVixJQUFJLEVBQUUsSUFBSTtTQUNYLENBQUMsQ0FBQztJQUNILFFBQVEsQ0FBQyxRQUFRLENBQUMsQ0FBQztBQUNyQixDQUFDO0FBRUQsa0JBQWtCLFFBQWtCO0lBQ2xDLEVBQUUsQ0FBQyxDQUFDLFFBQVEsQ0FBQyxRQUFRLENBQUM7UUFBQyxRQUFRLENBQUMsUUFBUSxDQUFDLFFBQVEsQ0FBQyxNQUFNLENBQUMsQ0FBQztBQUM1RCxDQUFDOzs7OztBQzNKRCw2QkFBOEI7QUFDOUIsNkJBQThCO0FBQzlCLCtCQUEyQztBQU0zQyxtQkFBMEIsQ0FBUTtJQUVoQyxJQUFNLE9BQU8sR0FBRyxDQUFDLENBQUMsR0FBRyxDQUFDLFFBQVEsQ0FBQyxLQUFLLENBQUM7SUFFckMsRUFBRSxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsUUFBUSxDQUFDLENBQUMsQ0FBQztRQUNoQixDQUFDLFlBQVksRUFBRSxXQUFXLENBQUMsQ0FBQyxPQUFPLENBQUMsVUFBQSxFQUFFLElBQUksT0FBQSxPQUFPLENBQUMsZ0JBQWdCLENBQUMsRUFBRSxFQUFFLGVBQWUsQ0FBQyxDQUFDLENBQUMsQ0FBQyxFQUFoRCxDQUFnRCxDQUFDLENBQUM7SUFDOUYsQ0FBQztJQUVELEVBQUUsQ0FBQyxDQUFDLENBQUMsQ0FBQyxrQkFBa0IsSUFBSSxDQUFDLENBQUMsUUFBUSxDQUFDLE9BQU8sQ0FBQyxDQUFDLENBQUM7UUFDL0MsT0FBTyxDQUFDLGdCQUFnQixDQUFDLGFBQWEsRUFBRSxVQUFBLENBQUM7WUFDdkMsQ0FBQyxDQUFDLGNBQWMsRUFBRSxDQUFDO1lBQ25CLE1BQU0sQ0FBQyxLQUFLLENBQUM7UUFDZixDQUFDLENBQUMsQ0FBQztJQUNMLENBQUM7QUFDSCxDQUFDO0FBZEQsOEJBY0M7QUFHRCxzQkFBNkIsQ0FBUSxFQUFFLFNBQW9CO0lBRXpELElBQU0sTUFBTSxHQUFjLFVBQVUsQ0FBQyxDQUFDLEVBQUUsSUFBSSxDQUFDLElBQUksRUFBRSxJQUFJLENBQUMsSUFBSSxDQUFDLENBQUM7SUFDOUQsSUFBTSxLQUFLLEdBQWMsVUFBVSxDQUFDLENBQUMsRUFBRSxJQUFJLENBQUMsR0FBRyxFQUFFLElBQUksQ0FBQyxHQUFHLENBQUMsQ0FBQztJQUUzRCxJQUFNLE9BQU8sR0FBZ0IsRUFBRSxDQUFDO0lBRWhDLEVBQUUsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLFFBQVEsQ0FBQyxDQUFDLENBQUM7UUFDaEIsQ0FBQyxXQUFXLEVBQUUsV0FBVyxDQUFDLENBQUMsT0FBTyxDQUFDLFVBQUEsRUFBRSxJQUFJLE9BQUEsT0FBTyxDQUFDLElBQUksQ0FBQyxVQUFVLENBQUMsUUFBUSxFQUFFLEVBQUUsRUFBRSxNQUFNLENBQUMsQ0FBQyxFQUE5QyxDQUE4QyxDQUFDLENBQUM7UUFDekYsQ0FBQyxVQUFVLEVBQUUsU0FBUyxDQUFDLENBQUMsT0FBTyxDQUFDLFVBQUEsRUFBRSxJQUFJLE9BQUEsT0FBTyxDQUFDLElBQUksQ0FBQyxVQUFVLENBQUMsUUFBUSxFQUFFLEVBQUUsRUFBRSxLQUFLLENBQUMsQ0FBQyxFQUE3QyxDQUE2QyxDQUFDLENBQUM7SUFDdkYsQ0FBQztJQUVELElBQU0sUUFBUSxHQUFHO1FBQ2YsQ0FBQyxDQUFDLEdBQUcsQ0FBQyxNQUFNLENBQUMsS0FBSyxFQUFFLENBQUM7UUFDckIsVUFBRyxDQUFDLFNBQVMsQ0FBQyxDQUFDO0lBQ2pCLENBQUMsQ0FBQztJQUNGLEVBQUUsQ0FBQyxDQUFDLENBQUMsQ0FBQyxTQUFTLENBQUM7UUFBQyxPQUFPLENBQUMsSUFBSSxDQUFDLFVBQVUsQ0FBQyxRQUFRLENBQUMsSUFBSSxFQUFFLG9CQUFvQixFQUFFLFFBQVEsQ0FBQyxDQUFDLENBQUM7SUFFekYsSUFBTSxRQUFRLEdBQUcsY0FBTSxPQUFBLENBQUMsQ0FBQyxHQUFHLENBQUMsTUFBTSxDQUFDLEtBQUssRUFBRSxFQUFwQixDQUFvQixDQUFDO0lBQzVDLE9BQU8sQ0FBQyxJQUFJLENBQUMsVUFBVSxDQUFDLE1BQU0sRUFBRSxRQUFRLEVBQUUsUUFBUSxFQUFFLEVBQUUsT0FBTyxFQUFFLElBQUksRUFBRSxDQUFDLENBQUMsQ0FBQztJQUN4RSxPQUFPLENBQUMsSUFBSSxDQUFDLFVBQVUsQ0FBQyxNQUFNLEVBQUUsUUFBUSxFQUFFLFFBQVEsRUFBRSxFQUFFLE9BQU8sRUFBRSxJQUFJLEVBQUUsQ0FBQyxDQUFDLENBQUM7SUFFeEUsTUFBTSxDQUFDLGNBQU0sT0FBQSxPQUFPLENBQUMsT0FBTyxDQUFDLFVBQUEsQ0FBQyxJQUFJLE9BQUEsQ0FBQyxFQUFFLEVBQUgsQ0FBRyxDQUFDLEVBQXpCLENBQXlCLENBQUM7QUFDekMsQ0FBQztBQXZCRCxvQ0F1QkM7QUFFRCxvQkFBb0IsRUFBZSxFQUFFLFNBQWlCLEVBQUUsUUFBbUIsRUFBRSxPQUFhO0lBQ3hGLEVBQUUsQ0FBQyxnQkFBZ0IsQ0FBQyxTQUFTLEVBQUUsUUFBUSxFQUFFLE9BQU8sQ0FBQyxDQUFDO0lBQ2xELE1BQU0sQ0FBQyxjQUFNLE9BQUEsRUFBRSxDQUFDLG1CQUFtQixDQUFDLFNBQVMsRUFBRSxRQUFRLENBQUMsRUFBM0MsQ0FBMkMsQ0FBQztBQUMzRCxDQUFDO0FBRUQseUJBQXlCLENBQVE7SUFDL0IsTUFBTSxDQUFDLFVBQUEsQ0FBQztRQUNOLEVBQUUsQ0FBQyxDQUFDLENBQUMsQ0FBQyxTQUFTLENBQUMsT0FBTyxDQUFDO1lBQUMsSUFBSSxDQUFDLE1BQU0sQ0FBQyxDQUFDLENBQUMsQ0FBQztRQUN4QyxJQUFJLENBQUMsRUFBRSxDQUFDLENBQUMsQ0FBQyxDQUFDLFFBQVEsQ0FBQyxPQUFPLENBQUM7WUFBQyxJQUFJLENBQUMsTUFBTSxDQUFDLENBQUMsQ0FBQyxDQUFDO1FBQzVDLElBQUksQ0FBQyxFQUFFLENBQUMsQ0FBQyxDQUFDLENBQUMsUUFBUSxJQUFJLG9CQUFhLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDO1lBQUMsRUFBRSxDQUFDLENBQUMsQ0FBQyxDQUFDLFFBQVEsQ0FBQyxPQUFPLENBQUM7Z0JBQUMsSUFBSSxDQUFDLEtBQUssQ0FBQyxDQUFDLEVBQUUsQ0FBQyxDQUFDLENBQUM7UUFBQyxDQUFDO1FBQ3RGLElBQUksQ0FBQyxFQUFFLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxRQUFRLENBQUM7WUFBQyxJQUFJLENBQUMsS0FBSyxDQUFDLENBQUMsRUFBRSxDQUFDLENBQUMsQ0FBQztJQUN6QyxDQUFDLENBQUM7QUFDSixDQUFDO0FBRUQsb0JBQW9CLENBQVEsRUFBRSxRQUF3QixFQUFFLFFBQXdCO0lBQzlFLE1BQU0sQ0FBQyxVQUFBLENBQUM7UUFDTixFQUFFLENBQUMsQ0FBQyxDQUFDLENBQUMsUUFBUSxJQUFJLG9CQUFhLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDO1lBQUMsRUFBRSxDQUFDLENBQUMsQ0FBQyxDQUFDLFFBQVEsQ0FBQyxPQUFPLENBQUM7Z0JBQUMsUUFBUSxDQUFDLENBQUMsRUFBRSxDQUFDLENBQUMsQ0FBQztRQUFDLENBQUM7UUFDL0UsSUFBSSxDQUFDLEVBQUUsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLFFBQVEsQ0FBQztZQUFDLFFBQVEsQ0FBQyxDQUFDLEVBQUUsQ0FBQyxDQUFDLENBQUM7SUFDdkMsQ0FBQyxDQUFDO0FBQ0osQ0FBQzs7Ozs7QUNuRUQsbUJBQWtDLEtBQVksRUFBRSxJQUFXO0lBQ3pELEtBQUssQ0FBQyxTQUFTLEdBQUc7UUFDaEIsS0FBSyxFQUFFLENBQUM7UUFDUixJQUFJLEVBQUUsSUFBSTtLQUNYLENBQUM7SUFDRixLQUFLLENBQUMsR0FBRyxDQUFDLE1BQU0sRUFBRSxDQUFDO0lBQ25CLFVBQVUsQ0FBQztRQUNULFFBQVEsQ0FBQyxLQUFLLEVBQUUsQ0FBQyxDQUFDLENBQUM7UUFDbkIsVUFBVSxDQUFDLGNBQU0sT0FBQSxRQUFRLENBQUMsS0FBSyxFQUFFLFNBQVMsQ0FBQyxFQUExQixDQUEwQixFQUFFLEdBQUcsQ0FBQyxDQUFDO0lBQ3BELENBQUMsRUFBRSxHQUFHLENBQUMsQ0FBQztBQUNWLENBQUM7QUFWRCw0QkFVQztBQUVELGtCQUFrQixLQUFZLEVBQUUsS0FBeUI7SUFDdkQsRUFBRSxDQUFDLENBQUMsS0FBSyxDQUFDLFNBQVMsQ0FBQyxDQUFDLENBQUM7UUFDcEIsRUFBRSxDQUFDLENBQUMsS0FBSyxDQUFDO1lBQUMsS0FBSyxDQUFDLFNBQVMsQ0FBQyxLQUFLLEdBQUcsS0FBSyxDQUFDO1FBQ3pDLElBQUk7WUFBQyxLQUFLLENBQUMsU0FBUyxHQUFHLFNBQVMsQ0FBQztRQUNqQyxLQUFLLENBQUMsR0FBRyxDQUFDLE1BQU0sRUFBRSxDQUFDO0lBQ3JCLENBQUM7QUFDSCxDQUFDOzs7OztBQ3JCRCwrQkFBMEM7QUFDMUMsNEJBQTZCO0FBRWhCLFFBQUEsT0FBTyxHQUFXLDZDQUE2QyxDQUFDO0FBRTdFLElBQU0sS0FBSyxHQUFrQyxFQUFFLENBQUMsRUFBRSxNQUFNLEVBQUUsQ0FBQyxFQUFFLE1BQU0sRUFBRSxDQUFDLEVBQUUsUUFBUSxFQUFFLENBQUMsRUFBRSxRQUFRLEVBQUUsQ0FBQyxFQUFFLE9BQU8sRUFBRSxDQUFDLEVBQUUsTUFBTSxFQUFFLENBQUM7QUFFdkgsSUFBTSxPQUFPLEdBQUcsRUFBRSxJQUFJLEVBQUUsR0FBRyxFQUFFLElBQUksRUFBRSxHQUFHLEVBQUUsTUFBTSxFQUFFLEdBQUcsRUFBRSxNQUFNLEVBQUUsR0FBRyxFQUFFLEtBQUssRUFBRSxHQUFHLEVBQUUsSUFBSSxFQUFFLEdBQUcsRUFBRSxDQUFDO0FBRzFGLGNBQXFCLEdBQVc7SUFDOUIsRUFBRSxDQUFDLENBQUMsR0FBRyxLQUFLLE9BQU8sQ0FBQztRQUFDLEdBQUcsR0FBRyxlQUFPLENBQUM7SUFDbkMsSUFBTSxNQUFNLEdBQWMsRUFBRSxDQUFDO0lBQzdCLElBQUksR0FBRyxHQUFXLENBQUMsQ0FBQztJQUNwQixJQUFJLEdBQUcsR0FBVyxDQUFDLENBQUM7SUFDcEIsR0FBRyxDQUFDLENBQVksVUFBRyxFQUFILFdBQUcsRUFBSCxpQkFBRyxFQUFILElBQUc7UUFBZCxJQUFNLENBQUMsWUFBQTtRQUNWLE1BQU0sQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUM7WUFDVixLQUFLLEdBQUcsRUFBRSxNQUFNLENBQUMsTUFBTSxDQUFDO1lBQ3hCLEtBQUssR0FBRztnQkFDTixFQUFFLEdBQUcsQ0FBQztnQkFDTixFQUFFLENBQUMsQ0FBQyxHQUFHLEtBQUssQ0FBQyxDQUFDO29CQUFDLE1BQU0sQ0FBQyxNQUFNLENBQUM7Z0JBQzdCLEdBQUcsR0FBRyxDQUFDLENBQUM7Z0JBQ1IsS0FBSyxDQUFDO1lBQ1IsS0FBSyxHQUFHO2dCQUNOLE1BQU0sQ0FBQyxjQUFPLENBQUMsQ0FBQyxHQUFHLEVBQUUsR0FBRyxDQUFDLENBQUMsQ0FBQyxDQUFDLFFBQVEsR0FBRyxJQUFJLENBQUM7Z0JBQzVDLEtBQUssQ0FBQztZQUNSO2dCQUNFLElBQU0sRUFBRSxHQUFHLENBQUMsQ0FBQyxVQUFVLENBQUMsQ0FBQyxDQUFDLENBQUM7Z0JBQzNCLEVBQUUsQ0FBQyxDQUFDLEVBQUUsR0FBRyxFQUFFLENBQUM7b0JBQUMsR0FBRyxJQUFJLEVBQUUsR0FBRyxFQUFFLENBQUM7Z0JBQzVCLElBQUksQ0FBQyxDQUFDO29CQUNKLEVBQUUsR0FBRyxDQUFDO29CQUNOLElBQU0sSUFBSSxHQUFHLENBQUMsQ0FBQyxXQUFXLEVBQUUsQ0FBQztvQkFDN0IsTUFBTSxDQUFDLGNBQU8sQ0FBQyxDQUFDLEdBQUcsRUFBRSxHQUFHLENBQUMsQ0FBQyxDQUFDLEdBQUc7d0JBQzVCLElBQUksRUFBRSxLQUFLLENBQUMsSUFBSSxDQUFDO3dCQUNqQixLQUFLLEVBQUUsQ0FBQyxDQUFDLEtBQUssSUFBSSxHQUFHLE9BQU8sR0FBRyxPQUFPLENBQWE7cUJBQ3BELENBQUM7Z0JBQ0osQ0FBQztRQUNMLENBQUM7S0FDRjtJQUNELE1BQU0sQ0FBQyxNQUFNLENBQUM7QUFDaEIsQ0FBQztBQTlCRCxvQkE4QkM7QUFFRCxlQUFzQixNQUFpQjtJQUNyQyxJQUFJLEtBQWUsRUFBRSxNQUFjLENBQUM7SUFDcEMsTUFBTSxDQUFDLGVBQVEsQ0FBQyxHQUFHLENBQUMsVUFBQSxDQUFDLElBQUksT0FBQSxFQUFFLENBQUMsS0FBSyxDQUFDLEdBQUcsQ0FBQyxVQUFBLENBQUM7UUFDbkMsS0FBSyxHQUFHLE1BQU0sQ0FBQyxjQUFPLENBQUMsQ0FBQyxDQUFDLEVBQUUsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDO1FBQ2hDLEVBQUUsQ0FBQyxDQUFDLEtBQUssQ0FBQyxDQUFDLENBQUM7WUFDVixNQUFNLEdBQUcsT0FBTyxDQUFDLEtBQUssQ0FBQyxJQUFJLENBQUMsQ0FBQztZQUM3QixNQUFNLENBQUMsS0FBSyxDQUFDLEtBQUssS0FBSyxPQUFPLEdBQUcsTUFBTSxDQUFDLFdBQVcsRUFBRSxHQUFHLE1BQU0sQ0FBQztRQUNqRSxDQUFDO1FBQUMsSUFBSTtZQUFDLE1BQU0sQ0FBQyxHQUFHLENBQUM7SUFDcEIsQ0FBQyxDQUFDLENBQUMsSUFBSSxDQUFDLEVBQUUsQ0FBQyxFQU5ZLENBTVosQ0FDWixDQUFDLElBQUksQ0FBQyxHQUFHLENBQUMsQ0FBQyxPQUFPLENBQUMsUUFBUSxFQUFFLFVBQUEsQ0FBQyxJQUFJLE9BQUEsQ0FBQyxDQUFDLE1BQU0sQ0FBQyxRQUFRLEVBQUUsRUFBbkIsQ0FBbUIsQ0FBQyxDQUFDO0FBQzFELENBQUM7QUFWRCxzQkFVQzs7O0FDcEREO0FBQ0E7Ozs7QUNEQSw2QkFBOEI7QUFLOUIsY0FBYyxDQUFTLEVBQUUsQ0FBUTtJQUMvQixNQUFNLENBQUMsSUFBSSxDQUFDLEdBQUcsQ0FBQyxDQUFDLEdBQUcsQ0FBQyxDQUFDLENBQUM7QUFDekIsQ0FBQztBQUVELGNBQWMsS0FBZTtJQUMzQixNQUFNLENBQUMsVUFBQyxFQUFFLEVBQUUsRUFBRSxFQUFFLEVBQUUsRUFBRSxFQUFFLElBQUssT0FBQSxJQUFJLENBQUMsRUFBRSxFQUFFLEVBQUUsQ0FBQyxHQUFHLENBQUMsSUFBSSxDQUM3QyxLQUFLLEtBQUssT0FBTyxHQUFHLENBRWxCLEVBQUUsS0FBSyxFQUFFLEdBQUcsQ0FBQyxJQUFJLENBQUMsRUFBRSxJQUFJLENBQUMsSUFBSSxFQUFFLEtBQUssQ0FBQyxFQUFFLEdBQUcsQ0FBQyxDQUFDLElBQUksRUFBRSxLQUFLLEVBQUUsQ0FBQyxDQUMzRCxHQUFHLENBQ0YsRUFBRSxLQUFLLEVBQUUsR0FBRyxDQUFDLElBQUksQ0FBQyxFQUFFLElBQUksQ0FBQyxJQUFJLEVBQUUsS0FBSyxDQUFDLEVBQUUsR0FBRyxDQUFDLENBQUMsSUFBSSxFQUFFLEtBQUssRUFBRSxDQUFDLENBQzNELENBQ0YsRUFQMEIsQ0FPMUIsQ0FBQztBQUNKLENBQUM7QUFFRCxJQUFNLE1BQU0sR0FBYSxVQUFDLEVBQUUsRUFBRSxFQUFFLEVBQUUsRUFBRSxFQUFFLEVBQUU7SUFDdEMsSUFBTSxFQUFFLEdBQUcsSUFBSSxDQUFDLEVBQUUsRUFBRSxFQUFFLENBQUMsQ0FBQztJQUN4QixJQUFNLEVBQUUsR0FBRyxJQUFJLENBQUMsRUFBRSxFQUFFLEVBQUUsQ0FBQyxDQUFDO0lBQ3hCLE1BQU0sQ0FBQyxDQUFDLEVBQUUsS0FBSyxDQUFDLElBQUksRUFBRSxLQUFLLENBQUMsQ0FBQyxJQUFJLENBQUMsRUFBRSxLQUFLLENBQUMsSUFBSSxFQUFFLEtBQUssQ0FBQyxDQUFDLENBQUM7QUFDMUQsQ0FBQyxDQUFBO0FBRUQsSUFBTSxNQUFNLEdBQWEsVUFBQyxFQUFFLEVBQUUsRUFBRSxFQUFFLEVBQUUsRUFBRSxFQUFFO0lBQ3RDLE1BQU0sQ0FBQyxJQUFJLENBQUMsRUFBRSxFQUFFLEVBQUUsQ0FBQyxLQUFLLElBQUksQ0FBQyxFQUFFLEVBQUUsRUFBRSxDQUFDLENBQUM7QUFDdkMsQ0FBQyxDQUFBO0FBRUQsSUFBTSxJQUFJLEdBQWEsVUFBQyxFQUFFLEVBQUUsRUFBRSxFQUFFLEVBQUUsRUFBRSxFQUFFO0lBQ3BDLE1BQU0sQ0FBQyxFQUFFLEtBQUssRUFBRSxJQUFJLEVBQUUsS0FBSyxFQUFFLENBQUM7QUFDaEMsQ0FBQyxDQUFBO0FBRUQsSUFBTSxLQUFLLEdBQWEsVUFBQyxFQUFFLEVBQUUsRUFBRSxFQUFFLEVBQUUsRUFBRSxFQUFFO0lBQ3JDLE1BQU0sQ0FBQyxNQUFNLENBQUMsRUFBRSxFQUFFLEVBQUUsRUFBRSxFQUFFLEVBQUUsRUFBRSxDQUFDLElBQUksSUFBSSxDQUFDLEVBQUUsRUFBRSxFQUFFLEVBQUUsRUFBRSxFQUFFLEVBQUUsQ0FBQyxDQUFDO0FBQ3hELENBQUMsQ0FBQTtBQUVELGNBQWMsS0FBZSxFQUFFLFNBQW1CLEVBQUUsU0FBa0I7SUFDcEUsTUFBTSxDQUFDLFVBQUMsRUFBRSxFQUFFLEVBQUUsRUFBRSxFQUFFLEVBQUUsRUFBRSxJQUFNLE9BQUEsQ0FDMUIsSUFBSSxDQUFDLEVBQUUsRUFBRSxFQUFFLENBQUMsR0FBRyxDQUFDLElBQUksSUFBSSxDQUFDLEVBQUUsRUFBRSxFQUFFLENBQUMsR0FBRyxDQUFDLENBQ3JDLElBQUksQ0FDSCxTQUFTLElBQUksRUFBRSxLQUFLLEVBQUUsSUFBSSxFQUFFLEtBQUssQ0FBQyxLQUFLLEtBQUss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QyxRQUFRLEVBQUUsU0FBUyxDQUFDLENBQUM7SUFDekMsSUFBSSxDQUFjLENBQUM7SUFDbkIsR0FBRyxDQUFDLENBQUMsSUFBSSxDQUFDLElBQUksS0FBSyxDQUFDLENBQUMsQ0FBQztRQUNwQixDQUFDLEdBQUcsZUFBUSxDQUFDLE9BQU8sQ0FBQyxDQUFDO1FBQ3RCLENBQUMsQ0FBQyxXQUFXLEdBQUcsS0FBSyxDQUFDLENBQUMsQ0FBQyxDQUFDO1FBQ3pCLEVBQUUsQ0FBQyxXQUFXLENBQUMsQ0FBQyxDQUFDLENBQUM7SUFDcEIsQ0FBQztJQUNELE1BQU0sQ0FBQyxFQUFFLENBQUM7QUFDWixDQUFDIiwiZmlsZSI6ImdlbmVyYXRlZC5qcyIsInNvdXJjZVJvb3QiOiIiLCJzb3VyY2VzQ29udGVudCI6WyIoZnVuY3Rpb24gZSh0LG4scil7ZnVuY3Rpb24gcyhvLHUpe2lmKCFuW29dKXtpZighdFtvXSl7dmFyIGE9dHlwZW9mIHJlcXVpcmU9PVwiZnVuY3Rpb25cIiYmcmVxdWlyZTtpZighdSYmYSlyZXR1cm4gYShvLCEwKTtpZihpKXJldHVybiBpKG8sITApO3ZhciBmPW5ldyBFcnJvcihcIkNhbm5vdCBmaW5kIG1vZHVsZSAnXCIrbytcIidcIik7dGhyb3cgZi5jb2RlPVwiTU9EVUxFX05PVF9GT1VORFwiLGZ9dmFyIGw9bltvXT17ZXhwb3J0czp7fX07dFtvXVswXS5jYWxsKGwuZXhwb3J0cyxmdW5jdGlvbihlKXt2YXIgbj10W29dWzFdW2VdO3JldHVybiBzKG4/bjplKX0sbCxsLmV4cG9ydHMsZSx0LG4scil9cmV0dXJuIG5bb10uZXhwb3J0c312YXIgaT10eXBlb2YgcmVxdWlyZT09XCJmdW5jdGlvblwiJiZyZXF1aXJlO2Zvcih2YXIgbz0wO288ci5sZW5ndGg7bysrKXMocltvXSk7cmV0dXJuIHN9KSIsImltcG9ydCB7IFN0YXRlIH0gZnJvbSAnLi9zdGF0ZSdcbmltcG9ydCAqIGFzIHV0aWwgZnJvbSAnLi91dGlsJ1xuaW1wb3J0ICogYXMgY2cgZnJvbSAnLi90eXBlcydcblxuZXhwb3J0IHR5cGUgTXV0YXRpb248QT4gPSAoc3RhdGU6IFN0YXRlKSA9PiBBO1xuXG5leHBvcnQgaW50ZXJmYWNlIEFuaW1WZWN0b3Ige1xuICAwOiBjZy5OdW1iZXJQYWlyOyAvLyBhbmltYXRpb24gZ29hbFxuICAxOiBjZy5OdW1iZXJQYWlyOyAvLyBhbmltYXRpb24gY3VycmVudCBzdGF0dXNcbn1cblxuZXhwb3J0IGludGVyZmFjZSBBbmltVmVjdG9ycyB7XG4gIFtrZXk6IHN0cmluZ106IEFuaW1WZWN0b3Jcbn1cblxuZXhwb3J0IGludGVyZmFjZSBBbmltRmFkaW5ncyB7XG4gIFtrZXk6IHN0cmluZ106IGNnLlBpZWNlXG59XG5cbmV4cG9ydCBpbnRlcmZhY2UgQW5pbVBsYW4ge1xuICBhbmltczogQW5pbVZlY3RvcnM7XG4gIGZhZGluZ3M6IEFuaW1GYWRpbmdzO1xufVxuXG5leHBvcnQgaW50ZXJmYWNlIEFuaW1DdXJyZW50IHtcbiAgc3RhcnQ6IGNnLlRpbWVzdGFtcDtcbiAgZHVyYXRpb246IGNnLk1pbGxpc2Vjb25kcztcbiAgcGxhbjogQW5pbVBsYW47XG59XG5cbi8vIHRyYW5zZm9ybWF0aW9uIGlzIGEgZnVuY3Rpb25cbi8vIGFjY2VwdHMgYm9hcmQgc3RhdGUgYW5kIGFueSBudW1iZXIgb2YgYXJndW1lbnRzLFxuLy8gYW5kIG11dGF0ZXMgdGhlIGJvYXJkLlxuZXhwb3J0IGZ1bmN0aW9uIGFuaW08QT4obXV0YXRpb246IE11dGF0aW9uPEE+LCBzdGF0ZTogU3RhdGUpOiBBIHtcbiAgcmV0dXJuIHN0YXRlLmFuaW1hdGlvbi5lbmFibGVkID8gYW5pbWF0ZShtdXRhdGlvbiwgc3RhdGUpIDogcmVuZGVyKG11dGF0aW9uLCBzdGF0ZSk7XG59XG5cbmV4cG9ydCBmdW5jdGlvbiByZW5kZXI8QT4obXV0YXRpb246IE11dGF0aW9uPEE+LCBzdGF0ZTogU3RhdGUpOiBBIHtcbiAgY29uc3QgcmVzdWx0ID0gbXV0YXRpb24oc3RhdGUpO1xuICBzdGF0ZS5kb20ucmVkcmF3KCk7XG4gIHJldHVybiByZXN1bHQ7XG59XG5cbmludGVyZmFjZSBBbmltUGllY2Uge1xuICBrZXk6IGNnLktleTtcbiAgcG9zOiBjZy5Qb3M7XG4gIHBpZWNlOiBjZy5QaWVjZTtcbn1cbmludGVyZmFjZSBBbmltUGllY2VzIHtcbiAgW2tleTogc3RyaW5nXTogQW5pbVBpZWNlXG59XG5cbmZ1bmN0aW9uIG1ha2VQaWVjZShrZXk6IGNnLktleSwgcGllY2U6IGNnLlBpZWNlKTogQW5pbVBpZWNlIHtcbiAgcmV0dXJuIHtcbiAgICBrZXk6IGtleSxcbiAgICBwb3M6IHV0aWwua2V5MnBvcyhrZXkpLFxuICAgIHBpZWNlOiBwaWVjZVxuICB9O1xufVxuXG5mdW5jdGlvbiBjbG9zZXIocGllY2U6IEFuaW1QaWVjZSwgcGllY2VzOiBBbmltUGllY2VbXSk6IEFuaW1QaWVjZSB7XG4gIHJldHVybiBwaWVjZXMuc29ydCgocDEsIHAyKSA9PiB7XG4gICAgcmV0dXJuIHV0aWwuZGlzdGFuY2VTcShwaWVjZS5wb3MsIHAxLnBvcykgLSB1dGlsLmRpc3RhbmNlU3EocGllY2UucG9zLCBwMi5wb3MpO1xuICB9KVswXTtcbn1cblxuZnVuY3Rpb24gY29tcHV0ZVBsYW4ocHJldlBpZWNlczogY2cuUGllY2VzLCBjdXJyZW50OiBTdGF0ZSk6IEFuaW1QbGFuIHtcbiAgY29uc3QgYm91bmRzID0gY3VycmVudC5kb20uYm91bmRzKCksXG4gIHdpZHRoID0gYm91bmRzLndpZHRoIC8gOCxcbiAgaGVpZ2h0ID0gYm91bmRzLmhlaWdodCAvIDgsXG4gIGFuaW1zOiBBbmltVmVjdG9ycyA9IHt9LFxuICBhbmltZWRPcmlnczogY2cuS2V5W10gPSBbXSxcbiAgZmFkaW5nczogQW5pbUZhZGluZ3MgPSB7fSxcbiAgbWlzc2luZ3M6IEFuaW1QaWVjZVtdID0gW10sXG4gIG5ld3M6IEFuaW1QaWVjZVtdID0gW10sXG4gIHByZVBpZWNlczogQW5pbVBpZWNlcyA9IHt9LFxuICB3aGl0ZSA9IGN1cnJlbnQub3JpZW50YXRpb24gPT09ICd3aGl0ZSc7XG4gIGxldCBjdXJQOiBjZy5QaWVjZSwgcHJlUDogQW5pbVBpZWNlLCBpOiBhbnksIG9yaWc6IGNnLlBvcywgZGVzdDogY2cuUG9zLCB2ZWN0b3I6IGNnLk51bWJlclBhaXI7XG4gIGZvciAoaSBpbiBwcmV2UGllY2VzKSB7XG4gICAgcHJlUGllY2VzW2ldID0gbWFrZVBpZWNlKGkgYXMgY2cuS2V5LCBwcmV2UGllY2VzW2ldKTtcbiAgfVxuICBmb3IgKGNvbnN0IGtleSBvZiB1dGlsLmFsbEtleXMpIHtcbiAgICBjdXJQID0gY3VycmVudC5waWVjZXNba2V5XTtcbiAgICBwcmVQID0gcHJlUGllY2VzW2tleV07XG4gICAgaWYgKGN1clApIHtcbiAgICAgIGlmIChwcmVQKSB7XG4gICAgICAgIGlmICghdXRpbC5zYW1lUGllY2UoY3VyUCwgcHJlUC5waWVjZSkpIHtcbiAgICAgICAgICBtaXNzaW5ncy5wdXNoKHByZVApO1xuICAgICAgICAgIG5ld3MucHVzaChtYWtlUGllY2Uoa2V5LCBjdXJQKSk7XG4gICAgICAgIH1cbiAgICAgIH0gZWxzZSBuZXdzLnB1c2gobWFrZVBpZWNlKGtleSwgY3VyUCkpO1xuICAgIH0gZWxzZSBpZiAocHJlUCkgbWlzc2luZ3MucHVzaChwcmVQKTtcbiAgfVxuICBuZXdzLmZvckVhY2gobmV3UCA9PiB7XG4gICAgcHJlUCA9IGNsb3NlcihuZXdQLCBtaXNzaW5ncy5maWx0ZXIocCA9PiB1dGlsLnNhbWVQaWVjZShuZXdQLnBpZWNlLCBwLnBpZWNlKSkpO1xuICAgIGlmIChwcmVQKSB7XG4gICAgICBvcmlnID0gd2hpdGUgPyBwcmVQLnBvcyA6IG5ld1AucG9zO1xuICAgICAgZGVzdCA9IHdoaXRlID8gbmV3UC5wb3MgOiBwcmVQLnBvcztcbiAgICAgIHZlY3RvciA9IFsob3JpZ1swXSAtIGRlc3RbMF0pICogd2lkdGgsIChkZXN0WzFdIC0gb3JpZ1sxXSkgKiBoZWlnaHRdO1xuICAgICAgYW5pbXNbbmV3UC5rZXldID0gW3ZlY3RvciwgdmVjdG9yXTtcbiAgICAgIGFuaW1lZE9yaWdzLnB1c2gocHJlUC5rZXkpO1xuICAgIH1cbiAgfSk7XG4gIG1pc3NpbmdzLmZvckVhY2gocCA9PiB7XG4gICAgaWYgKFxuICAgICAgIXV0aWwuY29udGFpbnNYKGFuaW1lZE9yaWdzLCBwLmtleSkgJiZcbiAgICAgICEoY3VycmVudC5pdGVtcyA/IGN1cnJlbnQuaXRlbXMocC5wb3MsIHAua2V5KSA6IGZhbHNlKVxuICAgIClcbiAgICBmYWRpbmdzW3Aua2V5XSA9IHAucGllY2U7XG4gIH0pO1xuXG4gIHJldHVybiB7XG4gICAgYW5pbXM6IGFuaW1zLFxuICAgIGZhZGluZ3M6IGZhZGluZ3NcbiAgfTtcbn1cblxuZnVuY3Rpb24gc3RlcChzdGF0ZTogU3RhdGUpOiB2b2lkIHtcbiAgY29uc3QgY3VyID0gc3RhdGUuYW5pbWF0aW9uLmN1cnJlbnQ7XG4gIGlmICghY3VyKSB7IC8vIGFuaW1hdGlvbiB3YXMgY2FuY2VsZWQgOihcbiAgICBpZiAoIXN0YXRlLmRvbS5kZXN0cm95ZWQpIHN0YXRlLmRvbS5yZWRyYXdOb3coKTtcbiAgICByZXR1cm47XG4gIH1cbiAgY29uc3QgcmVzdCA9IDEgLSAobmV3IERhdGUoKS5nZXRUaW1lKCkgLSBjdXIuc3RhcnQpIC8gY3VyLmR1cmF0aW9uO1xuICBpZiAocmVzdCA8PSAwKSB7XG4gICAgc3RhdGUuYW5pbWF0aW9uLmN1cnJlbnQgPSB1bmRlZmluZWQ7XG4gICAgc3RhdGUuZG9tLnJlZHJhd05vdygpO1xuICB9IGVsc2Uge1xuICAgIGNvbnN0IGVhc2UgPSBlYXNpbmcocmVzdCk7XG4gICAgZm9yIChsZXQgaSBpbiBjdXIucGxhbi5hbmltcykge1xuICAgICAgY29uc3QgY2ZnID0gY3VyLnBsYW4uYW5pbXNbaV07XG4gICAgICBjZmdbMV0gPSBbcm91bmRCeShjZmdbMF1bMF0gKiBlYXNlLCAxMCksIHJvdW5kQnkoY2ZnWzBdWzFdICogZWFzZSwgMTApXTtcbiAgICB9XG4gICAgc3RhdGUuZG9tLnJlZHJhd05vdyh0cnVlKTsgLy8gb3B0aW1pc2F0aW9uOiBkb24ndCByZW5kZXIgU1ZHIGNoYW5nZXMgZHVyaW5nIGFuaW1hdGlvbnNcbiAgICB1dGlsLnJhZigoKSA9PiBzdGVwKHN0YXRlKSk7XG4gIH1cbn1cblxuZnVuY3Rpb24gYW5pbWF0ZTxBPihtdXRhdGlvbjogTXV0YXRpb248QT4sIHN0YXRlOiBTdGF0ZSk6IEEge1xuICAvLyBjbG9uZSBzdGF0ZSBiZWZvcmUgbXV0YXRpbmcgaXRcbiAgY29uc3QgcHJldlBpZWNlczogY2cuUGllY2VzID0gey4uLnN0YXRlLnBpZWNlc307XG5cbiAgY29uc3QgcmVzdWx0ID0gbXV0YXRpb24oc3RhdGUpO1xuICBjb25zdCBwbGFuID0gY29tcHV0ZVBsYW4ocHJldlBpZWNlcywgc3RhdGUpO1xuICBpZiAoIWlzT2JqZWN0RW1wdHkocGxhbi5hbmltcykgfHwgIWlzT2JqZWN0RW1wdHkocGxhbi5mYWRpbmdzKSkge1xuICAgIGNvbnN0IGFscmVhZHlSdW5uaW5nID0gc3RhdGUuYW5pbWF0aW9uLmN1cnJlbnQgJiYgc3RhdGUuYW5pbWF0aW9uLmN1cnJlbnQuc3RhcnQ7XG4gICAgc3RhdGUuYW5pbWF0aW9uLmN1cnJlbnQgPSB7XG4gICAgICBzdGFydDogbmV3IERhdGUoKS5nZXRUaW1lKCksXG4gICAgICBkdXJhdGlvbjogc3RhdGUuYW5pbWF0aW9uLmR1cmF0aW9uLFxuICAgICAgcGxhbjogcGxhblxuICAgIH07XG4gICAgaWYgKCFhbHJlYWR5UnVubmluZykgc3RlcChzdGF0ZSk7XG4gIH0gZWxzZSB7XG4gICAgLy8gZG9uJ3QgYW5pbWF0ZSwganVzdCByZW5kZXIgcmlnaHQgYXdheVxuICAgIHN0YXRlLmRvbS5yZWRyYXcoKTtcbiAgfVxuICByZXR1cm4gcmVzdWx0O1xufVxuXG5mdW5jdGlvbiBpc09iamVjdEVtcHR5KG86IGFueSk6IGJvb2xlYW4ge1xuICBmb3IgKGxldCBfIGluIG8pIHJldHVybiBmYWxzZTtcbiAgcmV0dXJuIHRydWU7XG59XG4vLyBodHRwczovL2dpc3QuZ2l0aHViLmNvbS9ncmUvMTY1MDI5NFxuZnVuY3Rpb24gZWFzaW5nKHQ6IG51bWJlcik6IG51bWJlciB7XG4gIHJldHVybiB0IDwgMC41ID8gNCAqIHQgKiB0ICogdCA6ICh0IC0gMSkgKiAoMiAqIHQgLSAyKSAqICgyICogdCAtIDIpICsgMTtcbn1cbmZ1bmN0aW9uIHJvdW5kQnkobjogbnVtYmVyLCBieTogbnVtYmVyKTogbnVtYmVyIHtcbiAgcmV0dXJuIE1hdGgucm91bmQobiAqIGJ5KSAvIGJ5O1xufVxuIiwiaW1wb3J0IHsgU3RhdGUgfSBmcm9tICcuL3N0YXRlJ1xuaW1wb3J0ICogYXMgYm9hcmQgZnJvbSAnLi9ib2FyZCdcbmltcG9ydCB7IHdyaXRlIGFzIGZlbldyaXRlIH0gZnJvbSAnLi9mZW4nXG5pbXBvcnQgeyBDb25maWcsIGNvbmZpZ3VyZSB9IGZyb20gJy4vY29uZmlnJ1xuaW1wb3J0IHsgYW5pbSwgcmVuZGVyIH0gZnJvbSAnLi9hbmltJ1xuaW1wb3J0IHsgY2FuY2VsIGFzIGRyYWdDYW5jZWwsIGRyYWdOZXdQaWVjZSB9IGZyb20gJy4vZHJhZydcbmltcG9ydCB7IERyYXdTaGFwZSB9IGZyb20gJy4vZHJhdydcbmltcG9ydCBleHBsb3Npb24gZnJvbSAnLi9leHBsb3Npb24nXG5pbXBvcnQgKiBhcyBjZyBmcm9tICcuL3R5cGVzJ1xuXG5leHBvcnQgaW50ZXJmYWNlIEFwaSB7XG5cbiAgLy8gcmVjb25maWd1cmUgdGhlIGluc3RhbmNlLiBBY2NlcHRzIGFsbCBjb25maWcgb3B0aW9ucywgZXhjZXB0IGZvciB2aWV3T25seSAmIG1pbmltYWxEb20uXG4gIC8vIGJvYXJkIHdpbGwgYmUgYW5pbWF0ZWQgYWNjb3JkaW5nbHksIGlmIGFuaW1hdGlvbnMgYXJlIGVuYWJsZWQuXG4gIHNldChjb25maWc6IENvbmZpZyk6IHZvaWQ7XG5cbiAgLy8gcmVhZCBjaGVzc2dyb3VuZCBzdGF0ZTsgd3JpdGUgYXQgeW91ciBvd24gcmlza3MuXG4gIHN0YXRlOiBTdGF0ZTtcblxuICAvLyBnZXQgdGhlIHBvc2l0aW9uIGFzIGEgRkVOIHN0cmluZyAob25seSBjb250YWlucyBwaWVjZXMsIG5vIGZsYWdzKVxuICAvLyBlLmcuIHJuYnFrYm5yL3BwcHBwcHBwLzgvOC84LzgvUFBQUFBQUFAvUk5CUUtCTlJcbiAgZ2V0RmVuKCk6IGNnLkZFTjtcblxuICAvLyBjaGFuZ2UgdGhlIHZpZXcgYW5nbGVcbiAgdG9nZ2xlT3JpZW50YXRpb24oKTogdm9pZDtcblxuICAvLyBwZXJmb3JtIGEgbW92ZSBwcm9ncmFtbWF0aWNhbGx5XG4gIG1vdmUob3JpZzogY2cuS2V5LCBkZXN0OiBjZy5LZXkpOiB2b2lkO1xuXG4gIC8vIGFkZCBhbmQvb3IgcmVtb3ZlIGFyYml0cmFyeSBwaWVjZXMgb24gdGhlIGJvYXJkXG4gIHNldFBpZWNlcyhwaWVjZXM6IGNnLlBpZWNlc0RpZmYpOiB2b2lkO1xuXG4gIC8vIGNsaWNrIGEgc3F1YXJlIHByb2dyYW1tYXRpY2FsbHlcbiAgc2VsZWN0U3F1YXJlKGtleTogY2cuS2V5LCBmb3JjZT86IGJvb2xlYW4pOiB2b2lkO1xuXG4gIC8vIHB1dCBhIG5ldyBwaWVjZSBvbiB0aGUgYm9hcmRcbiAgbmV3UGllY2UocGllY2U6IGNnLlBpZWNlLCBrZXk6IGNnLktleSk6IHZvaWQ7XG5cbiAgLy8gcGxheSB0aGUgY3VycmVudCBwcmVtb3ZlLCBpZiBhbnk7IHJldHVybnMgdHJ1ZSBpZiBwcmVtb3ZlIHdhcyBwbGF5ZWRcbiAgcGxheVByZW1vdmUoKTogYm9vbGVhbjtcblxuICAvLyBjYW5jZWwgdGhlIGN1cnJlbnQgcHJlbW92ZSwgaWYgYW55XG4gIGNhbmNlbFByZW1vdmUoKTogdm9pZDtcblxuICAvLyBwbGF5IHRoZSBjdXJyZW50IHByZWRyb3AsIGlmIGFueTsgcmV0dXJucyB0cnVlIGlmIHByZW1vdmUgd2FzIHBsYXllZFxuICBwbGF5UHJlZHJvcCh2YWxpZGF0ZTogKGRyb3A6IGNnLkRyb3ApID0+IGJvb2xlYW4pOiBib29sZWFuO1xuXG4gIC8vIGNhbmNlbCB0aGUgY3VycmVudCBwcmVkcm9wLCBpZiBhbnlcbiAgY2FuY2VsUHJlZHJvcCgpOiB2b2lkO1xuXG4gIC8vIGNhbmNlbCB0aGUgY3VycmVudCBtb3ZlIGJlaW5nIG1hZGVcbiAgY2FuY2VsTW92ZSgpOiB2b2lkO1xuXG4gIC8vIGNhbmNlbCBjdXJyZW50IG1vdmUgYW5kIHByZXZlbnQgZnVydGhlciBvbmVzXG4gIHN0b3AoKTogdm9pZDtcblxuICAvLyBtYWtlIHNxdWFyZXMgZXhwbG9kZSAoYXRvbWljIGNoZXNzKVxuICBleHBsb2RlKGtleXM6IGNnLktleVtdKTogdm9pZDtcblxuICAvLyBwcm9ncmFtbWF0aWNhbGx5IGRyYXcgdXNlciBzaGFwZXNcbiAgc2V0U2hhcGVzKHNoYXBlczogRHJhd1NoYXBlW10pOiB2b2lkO1xuXG4gIC8vIHByb2dyYW1tYXRpY2FsbHkgZHJhdyBhdXRvIHNoYXBlc1xuICBzZXRBdXRvU2hhcGVzKHNoYXBlczogRHJhd1NoYXBlW10pOiB2b2lkO1xuXG4gIC8vIHNxdWFyZSBuYW1lIGF0IHRoaXMgRE9NIHBvc2l0aW9uIChsaWtlIFwiZTRcIilcbiAgZ2V0S2V5QXREb21Qb3MocG9zOiBjZy5OdW1iZXJQYWlyKTogY2cuS2V5IHwgdW5kZWZpbmVkO1xuXG4gIC8vIG9ubHkgdXNlZnVsIHdoZW4gQ1NTIGNoYW5nZXMgdGhlIGJvYXJkIHdpZHRoL2hlaWdodCByYXRpbyAoZm9yIDNEKVxuICByZWRyYXdBbGw6IGNnLlJlZHJhdztcblxuICAvLyBmb3IgY3Jhenlob3VzZSBhbmQgYm9hcmQgZWRpdG9yc1xuICBkcmFnTmV3UGllY2UocGllY2U6IGNnLlBpZWNlLCBldmVudDogY2cuTW91Y2hFdmVudCwgZm9yY2U/OiBib29sZWFuKTogdm9pZDtcblxuICAvLyB1bmJpbmRzIGFsbCBldmVudHNcbiAgLy8gKGltcG9ydGFudCBmb3IgZG9jdW1lbnQtd2lkZSBldmVudHMgbGlrZSBzY3JvbGwgYW5kIG1vdXNlbW92ZSlcbiAgZGVzdHJveTogY2cuVW5iaW5kXG59XG5cbi8vIHNlZSBBUEkgdHlwZXMgYW5kIGRvY3VtZW50YXRpb25zIGluIGR0cy9hcGkuZC50c1xuZXhwb3J0IGZ1bmN0aW9uIHN0YXJ0KHN0YXRlOiBTdGF0ZSwgcmVkcmF3QWxsOiBjZy5SZWRyYXcpOiBBcGkge1xuXG4gIGZ1bmN0aW9uIHRvZ2dsZU9yaWVudGF0aW9uKCkge1xuICAgIGJvYXJkLnRvZ2dsZU9yaWVudGF0aW9uKHN0YXRlKTtcbiAgICByZWRyYXdBbGwoKTtcbiAgfTtcblxuICByZXR1cm4ge1xuXG4gICAgc2V0KGNvbmZpZykge1xuICAgICAgaWYgKGNvbmZpZy5vcmllbnRhdGlvbiAmJiBjb25maWcub3JpZW50YXRpb24gIT09IHN0YXRlLm9yaWVudGF0aW9uKSB0b2dnbGVPcmllbnRhdGlvbigpO1xuICAgICAgKGNvbmZpZy5mZW4gPyBhbmltIDogcmVuZGVyKShzdGF0ZSA9PiBjb25maWd1cmUoc3RhdGUsIGNvbmZpZyksIHN0YXRlKTtcbiAgICB9LFxuXG4gICAgc3RhdGUsXG5cbiAgICBnZXRGZW46ICgpID0+IGZlbldyaXRlKHN0YXRlLnBpZWNlcyksXG5cbiAgICB0b2dnbGVPcmllbnRhdGlvbixcblxuICAgIHNldFBpZWNlcyhwaWVjZXMpIHtcbiAgICAgIGFuaW0oc3RhdGUgPT4gYm9hcmQuc2V0UGllY2VzKHN0YXRlLCBwaWVjZXMpLCBzdGF0ZSk7XG4gICAgfSxcblxuICAgIHNlbGVjdFNxdWFyZShrZXksIGZvcmNlKSB7XG4gICAgICBpZiAoa2V5IHx8IHN0YXRlLnNlbGVjdGVkKSBhbmltKHN0YXRlID0+IGJvYXJkLnNlbGVjdFNxdWFyZShzdGF0ZSwga2V5LCBmb3JjZSksIHN0YXRlKTtcbiAgICB9LFxuXG4gICAgbW92ZShvcmlnLCBkZXN0KSB7XG4gICAgICBhbmltKHN0YXRlID0+IGJvYXJkLmJhc2VNb3ZlKHN0YXRlLCBvcmlnLCBkZXN0KSwgc3RhdGUpO1xuICAgIH0sXG5cbiAgICBuZXdQaWVjZShwaWVjZSwga2V5KSB7XG4gICAgICBhbmltKHN0YXRlID0+IGJvYXJkLmJhc2VOZXdQaWVjZShzdGF0ZSwgcGllY2UsIGtleSksIHN0YXRlKTtcbiAgICB9LFxuXG4gICAgcGxheVByZW1vdmUoKSB7XG4gICAgICBpZiAoc3RhdGUucHJlbW92YWJsZS5jdXJyZW50KSB7XG4gICAgICAgIGlmIChhbmltKGJvYXJkLnBsYXlQcmVtb3ZlLCBzdGF0ZSkpIHJldHVybiB0cnVlO1xuICAgICAgICAvLyBpZiB0aGUgcHJlbW92ZSBjb3VsZG4ndCBiZSBwbGF5ZWQsIHJlZHJhdyB0byBjbGVhciBpdCB1cFxuICAgICAgICBzdGF0ZS5kb20ucmVkcmF3KCk7XG4gICAgICB9XG4gICAgICByZXR1cm4gZmFsc2U7XG4gICAgfSxcblxuICAgIHBsYXlQcmVkcm9wKHZhbGlkYXRlKSB7XG4gICAgICBpZiAoc3RhdGUucHJlZHJvcHBhYmxlLmN1cnJlbnQpIHtcbiAgICAgICAgY29uc3QgcmVzdWx0ID0gYm9hcmQucGxheVByZWRyb3Aoc3RhdGUsIHZhbGlkYXRlKTtcbiAgICAgICAgc3RhdGUuZG9tLnJlZHJhdygpO1xuICAgICAgICByZXR1cm4gcmVzdWx0O1xuICAgICAgfVxuICAgICAgcmV0dXJuIGZhbHNlO1xuICAgIH0sXG5cbiAgICBjYW5jZWxQcmVtb3ZlKCkge1xuICAgICAgcmVuZGVyKGJvYXJkLnVuc2V0UHJlbW92ZSwgc3RhdGUpO1xuICAgIH0sXG5cbiAgICBjYW5jZWxQcmVkcm9wKCkge1xuICAgICAgcmVuZGVyKGJvYXJkLnVuc2V0UHJlZHJvcCwgc3RhdGUpO1xuICAgIH0sXG5cbiAgICBjYW5jZWxNb3ZlKCkge1xuICAgICAgcmVuZGVyKHN0YXRlID0+IHsgYm9hcmQuY2FuY2VsTW92ZShzdGF0ZSk7IGRyYWdDYW5jZWwoc3RhdGUpOyB9LCBzdGF0ZSk7XG4gICAgfSxcblxuICAgIHN0b3AoKSB7XG4gICAgICByZW5kZXIoc3RhdGUgPT4geyBib2FyZC5zdG9wKHN0YXRlKTsgZHJhZ0NhbmNlbChzdGF0ZSk7IH0sIHN0YXRlKTtcbiAgICB9LFxuXG4gICAgZXhwbG9kZShrZXlzOiBjZy5LZXlbXSkge1xuICAgICAgZXhwbG9zaW9uKHN0YXRlLCBrZXlzKTtcbiAgICB9LFxuXG4gICAgc2V0QXV0b1NoYXBlcyhzaGFwZXM6IERyYXdTaGFwZVtdKSB7XG4gICAgICByZW5kZXIoc3RhdGUgPT4gc3RhdGUuZHJhd2FibGUuYXV0b1NoYXBlcyA9IHNoYXBlcywgc3RhdGUpO1xuICAgIH0sXG5cbiAgICBzZXRTaGFwZXMoc2hhcGVzOiBEcmF3U2hhcGVbXSkge1xuICAgICAgcmVuZGVyKHN0YXRlID0+IHN0YXRlLmRyYXdhYmxlLnNoYXBlcyA9IHNoYXBlcywgc3RhdGUpO1xuICAgIH0sXG5cbiAgICBnZXRLZXlBdERvbVBvcyhwb3MpIHtcbiAgICAgIHJldHVybiBib2FyZC5nZXRLZXlBdERvbVBvcyhwb3MsIHN0YXRlLm9yaWVudGF0aW9uID09PSAnd2hpdGUnLCBzdGF0ZS5kb20uYm91bmRzKCkpO1xuICAgIH0sXG5cbiAgICByZWRyYXdBbGwsXG5cbiAgICBkcmFnTmV3UGllY2UocGllY2UsIGV2ZW50LCBmb3JjZSkge1xuICAgICAgZHJhZ05ld1BpZWNlKHN0YXRlLCBwaWVjZSwgZXZlbnQsIGZvcmNlKVxuICAgIH0sXG5cbiAgICBkZXN0cm95KCkge1xuICAgICAgYm9hcmQuc3RvcChzdGF0ZSk7XG4gICAgICBzdGF0ZS5kb20udW5iaW5kICYmIHN0YXRlLmRvbS51bmJpbmQoKTtcbiAgICAgIHN0YXRlLmRvbS5kZXN0cm95ZWQgPSB0cnVlO1xuICAgIH1cbiAgfTtcbn1cbiIsImltcG9ydCB7IFN0YXRlIH0gZnJvbSAnLi9zdGF0ZSdcbmltcG9ydCB7IHBvczJrZXksIGtleTJwb3MsIG9wcG9zaXRlLCBjb250YWluc1ggfSBmcm9tICcuL3V0aWwnXG5pbXBvcnQgcHJlbW92ZSBmcm9tICcuL3ByZW1vdmUnXG5pbXBvcnQgKiBhcyBjZyBmcm9tICcuL3R5cGVzJ1xuXG5leHBvcnQgdHlwZSBDYWxsYmFjayA9ICguLi5hcmdzOiBhbnlbXSkgPT4gdm9pZDtcblxuZXhwb3J0IGZ1bmN0aW9uIGNhbGxVc2VyRnVuY3Rpb24oZjogQ2FsbGJhY2sgfCB1bmRlZmluZWQsIC4uLmFyZ3M6IGFueVtdKTogdm9pZCB7XG4gIGlmIChmKSBzZXRUaW1lb3V0KCgpID0+IGYoLi4uYXJncyksIDEpO1xufVxuXG5leHBvcnQgZnVuY3Rpb24gdG9nZ2xlT3JpZW50YXRpb24oc3RhdGU6IFN0YXRlKTogdm9pZCB7XG4gIHN0YXRlLm9yaWVudGF0aW9uID0gb3Bwb3NpdGUoc3RhdGUub3JpZW50YXRpb24pO1xuICBzdGF0ZS5hbmltYXRpb24uY3VycmVudCA9XG4gIHN0YXRlLmRyYWdnYWJsZS5jdXJyZW50ID1cbiAgc3RhdGUuc2VsZWN0ZWQgPSB1bmRlZmluZWQ7XG59XG5cbmV4cG9ydCBmdW5jdGlvbiByZXNldChzdGF0ZTogU3RhdGUpOiB2b2lkIHtcbiAgc3RhdGUubGFzdE1vdmUgPSB1bmRlZmluZWQ7XG4gIHVuc2VsZWN0KHN0YXRlKTtcbiAgdW5zZXRQcmVtb3ZlKHN0YXRlKTtcbiAgdW5zZXRQcmVkcm9wKHN0YXRlKTtcbn1cblxuZXhwb3J0IGZ1bmN0aW9uIHNldFBpZWNlcyhzdGF0ZTogU3RhdGUsIHBpZWNlczogY2cuUGllY2VzRGlmZik6IHZvaWQge1xuICBmb3IgKGxldCBrZXkgaW4gcGllY2VzKSB7XG4gICAgY29uc3QgcGllY2UgPSBwaWVjZXNba2V5XTtcbiAgICBpZiAocGllY2UpIHN0YXRlLnBpZWNlc1trZXldID0gcGllY2U7XG4gICAgZWxzZSBkZWxldGUgc3RhdGUucGllY2VzW2tleV07XG4gIH1cbn1cblxuZXhwb3J0IGZ1bmN0aW9uIHNldENoZWNrKHN0YXRlOiBTdGF0ZSwgY29sb3I6IGNnLkNvbG9yIHwgYm9vbGVhbik6IHZvaWQge1xuICBpZiAoY29sb3IgPT09IHRydWUpIGNvbG9yID0gc3RhdGUudHVybkNvbG9yO1xuICBpZiAoIWNvbG9yKSBzdGF0ZS5jaGVjayA9IHVuZGVmaW5lZDtcbiAgZWxzZSBmb3IgKGxldCBrIGluIHN0YXRlLnBpZWNlcykge1xuICAgIGlmIChzdGF0ZS5waWVjZXNba10ucm9sZSA9PT0gJ2tpbmcnICYmIHN0YXRlLnBpZWNlc1trXS5jb2xvciA9PT0gY29sb3IpIHtcbiAgICAgIHN0YXRlLmNoZWNrID0gayBhcyBjZy5LZXk7XG4gICAgfVxuICB9XG59XG5cbmZ1bmN0aW9uIHNldFByZW1vdmUoc3RhdGU6IFN0YXRlLCBvcmlnOiBjZy5LZXksIGRlc3Q6IGNnLktleSwgbWV0YTogY2cuU2V0UHJlbW92ZU1ldGFkYXRhKTogdm9pZCB7XG4gIHVuc2V0UHJlZHJvcChzdGF0ZSk7XG4gIHN0YXRlLnByZW1vdmFibGUuY3VycmVudCA9IFtvcmlnLCBkZXN0XTtcbiAgY2FsbFVzZXJGdW5jdGlvbihzdGF0ZS5wcmVtb3ZhYmxlLmV2ZW50cy5zZXQsIG9yaWcsIGRlc3QsIG1ldGEpO1xufVxuXG5leHBvcnQgZnVuY3Rpb24gdW5zZXRQcmVtb3ZlKHN0YXRlOiBTdGF0ZSk6IHZvaWQge1xuICBpZiAoc3RhdGUucHJlbW92YWJsZS5jdXJyZW50KSB7XG4gICAgc3RhdGUucHJlbW92YWJsZS5jdXJyZW50ID0gdW5kZWZpbmVkO1xuICAgIGNhbGxVc2VyRnVuY3Rpb24oc3RhdGUucHJlbW92YWJsZS5ldmVudHMudW5zZXQpO1xuICB9XG59XG5cbmZ1bmN0aW9uIHNldFByZWRyb3Aoc3RhdGU6IFN0YXRlLCByb2xlOiBjZy5Sb2xlLCBrZXk6IGNnLktleSk6IHZvaWQge1xuICB1bnNldFByZW1vdmUoc3RhdGUpO1xuICBzdGF0ZS5wcmVkcm9wcGFibGUuY3VycmVudCA9IHtcbiAgICByb2xlOiByb2xlLFxuICAgIGtleToga2V5XG4gIH07XG4gIGNhbGxVc2VyRnVuY3Rpb24oc3RhdGUucHJlZHJvcHBhYmxlLmV2ZW50cy5zZXQsIHJvbGUsIGtleSk7XG59XG5cbmV4cG9ydCBmdW5jdGlvbiB1bnNldFByZWRyb3Aoc3RhdGU6IFN0YXRlKTogdm9pZCB7XG4gIGNvbnN0IHBkID0gc3RhdGUucHJlZHJvcHBhYmxlO1xuICBpZiAocGQuY3VycmVudCkge1xuICAgIHBkLmN1cnJlbnQgPSB1bmRlZmluZWQ7XG4gICAgY2FsbFVzZXJGdW5jdGlvbihwZC5ldmVudHMudW5zZXQpO1xuICB9XG59XG5cbmZ1bmN0aW9uIHRyeUF1dG9DYXN0bGUoc3RhdGU6IFN0YXRlLCBvcmlnOiBjZy5LZXksIGRlc3Q6IGNnLktleSk6IGJvb2xlYW4ge1xuICBpZiAoIXN0YXRlLmF1dG9DYXN0bGUpIHJldHVybiBmYWxzZTtcbiAgY29uc3Qga2luZyA9IHN0YXRlLnBpZWNlc1tvcmlnXTtcbiAgaWYgKGtpbmcucm9sZSAhPT0gJ2tpbmcnKSByZXR1cm4gZmFsc2U7XG4gIGNvbnN0IG9yaWdQb3MgPSBrZXkycG9zKG9yaWcpO1xuICBpZiAob3JpZ1Bvc1swXSAhPT0gNSkgcmV0dXJuIGZhbHNlO1xuICBpZiAob3JpZ1Bvc1sxXSAhPT0gMSAmJiBvcmlnUG9zWzFdICE9PSA4KSByZXR1cm4gZmFsc2U7XG4gIGNvbnN0IGRlc3RQb3MgPSBrZXkycG9zKGRlc3QpO1xuICBsZXQgb2xkUm9va1BvcywgbmV3Um9va1BvcywgbmV3S2luZ1BvcztcbiAgaWYgKGRlc3RQb3NbMF0gPT09IDcgfHwgZGVzdFBvc1swXSA9PT0gOCkge1xuICAgIG9sZFJvb2tQb3MgPSBwb3Mya2V5KFs4LCBvcmlnUG9zWzFdXSk7XG4gICAgbmV3Um9va1BvcyA9IHBvczJrZXkoWzYsIG9yaWdQb3NbMV1dKTtcbiAgICBuZXdLaW5nUG9zID0gcG9zMmtleShbNywgb3JpZ1Bvc1sxXV0pO1xuICB9IGVsc2UgaWYgKGRlc3RQb3NbMF0gPT09IDMgfHwgZGVzdFBvc1swXSA9PT0gMSkge1xuICAgIG9sZFJvb2tQb3MgPSBwb3Mya2V5KFsxLCBvcmlnUG9zWzFdXSk7XG4gICAgbmV3Um9va1BvcyA9IHBvczJrZXkoWzQsIG9yaWdQb3NbMV1dKTtcbiAgICBuZXdLaW5nUG9zID0gcG9zMmtleShbMywgb3JpZ1Bvc1sxXV0pO1xuICB9IGVsc2UgcmV0dXJuIGZhbHNlO1xuXG4gIGNvbnN0IHJvb2sgPSBzdGF0ZS5waWVjZXNbb2xkUm9va1Bvc107XG4gIGlmIChyb29rLnJvbGUgIT09ICdyb29rJykgcmV0dXJuIGZhbHNlO1xuXG4gIGRlbGV0ZSBzdGF0ZS5waWVjZXNbb3JpZ107XG4gIGRlbGV0ZSBzdGF0ZS5waWVjZXNbb2xkUm9va1Bvc107XG5cbiAgc3RhdGUucGllY2VzW25ld0tpbmdQb3NdID0ga2luZ1xuICBzdGF0ZS5waWVjZXNbbmV3Um9va1Bvc10gPSByb29rO1xuICByZXR1cm4gdHJ1ZTtcbn1cblxuZXhwb3J0IGZ1bmN0aW9uIGJhc2VNb3ZlKHN0YXRlOiBTdGF0ZSwgb3JpZzogY2cuS2V5LCBkZXN0OiBjZy5LZXkpOiBjZy5QaWVjZSB8IGJvb2xlYW4ge1xuICBpZiAob3JpZyA9PT0gZGVzdCB8fCAhc3RhdGUucGllY2VzW29yaWddKSByZXR1cm4gZmFsc2U7XG4gIGNvbnN0IGNhcHR1cmVkOiBjZy5QaWVjZSB8IHVuZGVmaW5lZCA9IChcbiAgICBzdGF0ZS5waWVjZXNbZGVzdF0gJiZcbiAgICBzdGF0ZS5waWVjZXNbZGVzdF0uY29sb3IgIT09IHN0YXRlLnBpZWNlc1tvcmlnXS5jb2xvclxuICApID8gc3RhdGUucGllY2VzW2Rlc3RdIDogdW5kZWZpbmVkO1xuICBpZiAoZGVzdCA9PSBzdGF0ZS5zZWxlY3RlZCkgdW5zZWxlY3Qoc3RhdGUpO1xuICBjYWxsVXNlckZ1bmN0aW9uKHN0YXRlLmV2ZW50cy5tb3ZlLCBvcmlnLCBkZXN0LCBjYXB0dXJlZCk7XG4gIGlmICghdHJ5QXV0b0Nhc3RsZShzdGF0ZSwgb3JpZywgZGVzdCkpIHtcbiAgICBzdGF0ZS5waWVjZXNbZGVzdF0gPSBzdGF0ZS5waWVjZXNbb3JpZ107XG4gICAgZGVsZXRlIHN0YXRlLnBpZWNlc1tvcmlnXTtcbiAgfVxuICBzdGF0ZS5sYXN0TW92ZSA9IFtvcmlnLCBkZXN0XTtcbiAgc3RhdGUuY2hlY2sgPSB1bmRlZmluZWQ7XG4gIGNhbGxVc2VyRnVuY3Rpb24oc3RhdGUuZXZlbnRzLmNoYW5nZSk7XG4gIHJldHVybiBjYXB0dXJlZCB8fCB0cnVlO1xufVxuXG5leHBvcnQgZnVuY3Rpb24gYmFzZU5ld1BpZWNlKHN0YXRlOiBTdGF0ZSwgcGllY2U6IGNnLlBpZWNlLCBrZXk6IGNnLktleSwgZm9yY2U/OiBib29sZWFuKTogYm9vbGVhbiB7XG4gIGlmIChzdGF0ZS5waWVjZXNba2V5XSkge1xuICAgIGlmIChmb3JjZSkgZGVsZXRlIHN0YXRlLnBpZWNlc1trZXldO1xuICAgIGVsc2UgcmV0dXJuIGZhbHNlO1xuICB9XG4gIGNhbGxVc2VyRnVuY3Rpb24oc3RhdGUuZXZlbnRzLmRyb3BOZXdQaWVjZSwgcGllY2UsIGtleSk7XG4gIHN0YXRlLnBpZWNlc1trZXldID0gcGllY2U7XG4gIHN0YXRlLmxhc3RNb3ZlID0gW2tleV07XG4gIHN0YXRlLmNoZWNrID0gdW5kZWZpbmVkO1xuICBjYWxsVXNlckZ1bmN0aW9uKHN0YXRlLmV2ZW50cy5jaGFuZ2UpO1xuICBzdGF0ZS5tb3ZhYmxlLmRlc3RzID0gdW5kZWZpbmVkO1xuICBzdGF0ZS50dXJuQ29sb3IgPSBvcHBvc2l0ZShzdGF0ZS50dXJuQ29sb3IpO1xuICByZXR1cm4gdHJ1ZTtcbn1cblxuZnVuY3Rpb24gYmFzZVVzZXJNb3ZlKHN0YXRlOiBTdGF0ZSwgb3JpZzogY2cuS2V5LCBkZXN0OiBjZy5LZXkpOiBjZy5QaWVjZSB8IGJvb2xlYW4ge1xuICBjb25zdCByZXN1bHQgPSBiYXNlTW92ZShzdGF0ZSwgb3JpZywgZGVzdCk7XG4gIGlmIChyZXN1bHQpIHtcbiAgICBzdGF0ZS5tb3ZhYmxlLmRlc3RzID0gdW5kZWZpbmVkO1xuICAgIHN0YXRlLnR1cm5Db2xvciA9IG9wcG9zaXRlKHN0YXRlLnR1cm5Db2xvcik7XG4gICAgc3RhdGUuYW5pbWF0aW9uLmN1cnJlbnQgPSB1bmRlZmluZWQ7XG4gIH1cbiAgcmV0dXJuIHJlc3VsdDtcbn1cblxuZXhwb3J0IGZ1bmN0aW9uIHVzZXJNb3ZlKHN0YXRlOiBTdGF0ZSwgb3JpZzogY2cuS2V5LCBkZXN0OiBjZy5LZXkpOiBib29sZWFuIHtcbiAgaWYgKGNhbk1vdmUoc3RhdGUsIG9yaWcsIGRlc3QpKSB7XG4gICAgY29uc3QgcmVzdWx0ID0gYmFzZVVzZXJNb3ZlKHN0YXRlLCBvcmlnLCBkZXN0KTtcbiAgICBpZiAocmVzdWx0KSB7XG4gICAgICBjb25zdCBob2xkVGltZSA9IHN0YXRlLmhvbGQuc3RvcCgpO1xuICAgICAgdW5zZWxlY3Qoc3RhdGUpO1xuICAgICAgY29uc3QgbWV0YWRhdGE6IGNnLk1vdmVNZXRhZGF0YSA9IHtcbiAgICAgICAgcHJlbW92ZTogZmFsc2UsXG4gICAgICAgIGN0cmxLZXk6IHN0YXRlLnN0YXRzLmN0cmxLZXksXG4gICAgICAgIGhvbGRUaW1lOiBob2xkVGltZVxuICAgICAgfTtcbiAgICAgIGlmIChyZXN1bHQgIT09IHRydWUpIG1ldGFkYXRhLmNhcHR1cmVkID0gcmVzdWx0O1xuICAgICAgY2FsbFVzZXJGdW5jdGlvbihzdGF0ZS5tb3ZhYmxlLmV2ZW50cy5hZnRlciwgb3JpZywgZGVzdCwgbWV0YWRhdGEpO1xuICAgICAgcmV0dXJuIHRydWU7XG4gICAgfVxuICB9IGVsc2UgaWYgKGNhblByZW1vdmUoc3RhdGUsIG9yaWcsIGRlc3QpKSB7XG4gICAgc2V0UHJlbW92ZShzdGF0ZSwgb3JpZywgZGVzdCwge1xuICAgICAgY3RybEtleTogc3RhdGUuc3RhdHMuY3RybEtleVxuICAgIH0pO1xuICAgIHVuc2VsZWN0KHN0YXRlKTtcbiAgfSBlbHNlIGlmIChpc01vdmFibGUoc3RhdGUsIGRlc3QpIHx8IGlzUHJlbW92YWJsZShzdGF0ZSwgZGVzdCkpIHtcbiAgICBzZXRTZWxlY3RlZChzdGF0ZSwgZGVzdCk7XG4gICAgc3RhdGUuaG9sZC5zdGFydCgpO1xuICB9IGVsc2UgdW5zZWxlY3Qoc3RhdGUpO1xuICByZXR1cm4gZmFsc2U7XG59XG5cbmV4cG9ydCBmdW5jdGlvbiBkcm9wTmV3UGllY2Uoc3RhdGU6IFN0YXRlLCBvcmlnOiBjZy5LZXksIGRlc3Q6IGNnLktleSwgZm9yY2U/OiBib29sZWFuKTogdm9pZCB7XG4gIGlmIChjYW5Ecm9wKHN0YXRlLCBvcmlnLCBkZXN0KSB8fCBmb3JjZSkge1xuICAgIGNvbnN0IHBpZWNlID0gc3RhdGUucGllY2VzW29yaWddO1xuICAgIGRlbGV0ZSBzdGF0ZS5waWVjZXNbb3JpZ107XG4gICAgYmFzZU5ld1BpZWNlKHN0YXRlLCBwaWVjZSwgZGVzdCwgZm9yY2UpO1xuICAgIGNhbGxVc2VyRnVuY3Rpb24oc3RhdGUubW92YWJsZS5ldmVudHMuYWZ0ZXJOZXdQaWVjZSwgcGllY2Uucm9sZSwgZGVzdCwge1xuICAgICAgcHJlZHJvcDogZmFsc2VcbiAgICB9KTtcbiAgfSBlbHNlIGlmIChjYW5QcmVkcm9wKHN0YXRlLCBvcmlnLCBkZXN0KSkge1xuICAgIHNldFByZWRyb3Aoc3RhdGUsIHN0YXRlLnBpZWNlc1tvcmlnXS5yb2xlLCBkZXN0KTtcbiAgfSBlbHNlIHtcbiAgICB1bnNldFByZW1vdmUoc3RhdGUpO1xuICAgIHVuc2V0UHJlZHJvcChzdGF0ZSk7XG4gIH1cbiAgZGVsZXRlIHN0YXRlLnBpZWNlc1tvcmlnXTtcbiAgdW5zZWxlY3Qoc3RhdGUpO1xufVxuXG5leHBvcnQgZnVuY3Rpb24gc2VsZWN0U3F1YXJlKHN0YXRlOiBTdGF0ZSwga2V5OiBjZy5LZXksIGZvcmNlPzogYm9vbGVhbik6IHZvaWQge1xuICBpZiAoc3RhdGUuc2VsZWN0ZWQpIHtcbiAgICBpZiAoc3RhdGUuc2VsZWN0ZWQgPT09IGtleSAmJiAhc3RhdGUuZHJhZ2dhYmxlLmVuYWJsZWQpIHtcbiAgICAgIHVuc2VsZWN0KHN0YXRlKTtcbiAgICAgIHN0YXRlLmhvbGQuY2FuY2VsKCk7XG4gICAgfSBlbHNlIGlmICgoc3RhdGUuc2VsZWN0YWJsZS5lbmFibGVkIHx8IGZvcmNlKSAmJiBzdGF0ZS5zZWxlY3RlZCAhPT0ga2V5KSB7XG4gICAgICBpZiAodXNlck1vdmUoc3RhdGUsIHN0YXRlLnNlbGVjdGVkLCBrZXkpKSBzdGF0ZS5zdGF0cy5kcmFnZ2VkID0gZmFsc2U7XG4gICAgfSBlbHNlIHN0YXRlLmhvbGQuc3RhcnQoKTtcbiAgfSBlbHNlIGlmIChpc01vdmFibGUoc3RhdGUsIGtleSkgfHwgaXNQcmVtb3ZhYmxlKHN0YXRlLCBrZXkpKSB7XG4gICAgc2V0U2VsZWN0ZWQoc3RhdGUsIGtleSk7XG4gICAgc3RhdGUuaG9sZC5zdGFydCgpO1xuICB9XG4gIGlmIChrZXkpIGNhbGxVc2VyRnVuY3Rpb24oc3RhdGUuZXZlbnRzLnNlbGVjdCwga2V5KTtcbn1cblxuZXhwb3J0IGZ1bmN0aW9uIHNldFNlbGVjdGVkKHN0YXRlOiBTdGF0ZSwga2V5OiBjZy5LZXkpOiB2b2lkIHtcbiAgc3RhdGUuc2VsZWN0ZWQgPSBrZXk7XG4gIGlmIChpc1ByZW1vdmFibGUoc3RhdGUsIGtleSkpIHtcbiAgICBzdGF0ZS5wcmVtb3ZhYmxlLmRlc3RzID0gcHJlbW92ZShzdGF0ZS5waWVjZXMsIGtleSwgc3RhdGUucHJlbW92YWJsZS5jYXN0bGUpO1xuICB9XG4gIGVsc2Ugc3RhdGUucHJlbW92YWJsZS5kZXN0cyA9IHVuZGVmaW5lZDtcbn1cblxuZXhwb3J0IGZ1bmN0aW9uIHVuc2VsZWN0KHN0YXRlOiBTdGF0ZSk6IHZvaWQge1xuICBzdGF0ZS5zZWxlY3RlZCA9IHVuZGVmaW5lZDtcbiAgc3RhdGUucHJlbW92YWJsZS5kZXN0cyA9IHVuZGVmaW5lZDtcbiAgc3RhdGUuaG9sZC5jYW5jZWwoKTtcbn1cblxuZnVuY3Rpb24gaXNNb3ZhYmxlKHN0YXRlOiBTdGF0ZSwgb3JpZzogY2cuS2V5KTogYm9vbGVhbiB7XG4gIGNvbnN0IHBpZWNlID0gc3RhdGUucGllY2VzW29yaWddO1xuICByZXR1cm4gcGllY2UgJiYgKFxuICAgIHN0YXRlLm1vdmFibGUuY29sb3IgPT09ICdib3RoJyB8fCAoXG4gICAgICBzdGF0ZS5tb3ZhYmxlLmNvbG9yID09PSBwaWVjZS5jb2xvciAmJlxuICAgICAgICBzdGF0ZS50dXJuQ29sb3IgPT09IHBpZWNlLmNvbG9yXG4gICAgKSk7XG59XG5cbmV4cG9ydCBmdW5jdGlvbiBjYW5Nb3ZlKHN0YXRlOiBTdGF0ZSwgb3JpZzogY2cuS2V5LCBkZXN0OiBjZy5LZXkpOiBib29sZWFuIHtcbiAgcmV0dXJuIG9yaWcgIT09IGRlc3QgJiYgaXNNb3ZhYmxlKHN0YXRlLCBvcmlnKSAmJiAoXG4gICAgc3RhdGUubW92YWJsZS5mcmVlIHx8ICghIXN0YXRlLm1vdmFibGUuZGVzdHMgJiYgY29udGFpbnNYKHN0YXRlLm1vdmFibGUuZGVzdHNbb3JpZ10sIGRlc3QpKVxuICApO1xufVxuXG5mdW5jdGlvbiBjYW5Ecm9wKHN0YXRlOiBTdGF0ZSwgb3JpZzogY2cuS2V5LCBkZXN0OiBjZy5LZXkpOiBib29sZWFuIHtcbiAgY29uc3QgcGllY2UgPSBzdGF0ZS5waWVjZXNbb3JpZ107XG4gIHJldHVybiBwaWVjZSAmJiBkZXN0ICYmIChvcmlnID09PSBkZXN0IHx8ICFzdGF0ZS5waWVjZXNbZGVzdF0pICYmIChcbiAgICBzdGF0ZS5tb3ZhYmxlLmNvbG9yID09PSAnYm90aCcgfHwgKFxuICAgICAgc3RhdGUubW92YWJsZS5jb2xvciA9PT0gcGllY2UuY29sb3IgJiZcbiAgICAgICAgc3RhdGUudHVybkNvbG9yID09PSBwaWVjZS5jb2xvclxuICAgICkpO1xufVxuXG5cbmZ1bmN0aW9uIGlzUHJlbW92YWJsZShzdGF0ZTogU3RhdGUsIG9yaWc6IGNnLktleSk6IGJvb2xlYW4ge1xuICBjb25zdCBwaWVjZSA9IHN0YXRlLnBpZWNlc1tvcmlnXTtcbiAgcmV0dXJuIHBpZWNlICYmIHN0YXRlLnByZW1vdmFibGUuZW5hYmxlZCAmJlxuICBzdGF0ZS5tb3ZhYmxlLmNvbG9yID09PSBwaWVjZS5jb2xvciAmJlxuICAgIHN0YXRlLnR1cm5Db2xvciAhPT0gcGllY2UuY29sb3I7XG59XG5cbmZ1bmN0aW9uIGNhblByZW1vdmUoc3RhdGU6IFN0YXRlLCBvcmlnOiBjZy5LZXksIGRlc3Q6IGNnLktleSk6IGJvb2xlYW4ge1xuICByZXR1cm4gb3JpZyAhPT0gZGVzdCAmJlxuICBpc1ByZW1vdmFibGUoc3RhdGUsIG9yaWcpICYmXG4gIGNvbnRhaW5zWChwcmVtb3ZlKHN0YXRlLnBpZWNlcywgb3JpZywgc3RhdGUucHJlbW92YWJsZS5jYXN0bGUpLCBkZXN0KTtcbn1cblxuZnVuY3Rpb24gY2FuUHJlZHJvcChzdGF0ZTogU3RhdGUsIG9yaWc6IGNnLktleSwgZGVzdDogY2cuS2V5KTogYm9vbGVhbiB7XG4gIGNvbnN0IHBpZWNlID0gc3RhdGUucGllY2VzW29yaWddO1xuICByZXR1cm4gcGllY2UgJiYgZGVzdCAmJlxuICAoIXN0YXRlLnBpZWNlc1tkZXN0XSB8fCBzdGF0ZS5waWVjZXNbZGVzdF0uY29sb3IgIT09IHN0YXRlLm1vdmFibGUuY29sb3IpICYmXG4gIHN0YXRlLnByZWRyb3BwYWJsZS5lbmFibGVkICYmXG4gIChwaWVjZS5yb2xlICE9PSAncGF3bicgfHwgKGRlc3RbMV0gIT09ICcxJyAmJiBkZXN0WzFdICE9PSAnOCcpKSAmJlxuICBzdGF0ZS5tb3ZhYmxlLmNvbG9yID09PSBwaWVjZS5jb2xvciAmJlxuICAgIHN0YXRlLnR1cm5Db2xvciAhPT0gcGllY2UuY29sb3I7XG59XG5cbmV4cG9ydCBmdW5jdGlvbiBpc0RyYWdnYWJsZShzdGF0ZTogU3RhdGUsIG9yaWc6IGNnLktleSk6IGJvb2xlYW4ge1xuICBjb25zdCBwaWVjZSA9IHN0YXRlLnBpZWNlc1tvcmlnXTtcbiAgcmV0dXJuIHBpZWNlICYmIHN0YXRlLmRyYWdnYWJsZS5lbmFibGVkICYmIChcbiAgICBzdGF0ZS5tb3ZhYmxlLmNvbG9yID09PSAnYm90aCcgfHwgKFxuICAgICAgc3RhdGUubW92YWJsZS5jb2xvciA9PT0gcGllY2UuY29sb3IgJiYgKFxuICAgICAgICBzdGF0ZS50dXJuQ29sb3IgPT09IHBpZWNlLmNvbG9yIHx8IHN0YXRlLnByZW1vdmFibGUuZW5hYmxlZFxuICAgICAgKVxuICAgIClcbiAgKTtcbn1cblxuZXhwb3J0IGZ1bmN0aW9uIHBsYXlQcmVtb3ZlKHN0YXRlOiBTdGF0ZSk6IGJvb2xlYW4ge1xuICBjb25zdCBtb3ZlID0gc3RhdGUucHJlbW92YWJsZS5jdXJyZW50O1xuICBpZiAoIW1vdmUpIHJldHVybiBmYWxzZTtcbiAgY29uc3Qgb3JpZyA9IG1vdmVbMF0sIGRlc3QgPSBtb3ZlWzFdO1xuICBsZXQgc3VjY2VzcyA9IGZhbHNlO1xuICBpZiAoY2FuTW92ZShzdGF0ZSwgb3JpZywgZGVzdCkpIHtcbiAgICBjb25zdCByZXN1bHQgPSBiYXNlVXNlck1vdmUoc3RhdGUsIG9yaWcsIGRlc3QpO1xuICAgIGlmIChyZXN1bHQpIHtcbiAgICAgIGNvbnN0IG1ldGFkYXRhOiBjZy5Nb3ZlTWV0YWRhdGEgPSB7IHByZW1vdmU6IHRydWUgfTtcbiAgICAgIGlmIChyZXN1bHQgIT09IHRydWUpIG1ldGFkYXRhLmNhcHR1cmVkID0gcmVzdWx0O1xuICAgICAgY2FsbFVzZXJGdW5jdGlvbihzdGF0ZS5tb3ZhYmxlLmV2ZW50cy5hZnRlciwgb3JpZywgZGVzdCwgbWV0YWRhdGEpO1xuICAgICAgc3VjY2VzcyA9IHRydWU7XG4gICAgfVxuICB9XG4gIHVuc2V0UHJlbW92ZShzdGF0ZSk7XG4gIHJldHVybiBzdWNjZXNzO1xufVxuXG5leHBvcnQgZnVuY3Rpb24gcGxheVByZWRyb3Aoc3RhdGU6IFN0YXRlLCB2YWxpZGF0ZTogKGRyb3A6IGNnLkRyb3ApID0+IGJvb2xlYW4pOiBib29sZWFuIHtcbiAgbGV0IGRyb3AgPSBzdGF0ZS5wcmVkcm9wcGFibGUuY3VycmVudCxcbiAgc3VjY2VzcyA9IGZhbHNlO1xuICBpZiAoIWRyb3ApIHJldHVybiBmYWxzZTtcbiAgaWYgKHZhbGlkYXRlKGRyb3ApKSB7XG4gICAgY29uc3QgcGllY2UgPSB7XG4gICAgICByb2xlOiBkcm9wLnJvbGUsXG4gICAgICBjb2xvcjogc3RhdGUubW92YWJsZS5jb2xvclxuICAgIH0gYXMgY2cuUGllY2U7XG4gICAgaWYgKGJhc2VOZXdQaWVjZShzdGF0ZSwgcGllY2UsIGRyb3Aua2V5KSkge1xuICAgICAgY2FsbFVzZXJGdW5jdGlvbihzdGF0ZS5tb3ZhYmxlLmV2ZW50cy5hZnRlck5ld1BpZWNlLCBkcm9wLnJvbGUsIGRyb3Aua2V5LCB7XG4gICAgICAgIHByZWRyb3A6IHRydWVcbiAgICAgIH0pO1xuICAgICAgc3VjY2VzcyA9IHRydWU7XG4gICAgfVxuICB9XG4gIHVuc2V0UHJlZHJvcChzdGF0ZSk7XG4gIHJldHVybiBzdWNjZXNzO1xufVxuXG5leHBvcnQgZnVuY3Rpb24gY2FuY2VsTW92ZShzdGF0ZTogU3RhdGUpOiB2b2lkIHtcbiAgdW5zZXRQcmVtb3ZlKHN0YXRlKTtcbiAgdW5zZXRQcmVkcm9wKHN0YXRlKTtcbiAgdW5zZWxlY3Qoc3RhdGUpO1xufVxuXG5leHBvcnQgZnVuY3Rpb24gc3RvcChzdGF0ZTogU3RhdGUpOiB2b2lkIHtcbiAgc3RhdGUubW92YWJsZS5jb2xvciA9XG4gIHN0YXRlLm1vdmFibGUuZGVzdHMgPVxuICBzdGF0ZS5hbmltYXRpb24uY3VycmVudCA9IHVuZGVmaW5lZDtcbiAgY2FuY2VsTW92ZShzdGF0ZSk7XG59XG5cbmV4cG9ydCBmdW5jdGlvbiBnZXRLZXlBdERvbVBvcyhwb3M6IGNnLk51bWJlclBhaXIsIGFzV2hpdGU6IGJvb2xlYW4sIGJvdW5kczogQ2xpZW50UmVjdCk6IGNnLktleSB8IHVuZGVmaW5lZCB7XG4gIGxldCBmaWxlID0gTWF0aC5jZWlsKDggKiAoKHBvc1swXSAtIGJvdW5kcy5sZWZ0KSAvIGJvdW5kcy53aWR0aCkpO1xuICBpZiAoIWFzV2hpdGUpIGZpbGUgPSA5IC0gZmlsZTtcbiAgbGV0IHJhbmsgPSBNYXRoLmNlaWwoOCAtICg4ICogKChwb3NbMV0gLSBib3VuZHMudG9wKSAvIGJvdW5kcy5oZWlnaHQpKSk7XG4gIGlmICghYXNXaGl0ZSkgcmFuayA9IDkgLSByYW5rO1xuICByZXR1cm4gKGZpbGUgPiAwICYmIGZpbGUgPCA5ICYmIHJhbmsgPiAwICYmIHJhbmsgPCA5KSA/IHBvczJrZXkoW2ZpbGUsIHJhbmtdKSA6IHVuZGVmaW5lZDtcbn1cbiIsImltcG9ydCB7IEFwaSwgc3RhcnQgfSBmcm9tICcuL2FwaSdcbmltcG9ydCB7IENvbmZpZywgY29uZmlndXJlIH0gZnJvbSAnLi9jb25maWcnXG5pbXBvcnQgeyBTdGF0ZSwgZGVmYXVsdHMgfSBmcm9tICcuL3N0YXRlJ1xuXG5pbXBvcnQgcmVuZGVyV3JhcCBmcm9tICcuL3dyYXAnO1xuaW1wb3J0ICogYXMgZXZlbnRzIGZyb20gJy4vZXZlbnRzJ1xuaW1wb3J0IHJlbmRlciBmcm9tICcuL3JlbmRlcic7XG5pbXBvcnQgKiBhcyBzdmcgZnJvbSAnLi9zdmcnO1xuaW1wb3J0ICogYXMgdXRpbCBmcm9tICcuL3V0aWwnO1xuXG5leHBvcnQgZnVuY3Rpb24gQ2hlc3Nncm91bmQoZWxlbWVudDogSFRNTEVsZW1lbnQsIGNvbmZpZz86IENvbmZpZyk6IEFwaSB7XG5cbiAgY29uc3Qgc3RhdGUgPSBkZWZhdWx0cygpIGFzIFN0YXRlO1xuXG4gIGNvbmZpZ3VyZShzdGF0ZSwgY29uZmlnIHx8IHt9KTtcblxuICBzdGF0ZS5icm93c2VyID0ge1xuICAgIHRyYW5zZm9ybTogdXRpbC50cmFuc2Zvcm1GdW5jdGlvbigpXG4gIH07XG5cbiAgZnVuY3Rpb24gcmVkcmF3QWxsKCkge1xuICAgIGxldCBwcmV2VW5iaW5kID0gc3RhdGUuZG9tICYmIHN0YXRlLmRvbS51bmJpbmQ7XG4gICAgLy8gZmlyc3QgZW5zdXJlIHRoZSBjZy1ib2FyZC13cmFwIGNsYXNzIGlzIHNldFxuICAgIC8vIHNvIGJvdW5kcyBjYWxjdWxhdGlvbiBjYW4gdXNlIHRoZSBDU1Mgd2lkdGgvaGVpZ2h0IHZhbHVlc1xuICAgIC8vIGFkZCB0aGF0IGNsYXNzIHlvdXJzZWxmIHRvIHRoZSBlbGVtZW50IGJlZm9yZSBjYWxsaW5nIGNoZXNzZ3JvdW5kXG4gICAgLy8gZm9yIGEgc2xpZ2h0IHBlcmZvcm1hbmNlIGltcHJvdmVtZW50ISAoYXZvaWRzIHJlY29tcHV0aW5nIHN0eWxlKVxuICAgIGVsZW1lbnQuY2xhc3NMaXN0LmFkZCgnY2ctYm9hcmQtd3JhcCcpO1xuICAgIC8vIGNvbXB1dGUgYm91bmRzIGZyb20gZXhpc3RpbmcgYm9hcmQgZWxlbWVudCBpZiBwb3NzaWJsZVxuICAgIC8vIHRoaXMgYWxsb3dzIG5vbi1zcXVhcmUgYm9hcmRzIGZyb20gQ1NTIHRvIGJlIGhhbmRsZWQgKGZvciAzRClcbiAgICBjb25zdCBib3VuZHMgPSB1dGlsLm1lbW8oKCkgPT4gZWxlbWVudC5nZXRCb3VuZGluZ0NsaWVudFJlY3QoKSk7XG4gICAgY29uc3QgZWxlbWVudHMgPSByZW5kZXJXcmFwKGVsZW1lbnQsIHN0YXRlLCBib3VuZHMoKSk7XG4gICAgY29uc3QgcmVkcmF3Tm93ID0gKHNraXBTdmc6IGJvb2xlYW4pID0+IHtcbiAgICAgIHJlbmRlcihzdGF0ZSk7XG4gICAgICBpZiAoIXNraXBTdmcgJiYgZWxlbWVudHMuc3ZnKSBzdmcucmVuZGVyU3ZnKHN0YXRlLCBlbGVtZW50cy5zdmcpO1xuICAgIH07XG4gICAgc3RhdGUuZG9tID0ge1xuICAgICAgZWxlbWVudHM6IGVsZW1lbnRzLFxuICAgICAgYm91bmRzOiBib3VuZHMsXG4gICAgICByZWRyYXc6IGRlYm91bmNlUmVkcmF3KHJlZHJhd05vdyksXG4gICAgICByZWRyYXdOb3c6IHJlZHJhd05vdyxcbiAgICAgIHVuYmluZDogcHJldlVuYmluZFxuICAgIH07XG4gICAgc3ZnLmNsZWFyQ2FjaGUoKTtcbiAgICByZWRyYXdOb3coZmFsc2UpO1xuICAgIGV2ZW50cy5iaW5kQm9hcmQoc3RhdGUpO1xuICAgIGlmICghcHJldlVuYmluZCkgc3RhdGUuZG9tLnVuYmluZCA9IGV2ZW50cy5iaW5kRG9jdW1lbnQoc3RhdGUsIHJlZHJhd0FsbCk7XG4gIH1cbiAgcmVkcmF3QWxsKCk7XG5cbiAgY29uc3QgYXBpID0gc3RhcnQoc3RhdGUsIHJlZHJhd0FsbCk7XG5cbiAgcmV0dXJuIGFwaTtcbn07XG5cbmZ1bmN0aW9uIGRlYm91bmNlUmVkcmF3KHJlZHJhd05vdzogKHNraXBTdmc/OiBib29sZWFuKSA9PiB2b2lkKTogKCkgPT4gdm9pZCB7XG4gIGxldCByZWRyYXdpbmcgPSBmYWxzZTtcbiAgcmV0dXJuICgpID0+IHtcbiAgICBpZiAocmVkcmF3aW5nKSByZXR1cm47XG4gICAgcmVkcmF3aW5nID0gdHJ1ZTtcbiAgICB1dGlsLnJhZigoKSA9PiB7XG4gICAgICByZWRyYXdOb3coKTtcbiAgICAgIHJlZHJhd2luZyA9IGZhbHNlO1xuICAgIH0pO1xuICB9O1xufVxuIiwiaW1wb3J0IHsgU3RhdGUgfSBmcm9tICcuL3N0YXRlJ1xuaW1wb3J0IHsgc2V0Q2hlY2ssIHNldFNlbGVjdGVkIH0gZnJvbSAnLi9ib2FyZCdcbmltcG9ydCB7IHJlYWQgYXMgZmVuUmVhZCB9IGZyb20gJy4vZmVuJ1xuaW1wb3J0IHsgRHJhd1NoYXBlLCBEcmF3QnJ1c2ggfSBmcm9tICcuL2RyYXcnXG5pbXBvcnQgKiBhcyBjZyBmcm9tICcuL3R5cGVzJ1xuXG5leHBvcnQgaW50ZXJmYWNlIENvbmZpZyB7XG4gIGZlbj86IGNnLkZFTjsgLy8gY2hlc3MgcG9zaXRpb24gaW4gRm9yc3l0aCBub3RhdGlvblxuICBvcmllbnRhdGlvbj86IGNnLkNvbG9yOyAvLyBib2FyZCBvcmllbnRhdGlvbi4gd2hpdGUgfCBibGFja1xuICB0dXJuQ29sb3I/OiBjZy5Db2xvcjsgLy8gdHVybiB0byBwbGF5LiB3aGl0ZSB8IGJsYWNrXG4gIGNoZWNrPzogY2cuQ29sb3IgfCBib29sZWFuOyAvLyB0cnVlIGZvciBjdXJyZW50IGNvbG9yLCBmYWxzZSB0byB1bnNldFxuICBsYXN0TW92ZT86IGNnLktleVtdOyAvLyBzcXVhcmVzIHBhcnQgb2YgdGhlIGxhc3QgbW92ZSBbXCJjM1wiLCBcImM0XCJdXG4gIHNlbGVjdGVkPzogY2cuS2V5OyAvLyBzcXVhcmUgY3VycmVudGx5IHNlbGVjdGVkIFwiYTFcIlxuICBjb29yZGluYXRlcz86IGJvb2xlYW47IC8vIGluY2x1ZGUgY29vcmRzIGF0dHJpYnV0ZXNcbiAgYXV0b0Nhc3RsZT86IGJvb2xlYW47IC8vIGltbWVkaWF0ZWx5IGNvbXBsZXRlIHRoZSBjYXN0bGUgYnkgbW92aW5nIHRoZSByb29rIGFmdGVyIGtpbmcgbW92ZVxuICB2aWV3T25seT86IGJvb2xlYW47IC8vIGRvbid0IGJpbmQgZXZlbnRzOiB0aGUgdXNlciB3aWxsIG5ldmVyIGJlIGFibGUgdG8gbW92ZSBwaWVjZXMgYXJvdW5kXG4gIGRpc2FibGVDb250ZXh0TWVudT86IGJvb2xlYW47IC8vIGJlY2F1c2Ugd2hvIG5lZWRzIGEgY29udGV4dCBtZW51IG9uIGEgY2hlc3Nib2FyZFxuICByZXNpemFibGU/OiBib29sZWFuOyAvLyBsaXN0ZW5zIHRvIGNoZXNzZ3JvdW5kLnJlc2l6ZSBvbiBkb2N1bWVudC5ib2R5IHRvIGNsZWFyIGJvdW5kcyBjYWNoZVxuICBhZGRQaWVjZVpJbmRleD86IGJvb2xlYW47IC8vIGFkZHMgei1pbmRleCB2YWx1ZXMgdG8gcGllY2VzIChmb3IgM0QpXG4gIC8vIHBpZWNlS2V5OiBib29sZWFuOyAvLyBhZGQgYSBkYXRhLWtleSBhdHRyaWJ1dGUgdG8gcGllY2UgZWxlbWVudHNcbiAgaGlnaGxpZ2h0Pzoge1xuICAgIGxhc3RNb3ZlPzogYm9vbGVhbjsgLy8gYWRkIGxhc3QtbW92ZSBjbGFzcyB0byBzcXVhcmVzXG4gICAgY2hlY2s/OiBib29sZWFuOyAvLyBhZGQgY2hlY2sgY2xhc3MgdG8gc3F1YXJlc1xuICB9O1xuICBhbmltYXRpb24/OiB7XG4gICAgZW5hYmxlZD86IGJvb2xlYW47XG4gICAgZHVyYXRpb24/OiBudW1iZXI7XG4gIH07XG4gIG1vdmFibGU/OiB7XG4gICAgZnJlZT86IGJvb2xlYW47IC8vIGFsbCBtb3ZlcyBhcmUgdmFsaWQgLSBib2FyZCBlZGl0b3JcbiAgICBjb2xvcj86IGNnLkNvbG9yIHwgJ2JvdGgnOyAvLyBjb2xvciB0aGF0IGNhbiBtb3ZlLiB3aGl0ZSB8IGJsYWNrIHwgYm90aCB8IHVuZGVmaW5lZFxuICAgIGRlc3RzPzoge1xuICAgICAgW2tleTogc3RyaW5nXTogY2cuS2V5W11cbiAgICB9OyAvLyB2YWxpZCBtb3Zlcy4ge1wiYTJcIiBbXCJhM1wiIFwiYTRcIl0gXCJiMVwiIFtcImEzXCIgXCJjM1wiXX1cbiAgICBzaG93RGVzdHM/OiBib29sZWFuOyAvLyB3aGV0aGVyIHRvIGFkZCB0aGUgbW92ZS1kZXN0IGNsYXNzIG9uIHNxdWFyZXNcbiAgICBldmVudHM/OiB7XG4gICAgICBhZnRlcj86IChvcmlnOiBjZy5LZXksIGRlc3Q6IGNnLktleSwgbWV0YWRhdGE6IGNnLk1vdmVNZXRhZGF0YSkgPT4gdm9pZDsgLy8gY2FsbGVkIGFmdGVyIHRoZSBtb3ZlIGhhcyBiZWVuIHBsYXllZFxuICAgICAgYWZ0ZXJOZXdQaWVjZT86IChyb2xlOiBjZy5Sb2xlLCBwb3M6IGNnLlBvcykgPT4gdm9pZDsgLy8gY2FsbGVkIGFmdGVyIGEgbmV3IHBpZWNlIGlzIGRyb3BwZWQgb24gdGhlIGJvYXJkXG4gICAgfTtcbiAgICByb29rQ2FzdGxlPzogYm9vbGVhbiAvLyBjYXN0bGUgYnkgbW92aW5nIHRoZSBraW5nIHRvIHRoZSByb29rXG4gIH07XG4gIHByZW1vdmFibGU/OiB7XG4gICAgZW5hYmxlZD86IGJvb2xlYW47IC8vIGFsbG93IHByZW1vdmVzIGZvciBjb2xvciB0aGF0IGNhbiBub3QgbW92ZVxuICAgIHNob3dEZXN0cz86IGJvb2xlYW47IC8vIHdoZXRoZXIgdG8gYWRkIHRoZSBwcmVtb3ZlLWRlc3QgY2xhc3Mgb24gc3F1YXJlc1xuICAgIGNhc3RsZT86IGJvb2xlYW47IC8vIHdoZXRoZXIgdG8gYWxsb3cga2luZyBjYXN0bGUgcHJlbW92ZXNcbiAgICBkZXN0cz86IGNnLktleVtdOyAvLyBwcmVtb3ZlIGRlc3RpbmF0aW9ucyBmb3IgdGhlIGN1cnJlbnQgc2VsZWN0aW9uXG4gICAgZXZlbnRzPzoge1xuICAgICAgc2V0PzogKG9yaWc6IGNnLktleSwgZGVzdDogY2cuS2V5KSA9PiB2b2lkOyAvLyBjYWxsZWQgYWZ0ZXIgdGhlIHByZW1vdmUgaGFzIGJlZW4gc2V0XG4gICAgICB1bnNldD86ICgpID0+IHZvaWQ7ICAvLyBjYWxsZWQgYWZ0ZXIgdGhlIHByZW1vdmUgaGFzIGJlZW4gdW5zZXRcbiAgICB9XG4gIH07XG4gIHByZWRyb3BwYWJsZT86IHtcbiAgICBlbmFibGVkPzogYm9vbGVhbjsgLy8gYWxsb3cgcHJlZHJvcHMgZm9yIGNvbG9yIHRoYXQgY2FuIG5vdCBtb3ZlXG4gICAgZXZlbnRzPzoge1xuICAgICAgc2V0PzogKHJvbGU6IGNnLlJvbGUsIGtleTogY2cuS2V5KSA9PiB2b2lkOyAvLyBjYWxsZWQgYWZ0ZXIgdGhlIHByZWRyb3AgaGFzIGJlZW4gc2V0XG4gICAgICB1bnNldD86ICgpID0+IHZvaWQ7IC8vIGNhbGxlZCBhZnRlciB0aGUgcHJlZHJvcCBoYXMgYmVlbiB1bnNldFxuICAgIH1cbiAgfTtcbiAgZHJhZ2dhYmxlPzoge1xuICAgIGVuYWJsZWQ/OiBib29sZWFuOyAvLyBhbGxvdyBtb3ZlcyAmIHByZW1vdmVzIHRvIHVzZSBkcmFnJ24gZHJvcFxuICAgIGRpc3RhbmNlPzogbnVtYmVyOyAvLyBtaW5pbXVtIGRpc3RhbmNlIHRvIGluaXRpYXRlIGEgZHJhZzsgaW4gcGl4ZWxzXG4gICAgYXV0b0Rpc3RhbmNlPzogYm9vbGVhbjsgLy8gbGV0cyBjaGVzc2dyb3VuZCBzZXQgZGlzdGFuY2UgdG8gemVybyB3aGVuIHVzZXIgZHJhZ3MgcGllY2VzXG4gICAgY2VudGVyUGllY2U/OiBib29sZWFuOyAvLyBjZW50ZXIgdGhlIHBpZWNlIG9uIGN1cnNvciBhdCBkcmFnIHN0YXJ0XG4gICAgc2hvd0dob3N0PzogYm9vbGVhbjsgLy8gc2hvdyBnaG9zdCBvZiBwaWVjZSBiZWluZyBkcmFnZ2VkXG4gICAgZGVsZXRlT25Ecm9wT2ZmPzogYm9vbGVhbjsgLy8gZGVsZXRlIGEgcGllY2Ugd2hlbiBpdCBpcyBkcm9wcGVkIG9mZiB0aGUgYm9hcmRcbiAgfTtcbiAgc2VsZWN0YWJsZT86IHtcbiAgICAvLyBkaXNhYmxlIHRvIGVuZm9yY2UgZHJhZ2dpbmcgb3ZlciBjbGljay1jbGljayBtb3ZlXG4gICAgZW5hYmxlZD86IGJvb2xlYW5cbiAgfTtcbiAgZXZlbnRzPzoge1xuICAgIGNoYW5nZT86ICgpID0+IHZvaWQ7IC8vIGNhbGxlZCBhZnRlciB0aGUgc2l0dWF0aW9uIGNoYW5nZXMgb24gdGhlIGJvYXJkXG4gICAgLy8gY2FsbGVkIGFmdGVyIGEgcGllY2UgaGFzIGJlZW4gbW92ZWQuXG4gICAgLy8gY2FwdHVyZWRQaWVjZSBpcyB1bmRlZmluZWQgb3IgbGlrZSB7Y29sb3I6ICd3aGl0ZSc7ICdyb2xlJzogJ3F1ZWVuJ31cbiAgICBtb3ZlPzogKG9yaWc6IGNnLktleSwgZGVzdDogY2cuS2V5LCBjYXB0dXJlZFBpZWNlPzogY2cuUGllY2UpID0+IHZvaWQ7XG4gICAgZHJvcE5ld1BpZWNlPzogKHJvbGU6IGNnLlJvbGUsIHBvczogY2cuUG9zKSA9PiB2b2lkO1xuICAgIHNlbGVjdD86IChrZXk6IGNnLktleSkgPT4gdm9pZCAvLyBjYWxsZWQgd2hlbiBhIHNxdWFyZSBpcyBzZWxlY3RlZFxuICB9O1xuICBpdGVtcz86IChwb3M6IGNnLlBvcywga2V5OiBjZy5LZXkpID0+IGFueSB8IHVuZGVmaW5lZDsgLy8gaXRlbXMgb24gdGhlIGJvYXJkIHsgcmVuZGVyOiBrZXkgLT4gdmRvbSB9XG4gIGRyYXdhYmxlPzoge1xuICAgIGVuYWJsZWQ/OiBib29sZWFuO1xuICAgIGVyYXNlT25DbGljaz86IGJvb2xlYW47XG4gICAgc2hhcGVzPzogRHJhd1NoYXBlW107XG4gICAgYXV0b1NoYXBlcz86IERyYXdTaGFwZVtdO1xuICAgIGJydXNoZXM/OiBEcmF3QnJ1c2hbXTtcbiAgICBwaWVjZXM/OiB7XG4gICAgICBiYXNlVXJsPzogc3RyaW5nO1xuICAgIH1cbiAgfVxufVxuXG5leHBvcnQgZnVuY3Rpb24gY29uZmlndXJlKHN0YXRlOiBTdGF0ZSwgY29uZmlnOiBDb25maWcpIHtcblxuICAvLyBkb24ndCBtZXJnZSBkZXN0aW5hdGlvbnMuIEp1c3Qgb3ZlcnJpZGUuXG4gIGlmIChjb25maWcubW92YWJsZSAmJiBjb25maWcubW92YWJsZS5kZXN0cykgc3RhdGUubW92YWJsZS5kZXN0cyA9IHVuZGVmaW5lZDtcblxuICBtZXJnZShzdGF0ZSwgY29uZmlnKTtcblxuICAvLyBpZiBhIGZlbiB3YXMgcHJvdmlkZWQsIHJlcGxhY2UgdGhlIHBpZWNlc1xuICBpZiAoY29uZmlnLmZlbikge1xuICAgIHN0YXRlLnBpZWNlcyA9IGZlblJlYWQoY29uZmlnLmZlbik7XG4gICAgc3RhdGUuZHJhd2FibGUuc2hhcGVzID0gW107XG4gIH1cblxuICAvLyBhcHBseSBjb25maWcgdmFsdWVzIHRoYXQgY291bGQgYmUgdW5kZWZpbmVkIHlldCBtZWFuaW5nZnVsXG4gIGlmIChjb25maWcuaGFzT3duUHJvcGVydHkoJ2NoZWNrJykpIHNldENoZWNrKHN0YXRlLCBjb25maWcuY2hlY2sgfHwgZmFsc2UpO1xuICBpZiAoY29uZmlnLmhhc093blByb3BlcnR5KCdsYXN0TW92ZScpICYmICFjb25maWcubGFzdE1vdmUpIHN0YXRlLmxhc3RNb3ZlID0gdW5kZWZpbmVkO1xuICAvLyBpbiBjYXNlIG9mIFpIIGRyb3AgbGFzdCBtb3ZlLCB0aGVyZSdzIGEgc2luZ2xlIHNxdWFyZS5cbiAgLy8gaWYgdGhlIHByZXZpb3VzIGxhc3QgbW92ZSBoYWQgdHdvIHNxdWFyZXMsXG4gIC8vIHRoZSBtZXJnZSBhbGdvcml0aG0gd2lsbCBpbmNvcnJlY3RseSBrZWVwIHRoZSBzZWNvbmQgc3F1YXJlLlxuICBlbHNlIGlmIChjb25maWcubGFzdE1vdmUpIHN0YXRlLmxhc3RNb3ZlID0gY29uZmlnLmxhc3RNb3ZlO1xuXG4gIC8vIGZpeCBtb3ZlL3ByZW1vdmUgZGVzdHNcbiAgaWYgKHN0YXRlLnNlbGVjdGVkKSBzZXRTZWxlY3RlZChzdGF0ZSwgc3RhdGUuc2VsZWN0ZWQpO1xuXG4gIC8vIG5vIG5lZWQgZm9yIHN1Y2ggc2hvcnQgYW5pbWF0aW9uc1xuICBpZiAoIXN0YXRlLmFuaW1hdGlvbi5kdXJhdGlvbiB8fCBzdGF0ZS5hbmltYXRpb24uZHVyYXRpb24gPCAxMDApIHN0YXRlLmFuaW1hdGlvbi5lbmFibGVkID0gZmFsc2U7XG5cbiAgaWYgKCFzdGF0ZS5tb3ZhYmxlLnJvb2tDYXN0bGUgJiYgc3RhdGUubW92YWJsZS5kZXN0cykge1xuICAgIGNvbnN0IHJhbmsgPSBzdGF0ZS5tb3ZhYmxlLmNvbG9yID09PSAnd2hpdGUnID8gMSA6IDg7XG4gICAgY29uc3Qga2luZ1N0YXJ0UG9zID0gJ2UnICsgcmFuaztcbiAgICBjb25zdCBkZXN0cyA9IHN0YXRlLm1vdmFibGUuZGVzdHNba2luZ1N0YXJ0UG9zXTtcbiAgICBpZiAoIWRlc3RzIHx8IHN0YXRlLnBpZWNlc1traW5nU3RhcnRQb3NdLnJvbGUgIT09ICdraW5nJykgcmV0dXJuO1xuICAgIHN0YXRlLm1vdmFibGUuZGVzdHNba2luZ1N0YXJ0UG9zXSA9IGRlc3RzLmZpbHRlcihkID0+IHtcbiAgICAgIGlmICgoZCA9PT0gJ2EnICsgcmFuaykgJiYgZGVzdHMuaW5kZXhPZignYycgKyByYW5rIGFzIGNnLktleSkgIT09IC0xKSByZXR1cm4gZmFsc2U7XG4gICAgICBpZiAoKGQgPT09ICdoJyArIHJhbmspICYmIGRlc3RzLmluZGV4T2YoJ2cnICsgcmFuayBhcyBjZy5LZXkpICE9PSAtMSkgcmV0dXJuIGZhbHNlO1xuICAgICAgcmV0dXJuIHRydWU7XG4gICAgfSk7XG4gIH1cbn07XG5cbmZ1bmN0aW9uIG1lcmdlKGJhc2U6IGFueSwgZXh0ZW5kOiBhbnkpIHtcbiAgZm9yICh2YXIga2V5IGluIGV4dGVuZCkge1xuICAgIGlmIChpc09iamVjdChiYXNlW2tleV0pICYmIGlzT2JqZWN0KGV4dGVuZFtrZXldKSkgbWVyZ2UoYmFzZVtrZXldLCBleHRlbmRba2V5XSk7XG4gICAgZWxzZSBiYXNlW2tleV0gPSBleHRlbmRba2V5XTtcbiAgfVxufVxuXG5mdW5jdGlvbiBpc09iamVjdChvOiBhbnkpOiBib29sZWFuIHtcbiAgcmV0dXJuIHR5cGVvZiBvID09PSAnb2JqZWN0Jztcbn1cbiIsImltcG9ydCB7IFN0YXRlIH0gZnJvbSAnLi9zdGF0ZSdcbmltcG9ydCAqIGFzIGJvYXJkIGZyb20gJy4vYm9hcmQnXG5pbXBvcnQgKiBhcyB1dGlsIGZyb20gJy4vdXRpbCdcbmltcG9ydCB7IGNsZWFyIGFzIGRyYXdDbGVhciB9IGZyb20gJy4vZHJhdydcbmltcG9ydCAqIGFzIGNnIGZyb20gJy4vdHlwZXMnXG5pbXBvcnQgeyBhbmltIH0gZnJvbSAnLi9hbmltJ1xuXG5leHBvcnQgaW50ZXJmYWNlIERyYWdDdXJyZW50IHtcbiAgb3JpZzogY2cuS2V5OyAvLyBvcmlnIGtleSBvZiBkcmFnZ2luZyBwaWVjZVxuICBvcmlnUG9zOiBjZy5Qb3M7XG4gIHBpZWNlOiBjZy5QaWVjZTtcbiAgcmVsOiBjZy5OdW1iZXJQYWlyOyAvLyB4OyB5IG9mIHRoZSBwaWVjZSBhdCBvcmlnaW5hbCBwb3NpdGlvblxuICBlcG9zOiBjZy5OdW1iZXJQYWlyOyAvLyBpbml0aWFsIGV2ZW50IHBvc2l0aW9uXG4gIHBvczogY2cuTnVtYmVyUGFpcjsgLy8gcmVsYXRpdmUgY3VycmVudCBwb3NpdGlvblxuICBkZWM6IGNnLk51bWJlclBhaXI7IC8vIHBpZWNlIGNlbnRlciBkZWNheVxuICBvdmVyPzogY2cuS2V5OyAvLyBzcXVhcmUgYmVpbmcgbW91c2VkIG92ZXJcbiAgb3ZlclByZXY/OiBjZy5LZXk7IC8vIHNxdWFyZSBwcmV2aW91c2x5IG1vdXNlZCBvdmVyXG4gIHN0YXJ0ZWQ6IGJvb2xlYW47IC8vIHdoZXRoZXIgdGhlIGRyYWcgaGFzIHN0YXJ0ZWQ7IGFzIHBlciB0aGUgZGlzdGFuY2Ugc2V0dGluZ1xuICBlbGVtZW50OiBjZy5QaWVjZU5vZGUgfCAoKCkgPT4gY2cuUGllY2VOb2RlIHwgdW5kZWZpbmVkKTtcbiAgbmV3UGllY2U/OiBib29sZWFuOyAvLyBpdCBpdCBhIG5ldyBwaWVjZSBmcm9tIG91dHNpZGUgdGhlIGJvYXJkXG4gIGZvcmNlPzogYm9vbGVhbjsgLy8gY2FuIHRoZSBuZXcgcGllY2UgcmVwbGFjZSBhbiBleGlzdGluZyBvbmUgKGVkaXRvcilcbiAgcHJldmlvdXNseVNlbGVjdGVkPzogY2cuS2V5O1xuICBvcmlnaW5UYXJnZXQ6IEV2ZW50VGFyZ2V0O1xufVxuXG5leHBvcnQgZnVuY3Rpb24gc3RhcnQoczogU3RhdGUsIGU6IGNnLk1vdWNoRXZlbnQpOiB2b2lkIHtcbiAgaWYgKGUuYnV0dG9uICE9PSB1bmRlZmluZWQgJiYgZS5idXR0b24gIT09IDApIHJldHVybjsgLy8gb25seSB0b3VjaCBvciBsZWZ0IGNsaWNrXG4gIGlmIChlLnRvdWNoZXMgJiYgZS50b3VjaGVzLmxlbmd0aCA+IDEpIHJldHVybjsgLy8gc3VwcG9ydCBvbmUgZmluZ2VyIHRvdWNoIG9ubHlcbiAgZS5wcmV2ZW50RGVmYXVsdCgpO1xuICBjb25zdCBhc1doaXRlID0gcy5vcmllbnRhdGlvbiA9PT0gJ3doaXRlJyxcbiAgYm91bmRzID0gcy5kb20uYm91bmRzKCksXG4gIHBvc2l0aW9uID0gdXRpbC5ldmVudFBvc2l0aW9uKGUpIGFzIGNnLk51bWJlclBhaXIsXG4gIG9yaWcgPSBib2FyZC5nZXRLZXlBdERvbVBvcyhwb3NpdGlvbiwgYXNXaGl0ZSwgYm91bmRzKTtcbiAgaWYgKCFvcmlnKSByZXR1cm47XG4gIGNvbnN0IHBpZWNlID0gcy5waWVjZXNbb3JpZ107XG4gIGNvbnN0IHByZXZpb3VzbHlTZWxlY3RlZCA9IHMuc2VsZWN0ZWQ7XG4gIGlmICghcHJldmlvdXNseVNlbGVjdGVkICYmIChcbiAgICBzLmRyYXdhYmxlLmVyYXNlT25DbGljayB8fCAoIXBpZWNlIHx8IHBpZWNlLmNvbG9yICE9PSBzLnR1cm5Db2xvcilcbiAgKSkgZHJhd0NsZWFyKHMpO1xuICBpZiAocy52aWV3T25seSkgcmV0dXJuO1xuICBjb25zdCBoYWRQcmVtb3ZlID0gISFzLnByZW1vdmFibGUuY3VycmVudDtcbiAgY29uc3QgaGFkUHJlZHJvcCA9ICEhcy5wcmVkcm9wcGFibGUuY3VycmVudDtcbiAgcy5zdGF0cy5jdHJsS2V5ID0gZS5jdHJsS2V5O1xuICBpZiAocy5zZWxlY3RlZCAmJiBib2FyZC5jYW5Nb3ZlKHMsIHMuc2VsZWN0ZWQsIG9yaWcpKSB7XG4gICAgYW5pbShzdGF0ZSA9PiBib2FyZC5zZWxlY3RTcXVhcmUoc3RhdGUsIG9yaWcpLCBzKTtcbiAgfSBlbHNlIHtcbiAgICBib2FyZC5zZWxlY3RTcXVhcmUocywgb3JpZyk7XG4gIH1cbiAgY29uc3Qgc3RpbGxTZWxlY3RlZCA9IHMuc2VsZWN0ZWQgPT09IG9yaWc7XG4gIGNvbnN0IGVsZW1lbnQgPSBwaWVjZUVsZW1lbnRCeUtleShzLCBvcmlnKTtcbiAgaWYgKHBpZWNlICYmIGVsZW1lbnQgJiYgc3RpbGxTZWxlY3RlZCAmJiBib2FyZC5pc0RyYWdnYWJsZShzLCBvcmlnKSkge1xuICAgIGNvbnN0IHNxdWFyZUJvdW5kcyA9IGNvbXB1dGVTcXVhcmVCb3VuZHMob3JpZywgYXNXaGl0ZSwgYm91bmRzKTtcbiAgICBzLmRyYWdnYWJsZS5jdXJyZW50ID0ge1xuICAgICAgb3JpZzogb3JpZyxcbiAgICAgIG9yaWdQb3M6IHV0aWwua2V5MnBvcyhvcmlnKSxcbiAgICAgIHBpZWNlOiBwaWVjZSxcbiAgICAgIHJlbDogcG9zaXRpb24sXG4gICAgICBlcG9zOiBwb3NpdGlvbixcbiAgICAgIHBvczogWzAsIDBdLFxuICAgICAgZGVjOiBzLmRyYWdnYWJsZS5jZW50ZXJQaWVjZSA/IFtcbiAgICAgICAgcG9zaXRpb25bMF0gLSAoc3F1YXJlQm91bmRzLmxlZnQgKyBzcXVhcmVCb3VuZHMud2lkdGggLyAyKSxcbiAgICAgICAgcG9zaXRpb25bMV0gLSAoc3F1YXJlQm91bmRzLnRvcCArIHNxdWFyZUJvdW5kcy5oZWlnaHQgLyAyKVxuICAgICAgXSA6IFswLCAwXSxcbiAgICAgIHN0YXJ0ZWQ6IHMuZHJhZ2dhYmxlLmF1dG9EaXN0YW5jZSAmJiBzLnN0YXRzLmRyYWdnZWQsXG4gICAgICBlbGVtZW50OiBlbGVtZW50LFxuICAgICAgcHJldmlvdXNseVNlbGVjdGVkOiBwcmV2aW91c2x5U2VsZWN0ZWQsXG4gICAgICBvcmlnaW5UYXJnZXQ6IGUudGFyZ2V0XG4gICAgfTtcbiAgICBlbGVtZW50LmNnRHJhZ2dpbmcgPSB0cnVlO1xuICAgIGVsZW1lbnQuY2xhc3NMaXN0LmFkZCgnZHJhZ2dpbmcnKTtcbiAgICAvLyBwbGFjZSBnaG9zdFxuICAgIGNvbnN0IGdob3N0ID0gcy5kb20uZWxlbWVudHMuZ2hvc3Q7XG4gICAgaWYgKGdob3N0KSB7XG4gICAgICBnaG9zdC5jbGFzc05hbWUgPSBgZ2hvc3QgJHtwaWVjZS5jb2xvcn0gJHtwaWVjZS5yb2xlfWA7XG4gICAgICBjb25zdCB0cmFuc2xhdGlvbiA9IHV0aWwucG9zVG9UcmFuc2xhdGUodXRpbC5rZXkycG9zKG9yaWcpLCBhc1doaXRlLCBib3VuZHMpO1xuICAgICAgcy5icm93c2VyLnRyYW5zZm9ybShnaG9zdCwgdXRpbC50cmFuc2xhdGUodHJhbnNsYXRpb24pKTtcbiAgICB9XG4gICAgcHJvY2Vzc0RyYWcocyk7XG4gIH0gZWxzZSB7XG4gICAgaWYgKGhhZFByZW1vdmUpIGJvYXJkLnVuc2V0UHJlbW92ZShzKTtcbiAgICBpZiAoaGFkUHJlZHJvcCkgYm9hcmQudW5zZXRQcmVkcm9wKHMpO1xuICB9XG4gIHMuZG9tLnJlZHJhdygpO1xufVxuXG5leHBvcnQgZnVuY3Rpb24gZHJhZ05ld1BpZWNlKHM6IFN0YXRlLCBwaWVjZTogY2cuUGllY2UsIGU6IGNnLk1vdWNoRXZlbnQsIGZvcmNlPzogYm9vbGVhbik6IHZvaWQge1xuXG4gIGNvbnN0IGtleTogY2cuS2V5ID0gJ2EwJztcblxuICBzLnBpZWNlc1trZXldID0gcGllY2U7XG5cbiAgcy5kb20ucmVkcmF3KCk7XG5cbiAgY29uc3QgcG9zaXRpb24gPSB1dGlsLmV2ZW50UG9zaXRpb24oZSkgYXMgY2cuTnVtYmVyUGFpcixcbiAgYXNXaGl0ZSA9IHMub3JpZW50YXRpb24gPT09ICd3aGl0ZScsXG4gIGJvdW5kcyA9IHMuZG9tLmJvdW5kcygpLFxuICBzcXVhcmVCb3VuZHMgPSBjb21wdXRlU3F1YXJlQm91bmRzKGtleSwgYXNXaGl0ZSwgYm91bmRzKTtcblxuICBjb25zdCByZWw6IGNnLk51bWJlclBhaXIgPSBbXG4gICAgKGFzV2hpdGUgPyAwIDogNykgKiBzcXVhcmVCb3VuZHMud2lkdGggKyBib3VuZHMubGVmdCxcbiAgICAoYXNXaGl0ZSA/IDggOiAtMSkgKiBzcXVhcmVCb3VuZHMuaGVpZ2h0ICsgYm91bmRzLnRvcFxuICBdO1xuXG4gIHMuZHJhZ2dhYmxlLmN1cnJlbnQgPSB7XG4gICAgb3JpZzoga2V5LFxuICAgIG9yaWdQb3M6IHV0aWwua2V5MnBvcyhrZXkpLFxuICAgIHBpZWNlOiBwaWVjZSxcbiAgICByZWw6IHJlbCxcbiAgICBlcG9zOiBwb3NpdGlvbixcbiAgICBwb3M6IFtwb3NpdGlvblswXSAtIHJlbFswXSwgcG9zaXRpb25bMV0gLSByZWxbMV1dLFxuICAgIGRlYzogWy1zcXVhcmVCb3VuZHMud2lkdGggLyAyLCAtc3F1YXJlQm91bmRzLmhlaWdodCAvIDJdLFxuICAgIHN0YXJ0ZWQ6IHRydWUsXG4gICAgZWxlbWVudDogKCkgPT4gcGllY2VFbGVtZW50QnlLZXkocywga2V5KSxcbiAgICBvcmlnaW5UYXJnZXQ6IGUudGFyZ2V0LFxuICAgIG5ld1BpZWNlOiB0cnVlLFxuICAgIGZvcmNlOiBmb3JjZSB8fCBmYWxzZVxuICB9O1xuICBwcm9jZXNzRHJhZyhzKTtcbn1cblxuZnVuY3Rpb24gcHJvY2Vzc0RyYWcoczogU3RhdGUpOiB2b2lkIHtcbiAgdXRpbC5yYWYoKCkgPT4ge1xuICAgIGNvbnN0IGN1ciA9IHMuZHJhZ2dhYmxlLmN1cnJlbnQ7XG4gICAgaWYgKCFjdXIpIHJldHVybjtcbiAgICAvLyBjYW5jZWwgYW5pbWF0aW9ucyB3aGlsZSBkcmFnZ2luZ1xuICAgIGlmIChzLmFuaW1hdGlvbi5jdXJyZW50ICYmIHMuYW5pbWF0aW9uLmN1cnJlbnQucGxhbi5hbmltc1tjdXIub3JpZ10pIHMuYW5pbWF0aW9uLmN1cnJlbnQgPSB1bmRlZmluZWQ7XG4gICAgLy8gaWYgbW92aW5nIHBpZWNlIGlzIGdvbmUsIGNhbmNlbFxuICAgIGNvbnN0IG9yaWdQaWVjZSA9IHMucGllY2VzW2N1ci5vcmlnXTtcbiAgICBpZiAoIW9yaWdQaWVjZSB8fCAhdXRpbC5zYW1lUGllY2Uob3JpZ1BpZWNlLCBjdXIucGllY2UpKSBjYW5jZWwocyk7XG4gICAgZWxzZSB7XG4gICAgICBpZiAoIWN1ci5zdGFydGVkICYmIHV0aWwuZGlzdGFuY2VTcShjdXIuZXBvcywgY3VyLnJlbCkgPj0gTWF0aC5wb3cocy5kcmFnZ2FibGUuZGlzdGFuY2UsIDIpKSBjdXIuc3RhcnRlZCA9IHRydWU7XG4gICAgICBpZiAoY3VyLnN0YXJ0ZWQpIHtcblxuICAgICAgICAvLyBzdXBwb3J0IGxhenkgZWxlbWVudHNcbiAgICAgICAgaWYgKHR5cGVvZiBjdXIuZWxlbWVudCA9PT0gJ2Z1bmN0aW9uJykge1xuICAgICAgICAgIGxldCBmb3VuZCA9IGN1ci5lbGVtZW50KCk7XG4gICAgICAgICAgaWYgKCFmb3VuZCkgcmV0dXJuO1xuICAgICAgICAgIGN1ci5lbGVtZW50ID0gZm91bmQ7XG4gICAgICAgICAgY3VyLmVsZW1lbnQuY2dEcmFnZ2luZyA9IHRydWU7XG4gICAgICAgICAgY3VyLmVsZW1lbnQuY2xhc3NMaXN0LmFkZCgnZHJhZ2dpbmcnKTtcbiAgICAgICAgfVxuXG4gICAgICAgIGNvbnN0IGFzV2hpdGUgPSBzLm9yaWVudGF0aW9uID09PSAnd2hpdGUnLFxuICAgICAgICBib3VuZHMgPSBzLmRvbS5ib3VuZHMoKTtcbiAgICAgICAgY3VyLnBvcyA9IFtcbiAgICAgICAgICBjdXIuZXBvc1swXSAtIGN1ci5yZWxbMF0sXG4gICAgICAgICAgY3VyLmVwb3NbMV0gLSBjdXIucmVsWzFdXG4gICAgICAgIF07XG4gICAgICAgIGN1ci5vdmVyID0gYm9hcmQuZ2V0S2V5QXREb21Qb3MoY3VyLmVwb3MsIGFzV2hpdGUsIGJvdW5kcyk7XG5cbiAgICAgICAgLy8gbW92ZSBwaWVjZVxuICAgICAgICBjb25zdCB0cmFuc2xhdGlvbiA9IHV0aWwucG9zVG9UcmFuc2xhdGUoY3VyLm9yaWdQb3MsIGFzV2hpdGUsIGJvdW5kcyk7XG4gICAgICAgIHRyYW5zbGF0aW9uWzBdICs9IGN1ci5wb3NbMF0gKyBjdXIuZGVjWzBdO1xuICAgICAgICB0cmFuc2xhdGlvblsxXSArPSBjdXIucG9zWzFdICsgY3VyLmRlY1sxXTtcbiAgICAgICAgcy5icm93c2VyLnRyYW5zZm9ybShjdXIuZWxlbWVudCwgdXRpbC50cmFuc2xhdGUodHJhbnNsYXRpb24pKTtcblxuICAgICAgICAvLyBtb3ZlIG92ZXIgZWxlbWVudFxuICAgICAgICBjb25zdCBvdmVyRWwgPSBzLmRvbS5lbGVtZW50cy5vdmVyO1xuICAgICAgICBpZiAob3ZlckVsICYmIGN1ci5vdmVyICYmIGN1ci5vdmVyICE9PSBjdXIub3ZlclByZXYpIHtcbiAgICAgICAgICBjb25zdCBkZXN0cyA9IHMubW92YWJsZS5kZXN0cztcbiAgICAgICAgICBpZiAocy5tb3ZhYmxlLmZyZWUgfHxcbiAgICAgICAgICAgIHV0aWwuY29udGFpbnNYKGRlc3RzICYmIGRlc3RzW2N1ci5vcmlnXSwgY3VyLm92ZXIpIHx8XG4gICAgICAgICAgICB1dGlsLmNvbnRhaW5zWChzLnByZW1vdmFibGUuZGVzdHMsIGN1ci5vdmVyKSkge1xuICAgICAgICAgICAgY29uc3QgcG9zID0gdXRpbC5rZXkycG9zKGN1ci5vdmVyKSxcbiAgICAgICAgICAgIHZlY3RvcjogY2cuTnVtYmVyUGFpciA9IFtcbiAgICAgICAgICAgICAgKGFzV2hpdGUgPyBwb3NbMF0gLSAxIDogOCAtIHBvc1swXSkgKiBib3VuZHMud2lkdGggLyA4LFxuICAgICAgICAgICAgICAoYXNXaGl0ZSA/IDggLSBwb3NbMV0gOiBwb3NbMV0gLSAxKSAqIGJvdW5kcy5oZWlnaHQgLyA4XG4gICAgICAgICAgICBdO1xuICAgICAgICAgICAgcy5icm93c2VyLnRyYW5zZm9ybShvdmVyRWwsIHV0aWwudHJhbnNsYXRlKHZlY3RvcikpO1xuICAgICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgICBzLmJyb3dzZXIudHJhbnNmb3JtKG92ZXJFbCwgdXRpbC50cmFuc2xhdGVBd2F5KTtcbiAgICAgICAgICB9XG4gICAgICAgICAgY3VyLm92ZXJQcmV2ID0gY3VyLm92ZXI7XG4gICAgICAgIH1cbiAgICAgIH1cbiAgICB9XG4gICAgcHJvY2Vzc0RyYWcocyk7XG4gIH0pO1xufVxuXG5leHBvcnQgZnVuY3Rpb24gbW92ZShzOiBTdGF0ZSwgZTogY2cuTW91Y2hFdmVudCk6IHZvaWQge1xuICAvLyBzdXBwb3J0IG9uZSBmaW5nZXIgdG91Y2ggb25seVxuICBpZiAocy5kcmFnZ2FibGUuY3VycmVudCAmJiAoIWUudG91Y2hlcyB8fCBlLnRvdWNoZXMubGVuZ3RoIDwgMikpIHtcbiAgICBzLmRyYWdnYWJsZS5jdXJyZW50LmVwb3MgPSB1dGlsLmV2ZW50UG9zaXRpb24oZSkgYXMgY2cuTnVtYmVyUGFpcjtcbiAgfVxufVxuXG5leHBvcnQgZnVuY3Rpb24gZW5kKHM6IFN0YXRlLCBlOiBjZy5Nb3VjaEV2ZW50KTogdm9pZCB7XG4gIGNvbnN0IGN1ciA9IHMuZHJhZ2dhYmxlLmN1cnJlbnQ7XG4gIGlmICghY3VyKSByZXR1cm47XG4gIC8vIGNvbXBhcmluZyB3aXRoIHRoZSBvcmlnaW4gdGFyZ2V0IGlzIGFuIGVhc3kgd2F5IHRvIHRlc3QgdGhhdCB0aGUgZW5kIGV2ZW50XG4gIC8vIGhhcyB0aGUgc2FtZSB0b3VjaCBvcmlnaW5cbiAgaWYgKGUudHlwZSA9PT0gJ3RvdWNoZW5kJyAmJiBjdXIgJiYgY3VyLm9yaWdpblRhcmdldCAhPT0gZS50YXJnZXQgJiYgIWN1ci5uZXdQaWVjZSkge1xuICAgIHMuZHJhZ2dhYmxlLmN1cnJlbnQgPSB1bmRlZmluZWQ7XG4gICAgcmV0dXJuO1xuICB9XG4gIGJvYXJkLnVuc2V0UHJlbW92ZShzKTtcbiAgYm9hcmQudW5zZXRQcmVkcm9wKHMpO1xuICAvLyB0b3VjaGVuZCBoYXMgbm8gcG9zaXRpb247IHNvIHVzZSB0aGUgbGFzdCB0b3VjaG1vdmUgcG9zaXRpb24gaW5zdGVhZFxuICBjb25zdCBldmVudFBvczogY2cuTnVtYmVyUGFpciA9IHV0aWwuZXZlbnRQb3NpdGlvbihlKSB8fCBjdXIuZXBvcztcbiAgY29uc3QgZGVzdCA9IGJvYXJkLmdldEtleUF0RG9tUG9zKGV2ZW50UG9zLCBzLm9yaWVudGF0aW9uID09PSAnd2hpdGUnLCBzLmRvbS5ib3VuZHMoKSk7XG4gIGlmIChkZXN0ICYmIGN1ci5zdGFydGVkKSB7XG4gICAgaWYgKGN1ci5uZXdQaWVjZSkgYm9hcmQuZHJvcE5ld1BpZWNlKHMsIGN1ci5vcmlnLCBkZXN0LCBjdXIuZm9yY2UpO1xuICAgIGVsc2Uge1xuICAgICAgcy5zdGF0cy5jdHJsS2V5ID0gZS5jdHJsS2V5O1xuICAgICAgaWYgKGJvYXJkLnVzZXJNb3ZlKHMsIGN1ci5vcmlnLCBkZXN0KSkgcy5zdGF0cy5kcmFnZ2VkID0gdHJ1ZTtcbiAgICB9XG4gIH0gZWxzZSBpZiAoY3VyLm5ld1BpZWNlKSB7XG4gICAgZGVsZXRlIHMucGllY2VzW2N1ci5vcmlnXTtcbiAgfSBlbHNlIGlmIChzLmRyYWdnYWJsZS5kZWxldGVPbkRyb3BPZmYpIHtcbiAgICBkZWxldGUgcy5waWVjZXNbY3VyLm9yaWddO1xuICAgIGJvYXJkLmNhbGxVc2VyRnVuY3Rpb24ocy5ldmVudHMuY2hhbmdlKTtcbiAgfVxuICBpZiAoY3VyICYmIGN1ci5vcmlnID09PSBjdXIucHJldmlvdXNseVNlbGVjdGVkICYmIChjdXIub3JpZyA9PT0gZGVzdCB8fCAhZGVzdCkpXG4gICAgYm9hcmQudW5zZWxlY3Qocyk7XG4gIGVsc2UgaWYgKCFzLnNlbGVjdGFibGUuZW5hYmxlZCkgYm9hcmQudW5zZWxlY3Qocyk7XG5cbiAgcmVtb3ZlRHJhZ0VsZW1lbnRzKHMpO1xuXG4gIHMuZHJhZ2dhYmxlLmN1cnJlbnQgPSB1bmRlZmluZWQ7XG4gIHMuZG9tLnJlZHJhdygpO1xufVxuXG5leHBvcnQgZnVuY3Rpb24gY2FuY2VsKHM6IFN0YXRlKTogdm9pZCB7XG4gIGNvbnN0IGN1ciA9IHMuZHJhZ2dhYmxlLmN1cnJlbnQ7XG4gIGlmIChjdXIpIHtcbiAgICBpZiAoY3VyLm5ld1BpZWNlKSBkZWxldGUgcy5waWVjZXNbY3VyLm9yaWddO1xuICAgIHMuZHJhZ2dhYmxlLmN1cnJlbnQgPSB1bmRlZmluZWQ7XG4gICAgYm9hcmQudW5zZWxlY3Qocyk7XG4gICAgcmVtb3ZlRHJhZ0VsZW1lbnRzKHMpO1xuICAgIHMuZG9tLnJlZHJhdygpO1xuICB9XG59XG5cbmZ1bmN0aW9uIHJlbW92ZURyYWdFbGVtZW50cyhzOiBTdGF0ZSkge1xuICBjb25zdCBlID0gcy5kb20uZWxlbWVudHM7XG4gIGlmIChlLm92ZXIpIHMuYnJvd3Nlci50cmFuc2Zvcm0oZS5vdmVyLCB1dGlsLnRyYW5zbGF0ZUF3YXkpO1xuICBpZiAoZS5naG9zdCkgcy5icm93c2VyLnRyYW5zZm9ybShlLmdob3N0LCB1dGlsLnRyYW5zbGF0ZUF3YXkpO1xufVxuXG5mdW5jdGlvbiBjb21wdXRlU3F1YXJlQm91bmRzKGtleTogY2cuS2V5LCBhc1doaXRlOiBib29sZWFuLCBib3VuZHM6IENsaWVudFJlY3QpIHtcbiAgY29uc3QgcG9zID0gdXRpbC5rZXkycG9zKGtleSk7XG4gIGlmICghYXNXaGl0ZSkge1xuICAgIHBvc1swXSA9IDkgLSBwb3NbMF07XG4gICAgcG9zWzFdID0gOSAtIHBvc1sxXTtcbiAgfVxuICByZXR1cm4ge1xuICAgIGxlZnQ6IGJvdW5kcy5sZWZ0ICsgYm91bmRzLndpZHRoICogKHBvc1swXSAtIDEpIC8gOCxcbiAgICB0b3A6IGJvdW5kcy50b3AgKyBib3VuZHMuaGVpZ2h0ICogKDggLSBwb3NbMV0pIC8gOCxcbiAgICB3aWR0aDogYm91bmRzLndpZHRoIC8gOCxcbiAgICBoZWlnaHQ6IGJvdW5kcy5oZWlnaHQgLyA4XG4gIH07XG59XG5cbmZ1bmN0aW9uIHBpZWNlRWxlbWVudEJ5S2V5KHM6IFN0YXRlLCBrZXk6IGNnLktleSk6IGNnLlBpZWNlTm9kZSB8IHVuZGVmaW5lZCB7XG4gIGxldCBlbCA9IHMuZG9tLmVsZW1lbnRzLmJvYXJkLmZpcnN0Q2hpbGQgYXMgY2cuUGllY2VOb2RlO1xuICB3aGlsZSAoZWwpIHtcbiAgICBpZiAoZWwuY2dLZXkgPT09IGtleSAmJiBlbC50YWdOYW1lID09PSAnUElFQ0UnKSByZXR1cm4gZWw7XG4gICAgZWwgPSBlbC5uZXh0U2libGluZyBhcyBjZy5QaWVjZU5vZGU7XG4gIH1cbiAgcmV0dXJuIHVuZGVmaW5lZDtcbn1cbiIsImltcG9ydCB7IFN0YXRlIH0gZnJvbSAnLi9zdGF0ZSdcbmltcG9ydCB7IGNhbmNlbE1vdmUsIGdldEtleUF0RG9tUG9zIH0gZnJvbSAnLi9ib2FyZCdcbmltcG9ydCB7IGV2ZW50UG9zaXRpb24sIHJhZiwgaXNSaWdodEJ1dHRvbiB9IGZyb20gJy4vdXRpbCdcbmltcG9ydCAqIGFzIGNnIGZyb20gJy4vdHlwZXMnXG5cbmV4cG9ydCBpbnRlcmZhY2UgRHJhd1NoYXBlIHtcbiAgb3JpZzogY2cuS2V5O1xuICBkZXN0PzogY2cuS2V5O1xuICBicnVzaDogc3RyaW5nO1xuICBtb2RpZmllcnM/OiBEcmF3TW9kaWZpZXJzO1xuICBwaWVjZT86IERyYXdTaGFwZVBpZWNlO1xufVxuXG5leHBvcnQgaW50ZXJmYWNlIERyYXdTaGFwZVBpZWNlIHtcbiAgcm9sZTogY2cuUm9sZTtcbiAgY29sb3I6IGNnLkNvbG9yO1xuICBzY2FsZT86IG51bWJlcjtcbn1cblxuZXhwb3J0IGludGVyZmFjZSBEcmF3QnJ1c2gge1xuICBrZXk6IHN0cmluZztcbiAgY29sb3I6IHN0cmluZztcbiAgb3BhY2l0eTogbnVtYmVyO1xuICBsaW5lV2lkdGg6IG51bWJlclxufVxuXG5leHBvcnQgaW50ZXJmYWNlIERyYXdCcnVzaGVzIHtcbiAgW25hbWU6IHN0cmluZ106IERyYXdCcnVzaDtcbn1cblxuZXhwb3J0IGludGVyZmFjZSBEcmF3TW9kaWZpZXJzIHtcbiAgbGluZVdpZHRoPzogbnVtYmVyO1xufVxuXG5leHBvcnQgaW50ZXJmYWNlIERyYXdhYmxlIHtcbiAgZW5hYmxlZDogYm9vbGVhbjsgLy8gYWxsb3dzIFNWRyBkcmF3aW5nc1xuICBlcmFzZU9uQ2xpY2s6IGJvb2xlYW47XG4gIG9uQ2hhbmdlPzogKHNoYXBlczogRHJhd1NoYXBlW10pID0+IHZvaWQ7XG4gIHNoYXBlczogRHJhd1NoYXBlW107IC8vIHVzZXIgc2hhcGVzXG4gIGF1dG9TaGFwZXM6IERyYXdTaGFwZVtdOyAvLyBjb21wdXRlciBzaGFwZXNcbiAgY3VycmVudD86IERyYXdDdXJyZW50O1xuICBicnVzaGVzOiBEcmF3QnJ1c2hlcztcbiAgLy8gZHJhd2FibGUgU1ZHIHBpZWNlczsgdXNlZCBmb3IgY3Jhenlob3VzZSBkcm9wXG4gIHBpZWNlczoge1xuICAgIGJhc2VVcmw6IHN0cmluZ1xuICB9XG59XG5cbmV4cG9ydCBpbnRlcmZhY2UgRHJhd0N1cnJlbnQge1xuICBvcmlnOiBjZy5LZXk7IC8vIG9yaWcga2V5IG9mIGRyYXdpbmdcbiAgZGVzdD86IGNnLktleTsgLy8gc3F1YXJlIGJlaW5nIG1vdXNlZCBvdmVyLCBpZiAhPSBvcmlnXG4gIGRlc3RQcmV2PzogY2cuS2V5OyAvLyBzcXVhcmUgcHJldmlvdXNseSBtb3VzZWQgb3ZlclxuICBwb3M6IGNnLk51bWJlclBhaXI7IC8vIHJlbGF0aXZlIGN1cnJlbnQgcG9zaXRpb25cbiAgYnJ1c2g6IHN0cmluZzsgLy8gYnJ1c2ggbmFtZSBmb3Igc2hhcGVcbn1cblxuY29uc3QgYnJ1c2hlcyA9IFsnZ3JlZW4nLCAncmVkJywgJ2JsdWUnLCAneWVsbG93J107XG5cbmV4cG9ydCBmdW5jdGlvbiBzdGFydChzdGF0ZTogU3RhdGUsIGU6IGNnLk1vdWNoRXZlbnQpOiB2b2lkIHtcbiAgaWYgKGUudG91Y2hlcyAmJiBlLnRvdWNoZXMubGVuZ3RoID4gMSkgcmV0dXJuOyAvLyBzdXBwb3J0IG9uZSBmaW5nZXIgdG91Y2ggb25seVxuICBlLnN0b3BQcm9wYWdhdGlvbigpO1xuICBlLnByZXZlbnREZWZhdWx0KCk7XG4gIGNhbmNlbE1vdmUoc3RhdGUpO1xuICBjb25zdCBwb3NpdGlvbiA9IGV2ZW50UG9zaXRpb24oZSkgYXMgY2cuTnVtYmVyUGFpcjtcbiAgY29uc3Qgb3JpZyA9IGdldEtleUF0RG9tUG9zKHBvc2l0aW9uLCBzdGF0ZS5vcmllbnRhdGlvbiA9PT0gJ3doaXRlJywgc3RhdGUuZG9tLmJvdW5kcygpKTtcbiAgaWYgKCFvcmlnKSByZXR1cm47XG4gIHN0YXRlLmRyYXdhYmxlLmN1cnJlbnQgPSB7XG4gICAgb3JpZzogb3JpZyxcbiAgICBkZXN0OiBvcmlnLCAvLyB3aWxsIGltbWVkaWF0ZWx5IGJlIHNldCB0byB1bmRlZmluZWQgYnkgcHJvY2Vzc0RyYXcsIHRyaWdnZXJpbmcgcmVkcmF3XG4gICAgcG9zOiBwb3NpdGlvbixcbiAgICBicnVzaDogZXZlbnRCcnVzaChlKVxuICB9O1xuICBwcm9jZXNzRHJhdyhzdGF0ZSk7XG59XG5cbmV4cG9ydCBmdW5jdGlvbiBwcm9jZXNzRHJhdyhzdGF0ZTogU3RhdGUpOiB2b2lkIHtcbiAgcmFmKCgpID0+IHtcbiAgICBjb25zdCBjdXIgPSBzdGF0ZS5kcmF3YWJsZS5jdXJyZW50O1xuICAgIGlmIChjdXIpIHtcbiAgICAgIGNvbnN0IGRlc3QgPSBnZXRLZXlBdERvbVBvcyhjdXIucG9zLCBzdGF0ZS5vcmllbnRhdGlvbiA9PT0gJ3doaXRlJywgc3RhdGUuZG9tLmJvdW5kcygpKTtcbiAgICAgIGNvbnN0IG5ld0Rlc3QgPSAoY3VyLm9yaWcgPT09IGRlc3QpID8gdW5kZWZpbmVkIDogZGVzdDtcbiAgICAgIGlmIChuZXdEZXN0ICE9PSBjdXIuZGVzdCkge1xuICAgICAgICBjdXIuZGVzdCA9IG5ld0Rlc3Q7XG4gICAgICAgIHN0YXRlLmRvbS5yZWRyYXdOb3coKTtcbiAgICAgIH1cbiAgICAgIHByb2Nlc3NEcmF3KHN0YXRlKTtcbiAgICB9XG4gIH0pO1xufVxuXG5leHBvcnQgZnVuY3Rpb24gbW92ZShzdGF0ZTogU3RhdGUsIGU6IGNnLk1vdWNoRXZlbnQpOiB2b2lkIHtcbiAgaWYgKHN0YXRlLmRyYXdhYmxlLmN1cnJlbnQpIHN0YXRlLmRyYXdhYmxlLmN1cnJlbnQucG9zID0gZXZlbnRQb3NpdGlvbihlKSBhcyBjZy5OdW1iZXJQYWlyO1xufVxuXG5leHBvcnQgZnVuY3Rpb24gZW5kKHN0YXRlOiBTdGF0ZSk6IHZvaWQge1xuICBjb25zdCBjdXIgPSBzdGF0ZS5kcmF3YWJsZS5jdXJyZW50O1xuICBpZiAoIWN1cikgcmV0dXJuO1xuICBpZiAoY3VyLmRlc3QgJiYgY3VyLmRlc3QgIT09IGN1ci5vcmlnKSBhZGRMaW5lKHN0YXRlLmRyYXdhYmxlLCBjdXIsIGN1ci5kZXN0KTtcbiAgZWxzZSBhZGRDaXJjbGUoc3RhdGUuZHJhd2FibGUsIGN1cik7XG4gIGNhbmNlbChzdGF0ZSk7XG59XG5cbmV4cG9ydCBmdW5jdGlvbiBjYW5jZWwoc3RhdGU6IFN0YXRlKTogdm9pZCB7XG4gIGlmIChzdGF0ZS5kcmF3YWJsZS5jdXJyZW50KSB7XG4gICAgc3RhdGUuZHJhd2FibGUuY3VycmVudCA9IHVuZGVmaW5lZDtcbiAgICBzdGF0ZS5kb20ucmVkcmF3KCk7XG4gIH1cbn1cblxuZXhwb3J0IGZ1bmN0aW9uIGNsZWFyKHN0YXRlOiBTdGF0ZSk6IHZvaWQge1xuICBpZiAoc3RhdGUuZHJhd2FibGUuc2hhcGVzLmxlbmd0aCkge1xuICAgIHN0YXRlLmRyYXdhYmxlLnNoYXBlcyA9IFtdO1xuICAgIHN0YXRlLmRvbS5yZWRyYXcoKTtcbiAgICBvbkNoYW5nZShzdGF0ZS5kcmF3YWJsZSk7XG4gIH1cbn1cblxuZnVuY3Rpb24gZXZlbnRCcnVzaChlOiBjZy5Nb3VjaEV2ZW50KTogc3RyaW5nIHtcbiAgY29uc3QgYTogbnVtYmVyID0gZS5zaGlmdEtleSAmJiBpc1JpZ2h0QnV0dG9uKGUpID8gMSA6IDA7XG4gIGNvbnN0IGI6IG51bWJlciA9IGUuYWx0S2V5ID8gMiA6IDA7XG4gIHJldHVybiBicnVzaGVzW2EgKyBiXTtcbn1cblxuZnVuY3Rpb24gbm90PEE+KGY6IChhOiBBKSA9PiBib29sZWFuKTogKGE6IEEpID0+IGJvb2xlYW4ge1xuICByZXR1cm4gKHg6IEEpID0+ICFmKHgpO1xufVxuXG5mdW5jdGlvbiBhZGRDaXJjbGUoZHJhd2FibGU6IERyYXdhYmxlLCBjdXI6IERyYXdDdXJyZW50KTogdm9pZCB7XG4gIGNvbnN0IG9yaWcgPSBjdXIub3JpZztcbiAgY29uc3Qgc2FtZUNpcmNsZSA9IChzOiBEcmF3U2hhcGUpID0+IHMub3JpZyA9PT0gb3JpZyAmJiAhcy5kZXN0O1xuICBjb25zdCBzaW1pbGFyID0gZHJhd2FibGUuc2hhcGVzLmZpbHRlcihzYW1lQ2lyY2xlKVswXTtcbiAgaWYgKHNpbWlsYXIpIGRyYXdhYmxlLnNoYXBlcyA9IGRyYXdhYmxlLnNoYXBlcy5maWx0ZXIobm90KHNhbWVDaXJjbGUpKTtcbiAgaWYgKCFzaW1pbGFyIHx8IHNpbWlsYXIuYnJ1c2ggIT09IGN1ci5icnVzaCkgZHJhd2FibGUuc2hhcGVzLnB1c2goe1xuICAgIGJydXNoOiBjdXIuYnJ1c2gsXG4gICAgb3JpZzogb3JpZ1xuICB9KTtcbiAgb25DaGFuZ2UoZHJhd2FibGUpO1xufVxuXG5mdW5jdGlvbiBhZGRMaW5lKGRyYXdhYmxlOiBEcmF3YWJsZSwgY3VyOiBEcmF3Q3VycmVudCwgZGVzdDogY2cuS2V5KTogdm9pZCB7XG4gIGNvbnN0IG9yaWcgPSBjdXIub3JpZztcbiAgY29uc3Qgc2FtZUxpbmUgPSAoczogRHJhd1NoYXBlKSA9PiB7XG4gICAgcmV0dXJuICEhcy5kZXN0ICYmICgocy5vcmlnID09PSBvcmlnICYmIHMuZGVzdCA9PT0gZGVzdCkgfHwgKHMuZGVzdCA9PT0gb3JpZyAmJiBzLm9yaWcgPT09IGRlc3QpKTtcbiAgfTtcbiAgY29uc3QgZXhpc3RzID0gZHJhd2FibGUuc2hhcGVzLmZpbHRlcihzYW1lTGluZSkubGVuZ3RoID4gMDtcbiAgaWYgKGV4aXN0cykgZHJhd2FibGUuc2hhcGVzID0gZHJhd2FibGUuc2hhcGVzLmZpbHRlcihub3Qoc2FtZUxpbmUpKTtcbiAgZWxzZSBkcmF3YWJsZS5zaGFwZXMucHVzaCh7XG4gICAgYnJ1c2g6IGN1ci5icnVzaCxcbiAgICBvcmlnOiBvcmlnLFxuICAgIGRlc3Q6IGRlc3RcbiAgfSk7XG4gIG9uQ2hhbmdlKGRyYXdhYmxlKTtcbn1cblxuZnVuY3Rpb24gb25DaGFuZ2UoZHJhd2FibGU6IERyYXdhYmxlKTogdm9pZCB7XG4gIGlmIChkcmF3YWJsZS5vbkNoYW5nZSkgZHJhd2FibGUub25DaGFuZ2UoZHJhd2FibGUuc2hhcGVzKTtcbn1cbiIsImltcG9ydCB7IFN0YXRlIH0gZnJvbSAnLi9zdGF0ZSdcbmltcG9ydCAqIGFzIGRyYWcgZnJvbSAnLi9kcmFnJ1xuaW1wb3J0ICogYXMgZHJhdyBmcm9tICcuL2RyYXcnXG5pbXBvcnQgeyBpc1JpZ2h0QnV0dG9uLCByYWYgfSBmcm9tICcuL3V0aWwnXG5pbXBvcnQgKiBhcyBjZyBmcm9tICcuL3R5cGVzJ1xuXG50eXBlIE1vdWNoQmluZCA9IChlOiBjZy5Nb3VjaEV2ZW50KSA9PiB2b2lkO1xudHlwZSBTdGF0ZU1vdWNoQmluZCA9IChkOiBTdGF0ZSwgZTogY2cuTW91Y2hFdmVudCkgPT4gdm9pZDtcblxuZXhwb3J0IGZ1bmN0aW9uIGJpbmRCb2FyZChzOiBTdGF0ZSk6IHZvaWQge1xuXG4gIGNvbnN0IGJvYXJkRWwgPSBzLmRvbS5lbGVtZW50cy5ib2FyZDtcblxuICBpZiAoIXMudmlld09ubHkpIHtcbiAgICBbJ3RvdWNoc3RhcnQnLCAnbW91c2Vkb3duJ10uZm9yRWFjaChldiA9PiBib2FyZEVsLmFkZEV2ZW50TGlzdGVuZXIoZXYsIHN0YXJ0RHJhZ09yRHJhdyhzKSkpO1xuICB9XG5cbiAgaWYgKHMuZGlzYWJsZUNvbnRleHRNZW51IHx8IHMuZHJhd2FibGUuZW5hYmxlZCkge1xuICAgIGJvYXJkRWwuYWRkRXZlbnRMaXN0ZW5lcignY29udGV4dG1lbnUnLCBlID0+IHtcbiAgICAgIGUucHJldmVudERlZmF1bHQoKTtcbiAgICAgIHJldHVybiBmYWxzZTtcbiAgICB9KTtcbiAgfVxufVxuXG4vLyByZXR1cm5zIHRoZSB1bmJpbmQgZnVuY3Rpb25cbmV4cG9ydCBmdW5jdGlvbiBiaW5kRG9jdW1lbnQoczogU3RhdGUsIHJlZHJhd0FsbDogY2cuUmVkcmF3KTogY2cuVW5iaW5kIHtcblxuICBjb25zdCBvbm1vdmU6IE1vdWNoQmluZCA9IGRyYWdPckRyYXcocywgZHJhZy5tb3ZlLCBkcmF3Lm1vdmUpO1xuICBjb25zdCBvbmVuZDogTW91Y2hCaW5kID0gZHJhZ09yRHJhdyhzLCBkcmFnLmVuZCwgZHJhdy5lbmQpO1xuXG4gIGNvbnN0IHVuYmluZHM6IGNnLlVuYmluZFtdID0gW107XG5cbiAgaWYgKCFzLnZpZXdPbmx5KSB7XG4gICAgWyd0b3VjaG1vdmUnLCAnbW91c2Vtb3ZlJ10uZm9yRWFjaChldiA9PiB1bmJpbmRzLnB1c2godW5iaW5kYWJsZShkb2N1bWVudCwgZXYsIG9ubW92ZSkpKTtcbiAgICBbJ3RvdWNoZW5kJywgJ21vdXNldXAnXS5mb3JFYWNoKGV2ID0+IHVuYmluZHMucHVzaCh1bmJpbmRhYmxlKGRvY3VtZW50LCBldiwgb25lbmQpKSk7XG4gIH1cblxuICBjb25zdCBvblJlc2l6ZSA9ICgpID0+IHtcbiAgICBzLmRvbS5ib3VuZHMuY2xlYXIoKTtcbiAgICByYWYocmVkcmF3QWxsKTtcbiAgfTtcbiAgaWYgKHMucmVzaXphYmxlKSB1bmJpbmRzLnB1c2godW5iaW5kYWJsZShkb2N1bWVudC5ib2R5LCAnY2hlc3Nncm91bmQucmVzaXplJywgb25SZXNpemUpKTtcblxuICBjb25zdCBvblNjcm9sbCA9ICgpID0+IHMuZG9tLmJvdW5kcy5jbGVhcigpO1xuICB1bmJpbmRzLnB1c2godW5iaW5kYWJsZSh3aW5kb3csICdzY3JvbGwnLCBvblNjcm9sbCwgeyBwYXNzaXZlOiB0cnVlIH0pKTtcbiAgdW5iaW5kcy5wdXNoKHVuYmluZGFibGUod2luZG93LCAncmVzaXplJywgb25TY3JvbGwsIHsgcGFzc2l2ZTogdHJ1ZSB9KSk7XG5cbiAgcmV0dXJuICgpID0+IHVuYmluZHMuZm9yRWFjaChmID0+IGYoKSk7XG59XG5cbmZ1bmN0aW9uIHVuYmluZGFibGUoZWw6IEV2ZW50VGFyZ2V0LCBldmVudE5hbWU6IHN0cmluZywgY2FsbGJhY2s6IE1vdWNoQmluZCwgb3B0aW9ucz86IGFueSk6IGNnLlVuYmluZCB7XG4gIGVsLmFkZEV2ZW50TGlzdGVuZXIoZXZlbnROYW1lLCBjYWxsYmFjaywgb3B0aW9ucyk7XG4gIHJldHVybiAoKSA9PiBlbC5yZW1vdmVFdmVudExpc3RlbmVyKGV2ZW50TmFtZSwgY2FsbGJhY2spO1xufVxuXG5mdW5jdGlvbiBzdGFydERyYWdPckRyYXcoczogU3RhdGUpOiBNb3VjaEJpbmQge1xuICByZXR1cm4gZSA9PiB7XG4gICAgaWYgKHMuZHJhZ2dhYmxlLmN1cnJlbnQpIGRyYWcuY2FuY2VsKHMpO1xuICAgIGVsc2UgaWYgKHMuZHJhd2FibGUuY3VycmVudCkgZHJhdy5jYW5jZWwocyk7XG4gICAgZWxzZSBpZiAoZS5zaGlmdEtleSB8fCBpc1JpZ2h0QnV0dG9uKGUpKSB7IGlmIChzLmRyYXdhYmxlLmVuYWJsZWQpIGRyYXcuc3RhcnQocywgZSk7IH1cbiAgICBlbHNlIGlmICghcy52aWV3T25seSkgZHJhZy5zdGFydChzLCBlKTtcbiAgfTtcbn1cblxuZnVuY3Rpb24gZHJhZ09yRHJhdyhzOiBTdGF0ZSwgd2l0aERyYWc6IFN0YXRlTW91Y2hCaW5kLCB3aXRoRHJhdzogU3RhdGVNb3VjaEJpbmQpOiBNb3VjaEJpbmQge1xuICByZXR1cm4gZSA9PiB7XG4gICAgaWYgKGUuc2hpZnRLZXkgfHwgaXNSaWdodEJ1dHRvbihlKSkgeyBpZiAocy5kcmF3YWJsZS5lbmFibGVkKSB3aXRoRHJhdyhzLCBlKTsgfVxuICAgIGVsc2UgaWYgKCFzLnZpZXdPbmx5KSB3aXRoRHJhZyhzLCBlKTtcbiAgfTtcbn1cbiIsImltcG9ydCB7IFN0YXRlIH0gZnJvbSAnLi9zdGF0ZSdcbmltcG9ydCB7IEtleSB9IGZyb20gJy4vdHlwZXMnXG5cbmV4cG9ydCBkZWZhdWx0IGZ1bmN0aW9uIGV4cGxvc2lvbihzdGF0ZTogU3RhdGUsIGtleXM6IEtleVtdKTogdm9pZCB7XG4gIHN0YXRlLmV4cGxvZGluZyA9IHtcbiAgICBzdGFnZTogMSxcbiAgICBrZXlzOiBrZXlzXG4gIH07XG4gIHN0YXRlLmRvbS5yZWRyYXcoKTtcbiAgc2V0VGltZW91dCgoKSA9PiB7XG4gICAgc2V0U3RhZ2Uoc3RhdGUsIDIpO1xuICAgIHNldFRpbWVvdXQoKCkgPT4gc2V0U3RhZ2Uoc3RhdGUsIHVuZGVmaW5lZCksIDEyMCk7XG4gIH0sIDEyMCk7XG59XG5cbmZ1bmN0aW9uIHNldFN0YWdlKHN0YXRlOiBTdGF0ZSwgc3RhZ2U6IG51bWJlciB8IHVuZGVmaW5lZCk6IHZvaWQge1xuICBpZiAoc3RhdGUuZXhwbG9kaW5nKSB7XG4gICAgaWYgKHN0YWdlKSBzdGF0ZS5leHBsb2Rpbmcuc3RhZ2UgPSBzdGFnZTtcbiAgICBlbHNlIHN0YXRlLmV4cGxvZGluZyA9IHVuZGVmaW5lZDtcbiAgICBzdGF0ZS5kb20ucmVkcmF3KCk7XG4gIH1cbn1cbiIsImltcG9ydCB7IHBvczJrZXksIGludlJhbmtzIH0gZnJvbSAnLi91dGlsJ1xuaW1wb3J0ICogYXMgY2cgZnJvbSAnLi90eXBlcydcblxuZXhwb3J0IGNvbnN0IGluaXRpYWw6IGNnLkZFTiA9ICdybmJxa2Juci9wcHBwcHBwcC84LzgvOC84L1BQUFBQUFBQL1JOQlFLQk5SJztcblxuY29uc3Qgcm9sZXM6IHsgW2xldHRlcjogc3RyaW5nXTogY2cuUm9sZSB9ID0geyBwOiAncGF3bicsIHI6ICdyb29rJywgbjogJ2tuaWdodCcsIGI6ICdiaXNob3AnLCBxOiAncXVlZW4nLCBrOiAna2luZycgfTtcblxuY29uc3QgbGV0dGVycyA9IHsgcGF3bjogJ3AnLCByb29rOiAncicsIGtuaWdodDogJ24nLCBiaXNob3A6ICdiJywgcXVlZW46ICdxJywga2luZzogJ2snIH07XG5cblxuZXhwb3J0IGZ1bmN0aW9uIHJlYWQoZmVuOiBjZy5GRU4pOiBjZy5QaWVjZXMge1xuICBpZiAoZmVuID09PSAnc3RhcnQnKSBmZW4gPSBpbml0aWFsO1xuICBjb25zdCBwaWVjZXM6IGNnLlBpZWNlcyA9IHt9O1xuICBsZXQgcm93OiBudW1iZXIgPSA4O1xuICBsZXQgY29sOiBudW1iZXIgPSAwO1xuICBmb3IgKGNvbnN0IGMgb2YgZmVuKSB7XG4gICAgc3dpdGNoIChjKSB7XG4gICAgICBjYXNlICcgJzogcmV0dXJuIHBpZWNlcztcbiAgICAgIGNhc2UgJy8nOlxuICAgICAgICAtLXJvdztcbiAgICAgICAgaWYgKHJvdyA9PT0gMCkgcmV0dXJuIHBpZWNlcztcbiAgICAgICAgY29sID0gMDtcbiAgICAgICAgYnJlYWs7XG4gICAgICBjYXNlICd+JzpcbiAgICAgICAgcGllY2VzW3BvczJrZXkoW2NvbCwgcm93XSldLnByb21vdGVkID0gdHJ1ZTtcbiAgICAgICAgYnJlYWs7XG4gICAgICBkZWZhdWx0OlxuICAgICAgICBjb25zdCBuYiA9IGMuY2hhckNvZGVBdCgwKTtcbiAgICAgICAgaWYgKG5iIDwgNTcpIGNvbCArPSBuYiAtIDQ4O1xuICAgICAgICBlbHNlIHtcbiAgICAgICAgICArK2NvbDtcbiAgICAgICAgICBjb25zdCByb2xlID0gYy50b0xvd2VyQ2FzZSgpO1xuICAgICAgICAgIHBpZWNlc1twb3Mya2V5KFtjb2wsIHJvd10pXSA9IHtcbiAgICAgICAgICAgIHJvbGU6IHJvbGVzW3JvbGVdLFxuICAgICAgICAgICAgY29sb3I6IChjID09PSByb2xlID8gJ2JsYWNrJyA6ICd3aGl0ZScpIGFzIGNnLkNvbG9yXG4gICAgICAgICAgfTtcbiAgICAgICAgfVxuICAgIH1cbiAgfVxuICByZXR1cm4gcGllY2VzO1xufVxuXG5leHBvcnQgZnVuY3Rpb24gd3JpdGUocGllY2VzOiBjZy5QaWVjZXMpOiBjZy5GRU4ge1xuICBsZXQgcGllY2U6IGNnLlBpZWNlLCBsZXR0ZXI6IHN0cmluZztcbiAgcmV0dXJuIGludlJhbmtzLm1hcCh5ID0+IGNnLnJhbmtzLm1hcCh4ID0+IHtcbiAgICAgIHBpZWNlID0gcGllY2VzW3BvczJrZXkoW3gsIHldKV07XG4gICAgICBpZiAocGllY2UpIHtcbiAgICAgICAgbGV0dGVyID0gbGV0dGVyc1twaWVjZS5yb2xlXTtcbiAgICAgICAgcmV0dXJuIHBpZWNlLmNvbG9yID09PSAnd2hpdGUnID8gbGV0dGVyLnRvVXBwZXJDYXNlKCkgOiBsZXR0ZXI7XG4gICAgICB9IGVsc2UgcmV0dXJuICcxJztcbiAgICB9KS5qb2luKCcnKVxuICApLmpvaW4oJy8nKS5yZXBsYWNlKC8xezIsfS9nLCBzID0+IHMubGVuZ3RoLnRvU3RyaW5nKCkpO1xufVxuIiwibW9kdWxlLmV4cG9ydHMgPSByZXF1aXJlKFwiLi9jaGVzc2dyb3VuZFwiKS5DaGVzc2dyb3VuZDtcbiIsImltcG9ydCAqIGFzIHV0aWwgZnJvbSAnLi91dGlsJ1xuaW1wb3J0ICogYXMgY2cgZnJvbSAnLi90eXBlcydcblxudHlwZSBNb2JpbGl0eSA9ICh4MTpudW1iZXIsIHkxOm51bWJlciwgeDI6bnVtYmVyLCB5MjpudW1iZXIpID0+IGJvb2xlYW47XG5cbmZ1bmN0aW9uIGRpZmYoYTogbnVtYmVyLCBiOm51bWJlcik6bnVtYmVyIHtcbiAgcmV0dXJuIE1hdGguYWJzKGEgLSBiKTtcbn1cblxuZnVuY3Rpb24gcGF3bihjb2xvcjogY2cuQ29sb3IpOiBNb2JpbGl0eSB7XG4gIHJldHVybiAoeDEsIHkxLCB4MiwgeTIpID0+IGRpZmYoeDEsIHgyKSA8IDIgJiYgKFxuICAgIGNvbG9yID09PSAnd2hpdGUnID8gKFxuICAgICAgLy8gYWxsb3cgMiBzcXVhcmVzIGZyb20gMSBhbmQgOCwgZm9yIGhvcmRlXG4gICAgICB5MiA9PT0geTEgKyAxIHx8ICh5MSA8PSAyICYmIHkyID09PSAoeTEgKyAyKSAmJiB4MSA9PT0geDIpXG4gICAgKSA6IChcbiAgICAgIHkyID09PSB5MSAtIDEgfHwgKHkxID49IDcgJiYgeTIgPT09ICh5MSAtIDIpICYmIHgxID09PSB4MilcbiAgICApXG4gICk7XG59XG5cbmNvbnN0IGtuaWdodDogTW9iaWxpdHkgPSAoeDEsIHkxLCB4MiwgeTIpID0+IHtcbiAgY29uc3QgeGQgPSBkaWZmKHgxLCB4Mik7XG4gIGNvbnN0IHlkID0gZGlmZih5MSwgeTIpO1xuICByZXR1cm4gKHhkID09PSAxICYmIHlkID09PSAyKSB8fCAoeGQgPT09IDIgJiYgeWQgPT09IDEpO1xufVxuXG5jb25zdCBiaXNob3A6IE1vYmlsaXR5ID0gKHgxLCB5MSwgeDIsIHkyKSA9PiB7XG4gIHJldHVybiBkaWZmKHgxLCB4MikgPT09IGRpZmYoeTEsIHkyKTtcbn1cblxuY29uc3Qgcm9vazogTW9iaWxpdHkgPSAoeDEsIHkxLCB4MiwgeTIpID0+IHtcbiAgcmV0dXJuIHgxID09PSB4MiB8fCB5MSA9PT0geTI7XG59XG5cbmNvbnN0IHF1ZWVuOiBNb2JpbGl0eSA9ICh4MSwgeTEsIHgyLCB5MikgPT4ge1xuICByZXR1cm4gYmlzaG9wKHgxLCB5MSwgeDIsIHkyKSB8fCByb29rKHgxLCB5MSwgeDIsIHkyKTtcbn1cblxuZnVuY3Rpb24ga2luZyhjb2xvcjogY2cuQ29sb3IsIHJvb2tGaWxlczogbnVtYmVyW10sIGNhbkNhc3RsZTogYm9vbGVhbik6IE1vYmlsaXR5IHtcbiAgcmV0dXJuICh4MSwgeTEsIHgyLCB5MikgID0+IChcbiAgICBkaWZmKHgxLCB4MikgPCAyICYmIGRpZmYoeTEsIHkyKSA8IDJcbiAgKSB8fCAoXG4gICAgY2FuQ2FzdGxlICYmIHkxID09PSB5MiAmJiB5MSA9PT0gKGNvbG9yID09PSAnd2hpdGUnID8gMSA6IDgpICYmIChcbiAgICAgICh4MSA9PT0gNSAmJiAoeDIgPT09IDMgfHwgeDIgPT09IDcpKSB8fCB1dGlsLmNvbnRhaW5zWChyb29rRmlsZXMsIHgyKVxuICAgIClcbiAgKTtcbn1cblxuZnVuY3Rpb24gcm9va0ZpbGVzT2YocGllY2VzOiBjZy5QaWVjZXMsIGNvbG9yOiBjZy5Db2xvcikge1xuICBsZXQgcGllY2U6IGNnLlBpZWNlO1xuICByZXR1cm4gT2JqZWN0LmtleXMocGllY2VzKS5maWx0ZXIoa2V5ID0+IHtcbiAgICBwaWVjZSA9IHBpZWNlc1trZXldO1xuICAgIHJldHVybiBwaWVjZSAmJiBwaWVjZS5jb2xvciA9PT0gY29sb3IgJiYgcGllY2Uucm9sZSA9PT0gJ3Jvb2snO1xuICB9KS5tYXAoKGtleTogY2cuS2V5KSA9PiB1dGlsLmtleTJwb3Moa2V5KVswXSk7XG59XG5cbmV4cG9ydCBkZWZhdWx0IGZ1bmN0aW9uIHByZW1vdmUocGllY2VzOiBjZy5QaWVjZXMsIGtleTogY2cuS2V5LCBjYW5DYXN0bGU6IGJvb2xlYW4pOiBjZy5LZXlbXSB7XG4gIGNvbnN0IHBpZWNlID0gcGllY2VzW2tleV0sXG4gIHBvcyA9IHV0aWwua2V5MnBvcyhrZXkpO1xuICBsZXQgbW9iaWxpdHk6IE1vYmlsaXR5O1xuICBzd2l0Y2ggKHBpZWNlLnJvbGUpIHtcbiAgICBjYXNlICdwYXduJzpcbiAgICAgIG1vYmlsaXR5ID0gcGF3bihwaWVjZS5jb2xvcik7XG4gICAgICBicmVhaztcbiAgICBjYXNlICdrbmlnaHQnOlxuICAgICAgbW9iaWxpdHkgPSBrbmlnaHQ7XG4gICAgICBicmVhaztcbiAgICBjYXNlICdiaXNob3AnOlxuICAgICAgbW9iaWxpdHkgPSBiaXNob3A7XG4gICAgICBicmVhaztcbiAgICBjYXNlICdyb29rJzpcbiAgICAgIG1vYmlsaXR5ID0gcm9vaztcbiAgICAgIGJyZWFrO1xuICAgIGNhc2UgJ3F1ZWVuJzpcbiAgICAgIG1vYmlsaXR5ID0gcXVlZW47XG4gICAgICBicmVhaztcbiAgICBjYXNlICdraW5nJzpcbiAgICAgIG1vYmlsaXR5ID0ga2luZyhwaWVjZS5jb2xvciwgcm9va0ZpbGVzT2YocGllY2VzLCBwaWVjZS5jb2xvciksIGNhbkNhc3RsZSk7XG4gICAgICBicmVhaztcbiAgfVxuICByZXR1cm4gdXRpbC5hbGxLZXlzLm1hcCh1dGlsLmtleTJwb3MpLmZpbHRlcihwb3MyID0+IHtcbiAgICByZXR1cm4gKHBvc1swXSAhPT0gcG9zMlswXSB8fCBwb3NbMV0gIT09IHBvczJbMV0pICYmIG1vYmlsaXR5KHBvc1swXSwgcG9zWzFdLCBwb3MyWzBdLCBwb3MyWzFdKTtcbiAgfSkubWFwKHV0aWwucG9zMmtleSk7XG59O1xuIiwiaW1wb3J0IHsgU3RhdGUgfSBmcm9tICcuL3N0YXRlJ1xuaW1wb3J0IHsga2V5MnBvcywgdHJhbnNsYXRlLCBwb3NUb1RyYW5zbGF0ZSwgY3JlYXRlRWwgfSBmcm9tICcuL3V0aWwnXG5pbXBvcnQgeyBBbmltQ3VycmVudCwgQW5pbVZlY3RvcnMsIEFuaW1WZWN0b3IsIEFuaW1GYWRpbmdzIH0gZnJvbSAnLi9hbmltJ1xuaW1wb3J0IHsgRHJhZ0N1cnJlbnQgfSBmcm9tICcuL2RyYWcnXG5pbXBvcnQgKiBhcyBjZyBmcm9tICcuL3R5cGVzJ1xuXG4vLyBgJGNvbG9yICRyb2xlYFxudHlwZSBQaWVjZU5hbWUgPSBzdHJpbmc7XG5cbmludGVyZmFjZSBTYW1lUGllY2VzIHsgW2tleTogc3RyaW5nXTogYm9vbGVhbiB9XG5pbnRlcmZhY2UgU2FtZVNxdWFyZXMgeyBba2V5OiBzdHJpbmddOiBib29sZWFuIH1cbmludGVyZmFjZSBNb3ZlZFBpZWNlcyB7IFtwaWVjZU5hbWU6IHN0cmluZ106IGNnLlBpZWNlTm9kZVtdIH1cbmludGVyZmFjZSBNb3ZlZFNxdWFyZXMgeyBbY2xhc3NOYW1lOiBzdHJpbmddOiBjZy5TcXVhcmVOb2RlW10gfVxuaW50ZXJmYWNlIFNxdWFyZUNsYXNzZXMgeyBba2V5OiBzdHJpbmddOiBzdHJpbmcgfVxuXG4vLyBwb3J0ZWQgZnJvbSBodHRwczovL2dpdGh1Yi5jb20vdmVsb2NlL2xpY2hvYmlsZS9ibG9iL21hc3Rlci9zcmMvanMvY2hlc3Nncm91bmQvdmlldy5qc1xuLy8gaW4gY2FzZSBvZiBidWdzLCBibGFtZSBAdmVsb2NlXG5leHBvcnQgZGVmYXVsdCBmdW5jdGlvbiByZW5kZXIoczogU3RhdGUpOiB2b2lkIHtcbiAgY29uc3QgYXNXaGl0ZTogYm9vbGVhbiA9IHMub3JpZW50YXRpb24gPT09ICd3aGl0ZScsXG4gIGJvdW5kczogQ2xpZW50UmVjdCA9IHMuZG9tLmJvdW5kcygpLFxuICBib2FyZEVsOiBIVE1MRWxlbWVudCA9IHMuZG9tLmVsZW1lbnRzLmJvYXJkLFxuICBwaWVjZXM6IGNnLlBpZWNlcyA9IHMucGllY2VzLFxuICBjdXJBbmltOiBBbmltQ3VycmVudCB8IHVuZGVmaW5lZCA9IHMuYW5pbWF0aW9uLmN1cnJlbnQsXG4gIGFuaW1zOiBBbmltVmVjdG9ycyA9IGN1ckFuaW0gPyBjdXJBbmltLnBsYW4uYW5pbXMgOiB7fSxcbiAgZmFkaW5nczogQW5pbUZhZGluZ3MgPSBjdXJBbmltID8gY3VyQW5pbS5wbGFuLmZhZGluZ3MgOiB7fSxcbiAgY3VyRHJhZzogRHJhZ0N1cnJlbnQgfCB1bmRlZmluZWQgPSBzLmRyYWdnYWJsZS5jdXJyZW50LFxuICBzcXVhcmVzOiBTcXVhcmVDbGFzc2VzID0gY29tcHV0ZVNxdWFyZUNsYXNzZXMocyksXG4gIHNhbWVQaWVjZXM6IFNhbWVQaWVjZXMgPSB7fSxcbiAgc2FtZVNxdWFyZXM6IFNhbWVTcXVhcmVzID0ge30sXG4gIG1vdmVkUGllY2VzOiBNb3ZlZFBpZWNlcyA9IHt9LFxuICBtb3ZlZFNxdWFyZXM6IE1vdmVkU3F1YXJlcyA9IHt9LFxuICBwaWVjZXNLZXlzOiBjZy5LZXlbXSA9IE9iamVjdC5rZXlzKHBpZWNlcykgYXMgY2cuS2V5W10sXG4gIHRyYW5zZm9ybSA9IHMuYnJvd3Nlci50cmFuc2Zvcm07XG4gIGxldCBrOiBjZy5LZXksXG4gIHA6IGNnLlBpZWNlIHwgdW5kZWZpbmVkLFxuICBlbDogY2cuUGllY2VOb2RlIHwgY2cuU3F1YXJlTm9kZSxcbiAgcGllY2VBdEtleTogY2cuUGllY2UgfCB1bmRlZmluZWQsXG4gIGVsUGllY2VOYW1lOiBQaWVjZU5hbWUsXG4gIHRyYW5zbGF0aW9uOiBjZy5OdW1iZXJQYWlyLFxuICBhbmltOiBBbmltVmVjdG9yIHwgdW5kZWZpbmVkLFxuICBmYWRpbmc6IGNnLlBpZWNlIHwgdW5kZWZpbmVkLFxuICBwTXZkc2V0OiBjZy5QaWVjZU5vZGVbXSxcbiAgcE12ZDogY2cuUGllY2VOb2RlIHwgdW5kZWZpbmVkLFxuICBzTXZkc2V0OiBjZy5TcXVhcmVOb2RlW10sXG4gIHNNdmQ6IGNnLlNxdWFyZU5vZGUgfCB1bmRlZmluZWQ7XG5cbiAgLy8gd2FsayBvdmVyIGFsbCBib2FyZCBkb20gZWxlbWVudHMsIGFwcGx5IGFuaW1hdGlvbnMgYW5kIGZsYWcgbW92ZWQgcGllY2VzXG4gIGVsID0gYm9hcmRFbC5maXJzdENoaWxkIGFzIGNnLlBpZWNlTm9kZSB8IGNnLlNxdWFyZU5vZGU7XG4gIHdoaWxlIChlbCkge1xuICAgIGsgPSBlbC5jZ0tleTtcbiAgICBpZiAoaXNQaWVjZU5vZGUoZWwpKSB7XG4gICAgICBwaWVjZUF0S2V5ID0gcGllY2VzW2tdO1xuICAgICAgYW5pbSA9IGFuaW1zW2tdO1xuICAgICAgZmFkaW5nID0gZmFkaW5nc1trXTtcbiAgICAgIGVsUGllY2VOYW1lID0gZWwuY2dQaWVjZTtcbiAgICAgIC8vIGlmIHBpZWNlIG5vdCBiZWluZyBkcmFnZ2VkIGFueW1vcmUsIHJlbW92ZSBkcmFnZ2luZyBzdHlsZVxuICAgICAgaWYgKGVsLmNnRHJhZ2dpbmcgJiYgKCFjdXJEcmFnIHx8IGN1ckRyYWcub3JpZyAhPT0gaykpIHtcbiAgICAgICAgZWwuY2xhc3NMaXN0LnJlbW92ZSgnZHJhZ2dpbmcnKTtcbiAgICAgICAgdHJhbnNmb3JtKGVsLCB0cmFuc2xhdGUocG9zVG9UcmFuc2xhdGUoa2V5MnBvcyhrKSwgYXNXaGl0ZSwgYm91bmRzKSkpO1xuICAgICAgICBlbC5jZ0RyYWdnaW5nID0gZmFsc2U7XG4gICAgICB9XG4gICAgICAvLyByZW1vdmUgZmFkaW5nIGNsYXNzIGlmIGl0IHN0aWxsIHJlbWFpbnNcbiAgICAgIGlmICghZmFkaW5nICYmIGVsLmNnRmFkaW5nKSB7XG4gICAgICAgIGVsLmNnRmFkaW5nID0gZmFsc2U7XG4gICAgICAgIGVsLmNsYXNzTGlzdC5yZW1vdmUoJ2ZhZGluZycpO1xuICAgICAgfVxuICAgICAgLy8gdGhlcmUgaXMgbm93IGEgcGllY2UgYXQgdGhpcyBkb20ga2V5XG4gICAgICBpZiAocGllY2VBdEtleSkge1xuICAgICAgICAvLyBjb250aW51ZSBhbmltYXRpb24gaWYgYWxyZWFkeSBhbmltYXRpbmcgYW5kIHNhbWUgcGllY2VcbiAgICAgICAgLy8gKG90aGVyd2lzZSBpdCBjb3VsZCBhbmltYXRlIGEgY2FwdHVyZWQgcGllY2UpXG4gICAgICAgIGlmIChhbmltICYmIGVsLmNnQW5pbWF0aW5nICYmIGVsUGllY2VOYW1lID09PSBwaWVjZU5hbWVPZihwaWVjZUF0S2V5KSkge1xuICAgICAgICAgIHRyYW5zbGF0aW9uID0gcG9zVG9UcmFuc2xhdGUoa2V5MnBvcyhrKSwgYXNXaGl0ZSwgYm91bmRzKTtcbiAgICAgICAgICB0cmFuc2xhdGlvblswXSArPSBhbmltWzFdWzBdO1xuICAgICAgICAgIHRyYW5zbGF0aW9uWzFdICs9IGFuaW1bMV1bMV07XG4gICAgICAgICAgdHJhbnNmb3JtKGVsLCB0cmFuc2xhdGUodHJhbnNsYXRpb24pKTtcbiAgICAgICAgICBlbC5jbGFzc0xpc3QuYWRkKCdhbmltJyk7XG4gICAgICAgIH0gZWxzZSBpZiAoZWwuY2dBbmltYXRpbmcpIHtcbiAgICAgICAgICB0cmFuc2xhdGlvbiA9IHBvc1RvVHJhbnNsYXRlKGtleTJwb3MoayksIGFzV2hpdGUsIGJvdW5kcyk7XG4gICAgICAgICAgdHJhbnNmb3JtKGVsLCB0cmFuc2xhdGUodHJhbnNsYXRpb24pKTtcbiAgICAgICAgICBlbC5jZ0FuaW1hdGluZyA9IGZhbHNlO1xuICAgICAgICAgIGVsLmNsYXNzTGlzdC5yZW1vdmUoJ2FuaW0nKTtcbiAgICAgICAgfVxuICAgICAgICAvLyBzYW1lIHBpZWNlOiBmbGFnIGFzIHNhbWVcbiAgICAgICAgaWYgKGVsUGllY2VOYW1lID09PSBwaWVjZU5hbWVPZihwaWVjZUF0S2V5KSAmJiAoIWZhZGluZyB8fCAhZWwuY2dGYWRpbmcpKSB7XG4gICAgICAgICAgc2FtZVBpZWNlc1trXSA9IHRydWU7XG4gICAgICAgIH1cbiAgICAgICAgLy8gZGlmZmVyZW50IHBpZWNlOiBmbGFnIGFzIG1vdmVkIHVubGVzcyBpdCBpcyBhIGZhZGluZyBwaWVjZVxuICAgICAgICBlbHNlIHtcbiAgICAgICAgICBpZiAoZmFkaW5nICYmIGVsUGllY2VOYW1lID09PSBwaWVjZU5hbWVPZihmYWRpbmcpKSB7XG4gICAgICAgICAgICBlbC5jbGFzc0xpc3QuYWRkKCdmYWRpbmcnKTtcbiAgICAgICAgICAgIGVsLmNnRmFkaW5nID0gdHJ1ZTtcbiAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgaWYgKG1vdmVkUGllY2VzW2VsUGllY2VOYW1lXSkgbW92ZWRQaWVjZXNbZWxQaWVjZU5hbWVdLnB1c2goZWwpO1xuICAgICAgICAgICAgZWxzZSBtb3ZlZFBpZWNlc1tlbFBpZWNlTmFtZV0gPSBbZWxdO1xuICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgICAgfVxuICAgICAgLy8gbm8gcGllY2U6IGZsYWcgYXMgbW92ZWRcbiAgICAgIGVsc2Uge1xuICAgICAgICBpZiAobW92ZWRQaWVjZXNbZWxQaWVjZU5hbWVdKSBtb3ZlZFBpZWNlc1tlbFBpZWNlTmFtZV0ucHVzaChlbCk7XG4gICAgICAgIGVsc2UgbW92ZWRQaWVjZXNbZWxQaWVjZU5hbWVdID0gW2VsXTtcbiAgICAgIH1cbiAgICB9XG4gICAgZWxzZSBpZiAoaXNTcXVhcmVOb2RlKGVsKSkge1xuICAgICAgY29uc3QgY24gPSBlbC5jbGFzc05hbWU7XG4gICAgICBpZiAoc3F1YXJlc1trXSA9PT0gY24pIHNhbWVTcXVhcmVzW2tdID0gdHJ1ZTtcbiAgICAgIGVsc2UgaWYgKG1vdmVkU3F1YXJlc1tjbl0pIG1vdmVkU3F1YXJlc1tjbl0ucHVzaChlbCk7XG4gICAgICBlbHNlIG1vdmVkU3F1YXJlc1tjbl0gPSBbZWxdO1xuICAgIH1cbiAgICBlbCA9IGVsLm5leHRTaWJsaW5nIGFzIGNnLlBpZWNlTm9kZSB8IGNnLlNxdWFyZU5vZGU7XG4gIH1cblxuICAvLyB3YWxrIG92ZXIgYWxsIHNxdWFyZXMgaW4gY3VycmVudCBzZXQsIGFwcGx5IGRvbSBjaGFuZ2VzIHRvIG1vdmVkIHNxdWFyZXNcbiAgLy8gb3IgYXBwZW5kIG5ldyBzcXVhcmVzXG4gIGZvciAoY29uc3Qgc2sgaW4gc3F1YXJlcykge1xuICAgIGlmICghc2FtZVNxdWFyZXNbc2tdKSB7XG4gICAgICBzTXZkc2V0ID0gbW92ZWRTcXVhcmVzW3NxdWFyZXNbc2tdXTtcbiAgICAgIHNNdmQgPSBzTXZkc2V0ICYmIHNNdmRzZXQucG9wKCk7XG4gICAgICB0cmFuc2xhdGlvbiA9IHBvc1RvVHJhbnNsYXRlKGtleTJwb3Moc2sgYXMgY2cuS2V5KSwgYXNXaGl0ZSwgYm91bmRzKTtcbiAgICAgIGlmIChzTXZkKSB7XG4gICAgICAgIHNNdmQuY2dLZXkgPSBzayBhcyBjZy5LZXk7XG4gICAgICAgIHRyYW5zZm9ybShzTXZkLCB0cmFuc2xhdGUodHJhbnNsYXRpb24pKTtcbiAgICAgIH1cbiAgICAgIGVsc2Uge1xuICAgICAgICBib2FyZEVsLmluc2VydEJlZm9yZShcbiAgICAgICAgICByZW5kZXJTcXVhcmVEb20oc2sgYXMgY2cuS2V5LCBzcXVhcmVzW3NrXSwgdHJhbnNsYXRpb24sIHRyYW5zZm9ybSksXG4gICAgICAgICAgYm9hcmRFbC5maXJzdENoaWxkKTtcbiAgICAgIH1cbiAgICB9XG4gIH1cblxuICAvLyB3YWxrIG92ZXIgYWxsIHBpZWNlcyBpbiBjdXJyZW50IHNldCwgYXBwbHkgZG9tIGNoYW5nZXMgdG8gbW92ZWQgcGllY2VzXG4gIC8vIG9yIGFwcGVuZCBuZXcgcGllY2VzXG4gIGZvciAoY29uc3QgaiBpbiBwaWVjZXNLZXlzKSB7XG4gICAgayA9IHBpZWNlc0tleXNbal07XG4gICAgcCA9IHBpZWNlc1trXTtcbiAgICBhbmltID0gYW5pbXNba107XG4gICAgaWYgKCFzYW1lUGllY2VzW2tdKSB7XG4gICAgICBwTXZkc2V0ID0gbW92ZWRQaWVjZXNbcGllY2VOYW1lT2YocCldO1xuICAgICAgcE12ZCA9IHBNdmRzZXQgJiYgcE12ZHNldC5wb3AoKTtcbiAgICAgIC8vIGEgc2FtZSBwaWVjZSB3YXMgbW92ZWRcbiAgICAgIGlmIChwTXZkKSB7XG4gICAgICAgIC8vIGFwcGx5IGRvbSBjaGFuZ2VzXG4gICAgICAgIHBNdmQuY2dLZXkgPSBrO1xuICAgICAgICBpZiAocE12ZC5jZ0ZhZGluZykge1xuICAgICAgICAgIHBNdmQuY2xhc3NMaXN0LnJlbW92ZSgnZmFkaW5nJyk7XG4gICAgICAgICAgcE12ZC5jZ0ZhZGluZyA9IGZhbHNlO1xuICAgICAgICB9XG4gICAgICAgIGNvbnN0IHBvcyA9IGtleTJwb3Moayk7XG4gICAgICAgIGlmIChzLmFkZFBpZWNlWkluZGV4KSBwTXZkLnN0eWxlLnpJbmRleCA9IHBvc1pJbmRleChwb3MsIGFzV2hpdGUpO1xuICAgICAgICB0cmFuc2xhdGlvbiA9IHBvc1RvVHJhbnNsYXRlKHBvcywgYXNXaGl0ZSwgYm91bmRzKTtcbiAgICAgICAgaWYgKGFuaW0pIHtcbiAgICAgICAgICBwTXZkLmNnQW5pbWF0aW5nID0gdHJ1ZTtcbiAgICAgICAgICBwTXZkLmNsYXNzTGlzdC5hZGQoJ2FuaW0nKTtcbiAgICAgICAgICB0cmFuc2xhdGlvblswXSArPSBhbmltWzFdWzBdO1xuICAgICAgICAgIHRyYW5zbGF0aW9uWzFdICs9IGFuaW1bMV1bMV07XG4gICAgICAgIH1cbiAgICAgICAgdHJhbnNmb3JtKHBNdmQsIHRyYW5zbGF0ZSh0cmFuc2xhdGlvbikpO1xuICAgICAgfVxuICAgICAgLy8gbm8gcGllY2UgaW4gbW92ZWQgb2JqOiBpbnNlcnQgdGhlIG5ldyBwaWVjZVxuICAgICAgLy8gbmV3OiBhc3N1bWUgdGhlIG5ldyBwaWVjZSBpcyBub3QgYmVpbmcgZHJhZ2dlZFxuICAgICAgLy8gbWlnaHQgYmUgYSBiYWQgaWRlYVxuICAgICAgZWxzZSB7XG4gICAgICAgIGJvYXJkRWwuYXBwZW5kQ2hpbGQocmVuZGVyUGllY2VEb20ocywgcCwgaywgYXNXaGl0ZSwgYW5pbSwgYm91bmRzKSk7XG4gICAgICB9XG4gICAgfVxuICB9XG5cbiAgLy8gcmVtb3ZlIGFueSBlbGVtZW50IHRoYXQgcmVtYWlucyBpbiB0aGUgbW92ZWQgc2V0c1xuICBmb3IgKGNvbnN0IGkgaW4gbW92ZWRQaWVjZXMpIHJlbW92ZU5vZGVzKHMsIG1vdmVkUGllY2VzW2ldKTtcbiAgZm9yIChjb25zdCBpIGluIG1vdmVkU3F1YXJlcykgcmVtb3ZlTm9kZXMocywgbW92ZWRTcXVhcmVzW2ldKTtcbn1cblxuZnVuY3Rpb24gaXNQaWVjZU5vZGUoZWw6IGNnLlBpZWNlTm9kZSB8IGNnLlNxdWFyZU5vZGUpOiBlbCBpcyBjZy5QaWVjZU5vZGUge1xuICByZXR1cm4gZWwudGFnTmFtZSA9PT0gJ1BJRUNFJztcbn1cbmZ1bmN0aW9uIGlzU3F1YXJlTm9kZShlbDogY2cuUGllY2VOb2RlIHwgY2cuU3F1YXJlTm9kZSk6IGVsIGlzIGNnLlNxdWFyZU5vZGUge1xuICByZXR1cm4gZWwudGFnTmFtZSA9PT0gJ1NRVUFSRSc7XG59XG5cbmZ1bmN0aW9uIHJlbW92ZU5vZGVzKHM6IFN0YXRlLCBub2RlczogSFRNTEVsZW1lbnRbXSk6IHZvaWQge1xuICBmb3IgKGNvbnN0IGkgaW4gbm9kZXMpIHMuZG9tLmVsZW1lbnRzLmJvYXJkLnJlbW92ZUNoaWxkKG5vZGVzW2ldKTtcbn1cblxuZnVuY3Rpb24gcmVuZGVyU3F1YXJlRG9tKGtleTogY2cuS2V5LCBjbGFzc05hbWU6IHN0cmluZywgdHJhbnNsYXRpb246IGNnLk51bWJlclBhaXIsIHRyYW5zZm9ybTogY2cuVHJhbnNmb3JtKTogY2cuU3F1YXJlTm9kZSB7XG4gIGNvbnN0IHMgPSBjcmVhdGVFbCgnc3F1YXJlJywgY2xhc3NOYW1lKSBhcyBjZy5TcXVhcmVOb2RlO1xuICBzLmNnS2V5ID0ga2V5O1xuICB0cmFuc2Zvcm0ocywgdHJhbnNsYXRlKHRyYW5zbGF0aW9uKSk7XG4gIHJldHVybiBzO1xufVxuXG5mdW5jdGlvbiByZW5kZXJQaWVjZURvbShzOiBTdGF0ZSwgcGllY2U6IGNnLlBpZWNlLCBrZXk6IGNnLktleSwgYXNXaGl0ZTogYm9vbGVhbiwgYW5pbTogQW5pbVZlY3RvciB8IHVuZGVmaW5lZCwgYm91bmRzOiBDbGllbnRSZWN0KTogY2cuUGllY2VOb2RlIHtcblxuICBjb25zdCBwaWVjZU5hbWUgPSBwaWVjZU5hbWVPZihwaWVjZSksXG4gIHAgPSBjcmVhdGVFbCgncGllY2UnLCBwaWVjZU5hbWUpIGFzIGNnLlBpZWNlTm9kZSxcbiAgcG9zID0ga2V5MnBvcyhrZXkpO1xuXG4gIHAuY2dQaWVjZSA9IHBpZWNlTmFtZTtcbiAgcC5jZ0tleSA9IGtleTtcblxuICBjb25zdCB0cmFuc2xhdGlvbiA9IHBvc1RvVHJhbnNsYXRlKHBvcywgYXNXaGl0ZSwgYm91bmRzKTtcbiAgaWYgKGFuaW0pIHtcbiAgICBwLmNnQW5pbWF0aW5nID0gdHJ1ZTtcbiAgICB0cmFuc2xhdGlvblswXSArPSBhbmltWzFdWzBdO1xuICAgIHRyYW5zbGF0aW9uWzFdICs9IGFuaW1bMV1bMV07XG4gIH1cbiAgcy5icm93c2VyLnRyYW5zZm9ybShwLCB0cmFuc2xhdGUodHJhbnNsYXRpb24pKTtcblxuICBpZiAocy5hZGRQaWVjZVpJbmRleCkgcC5zdHlsZS56SW5kZXggPSBwb3NaSW5kZXgocG9zLCBhc1doaXRlKTtcblxuICByZXR1cm4gcDtcbn1cblxuZnVuY3Rpb24gcG9zWkluZGV4KHBvczogY2cuUG9zLCBhc1doaXRlOiBib29sZWFuKTogc3RyaW5nIHtcbiAgbGV0IHogPSAyICsgKHBvc1sxXSAtIDEpICogOCArICg4IC0gcG9zWzBdKTtcbiAgaWYgKGFzV2hpdGUpIHogPSA2NyAtIHo7XG4gIHJldHVybiB6ICsgJyc7XG59XG5cbmZ1bmN0aW9uIHBpZWNlTmFtZU9mKHBpZWNlOiBjZy5QaWVjZSk6IHN0cmluZyB7XG4gIHJldHVybiBgJHtwaWVjZS5jb2xvcn0gJHtwaWVjZS5yb2xlfWA7XG59XG5cbmZ1bmN0aW9uIGNvbXB1dGVTcXVhcmVDbGFzc2VzKHM6IFN0YXRlKTogU3F1YXJlQ2xhc3NlcyB7XG4gIGNvbnN0IHNxdWFyZXM6IFNxdWFyZUNsYXNzZXMgPSB7fTtcbiAgbGV0IGk6IGFueSwgazogY2cuS2V5O1xuICBpZiAocy5sYXN0TW92ZSAmJiBzLmhpZ2hsaWdodC5sYXN0TW92ZSkgZm9yIChpIGluIHMubGFzdE1vdmUpIHtcbiAgICBhZGRTcXVhcmUoc3F1YXJlcywgcy5sYXN0TW92ZVtpXSwgJ2xhc3QtbW92ZScpO1xuICB9XG4gIGlmIChzLmNoZWNrICYmIHMuaGlnaGxpZ2h0LmNoZWNrKSBhZGRTcXVhcmUoc3F1YXJlcywgcy5jaGVjaywgJ2NoZWNrJyk7XG4gIGlmIChzLnNlbGVjdGVkKSB7XG4gICAgYWRkU3F1YXJlKHNxdWFyZXMsIHMuc2VsZWN0ZWQsICdzZWxlY3RlZCcpO1xuICAgIGlmIChzLm1vdmFibGUuc2hvd0Rlc3RzKSB7XG4gICAgICBjb25zdCBkZXN0cyA9IHMubW92YWJsZS5kZXN0cyAmJiBzLm1vdmFibGUuZGVzdHNbcy5zZWxlY3RlZF07XG4gICAgICBpZiAoZGVzdHMpIGZvciAoaSBpbiBkZXN0cykge1xuICAgICAgICBrID0gZGVzdHNbaV07XG4gICAgICAgIGFkZFNxdWFyZShzcXVhcmVzLCBrLCAnbW92ZS1kZXN0JyArIChzLnBpZWNlc1trXSA/ICcgb2MnIDogJycpKTtcbiAgICAgIH1cbiAgICAgIGNvbnN0IHBEZXN0cyA9IHMucHJlbW92YWJsZS5kZXN0cztcbiAgICAgIGlmIChwRGVzdHMpIGZvciAoaSBpbiBwRGVzdHMpIHtcbiAgICAgICAgayA9IHBEZXN0c1tpXTtcbiAgICAgICAgYWRkU3F1YXJlKHNxdWFyZXMsIGssICdwcmVtb3ZlLWRlc3QnICsgKHMucGllY2VzW2tdID8gJyBvYycgOiAnJykpO1xuICAgICAgfVxuICAgIH1cbiAgfVxuICBjb25zdCBwcmVtb3ZlID0gcy5wcmVtb3ZhYmxlLmN1cnJlbnQ7XG4gIGlmIChwcmVtb3ZlKSBmb3IgKGkgaW4gcHJlbW92ZSkgYWRkU3F1YXJlKHNxdWFyZXMsIHByZW1vdmVbaV0sICdjdXJyZW50LXByZW1vdmUnKTtcbiAgZWxzZSBpZiAocy5wcmVkcm9wcGFibGUuY3VycmVudCkgYWRkU3F1YXJlKHNxdWFyZXMsIHMucHJlZHJvcHBhYmxlLmN1cnJlbnQua2V5LCAnY3VycmVudC1wcmVtb3ZlJyk7XG5cbiAgY29uc3QgbyA9IHMuZXhwbG9kaW5nO1xuICBpZiAobykgZm9yIChpIGluIG8ua2V5cykgYWRkU3F1YXJlKHNxdWFyZXMsIG8ua2V5c1tpXSwgJ2V4cGxvZGluZycgKyBvLnN0YWdlKTtcblxuICByZXR1cm4gc3F1YXJlcztcbn1cblxuZnVuY3Rpb24gYWRkU3F1YXJlKHNxdWFyZXM6IFNxdWFyZUNsYXNzZXMsIGtleTogY2cuS2V5LCBrbGFzczogc3RyaW5nKTogdm9pZCB7XG4gIGlmIChzcXVhcmVzW2tleV0pIHNxdWFyZXNba2V5XSArPSAnICcgKyBrbGFzcztcbiAgZWxzZSBzcXVhcmVzW2tleV0gPSBrbGFzcztcbn1cbiIsImltcG9ydCAqIGFzIGZlbiBmcm9tICcuL2ZlbidcbmltcG9ydCB7IEFuaW1DdXJyZW50IH0gZnJvbSAnLi9hbmltJ1xuaW1wb3J0IHsgRHJhZ0N1cnJlbnQgfSBmcm9tICcuL2RyYWcnXG5pbXBvcnQgeyBEcmF3YWJsZSB9IGZyb20gJy4vZHJhdydcbmltcG9ydCB7IHRpbWVyIH0gZnJvbSAnLi91dGlsJ1xuaW1wb3J0ICogYXMgY2cgZnJvbSAnLi90eXBlcyc7XG5cbmV4cG9ydCBpbnRlcmZhY2UgU3RhdGUge1xuICBwaWVjZXM6IGNnLlBpZWNlcztcbiAgb3JpZW50YXRpb246IGNnLkNvbG9yOyAvLyBib2FyZCBvcmllbnRhdGlvbi4gd2hpdGUgfCBibGFja1xuICB0dXJuQ29sb3I6IGNnLkNvbG9yOyAvLyB0dXJuIHRvIHBsYXkuIHdoaXRlIHwgYmxhY2tcbiAgY2hlY2s/OiBjZy5LZXk7IC8vIHNxdWFyZSBjdXJyZW50bHkgaW4gY2hlY2sgXCJhMlwiXG4gIGxhc3RNb3ZlPzogY2cuS2V5W107IC8vIHNxdWFyZXMgcGFydCBvZiB0aGUgbGFzdCBtb3ZlIFtcImMzXCI7IFwiYzRcIl1cbiAgc2VsZWN0ZWQ/OiBjZy5LZXk7IC8vIHNxdWFyZSBjdXJyZW50bHkgc2VsZWN0ZWQgXCJhMVwiXG4gIGNvb3JkaW5hdGVzOiBib29sZWFuOyAvLyBpbmNsdWRlIGNvb3JkcyBhdHRyaWJ1dGVzXG4gIGF1dG9DYXN0bGU6IGJvb2xlYW47IC8vIGltbWVkaWF0ZWx5IGNvbXBsZXRlIHRoZSBjYXN0bGUgYnkgbW92aW5nIHRoZSByb29rIGFmdGVyIGtpbmcgbW92ZVxuICB2aWV3T25seTogYm9vbGVhbjsgLy8gZG9uJ3QgYmluZCBldmVudHM6IHRoZSB1c2VyIHdpbGwgbmV2ZXIgYmUgYWJsZSB0byBtb3ZlIHBpZWNlcyBhcm91bmRcbiAgZGlzYWJsZUNvbnRleHRNZW51OiBib29sZWFuOyAvLyBiZWNhdXNlIHdobyBuZWVkcyBhIGNvbnRleHQgbWVudSBvbiBhIGNoZXNzYm9hcmRcbiAgcmVzaXphYmxlOiBib29sZWFuOyAvLyBsaXN0ZW5zIHRvIGNoZXNzZ3JvdW5kLnJlc2l6ZSBvbiBkb2N1bWVudC5ib2R5IHRvIGNsZWFyIGJvdW5kcyBjYWNoZVxuICBhZGRQaWVjZVpJbmRleDogYm9vbGVhbjsgLy8gYWRkcyB6LWluZGV4IHZhbHVlcyB0byBwaWVjZXMgKGZvciAzRClcbiAgcGllY2VLZXk6IGJvb2xlYW47IC8vIGFkZCBhIGRhdGEta2V5IGF0dHJpYnV0ZSB0byBwaWVjZSBlbGVtZW50c1xuICBoaWdobGlnaHQ6IHtcbiAgICBsYXN0TW92ZTogYm9vbGVhbjsgLy8gYWRkIGxhc3QtbW92ZSBjbGFzcyB0byBzcXVhcmVzXG4gICAgY2hlY2s6IGJvb2xlYW47IC8vIGFkZCBjaGVjayBjbGFzcyB0byBzcXVhcmVzXG4gIH07XG4gIGFuaW1hdGlvbjoge1xuICAgIGVuYWJsZWQ6IGJvb2xlYW47XG4gICAgZHVyYXRpb246IG51bWJlcjtcbiAgICBjdXJyZW50PzogQW5pbUN1cnJlbnQ7XG4gIH07XG4gIG1vdmFibGU6IHtcbiAgICBmcmVlOiBib29sZWFuOyAvLyBhbGwgbW92ZXMgYXJlIHZhbGlkIC0gYm9hcmQgZWRpdG9yXG4gICAgY29sb3I/OiBjZy5Db2xvciB8ICdib3RoJzsgLy8gY29sb3IgdGhhdCBjYW4gbW92ZS4gd2hpdGUgfCBibGFjayB8IGJvdGhcbiAgICBkZXN0cz86IGNnLkRlc3RzOyAvLyB2YWxpZCBtb3Zlcy4ge1wiYTJcIiBbXCJhM1wiIFwiYTRcIl0gXCJiMVwiIFtcImEzXCIgXCJjM1wiXX1cbiAgICBzaG93RGVzdHM6IGJvb2xlYW47IC8vIHdoZXRoZXIgdG8gYWRkIHRoZSBtb3ZlLWRlc3QgY2xhc3Mgb24gc3F1YXJlc1xuICAgIGV2ZW50czoge1xuICAgICAgYWZ0ZXI/OiAob3JpZzogY2cuS2V5LCBkZXN0OiBjZy5LZXksIG1ldGFkYXRhOiBjZy5Nb3ZlTWV0YWRhdGEpID0+IHZvaWQ7IC8vIGNhbGxlZCBhZnRlciB0aGUgbW92ZSBoYXMgYmVlbiBwbGF5ZWRcbiAgICAgIGFmdGVyTmV3UGllY2U/OiAocm9sZTogY2cuUm9sZSwgcG9zOiBjZy5Qb3MpID0+IHZvaWQ7IC8vIGNhbGxlZCBhZnRlciBhIG5ldyBwaWVjZSBpcyBkcm9wcGVkIG9uIHRoZSBib2FyZFxuICAgIH07XG4gICAgcm9va0Nhc3RsZTogYm9vbGVhbiAvLyBjYXN0bGUgYnkgbW92aW5nIHRoZSBraW5nIHRvIHRoZSByb29rXG4gIH07XG4gIHByZW1vdmFibGU6IHtcbiAgICBlbmFibGVkOiBib29sZWFuOyAvLyBhbGxvdyBwcmVtb3ZlcyBmb3IgY29sb3IgdGhhdCBjYW4gbm90IG1vdmVcbiAgICBzaG93RGVzdHM6IGJvb2xlYW47IC8vIHdoZXRoZXIgdG8gYWRkIHRoZSBwcmVtb3ZlLWRlc3QgY2xhc3Mgb24gc3F1YXJlc1xuICAgIGNhc3RsZTogYm9vbGVhbjsgLy8gd2hldGhlciB0byBhbGxvdyBraW5nIGNhc3RsZSBwcmVtb3Zlc1xuICAgIGRlc3RzPzogY2cuS2V5W107IC8vIHByZW1vdmUgZGVzdGluYXRpb25zIGZvciB0aGUgY3VycmVudCBzZWxlY3Rpb25cbiAgICBjdXJyZW50PzogY2cuS2V5UGFpcjsgLy8ga2V5cyBvZiB0aGUgY3VycmVudCBzYXZlZCBwcmVtb3ZlIFtcImUyXCIgXCJlNFwiXVxuICAgIGV2ZW50czoge1xuICAgICAgc2V0PzogKG9yaWc6IGNnLktleSwgZGVzdDogY2cuS2V5KSA9PiB2b2lkOyAvLyBjYWxsZWQgYWZ0ZXIgdGhlIHByZW1vdmUgaGFzIGJlZW4gc2V0XG4gICAgICB1bnNldD86ICgpID0+IHZvaWQ7ICAvLyBjYWxsZWQgYWZ0ZXIgdGhlIHByZW1vdmUgaGFzIGJlZW4gdW5zZXRcbiAgICB9XG4gIH07XG4gIHByZWRyb3BwYWJsZToge1xuICAgIGVuYWJsZWQ6IGJvb2xlYW47IC8vIGFsbG93IHByZWRyb3BzIGZvciBjb2xvciB0aGF0IGNhbiBub3QgbW92ZVxuICAgIGN1cnJlbnQ/OiB7IC8vIGN1cnJlbnQgc2F2ZWQgcHJlZHJvcCB7cm9sZTogJ2tuaWdodCc7IGtleTogJ2U0J31cbiAgICAgIHJvbGU6IGNnLlJvbGU7XG4gICAgICBrZXk6IGNnLktleVxuICAgIH07XG4gICAgZXZlbnRzOiB7XG4gICAgICBzZXQ/OiAocm9sZTogY2cuUm9sZSwga2V5OiBjZy5LZXkpID0+IHZvaWQ7IC8vIGNhbGxlZCBhZnRlciB0aGUgcHJlZHJvcCBoYXMgYmVlbiBzZXRcbiAgICAgIHVuc2V0PzogKCkgPT4gdm9pZDsgLy8gY2FsbGVkIGFmdGVyIHRoZSBwcmVkcm9wIGhhcyBiZWVuIHVuc2V0XG4gICAgfVxuICB9O1xuICBkcmFnZ2FibGU6IHtcbiAgICBlbmFibGVkOiBib29sZWFuOyAvLyBhbGxvdyBtb3ZlcyAmIHByZW1vdmVzIHRvIHVzZSBkcmFnJ24gZHJvcFxuICAgIGRpc3RhbmNlOiBudW1iZXI7IC8vIG1pbmltdW0gZGlzdGFuY2UgdG8gaW5pdGlhdGUgYSBkcmFnOyBpbiBwaXhlbHNcbiAgICBhdXRvRGlzdGFuY2U6IGJvb2xlYW47IC8vIGxldHMgY2hlc3Nncm91bmQgc2V0IGRpc3RhbmNlIHRvIHplcm8gd2hlbiB1c2VyIGRyYWdzIHBpZWNlc1xuICAgIGNlbnRlclBpZWNlOiBib29sZWFuOyAvLyBjZW50ZXIgdGhlIHBpZWNlIG9uIGN1cnNvciBhdCBkcmFnIHN0YXJ0XG4gICAgc2hvd0dob3N0OiBib29sZWFuOyAvLyBzaG93IGdob3N0IG9mIHBpZWNlIGJlaW5nIGRyYWdnZWRcbiAgICBkZWxldGVPbkRyb3BPZmY6IGJvb2xlYW47IC8vIGRlbGV0ZSBhIHBpZWNlIHdoZW4gaXQgaXMgZHJvcHBlZCBvZmYgdGhlIGJvYXJkXG4gICAgY3VycmVudD86IERyYWdDdXJyZW50O1xuICB9O1xuICBzZWxlY3RhYmxlOiB7XG4gICAgLy8gZGlzYWJsZSB0byBlbmZvcmNlIGRyYWdnaW5nIG92ZXIgY2xpY2stY2xpY2sgbW92ZVxuICAgIGVuYWJsZWQ6IGJvb2xlYW5cbiAgfTtcbiAgc3RhdHM6IHtcbiAgICAvLyB3YXMgbGFzdCBwaWVjZSBkcmFnZ2VkIG9yIGNsaWNrZWQ/XG4gICAgLy8gbmVlZHMgZGVmYXVsdCB0byBmYWxzZSBmb3IgdG91Y2hcbiAgICBkcmFnZ2VkOiBib29sZWFuLFxuICAgIGN0cmxLZXk/OiBib29sZWFuXG4gIH07XG4gIGV2ZW50czoge1xuICAgIGNoYW5nZT86ICgpID0+IHZvaWQ7IC8vIGNhbGxlZCBhZnRlciB0aGUgc2l0dWF0aW9uIGNoYW5nZXMgb24gdGhlIGJvYXJkXG4gICAgLy8gY2FsbGVkIGFmdGVyIGEgcGllY2UgaGFzIGJlZW4gbW92ZWQuXG4gICAgLy8gY2FwdHVyZWRQaWVjZSBpcyB1bmRlZmluZWQgb3IgbGlrZSB7Y29sb3I6ICd3aGl0ZSc7ICdyb2xlJzogJ3F1ZWVuJ31cbiAgICBtb3ZlPzogKG9yaWc6IGNnLktleSwgZGVzdDogY2cuS2V5LCBjYXB0dXJlZFBpZWNlPzogY2cuUGllY2UpID0+IHZvaWQ7XG4gICAgZHJvcE5ld1BpZWNlPzogKHJvbGU6IGNnLlJvbGUsIHBvczogY2cuUG9zKSA9PiB2b2lkO1xuICAgIHNlbGVjdD86IChrZXk6IGNnLktleSkgPT4gdm9pZCAvLyBjYWxsZWQgd2hlbiBhIHNxdWFyZSBpcyBzZWxlY3RlZFxuICB9O1xuICBpdGVtcz86IChwb3M6IGNnLlBvcywga2V5OiBjZy5LZXkpID0+IGFueSB8IHVuZGVmaW5lZDsgLy8gaXRlbXMgb24gdGhlIGJvYXJkIHsgcmVuZGVyOiBrZXkgLT4gdmRvbSB9XG4gIGRyYXdhYmxlOiBEcmF3YWJsZSxcbiAgZXhwbG9kaW5nPzogY2cuRXhwbG9kaW5nO1xuICBicm93c2VyOiBjZy5Ccm93c2VyLFxuICBkb206IGNnLkRvbSxcbiAgaG9sZDogY2cuVGltZXJcbn1cblxuZXhwb3J0IGZ1bmN0aW9uIGRlZmF1bHRzKCk6IFBhcnRpYWw8U3RhdGU+IHtcbiAgcmV0dXJuIHtcbiAgICBwaWVjZXM6IGZlbi5yZWFkKGZlbi5pbml0aWFsKSxcbiAgICBvcmllbnRhdGlvbjogJ3doaXRlJyxcbiAgICB0dXJuQ29sb3I6ICd3aGl0ZScsXG4gICAgY29vcmRpbmF0ZXM6IHRydWUsXG4gICAgYXV0b0Nhc3RsZTogdHJ1ZSxcbiAgICB2aWV3T25seTogZmFsc2UsXG4gICAgZGlzYWJsZUNvbnRleHRNZW51OiBmYWxzZSxcbiAgICByZXNpemFibGU6IHRydWUsXG4gICAgYWRkUGllY2VaSW5kZXg6IGZhbHNlLFxuICAgIHBpZWNlS2V5OiBmYWxzZSxcbiAgICBoaWdobGlnaHQ6IHtcbiAgICAgIGxhc3RNb3ZlOiB0cnVlLFxuICAgICAgY2hlY2s6IHRydWVcbiAgICB9LFxuICAgIGFuaW1hdGlvbjoge1xuICAgICAgZW5hYmxlZDogdHJ1ZSxcbiAgICAgIGR1cmF0aW9uOiAyMDBcbiAgICB9LFxuICAgIG1vdmFibGU6IHtcbiAgICAgIGZyZWU6IHRydWUsXG4gICAgICBjb2xvcjogJ2JvdGgnLFxuICAgICAgc2hvd0Rlc3RzOiB0cnVlLFxuICAgICAgZXZlbnRzOiB7fSxcbiAgICAgIHJvb2tDYXN0bGU6IHRydWVcbiAgICB9LFxuICAgIHByZW1vdmFibGU6IHtcbiAgICAgIGVuYWJsZWQ6IHRydWUsXG4gICAgICBzaG93RGVzdHM6IHRydWUsXG4gICAgICBjYXN0bGU6IHRydWUsXG4gICAgICBldmVudHM6IHt9XG4gICAgfSxcbiAgICBwcmVkcm9wcGFibGU6IHtcbiAgICAgIGVuYWJsZWQ6IGZhbHNlLFxuICAgICAgZXZlbnRzOiB7fVxuICAgIH0sXG4gICAgZHJhZ2dhYmxlOiB7XG4gICAgICBlbmFibGVkOiB0cnVlLFxuICAgICAgZGlzdGFuY2U6IDMsXG4gICAgICBhdXRvRGlzdGFuY2U6IHRydWUsXG4gICAgICBjZW50ZXJQaWVjZTogdHJ1ZSxcbiAgICAgIHNob3dHaG9zdDogdHJ1ZSxcbiAgICAgIGRlbGV0ZU9uRHJvcE9mZjogZmFsc2VcbiAgICB9LFxuICAgIHNlbGVjdGFibGU6IHtcbiAgICAgIGVuYWJsZWQ6IHRydWVcbiAgICB9LFxuICAgIHN0YXRzOiB7XG4gICAgICBkcmFnZ2VkOiAhKCdvbnRvdWNoc3RhcnQnIGluIHdpbmRvdylcbiAgICB9LFxuICAgIGV2ZW50czoge30sXG4gICAgZHJhd2FibGU6IHtcbiAgICAgIGVuYWJsZWQ6IHRydWUsXG4gICAgICBlcmFzZU9uQ2xpY2s6IHRydWUsXG4gICAgICBzaGFwZXM6IFtdLFxuICAgICAgYXV0b1NoYXBlczogW10sXG4gICAgICBicnVzaGVzOiB7XG4gICAgICAgIGdyZWVuOiB7IGtleTogJ2cnLCBjb2xvcjogJyMxNTc4MUInLCBvcGFjaXR5OiAxLCBsaW5lV2lkdGg6IDEwIH0sXG4gICAgICAgIHJlZDogeyBrZXk6ICdyJywgY29sb3I6ICcjODgyMDIwJywgb3BhY2l0eTogMSwgbGluZVdpZHRoOiAxMCB9LFxuICAgICAgICBibHVlOiB7IGtleTogJ2InLCBjb2xvcjogJyMwMDMwODgnLCBvcGFjaXR5OiAxLCBsaW5lV2lkdGg6IDEwIH0sXG4gICAgICAgIHllbGxvdzogeyBrZXk6ICd5JywgY29sb3I6ICcjZTY4ZjAwJywgb3BhY2l0eTogMSwgbGluZVdpZHRoOiAxMCB9LFxuICAgICAgICBwYWxlQmx1ZTogeyBrZXk6ICdwYicsIGNvbG9yOiAnIzAwMzA4OCcsIG9wYWNpdHk6IDAuNCwgbGluZVdpZHRoOiAxNSB9LFxuICAgICAgICBwYWxlR3JlZW46IHsga2V5OiAncGcnLCBjb2xvcjogJyMxNTc4MUInLCBvcGFjaXR5OiAwLjQsIGxpbmVXaWR0aDogMTUgfSxcbiAgICAgICAgcGFsZVJlZDogeyBrZXk6ICdwcicsIGNvbG9yOiAnIzg4MjAyMCcsIG9wYWNpdHk6IDAuNCwgbGluZVdpZHRoOiAxNSB9LFxuICAgICAgICBwYWxlR3JleTogeyBrZXk6ICdwZ3InLCBjb2xvcjogJyM0YTRhNGEnLCBvcGFjaXR5OiAwLjM1LCBsaW5lV2lkdGg6IDE1IH1cbiAgICAgIH0sXG4gICAgICBwaWVjZXM6IHtcbiAgICAgICAgYmFzZVVybDogJ2h0dHBzOi8vbGljaGVzczEub3JnL2Fzc2V0cy9waWVjZS9jYnVybmV0dC8nXG4gICAgICB9XG4gICAgfSxcbiAgICBob2xkOiB0aW1lcigpXG4gIH07XG59XG4iLCJpbXBvcnQgeyBTdGF0ZSB9IGZyb20gJy4vc3RhdGUnXG5pbXBvcnQgeyBrZXkycG9zLCBjb21wdXRlSXNUcmlkZW50IH0gZnJvbSAnLi91dGlsJ1xuaW1wb3J0IHsgRHJhd2FibGUsIERyYXdTaGFwZSwgRHJhd1NoYXBlUGllY2UsIERyYXdCcnVzaCwgRHJhd0JydXNoZXMsIERyYXdNb2RpZmllcnMgfSBmcm9tICcuL2RyYXcnXG5pbXBvcnQgKiBhcyBjZyBmcm9tICcuL3R5cGVzJ1xuXG5leHBvcnQgZnVuY3Rpb24gY3JlYXRlRWxlbWVudCh0YWdOYW1lOiBzdHJpbmcpOiBTVkdFbGVtZW50IHtcbiAgcmV0dXJuIGRvY3VtZW50LmNyZWF0ZUVsZW1lbnROUygnaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmcnLCB0YWdOYW1lKTtcbn1cblxuaW50ZXJmYWNlIFNoYXBlIHtcbiAgc2hhcGU6IERyYXdTaGFwZTtcbiAgY3VycmVudDogYm9vbGVhbjtcbiAgaGFzaDogSGFzaDtcbn1cblxuaW50ZXJmYWNlIEN1c3RvbUJydXNoZXMge1xuICBbaGFzaDogc3RyaW5nXTogRHJhd0JydXNoXG59XG5cbnR5cGUgSGFzaCA9IHN0cmluZztcblxubGV0IGlzVHJpZGVudDogYm9vbGVhbiB8IHVuZGVmaW5lZDtcbmxldCBmdWxsSGFzaFByZXY6IEhhc2ggPSAnJztcblxuZXhwb3J0IGZ1bmN0aW9uIGNsZWFyQ2FjaGUoKSB7XG4gIGZ1bGxIYXNoUHJldiA9ICcnO1xufVxuXG5leHBvcnQgZnVuY3Rpb24gcmVuZGVyU3ZnKHN0YXRlOiBTdGF0ZSwgcm9vdDogU1ZHRWxlbWVudCk6IHZvaWQge1xuXG4gIGNvbnN0IGQgPSBzdGF0ZS5kcmF3YWJsZSxcbiAgc2hhcGVzOiBTaGFwZVtdID0gZC5zaGFwZXMuY29uY2F0KGQuYXV0b1NoYXBlcykubWFwKChzOiBEcmF3U2hhcGUpID0+IHtcbiAgICByZXR1cm4ge1xuICAgICAgc2hhcGU6IHMsXG4gICAgICBjdXJyZW50OiBmYWxzZSxcbiAgICAgIGhhc2g6IHNoYXBlSGFzaChzLCBmYWxzZSlcbiAgICB9O1xuICB9KTtcbiAgaWYgKGQuY3VycmVudCkgc2hhcGVzLnB1c2goe1xuICAgIHNoYXBlOiBkLmN1cnJlbnQgYXMgRHJhd1NoYXBlLFxuICAgIGN1cnJlbnQ6IHRydWUsXG4gICAgaGFzaDogc2hhcGVIYXNoKGQuY3VycmVudCwgdHJ1ZSlcbiAgfSk7XG5cbiAgY29uc3QgZnVsbEhhc2ggPSBzaGFwZXMubWFwKHNjID0+IHNjLmhhc2gpLmpvaW4oJycpO1xuICBpZiAoZnVsbEhhc2ggPT09IGZ1bGxIYXNoUHJldikgcmV0dXJuO1xuICBmdWxsSGFzaFByZXYgPSBmdWxsSGFzaDtcblxuICBjb25zdCBkZWZzRWwgPSByb290LmZpcnN0Q2hpbGQgYXMgU1ZHRWxlbWVudDtcblxuICBzeW5jRGVmcyhkLCBzaGFwZXMsIGRlZnNFbCk7XG4gIHN5bmNTaGFwZXMoc3RhdGUsIHNoYXBlcywgZC5icnVzaGVzLCByb290LCBkZWZzRWwpO1xufVxuXG4vLyBhcHBlbmQgb25seS4gRG9uJ3QgdHJ5IHRvIHVwZGF0ZS9yZW1vdmUuXG5mdW5jdGlvbiBzeW5jRGVmcyhkOiBEcmF3YWJsZSwgc2hhcGVzOiBTaGFwZVtdLCBkZWZzRWw6IFNWR0VsZW1lbnQpIHtcbiAgY29uc3QgYnJ1c2hlczogQ3VzdG9tQnJ1c2hlcyA9IHt9O1xuICBsZXQgYnJ1c2g6IERyYXdCcnVzaDtcbiAgc2hhcGVzLmZvckVhY2gocyA9PiB7XG4gICAgaWYgKHMuc2hhcGUuZGVzdCkge1xuICAgICAgYnJ1c2ggPSBkLmJydXNoZXNbcy5zaGFwZS5icnVzaF07XG4gICAgICBpZiAocy5zaGFwZS5tb2RpZmllcnMpIGJydXNoID0gbWFrZUN1c3RvbUJydXNoKGJydXNoLCBzLnNoYXBlLm1vZGlmaWVycyk7XG4gICAgICBicnVzaGVzW2JydXNoLmtleV0gPSBicnVzaDtcbiAgICB9XG4gIH0pO1xuICBjb25zdCBrZXlzSW5Eb206IHtba2V5OiBzdHJpbmddOiBib29sZWFufSA9IHt9O1xuICBsZXQgZWw6IFNWR0VsZW1lbnQgPSBkZWZzRWwuZmlyc3RDaGlsZCBhcyBTVkdFbGVtZW50O1xuICB3aGlsZShlbCkge1xuICAgIGtleXNJbkRvbVtlbC5nZXRBdHRyaWJ1dGUoJ2NnS2V5JykgYXMgc3RyaW5nXSA9IHRydWU7XG4gICAgZWwgPSBlbC5uZXh0U2libGluZyBhcyBTVkdFbGVtZW50O1xuICB9XG4gIGZvciAobGV0IGtleSBpbiBicnVzaGVzKSB7XG4gICAgaWYgKCFrZXlzSW5Eb21ba2V5XSkgZGVmc0VsLmFwcGVuZENoaWxkKHJlbmRlck1hcmtlcihicnVzaGVzW2tleV0pKTtcbiAgfVxufVxuXG4vLyBhcHBlbmQgYW5kIHJlbW92ZSBvbmx5LiBObyB1cGRhdGVzLlxuZnVuY3Rpb24gc3luY1NoYXBlcyhzdGF0ZTogU3RhdGUsIHNoYXBlczogU2hhcGVbXSwgYnJ1c2hlczogRHJhd0JydXNoZXMsIHJvb3Q6IFNWR0VsZW1lbnQsIGRlZnNFbDogU1ZHRWxlbWVudCk6IHZvaWQge1xuICBpZiAoaXNUcmlkZW50ID09PSB1bmRlZmluZWQpIGlzVHJpZGVudCA9IGNvbXB1dGVJc1RyaWRlbnQoKTtcbiAgY29uc3QgYm91bmRzID0gc3RhdGUuZG9tLmJvdW5kcygpLFxuICBoYXNoZXNJbkRvbToge1toYXNoOiBzdHJpbmddOiBib29sZWFufSA9IHt9LFxuICB0b1JlbW92ZTogU1ZHRWxlbWVudFtdID0gW107XG4gIHNoYXBlcy5mb3JFYWNoKHNjID0+IHsgaGFzaGVzSW5Eb21bc2MuaGFzaF0gPSBmYWxzZTsgfSk7XG4gIGxldCBlbDogU1ZHRWxlbWVudCA9IGRlZnNFbC5uZXh0U2libGluZyBhcyBTVkdFbGVtZW50LCBlbEhhc2g6IEhhc2g7XG4gIHdoaWxlKGVsKSB7XG4gICAgZWxIYXNoID0gZWwuZ2V0QXR0cmlidXRlKCdjZ0hhc2gnKSBhcyBIYXNoO1xuICAgIC8vIGZvdW5kIGEgc2hhcGUgZWxlbWVudCB0aGF0J3MgaGVyZSB0byBzdGF5XG4gICAgaWYgKGhhc2hlc0luRG9tLmhhc093blByb3BlcnR5KGVsSGFzaCkpIGhhc2hlc0luRG9tW2VsSGFzaF0gPSB0cnVlO1xuICAgIC8vIG9yIHJlbW92ZSBpdFxuICAgIGVsc2UgdG9SZW1vdmUucHVzaChlbCk7XG4gICAgZWwgPSBlbC5uZXh0U2libGluZyBhcyBTVkdFbGVtZW50O1xuICB9XG4gIC8vIHJlbW92ZSBvbGQgc2hhcGVzXG4gIHRvUmVtb3ZlLmZvckVhY2goZWwgPT4gcm9vdC5yZW1vdmVDaGlsZChlbCkpO1xuICAvLyBpbnNlcnQgc2hhcGVzIHRoYXQgYXJlIG5vdCB5ZXQgaW4gZG9tXG4gIHNoYXBlcy5mb3JFYWNoKHNjID0+IHtcbiAgICBpZiAoIWhhc2hlc0luRG9tW3NjLmhhc2hdKSByb290LmFwcGVuZENoaWxkKHJlbmRlclNoYXBlKHN0YXRlLCBzYywgYnJ1c2hlcywgYm91bmRzKSk7XG4gIH0pO1xufVxuXG5mdW5jdGlvbiBzaGFwZUhhc2goe29yaWcsIGRlc3QsIGJydXNoLCBwaWVjZSwgbW9kaWZpZXJzfTogRHJhd1NoYXBlLCBjdXJyZW50OiBib29sZWFuKTogSGFzaCB7XG4gIHJldHVybiBbY3VycmVudCwgb3JpZywgZGVzdCwgYnJ1c2gsXG4gICAgcGllY2UgJiYgcGllY2VIYXNoKHBpZWNlKSxcbiAgICBtb2RpZmllcnMgJiYgbW9kaWZpZXJzSGFzaChtb2RpZmllcnMpXG4gIF0uZmlsdGVyKHggPT4geCkuam9pbignJyk7XG59XG5cbmZ1bmN0aW9uIHBpZWNlSGFzaChwaWVjZTogRHJhd1NoYXBlUGllY2UpOiBIYXNoIHtcbiAgcmV0dXJuIFtwaWVjZS5jb2xvciwgcGllY2Uucm9sZSwgcGllY2Uuc2NhbGVdLmZpbHRlcih4ID0+IHgpLmpvaW4oJycpO1xufVxuXG5mdW5jdGlvbiBtb2RpZmllcnNIYXNoKG06IERyYXdNb2RpZmllcnMpOiBIYXNoIHtcbiAgcmV0dXJuICcnICsgKG0ubGluZVdpZHRoIHx8ICcnKTtcbn1cblxuZnVuY3Rpb24gcmVuZGVyU2hhcGUoc3RhdGU6IFN0YXRlLCB7c2hhcGUsIGN1cnJlbnQsIGhhc2h9OiBTaGFwZSwgYnJ1c2hlczogRHJhd0JydXNoZXMsIGJvdW5kczogQ2xpZW50UmVjdCk6IFNWR0VsZW1lbnQge1xuICBsZXQgZWw6IFNWR0VsZW1lbnQ7XG4gIGlmIChzaGFwZS5waWVjZSkgZWwgPSByZW5kZXJQaWVjZShcbiAgICBzdGF0ZS5kcmF3YWJsZS5waWVjZXMuYmFzZVVybCxcbiAgICBvcmllbnQoa2V5MnBvcyhzaGFwZS5vcmlnKSwgc3RhdGUub3JpZW50YXRpb24pLFxuICAgIHNoYXBlLnBpZWNlLFxuICAgIGJvdW5kcyk7XG4gIGVsc2Uge1xuICAgIGNvbnN0IG9yaWcgPSBvcmllbnQoa2V5MnBvcyhzaGFwZS5vcmlnKSwgc3RhdGUub3JpZW50YXRpb24pO1xuICAgIGlmIChzaGFwZS5vcmlnICYmIHNoYXBlLmRlc3QpIHtcbiAgICAgIGxldCBicnVzaDogRHJhd0JydXNoID0gYnJ1c2hlc1tzaGFwZS5icnVzaF07XG4gICAgICBpZiAoc2hhcGUubW9kaWZpZXJzKSBicnVzaCA9IG1ha2VDdXN0b21CcnVzaChicnVzaCwgc2hhcGUubW9kaWZpZXJzKTtcbiAgICAgIGVsID0gcmVuZGVyQXJyb3coXG4gICAgICAgIGJydXNoLFxuICAgICAgICBvcmlnLFxuICAgICAgICBvcmllbnQoa2V5MnBvcyhzaGFwZS5kZXN0KSwgc3RhdGUub3JpZW50YXRpb24pLFxuICAgICAgICBjdXJyZW50LFxuICAgICAgICBib3VuZHMpO1xuICAgIH1cbiAgICBlbHNlIGVsID0gcmVuZGVyQ2lyY2xlKGJydXNoZXNbc2hhcGUuYnJ1c2hdLCBvcmlnLCBjdXJyZW50LCBib3VuZHMpO1xuICB9XG4gIGVsLnNldEF0dHJpYnV0ZSgnY2dIYXNoJywgaGFzaCk7XG4gIHJldHVybiBlbDtcbn1cblxuZnVuY3Rpb24gcmVuZGVyQ2lyY2xlKGJydXNoOiBEcmF3QnJ1c2gsIHBvczogY2cuUG9zLCBjdXJyZW50OiBib29sZWFuLCBib3VuZHM6IENsaWVudFJlY3QpOiBTVkdFbGVtZW50IHtcbiAgY29uc3QgbyA9IHBvczJweChwb3MsIGJvdW5kcyksXG4gIHdpZHRoID0gY2lyY2xlV2lkdGgoY3VycmVudCwgYm91bmRzKSxcbiAgcmFkaXVzID0gKGJvdW5kcy53aWR0aCArIGJvdW5kcy5oZWlnaHQpIC8gMzI7XG4gIHJldHVybiBzZXRBdHRyaWJ1dGVzKGNyZWF0ZUVsZW1lbnQoJ2NpcmNsZScpLCB7XG4gICAgc3Ryb2tlOiBicnVzaC5jb2xvcixcbiAgICAnc3Ryb2tlLXdpZHRoJzogd2lkdGgsXG4gICAgZmlsbDogJ25vbmUnLFxuICAgIG9wYWNpdHk6IG9wYWNpdHkoYnJ1c2gsIGN1cnJlbnQpLFxuICAgIGN4OiBvWzBdLFxuICAgIGN5OiBvWzFdLFxuICAgIHI6IHJhZGl1cyAtIHdpZHRoIC8gMlxuICB9KTtcbn1cblxuZnVuY3Rpb24gcmVuZGVyQXJyb3coYnJ1c2g6IERyYXdCcnVzaCwgb3JpZzogY2cuUG9zLCBkZXN0OiBjZy5Qb3MsIGN1cnJlbnQ6IGJvb2xlYW4sIGJvdW5kczogQ2xpZW50UmVjdCk6IFNWR0VsZW1lbnQge1xuICBjb25zdCBtID0gYXJyb3dNYXJnaW4oYm91bmRzLCBjdXJyZW50KSxcbiAgYSA9IHBvczJweChvcmlnLCBib3VuZHMpLFxuICBiID0gcG9zMnB4KGRlc3QsIGJvdW5kcyksXG4gIGR4ID0gYlswXSAtIGFbMF0sXG4gIGR5ID0gYlsxXSAtIGFbMV0sXG4gIGFuZ2xlID0gTWF0aC5hdGFuMihkeSwgZHgpLFxuICB4byA9IE1hdGguY29zKGFuZ2xlKSAqIG0sXG4gIHlvID0gTWF0aC5zaW4oYW5nbGUpICogbTtcbiAgcmV0dXJuIHNldEF0dHJpYnV0ZXMoY3JlYXRlRWxlbWVudCgnbGluZScpLCB7XG4gICAgc3Ryb2tlOiBicnVzaC5jb2xvcixcbiAgICAnc3Ryb2tlLXdpZHRoJzogbGluZVdpZHRoKGJydXNoLCBjdXJyZW50LCBib3VuZHMpLFxuICAgICdzdHJva2UtbGluZWNhcCc6ICdyb3VuZCcsXG4gICAgJ21hcmtlci1lbmQnOiBpc1RyaWRlbnQgPyB1bmRlZmluZWQgOiAndXJsKCNhcnJvd2hlYWQtJyArIGJydXNoLmtleSArICcpJyxcbiAgICBvcGFjaXR5OiBvcGFjaXR5KGJydXNoLCBjdXJyZW50KSxcbiAgICB4MTogYVswXSxcbiAgICB5MTogYVsxXSxcbiAgICB4MjogYlswXSAtIHhvLFxuICAgIHkyOiBiWzFdIC0geW9cbiAgfSk7XG59XG5cbmZ1bmN0aW9uIHJlbmRlclBpZWNlKGJhc2VVcmw6IHN0cmluZywgcG9zOiBjZy5Qb3MsIHBpZWNlOiBEcmF3U2hhcGVQaWVjZSwgYm91bmRzOiBDbGllbnRSZWN0KTogU1ZHRWxlbWVudCB7XG4gIGNvbnN0IG8gPSBwb3MycHgocG9zLCBib3VuZHMpLFxuICBzaXplID0gYm91bmRzLndpZHRoIC8gOCAqIChwaWVjZS5zY2FsZSB8fCAxKSxcbiAgbmFtZSA9IHBpZWNlLmNvbG9yWzBdICsgKHBpZWNlLnJvbGUgPT09ICdrbmlnaHQnID8gJ24nIDogcGllY2Uucm9sZVswXSkudG9VcHBlckNhc2UoKTtcbiAgcmV0dXJuIHNldEF0dHJpYnV0ZXMoY3JlYXRlRWxlbWVudCgnaW1hZ2UnKSwge1xuICAgIGNsYXNzTmFtZTogYCR7cGllY2Uucm9sZX0gJHtwaWVjZS5jb2xvcn1gLFxuICAgIHg6IG9bMF0gLSBzaXplIC8gMixcbiAgICB5OiBvWzFdIC0gc2l6ZSAvIDIsXG4gICAgd2lkdGg6IHNpemUsXG4gICAgaGVpZ2h0OiBzaXplLFxuICAgIGhyZWY6IGJhc2VVcmwgKyBuYW1lICsgJy5zdmcnXG4gIH0pO1xufVxuXG5mdW5jdGlvbiByZW5kZXJNYXJrZXIoYnJ1c2g6IERyYXdCcnVzaCk6IFNWR0VsZW1lbnQge1xuICBjb25zdCBtYXJrZXIgPSBzZXRBdHRyaWJ1dGVzKGNyZWF0ZUVsZW1lbnQoJ21hcmtlcicpLCB7XG4gICAgaWQ6ICdhcnJvd2hlYWQtJyArIGJydXNoLmtleSxcbiAgICBvcmllbnQ6ICdhdXRvJyxcbiAgICBtYXJrZXJXaWR0aDogNCxcbiAgICBtYXJrZXJIZWlnaHQ6IDgsXG4gICAgcmVmWDogMi4wNSxcbiAgICByZWZZOiAyLjAxXG4gIH0pO1xuICBtYXJrZXIuYXBwZW5kQ2hpbGQoc2V0QXR0cmlidXRlcyhjcmVhdGVFbGVtZW50KCdwYXRoJyksIHtcbiAgICBkOiAnTTAsMCBWNCBMMywyIFonLFxuICAgIGZpbGw6IGJydXNoLmNvbG9yXG4gIH0pKTtcbiAgbWFya2VyLnNldEF0dHJpYnV0ZSgnY2dLZXknLCBicnVzaC5rZXkpO1xuICByZXR1cm4gbWFya2VyO1xufVxuXG5mdW5jdGlvbiBzZXRBdHRyaWJ1dGVzKGVsOiBTVkdFbGVtZW50LCBhdHRyczogeyBba2V5OiBzdHJpbmddOiBhbnkgfSk6IFNWR0VsZW1lbnQge1xuICBmb3IgKGxldCBrZXkgaW4gYXR0cnMpIGVsLnNldEF0dHJpYnV0ZShrZXksIGF0dHJzW2tleV0pO1xuICByZXR1cm4gZWw7XG59XG5cbmZ1bmN0aW9uIG9yaWVudChwb3M6IGNnLlBvcywgY29sb3I6IGNnLkNvbG9yKTogY2cuUG9zIHtcbiAgcmV0dXJuIGNvbG9yID09PSAnd2hpdGUnID8gcG9zIDogWzkgLSBwb3NbMF0sIDkgLSBwb3NbMV1dO1xufVxuXG5mdW5jdGlvbiBtYWtlQ3VzdG9tQnJ1c2goYmFzZTogRHJhd0JydXNoLCBtb2RpZmllcnM6IERyYXdNb2RpZmllcnMpOiBEcmF3QnJ1c2gge1xuICBjb25zdCBicnVzaDogUGFydGlhbDxEcmF3QnJ1c2g+ID0ge1xuICAgIGNvbG9yOiBiYXNlLmNvbG9yLFxuICAgIG9wYWNpdHk6IE1hdGgucm91bmQoYmFzZS5vcGFjaXR5ICogMTApIC8gMTAsXG4gICAgbGluZVdpZHRoOiBNYXRoLnJvdW5kKG1vZGlmaWVycy5saW5lV2lkdGggfHwgYmFzZS5saW5lV2lkdGgpXG4gIH07XG4gIGJydXNoLmtleSA9IFtiYXNlLmtleSwgbW9kaWZpZXJzLmxpbmVXaWR0aF0uZmlsdGVyKHggPT4geCkuam9pbignJyk7XG4gIHJldHVybiBicnVzaCBhcyBEcmF3QnJ1c2g7XG59XG5cbmZ1bmN0aW9uIGNpcmNsZVdpZHRoKGN1cnJlbnQ6IGJvb2xlYW4sIGJvdW5kczogQ2xpZW50UmVjdCk6IG51bWJlciB7XG4gIHJldHVybiAoY3VycmVudCA/IDMgOiA0KSAvIDUxMiAqIGJvdW5kcy53aWR0aDtcbn1cblxuZnVuY3Rpb24gbGluZVdpZHRoKGJydXNoOiBEcmF3QnJ1c2gsIGN1cnJlbnQ6IGJvb2xlYW4sIGJvdW5kczogQ2xpZW50UmVjdCk6IG51bWJlciB7XG4gIHJldHVybiAoYnJ1c2gubGluZVdpZHRoIHx8IDEwKSAqIChjdXJyZW50ID8gMC44NSA6IDEpIC8gNTEyICogYm91bmRzLndpZHRoO1xufVxuXG5mdW5jdGlvbiBvcGFjaXR5KGJydXNoOiBEcmF3QnJ1c2gsIGN1cnJlbnQ6IGJvb2xlYW4pOiBudW1iZXIge1xuICByZXR1cm4gKGJydXNoLm9wYWNpdHkgfHwgMSkgKiAoY3VycmVudCA/IDAuOSA6IDEpO1xufVxuXG5mdW5jdGlvbiBhcnJvd01hcmdpbihib3VuZHM6IENsaWVudFJlY3QsIGN1cnJlbnQ6IGJvb2xlYW4pOiBudW1iZXIge1xuICByZXR1cm4gaXNUcmlkZW50ID8gMCA6ICgoY3VycmVudCA/IDEwIDogMjApIC8gNTEyICogYm91bmRzLndpZHRoKTtcbn1cblxuZnVuY3Rpb24gcG9zMnB4KHBvczogY2cuUG9zLCBib3VuZHM6IENsaWVudFJlY3QpOiBjZy5OdW1iZXJQYWlyIHtcbiAgcmV0dXJuIFsocG9zWzBdIC0gMC41KSAqIGJvdW5kcy53aWR0aCAvIDgsICg4LjUgLSBwb3NbMV0pICogYm91bmRzLmhlaWdodCAvIDhdO1xufVxuIiwiZXhwb3J0IHR5cGUgQ29sb3IgPSAnd2hpdGUnIHwgJ2JsYWNrJztcbmV4cG9ydCB0eXBlIFJvbGUgPSAna2luZycgfCAncXVlZW4nIHwgJ3Jvb2snIHwgJ2Jpc2hvcCcgfCAna25pZ2h0JyB8ICdwYXduJztcbmV4cG9ydCB0eXBlIEtleSA9ICdhMCcgfCAnYTEnIHwgJ2IxJyB8ICdjMScgfCAnZDEnIHwgJ2UxJyB8ICdmMScgfCAnZzEnIHwgJ2gxJyB8ICdhMicgfCAnYjInIHwgJ2MyJyB8ICdkMicgfCAnZTInIHwgJ2YyJyB8ICdnMicgfCAnaDInIHwgJ2EzJyB8ICdiMycgfCAnYzMnIHwgJ2QzJyB8ICdlMycgfCAnZjMnIHwgJ2czJyB8ICdoMycgfCAnYTQnIHwgJ2I0JyB8ICdjNCcgfCAnZDQnIHwgJ2U0JyB8ICdmNCcgfCAnZzQnIHwgJ2g0JyB8ICdhNScgfCAnYjUnIHwgJ2M1JyB8ICdkNScgfCAnZTUnIHwgJ2Y1JyB8ICdnNScgfCAnaDUnIHwgJ2E2JyB8ICdiNicgfCAnYzYnIHwgJ2Q2JyB8ICdlNicgfCAnZjYnIHwgJ2c2JyB8ICdoNicgfCAnYTcnIHwgJ2I3JyB8ICdjNycgfCAnZDcnIHwgJ2U3JyB8ICdmNycgfCAnZzcnIHwgJ2g3JyB8ICdhOCcgfCAnYjgnIHwgJ2M4JyB8ICdkOCcgfCAnZTgnIHwgJ2Y4JyB8ICdnOCcgfCAnaDgnO1xuZXhwb3J0IHR5cGUgRmlsZSA9ICdhJyB8ICdiJyB8ICdjJyB8ICdkJyB8ICdlJyB8ICdmJyB8ICdnJyB8ICdoJztcbmV4cG9ydCB0eXBlIFJhbmsgPSAxIHwgMiB8IDMgfCA0IHwgNSB8IDYgfCA3IHwgODtcbmV4cG9ydCB0eXBlIEZFTiA9IHN0cmluZztcbmV4cG9ydCB0eXBlIFBvcyA9IFtudW1iZXIsIG51bWJlcl07XG5leHBvcnQgaW50ZXJmYWNlIFBpZWNlIHtcbiAgcm9sZTogUm9sZTtcbiAgY29sb3I6IENvbG9yO1xuICBwcm9tb3RlZD86IGJvb2xlYW47XG59XG5leHBvcnQgaW50ZXJmYWNlIERyb3Age1xuICByb2xlOiBSb2xlO1xuICBrZXk6IEtleTtcbn1cbmV4cG9ydCBpbnRlcmZhY2UgUGllY2VzIHtcbiAgW2tleTogc3RyaW5nXTogUGllY2U7XG59XG5leHBvcnQgaW50ZXJmYWNlIFBpZWNlc0RpZmYge1xuICBba2V5OiBzdHJpbmddOiBQaWVjZSB8IG51bGw7XG59XG5cbmV4cG9ydCB0eXBlIEtleVBhaXIgPSBbS2V5LCBLZXldO1xuXG5leHBvcnQgdHlwZSBOdW1iZXJQYWlyID0gW251bWJlciwgbnVtYmVyXTtcblxuZXhwb3J0IGludGVyZmFjZSBEZXN0cyB7XG4gIFtrZXk6IHN0cmluZ106IEtleVtdXG59XG5leHBvcnQgaW50ZXJmYWNlIE1hdGVyaWFsRGlmZiB7XG4gIHdoaXRlOiB7IFtyb2xlOiBzdHJpbmddOiBudW1iZXIgfVxuICBibGFjazogeyBbcm9sZTogc3RyaW5nXTogbnVtYmVyIH1cbn1cblxuZXhwb3J0IGludGVyZmFjZSBCcm93c2VyIHtcbiAgdHJhbnNmb3JtOiBUcmFuc2Zvcm07XG59XG5leHBvcnQgaW50ZXJmYWNlIEVsZW1lbnRzIHtcbiAgYm9hcmQ6IEhUTUxFbGVtZW50O1xuICBvdmVyPzogSFRNTEVsZW1lbnQ7XG4gIGdob3N0PzogSFRNTEVsZW1lbnQ7XG4gIHN2Zz86IFNWR0VsZW1lbnQ7XG59XG5leHBvcnQgaW50ZXJmYWNlIERvbSB7XG4gIGVsZW1lbnRzOiBFbGVtZW50cyxcbiAgYm91bmRzOiBNZW1vPENsaWVudFJlY3Q+O1xuICByZWRyYXc6ICgpID0+IHZvaWQ7XG4gIHJlZHJhd05vdzogKHNraXBTdmc/OiBib29sZWFuKSA9PiB2b2lkO1xuICB1bmJpbmQ/OiBVbmJpbmQ7XG4gIGRlc3Ryb3llZD86IGJvb2xlYW47XG59XG5leHBvcnQgaW50ZXJmYWNlIEV4cGxvZGluZyB7XG4gIHN0YWdlOiBudW1iZXI7XG4gIGtleXM6IEtleVtdO1xufVxuXG5leHBvcnQgaW50ZXJmYWNlIE1vdmVNZXRhZGF0YSB7XG4gIHByZW1vdmU6IGJvb2xlYW47XG4gIGN0cmxLZXk/OiBib29sZWFuO1xuICBob2xkVGltZT86IG51bWJlcjtcbiAgY2FwdHVyZWQ/OiBQaWVjZTtcbn1cbmV4cG9ydCBpbnRlcmZhY2UgU2V0UHJlbW92ZU1ldGFkYXRhIHtcbiAgY3RybEtleT86IGJvb2xlYW47XG59XG5cbmV4cG9ydCB0eXBlIFdpbmRvd0V2ZW50ID0gJ29uc2Nyb2xsJyB8ICdvbnJlc2l6ZSc7XG5cbmV4cG9ydCB0eXBlIE1vdWNoRXZlbnQgPSBNb3VzZUV2ZW50ICYgVG91Y2hFdmVudDtcblxuZXhwb3J0IGludGVyZmFjZSBLZXllZE5vZGUgZXh0ZW5kcyBIVE1MRWxlbWVudCB7XG4gIGNnS2V5OiBLZXk7XG59XG5leHBvcnQgaW50ZXJmYWNlIFBpZWNlTm9kZSBleHRlbmRzIEtleWVkTm9kZSB7XG4gIGNnUGllY2U6IHN0cmluZztcbiAgY2dBbmltYXRpbmc/OiBib29sZWFuO1xuICBjZ0ZhZGluZz86IGJvb2xlYW47XG4gIGNnRHJhZ2dpbmc/OiBib29sZWFuO1xufVxuZXhwb3J0IGludGVyZmFjZSBTcXVhcmVOb2RlIGV4dGVuZHMgS2V5ZWROb2RlIHsgfVxuXG5leHBvcnQgaW50ZXJmYWNlIE1lbW88QT4geyAoKTogQTsgY2xlYXI6ICgpID0+IHZvaWQ7IH1cblxuZXhwb3J0IGludGVyZmFjZSBUaW1lciB7XG4gIHN0YXJ0OiAoKSA9PiB2b2lkO1xuICBjYW5jZWw6ICgpID0+IHZvaWQ7XG4gIHN0b3A6ICgpID0+IG51bWJlcjtcbn1cblxuZXhwb3J0IHR5cGUgVHJhbnNmb3JtID0gKGVsOiBIVE1MRWxlbWVudCwgdmFsdWU6IHN0cmluZykgPT4gdm9pZDtcblxuZXhwb3J0IHR5cGUgUmVkcmF3ID0gKCkgPT4gdm9pZDtcbmV4cG9ydCB0eXBlIFVuYmluZCA9ICgpID0+IHZvaWQ7XG5leHBvcnQgdHlwZSBUaW1lc3RhbXAgPSBudW1iZXI7XG5leHBvcnQgdHlwZSBNaWxsaXNlY29uZHMgPSBudW1iZXI7XG5cbmV4cG9ydCBjb25zdCBmaWxlczogRmlsZVtdID0gWydhJywgJ2InLCAnYycsICdkJywgJ2UnLCAnZicsICdnJywgJ2gnXTtcbmV4cG9ydCBjb25zdCByYW5rczogUmFua1tdID0gWzEsIDIsIDMsIDQsIDUsIDYsIDcsIDhdO1xuIiwiaW1wb3J0ICogYXMgY2cgZnJvbSAnLi90eXBlcyc7XG5cbmV4cG9ydCBjb25zdCBjb2xvcnM6IGNnLkNvbG9yW10gPSBbJ3doaXRlJywgJ2JsYWNrJ107XG5cbmV4cG9ydCBjb25zdCBpbnZSYW5rczogY2cuUmFua1tdID0gWzgsIDcsIDYsIDUsIDQsIDMsIDIsIDFdO1xuXG5leHBvcnQgY29uc3QgYWxsS2V5czogY2cuS2V5W10gPSBBcnJheS5wcm90b3R5cGUuY29uY2F0KC4uLmNnLmZpbGVzLm1hcChjID0+IGNnLnJhbmtzLm1hcChyID0+IGMrcikpKTtcblxuZXhwb3J0IGNvbnN0IHBvczJrZXkgPSAocG9zOiBjZy5Qb3MpID0+IGFsbEtleXNbOCAqIHBvc1swXSArIHBvc1sxXSAtIDldO1xuXG5leHBvcnQgY29uc3Qga2V5MnBvcyA9IChrOiBjZy5LZXkpID0+IFtrLmNoYXJDb2RlQXQoMCkgLSA5Niwgay5jaGFyQ29kZUF0KDEpIC0gNDhdIGFzIGNnLlBvcztcblxuZXhwb3J0IGZ1bmN0aW9uIG1lbW88QT4oZjogKCkgPT4gQSk6IGNnLk1lbW88QT4ge1xuICBsZXQgdjogQSB8IHVuZGVmaW5lZDtcbiAgY29uc3QgcmV0OiBhbnkgPSAoKSA9PiB7XG4gICAgaWYgKHYgPT09IHVuZGVmaW5lZCkgdiA9IGYoKTtcbiAgICByZXR1cm4gdjtcbiAgfTtcbiAgcmV0LmNsZWFyID0gKCkgPT4geyB2ID0gdW5kZWZpbmVkOyB9O1xuICByZXR1cm4gcmV0O1xufVxuXG5leHBvcnQgY29uc3QgdGltZXI6ICgpID0+IGNnLlRpbWVyID0gKCkgPT4ge1xuICBsZXQgc3RhcnRBdDogRGF0ZSB8IHVuZGVmaW5lZDtcbiAgcmV0dXJuIHtcbiAgICBzdGFydCgpIHsgc3RhcnRBdCA9IG5ldyBEYXRlKCk7IH0sXG4gICAgY2FuY2VsKCkgeyBzdGFydEF0ID0gdW5kZWZpbmVkOyB9LFxuICAgIHN0b3AoKSB7XG4gICAgICBpZiAoIXN0YXJ0QXQpIHJldHVybiAwO1xuICAgICAgY29uc3QgdGltZSA9IG5ldyBEYXRlKCkuZ2V0VGltZSgpIC0gc3RhcnRBdC5nZXRUaW1lKCk7XG4gICAgICBzdGFydEF0ID0gdW5kZWZpbmVkO1xuICAgICAgcmV0dXJuIHRpbWU7XG4gICAgfVxuICB9O1xufVxuXG5leHBvcnQgY29uc3Qgb3Bwb3NpdGUgPSAoYzogY2cuQ29sb3IpID0+IGMgPT09ICd3aGl0ZScgPyAnYmxhY2snIDogJ3doaXRlJztcblxuZXhwb3J0IGZ1bmN0aW9uIGNvbnRhaW5zWDxYPih4czogWFtdIHwgdW5kZWZpbmVkLCB4OiBYKTogYm9vbGVhbiB7XG4gIHJldHVybiB4cyA/IHhzLmluZGV4T2YoeCkgIT09IC0xIDogZmFsc2U7XG59XG5cbmV4cG9ydCBjb25zdCBkaXN0YW5jZVNxOiAocG9zMTogY2cuUG9zLCBwb3MyOiBjZy5Qb3MpID0+IG51bWJlciA9IChwb3MxLCBwb3MyKSA9PiB7XG4gIHJldHVybiBNYXRoLnBvdyhwb3MxWzBdIC0gcG9zMlswXSwgMikgKyBNYXRoLnBvdyhwb3MxWzFdIC0gcG9zMlsxXSwgMik7XG59XG5cbmV4cG9ydCBjb25zdCBzYW1lUGllY2U6IChwMTogY2cuUGllY2UsIHAyOiBjZy5QaWVjZSkgPT4gYm9vbGVhbiA9IChwMSwgcDIpID0+XG4gIHAxLnJvbGUgPT09IHAyLnJvbGUgJiYgcDEuY29sb3IgPT09IHAyLmNvbG9yO1xuXG5pbnRlcmZhY2UgQ1NTU3R5bGVEZWNsYXJhdGlvbiB7XG4gIFtrZXk6IHN0cmluZ106IGFueTtcbn1cblxuZXhwb3J0IGNvbnN0IHRyYW5zZm9ybUZ1bmN0aW9uOiAoKSA9PiBjZy5UcmFuc2Zvcm0gPSAoKSA9PiB7XG4gIGNvbnN0IHMgPSBkb2N1bWVudC5ib2R5LnN0eWxlO1xuICBjb25zdCBwcm9wID0gJ3RyYW5zZm9ybScgaW4gcyA/XG4gICAgJ3RyYW5zZm9ybScgOiAnd2Via2l0VHJhbnNmb3JtJyBpbiBzID9cbiAgICAnd2Via2l0VHJhbnNmb3JtJyA6ICdtb3pUcmFuc2Zvcm0nIGluIHMgP1xuICAgICdtb3pUcmFuc2Zvcm0nIDogJ29UcmFuc2Zvcm0nIGluIHMgP1xuICAgICdvVHJhbnNmb3JtJyA6ICdtc1RyYW5zZm9ybSc7XG4gIHJldHVybiAoZWwsIHZhbHVlKSA9PiB7XG4gICAgKGVsLnN0eWxlIGFzIENTU1N0eWxlRGVjbGFyYXRpb24pW3Byb3BdID0gdmFsdWU7XG4gIH07XG59XG5cbmV4cG9ydCBjb25zdCBjb21wdXRlSXNUcmlkZW50ID0gKCkgPT4gd2luZG93Lm5hdmlnYXRvci51c2VyQWdlbnQuaW5kZXhPZignVHJpZGVudC8nKSA+IC0xO1xuXG5leHBvcnQgY29uc3QgcG9zVG9UcmFuc2xhdGU6IChwb3M6IGNnLlBvcywgYXNXaGl0ZTogYm9vbGVhbiwgYm91bmRzOiBDbGllbnRSZWN0KSA9PiBjZy5OdW1iZXJQYWlyID1cbihwb3MsIGFzV2hpdGUsIGJvdW5kcykgPT4ge1xuICByZXR1cm4gW1xuICAgIChhc1doaXRlID8gcG9zWzBdIC0gMSA6IDggLSBwb3NbMF0pICogYm91bmRzLndpZHRoIC8gOCxcbiAgICAoYXNXaGl0ZSA/IDggLSBwb3NbMV0gOiBwb3NbMV0gLSAxKSAqIGJvdW5kcy5oZWlnaHQgLyA4XG4gIF07XG59XG5cbmV4cG9ydCBjb25zdCB0cmFuc2xhdGUgPSAocG9zOiBjZy5Qb3MpID0+ICd0cmFuc2xhdGUoJyArIHBvc1swXSArICdweCwnICsgcG9zWzFdICsgJ3B4KSc7XG5cbmV4cG9ydCBjb25zdCB0cmFuc2xhdGVBd2F5OiBzdHJpbmcgPSB0cmFuc2xhdGUoWy05OTk5OSwgLTk5OTk5XSk7XG5cbi8vIHRvdWNoZW5kIGhhcyBubyBwb3NpdGlvbiFcbmV4cG9ydCBjb25zdCBldmVudFBvc2l0aW9uOiAoZTogY2cuTW91Y2hFdmVudCkgPT4gY2cuTnVtYmVyUGFpciB8IHVuZGVmaW5lZCA9IGUgPT4ge1xuICBpZiAoZS5jbGllbnRYIHx8IGUuY2xpZW50WCA9PT0gMCkgcmV0dXJuIFtlLmNsaWVudFgsIGUuY2xpZW50WV07XG4gIGlmIChlLnRvdWNoZXMgJiYgZS50YXJnZXRUb3VjaGVzWzBdKSByZXR1cm4gW2UudGFyZ2V0VG91Y2hlc1swXS5jbGllbnRYLCBlLnRhcmdldFRvdWNoZXNbMF0uY2xpZW50WV07XG4gIHJldHVybiB1bmRlZmluZWQ7XG59XG5cbmV4cG9ydCBjb25zdCBpc1JpZ2h0QnV0dG9uID0gKGU6IE1vdXNlRXZlbnQpID0+IGUuYnV0dG9ucyA9PT0gMiB8fCBlLmJ1dHRvbiA9PT0gMjtcblxuZXhwb3J0IGNvbnN0IGNyZWF0ZUVsID0gKHRhZ05hbWU6IHN0cmluZywgY2xhc3NOYW1lPzogc3RyaW5nKSA9PiB7XG4gIGNvbnN0IGVsID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCh0YWdOYW1lKTtcbiAgaWYgKGNsYXNzTmFtZSkgZWwuY2xhc3NOYW1lID0gY2xhc3NOYW1lO1xuICByZXR1cm4gZWw7XG59XG5cbmV4cG9ydCBjb25zdCByYWYgPSAod2luZG93LnJlcXVlc3RBbmltYXRpb25GcmFtZSB8fCB3aW5kb3cuc2V0VGltZW91dCkuYmluZCh3aW5kb3cpO1xuIiwiaW1wb3J0IHsgU3RhdGUgfSBmcm9tICcuL3N0YXRlJ1xuaW1wb3J0IHsgY29sb3JzLCB0cmFuc2xhdGVBd2F5LCBjcmVhdGVFbCB9IGZyb20gJy4vdXRpbCdcbmltcG9ydCB7IGZpbGVzLCByYW5rcyB9IGZyb20gJy4vdHlwZXMnXG5pbXBvcnQgeyBjcmVhdGVFbGVtZW50IGFzIGNyZWF0ZVNWRyB9IGZyb20gJy4vc3ZnJ1xuaW1wb3J0IHsgRWxlbWVudHMgfSBmcm9tICcuL3R5cGVzJ1xuXG5leHBvcnQgZGVmYXVsdCBmdW5jdGlvbiB3cmFwKGVsZW1lbnQ6IEhUTUxFbGVtZW50LCBzOiBTdGF0ZSwgYm91bmRzOiBDbGllbnRSZWN0KTogRWxlbWVudHMge1xuXG4gIGVsZW1lbnQuaW5uZXJIVE1MID0gJyc7XG5cbiAgZWxlbWVudC5jbGFzc0xpc3QuYWRkKCdjZy1ib2FyZC13cmFwJyk7XG4gIGNvbG9ycy5mb3JFYWNoKGMgPT4ge1xuICAgIGVsZW1lbnQuY2xhc3NMaXN0LnRvZ2dsZSgnb3JpZW50YXRpb24tJyArIGMsIHMub3JpZW50YXRpb24gPT09IGMpO1xuICB9KTtcbiAgZWxlbWVudC5jbGFzc0xpc3QudG9nZ2xlKCdtYW5pcHVsYWJsZScsICFzLnZpZXdPbmx5KTtcblxuICBjb25zdCBib2FyZCA9IGNyZWF0ZUVsKCdkaXYnLCAnY2ctYm9hcmQnKTtcblxuICBlbGVtZW50LmFwcGVuZENoaWxkKGJvYXJkKTtcblxuICBsZXQgc3ZnOiBTVkdFbGVtZW50IHwgdW5kZWZpbmVkO1xuICBpZiAocy5kcmF3YWJsZS5lbmFibGVkKSB7XG4gICAgc3ZnID0gY3JlYXRlU1ZHKCdzdmcnKTtcbiAgICBzdmcuYXBwZW5kQ2hpbGQoY3JlYXRlU1ZHKCdkZWZzJykpO1xuICAgIGVsZW1lbnQuYXBwZW5kQ2hpbGQoc3ZnKTtcbiAgfVxuXG4gIGlmIChzLmNvb3JkaW5hdGVzKSB7XG4gICAgY29uc3Qgb3JpZW50Q2xhc3MgPSBzLm9yaWVudGF0aW9uID09PSAnYmxhY2snID8gJyBibGFjaycgOiAnJztcbiAgICBlbGVtZW50LmFwcGVuZENoaWxkKHJlbmRlckNvb3JkcyhyYW5rcywgJ3JhbmtzJyArIG9yaWVudENsYXNzKSk7XG4gICAgZWxlbWVudC5hcHBlbmRDaGlsZChyZW5kZXJDb29yZHMoZmlsZXMsICdmaWxlcycgKyBvcmllbnRDbGFzcykpO1xuICB9XG5cbiAgbGV0IG92ZXI6IEhUTUxFbGVtZW50IHwgdW5kZWZpbmVkO1xuICBpZiAoIXMudmlld09ubHkgJiYgKHMubW92YWJsZS5zaG93RGVzdHMgfHwgcy5wcmVtb3ZhYmxlLnNob3dEZXN0cykpIHtcbiAgICBvdmVyID0gY3JlYXRlRWwoJ2RpdicsICdvdmVyJyk7XG4gICAgcy5icm93c2VyLnRyYW5zZm9ybShvdmVyLCB0cmFuc2xhdGVBd2F5KTtcbiAgICBvdmVyLnN0eWxlLndpZHRoID0gKGJvdW5kcy53aWR0aCAvIDgpICsgJ3B4JztcbiAgICBvdmVyLnN0eWxlLmhlaWdodCA9IChib3VuZHMuaGVpZ2h0IC8gOCkgKyAncHgnO1xuICAgIGVsZW1lbnQuYXBwZW5kQ2hpbGQob3Zlcik7XG4gIH1cblxuICBsZXQgZ2hvc3Q6IEhUTUxFbGVtZW50IHwgdW5kZWZpbmVkO1xuICBpZiAoIXMudmlld09ubHkgJiYgcy5kcmFnZ2FibGUuc2hvd0dob3N0KSB7XG4gICAgZ2hvc3QgPSBjcmVhdGVFbCgncGllY2UnLCAnZ2hvc3QnKTtcbiAgICBzLmJyb3dzZXIudHJhbnNmb3JtKGdob3N0LCB0cmFuc2xhdGVBd2F5KTtcbiAgICBlbGVtZW50LmFwcGVuZENoaWxkKGdob3N0KTtcbiAgfVxuXG4gIHJldHVybiB7XG4gICAgYm9hcmQ6IGJvYXJkLFxuICAgIG92ZXI6IG92ZXIsXG4gICAgZ2hvc3Q6IGdob3N0LFxuICAgIHN2Zzogc3ZnXG4gIH07XG59XG5cbmZ1bmN0aW9uIHJlbmRlckNvb3JkcyhlbGVtczogYW55W10sIGNsYXNzTmFtZTogc3RyaW5nKTogSFRNTEVsZW1lbnQge1xuICBjb25zdCBlbCA9IGNyZWF0ZUVsKCdjb29yZHMnLCBjbGFzc05hbWUpO1xuICBsZXQgZjogSFRNTEVsZW1lbnQ7XG4gIGZvciAobGV0IGkgaW4gZWxlbXMpIHtcbiAgICBmID0gY3JlYXRlRWwoJ2Nvb3JkJyk7XG4gICAgZi50ZXh0Q29udGVudCA9IGVsZW1zW2ldO1xuICAgIGVsLmFwcGVuZENoaWxkKGYpO1xuICB9XG4gIHJldHVybiBlbDtcbn1cbiJdfQ==
