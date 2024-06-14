import random


piece_score = {'K': 0, 'Q': 10, 'R': 5, 'B': 3, 'N': 3, 'P': 1}

knight_scores = [[0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0],
                 [0.1, 0.3, 0.5, 0.5, 0.5, 0.5, 0.3, 0.1],
                 [0.2, 0.5, 0.6, 0.65, 0.65, 0.6, 0.5, 0.2],
                 [0.2, 0.55, 0.65, 0.7, 0.7, 0.65, 0.55, 0.2],
                 [0.2, 0.5, 0.65, 0.7, 0.7, 0.65, 0.5, 0.2],
                 [0.2, 0.55, 0.6, 0.65, 0.65, 0.6, 0.55, 0.2],
                 [0.1, 0.3, 0.5, 0.55, 0.55, 0.5, 0.3, 0.1],
                 [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0]]

bishop_scores = [[0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
                 [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                 [0.2, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.2],
                 [0.2, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.2],
                 [0.2, 0.4, 0.6, 0.6, 0.6, 0.6, 0.4, 0.2],
                 [0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2],
                 [0.2, 0.5, 0.4, 0.4, 0.4, 0.4, 0.5, 0.2],
                 [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0]]

rook_scores = [[0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
               [0.5, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.5],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.25, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.25]]

queen_scores = [[0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0],
                [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.4, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0]]

pawn_scores = [[0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
               [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
               [0.3, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.3],
               [0.25, 0.25, 0.3, 0.45, 0.45, 0.3, 0.25, 0.25],
               [0.2, 0.2, 0.2, 0.4, 0.4, 0.2, 0.2, 0.2],
               [0.25, 0.15, 0.1, 0.2, 0.2, 0.1, 0.15, 0.25],
               [0.25, 0.3, 0.3, 0.0, 0.0, 0.3, 0.3, 0.25],
               [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]]

piece_position_scores = {"wN": knight_scores,
                         "bN": knight_scores[::-1],
                         "wB": bishop_scores,
                         "bB": bishop_scores[::-1],
                         "wQ": queen_scores,
                         "bQ": queen_scores[::-1],
                         "wR": rook_scores,
                         "bR": rook_scores[::-1],
                         "wP": pawn_scores,
                         "bP": pawn_scores[::-1]}

CHECKMATE = 1000 # white wins; black tries to minimize score
STALEMATE = 0

# picks and returns a random move
def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves) - 1)]



# helper method to make the first recursive call
def find_best_move(gs, valid_moves, max_depth):
    global next_move, counter
    next_move = None
    random.shuffle(valid_moves)
    counter = 0
    find_move_nega_max_alpha_beta(gs, valid_moves, max_depth, max_depth, -CHECKMATE, CHECKMATE, 1 if gs.white_to_move else -1)
    print(f'Analyzed {counter} board states')
    return next_move
 

def score_board(gs, valid_moves):
    if gs.checkmate:
        if gs.white_to_move:
            return -CHECKMATE # black wins
        else:
            return CHECKMATE # white wins
    elif gs.stalemate:
        return STALEMATE
    
    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            piece = gs.board[row][col]
            if piece != '--':
                # score it positionally
                piece_position_score = 0
                if piece[1] != 'K':
                    piece_position_score = piece_position_scores[piece][row][col]
                if piece[0] == 'w':
                    score += piece_score[piece[1]] + piece_position_score
                if piece[0] == 'b':
                    score -= piece_score[piece[1]] + piece_position_score
            if piece[0] == 'w':
                score += piece_score[piece[1]]
            elif piece[0] == 'b':
                score -= piece_score[piece[1]]
    
    for move in valid_moves:
        if gs.white_to_move: 
            gs.make_move(move) # will switch players
            in_check, _, _ = gs.check_for_pins_and_checks()
            if gs.checkmate: # black is checkmated
                score += 1000
            elif in_check: # black is in check
                score += 0.7
        elif not gs.white_to_move:
            gs.make_move(move) # will switch players
            in_check, _, _ = gs.check_for_pins_and_checks()
            if gs.checkmate: # white is checkmated
                score -= 1000
            elif in_check: # white is in check
                score -= 0.7
                
        gs.undo_move()
    
    
    return score

def find_move_nega_max_alpha_beta(gs, valid_moves, curr_depth, max_depth, alpha, beta, turn_multiplier):
    global next_move, counter
    DEPTH = max_depth
    counter += 1
    if curr_depth == 0:
        return turn_multiplier * score_board(gs, valid_moves)
    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = -find_move_nega_max_alpha_beta(gs, next_moves, curr_depth - 1, DEPTH, -beta, -alpha, -turn_multiplier)
        if score > max_score:
            max_score = score
            if curr_depth == DEPTH:
                next_move = move
                #print(f'move: {move}, score: {score}')
        gs.undo_move()
        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break
    return max_score
