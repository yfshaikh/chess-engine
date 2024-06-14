"""
Main driver file. Responsible for handling user input and displaying the current GameState object
"""
from Chess.CastleRights import CastleRights
from Chess.Move import Move

class GameState:
    def __init__(self):
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
        ]
        self.move_functions = {'P': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves,
                              'B': self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}
        self.white_to_move = True
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.in_check = False
        self.pins = []
        self.checks = []
        self.enpassant_possible = () # ccordinates for the square where an en passant capture is possible
        self.enpassant_possible_log = [self.enpassant_possible]
        self.current_castling_right = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(self.current_castling_right.wks, self.current_castling_right.bks, 
                                             self.current_castling_right.wqs, self.current_castling_right.bqs)]

    
    # takes a move as a paramter and executes it
    def make_move(self, move):
        self.board[move.start_row][move.start_col] = '--'
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move) # log the move
        self.white_to_move = not self.white_to_move # switch players
        # update the king's location
        if move.piece_moved == 'wK':
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king_location = (move.end_row, move.end_col)
        

        # en passant
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] = '--' # capturing the pawn
        
        # update enpassantPossible variable
        if move.piece_moved[1] == 'P' and abs(move.start_row - move.end_row) == 2: # only on 2 square pawn advances
            self.enpassant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.enpassant_possible = ()

        # castle move
        if move.is_castle_move:
            if move.end_col - move.start_col == 2: # kingside castle
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1] # removes the rook
                self.board[move.end_row][move.end_col + 1] = '--' # erase the old rook
            else: # queenside castle
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2] # removes the rook
                self.board[move.end_row][move.end_col - 2] = '--' # erase the old rook

        self.enpassant_possible_log.append(self.enpassant_possible)

        # update castle rights
        self.update_castle_rights(move)
        self.castle_rights_log.append(CastleRights(self.current_castling_right.wks, self.current_castling_right.bks, 
                                             self.current_castling_right.wqs, self.current_castling_right.bqs))
        

    def check_pawn_promotion(self, move):
        if move.piece_moved == 'wP':
            if move.end_row == 0:
                return True
        elif move.piece_moved == 'bP':
            if move.end_row == 7:
                return True
        
        return False
    
    # undo the last move
    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.white_to_move = not self.white_to_move
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.board[move.start_row][move.start_col] = move.piece_moved
            
            
        # update the king's location
        if move.piece_moved == 'wK':
            self.white_king_location = (move.start_row, move.start_col)
        elif move.piece_moved == 'bK':
            self.black_king_location = (move.start_row, move.start_col)
        
        # undo en passant
        if move.is_enpassant_move:
            self.board[move.end_row][move.end_col] = '--' # leave landing square blank
            self.board[move.start_row][move.end_col] = move.piece_captured

        self.enpassant_possible_log.pop()
        self.enpassant_possible = self.enpassant_possible_log[-1]
        

        # undo castling rights
        self.castle_rights_log.pop() # get rid of new castle rights from the move we are undoing
        self.current_castling_right = self.castle_rights_log[-1] # set the current castle rights to the last one in the list

        # undo castle move
        if move.is_castle_move:
            if move.end_col - move.start_col == 2: # kingside
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1] # move rook back to original position
                self.board[move.end_row][move.end_col - 1] = '--'
            else: # queenside
                self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1] # move rook back to original position
                self.board[move.end_row][move.end_col + 1] = '--'

        # undo checkmate/stalemate
        self.checkmate = False
        self.stalemate = False

        

    # all moves considering checks
    def get_valid_moves(self):
        moves = []
        self.in_check, self.pins, self.checks = self.check_for_pins_and_checks() # check for pins and checks
        if self.white_to_move:
            king_row, king_col = self.white_king_location[0], self.white_king_location[1]
            self.get_castle_moves(king_row, king_col, moves, 'w')
        else:
            king_row, king_col = self.black_king_location[0], self.black_king_location[1]
            self.get_castle_moves(king_row, king_col, moves, 'b')



        if self.in_check:
            if len(self.checks) == 1: # only one check, can block or move king
                moves = self.get_all_moves()
                # to block a check you must move a piece into one of the squares between the enemy piece and king
                check = self.checks[0] # check information
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col] # enemy pice causing the check
                valid_squares = [] # squares that pieces can move to
                # if knight, we cannot block and must capture it or move the king
                if piece_checking[1] == 'N':
                    valid_squares = [(check_row, check_col)]
                else: # not a knight; blocking logic
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i) # check[2] and check[3] are the check directions
                        valid_squares.append(valid_square) # can move to any piece between the king and the attacker or move to the attacker's square itself
                        if valid_square[0] == check_row and valid_square[1] == check_col: # once you get to the attacker, there are no more valid squares after
                            break
                
                # get rid of any moves that don't block check or move king
                for i in range (len(moves) -1, -1, -1): # go through the list backwards when removing 
                    if moves[i].piece_moved[1] != 'K': # if the move doesn't move the king (must block or capture)
                        if not (moves[i].end_row, moves[i].end_col) in valid_squares: # move doesn't block check or capture piece
                            moves.remove(moves[i])

            else: # double check, king must move
                self.get_king_moves(king_row, king_col, moves)

        else: # not in check so all moves are fine
            moves = self.get_all_moves()
        

        if self.white_to_move:
            self.get_castle_moves(king_row, king_col, moves, 'w')
        else:
            self.get_castle_moves(king_row, king_col, moves, 'b')

        if len(moves) == 0:
            if self.in_check:
                self.checkmate = True
            else:
                # TODO stalemate on repeated moves
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        return moves

    # all moves not considering checks
    def get_all_moves(self):
        moves = []
        for r in range(len(self.board)): # number of rows
            for c in range(len(self.board[r])): # number of columns in a given row
                turn = self.board[r][c][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves) # calls the appropriate move function based on piece type
        return moves

    # determine if the enemy can attack the square r, c
    def square_under_attack(self, r, c):
        self.white_to_move = not self.white_to_move # switch to opponent's turn
        opp_moves = self.get_all_moves()
        self.white_to_move = not self.white_to_move # switch turns back
        for move in opp_moves:
            if move.end_row == r and move.end_col == c: # square is under attack
                return True
        return False

    def check_for_pins_and_checks(self):
        pins = [] # squares where the allied pin piece is and direction pinned from
        checks = [] # squares where enemy is applying a check
        in_check = False

        if self.white_to_move:
            enemy_color, ally_color = 'b', 'w'
            start_row, start_col = self.white_king_location[0], self.white_king_location[1]
        else:
            enemy_color, ally_color = 'w', 'b'
            start_row, start_col = self.black_king_location[0], self.black_king_location[1]


        # check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = () # reset possible pins
            for i in range(1, 8):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != 'K':
                        if possible_pin == (): # first allied piece that could be pinned
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else: # 2nd allied piece, so no pin or check possible in this direction
                            break
                    elif end_piece[0] == enemy_color:
                        type = end_piece[1]   
                        # 5 possibilities: 
                        # orthogonally away from king and piece is a rook
                        # diagonally away from king and piece is a bishop
                        # 1 square diagonally away from king and piece is a pawn
                        # any direction anf piece is a queen
                        # any direction one square away and piece is a king (prevent a king move to a square controlled by another king)

                        if(0 <= j <= 3 and type == 'R') or \
                            (4 <= j <= 7 and type == 'B') or \
                            (i == 1 and type == 'P' and ((enemy_color == 'w' and 6 <= j <= 7) or (enemy_color == 'b' and 4 <= j <= 5))) or \
                            (type == 'Q') or (i == 1 and type == 'K'):
                            if possible_pin == (): # no piece blocking so check
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else: # piece blocking so pin
                                pins.append(possible_pin)
                                break

                        else: # enemy piece not applying check
                            break

                else: # off board
                    break
                
        # check for knight checks
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knight_moves:
            end_row = start_row + m[0]
            end_col = start_col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == 'N': # enemy knight attacking king
                    in_check = True
                    checks.append((end_row, end_col, m[0], m[1]))

        return in_check, pins, checks
   
   # get all the pawn moves for the pawn located at row, col and add these moves to the list
    def get_pawn_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range (len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.white_to_move:
            move_amount, start_row, back_row, enemy_color = -1, 6, 0, 'b'
            king_row, king_col = self.white_king_location
        else:
            move_amount, start_row, back_row, enemy_color = 1, 1, 7, 'w'
            king_row, king_col = self.black_king_location

        pawn_promotion = False

        if self.board[r + move_amount][c] == '--': # one square pawn advance
            if not piece_pinned or pin_direction == (move_amount, 0):
                if r+move_amount == back_row: # if piece gets to back rank then it is pawn promotion  
                    pawn_promotion = True
                moves.append(Move((r,c), (r+move_amount, c), self.board, pawn_promotion = pawn_promotion))
                if r == start_row and self.board[r+2*move_amount][c] == '--': # two square pawn advance
                    moves.append(Move((r,c), (r+2*move_amount, c), self.board))
        if c-1 >= 0: # capture to left
            if not piece_pinned or pin_direction == (move_amount, -1):
                if self.board[r + move_amount][c-1][0] == enemy_color:
                    if r + move_amount == back_row: # if piece gets to the back rank then it is a pawn promotion
                        pawn_promotion = True
                    moves.append(Move((r,c), (r+move_amount, c-1), self.board, pawn_promotion = pawn_promotion))
                if (r+move_amount, c-1) == self.enpassant_possible:
                    attacking_piece = blocking_piece = False
                    if king_row == r:
                        if king_col < c: # king is left of the pawn
                            # inside range between king and pawn; outside range between pawn border
                            inside_range = range(king_col +1 , c - 1)
                            outside_range = range(c+1, 8)
                        else: # king right of the pawn
                            inside_range = range(king_col - 1, c, - 1)
                            outside_range = range(c - 2, -1, -1)
                        for i in inside_range:
                            if self.board[r][i] != '--': # some other piece beside enpassant pawn blocks
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[r][i]
                            if square[0] == enemy_color and (square[1] == 'R' or square[1] =='Q'): # attacking piece
                                attacking_piece = True
                            elif square != '--':
                                blocking_piece = True
                    
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((r,c), (r+move_amount, c-1), self.board, is_enpassant_move = True))
        
        if c+1 <= 7: # capture to right
            if not piece_pinned or pin_direction == (move_amount, 1):
                if self.board[r + move_amount][c+1][0] == enemy_color:
                    if r + move_amount == back_row: # if piece gets to the back rank then it is a pawn promotion
                        pawn_promotion = True
                    moves.append(Move((r,c), (r+move_amount, c+1), self.board, pawn_promotion = pawn_promotion))
                if (r+move_amount, c+1) == self.enpassant_possible:
                    attacking_piece = blocking_piece = False
                    if king_row == r:
                        if king_col < c: # king is left of the pawn
                            # inside range between king and pawn; outside range between pawn border
                            inside_range = range(king_col + 1 , c)
                            outside_range = range(c+2, 8)
                        else: # king right of the pawn
                            inside_range = range(king_col - 1, c + 1, - 1)
                            outside_range = range(c - 1, -1, -1)
                        for i in inside_range:
                            if self.board[r][i] != '--': # some other piece beside enpassant pawn blocks
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[r][i]
                            if square[0] == enemy_color and (square[1] == 'R' or square[1] =='Q'): # attacking piece
                                attacking_piece = True
                            elif square != '--':
                                blocking_piece = True
                    
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((r,c), (r+move_amount, c+1), self.board, is_enpassant_move = True))

    # get all the rook moves for the rook located at row, col and add these moves to the list
    def get_rook_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range (len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q': # can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1,0), (0, -1), (1,0),(0,1)) # up, left, down, right
        enemy_color = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8: # on board
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]): # rook can move in direction of pin or opposite direction without causing check
                        end_piece = self.board[end_row][end_col]
                        if end_piece == '--': # empty space valid
                            moves.append(Move((r,c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color: # enemy piece valid
                            moves.append(Move((r,c), (end_row, end_col), self.board))
                            break
                        else: # friendly piece invalid
                            break
                else: # off board
                    break

    # get all the knight moves for the knight located at row, col and add these moves to the list
    def get_knight_moves(self, r, c, moves):
        piece_pinned = False
        for i in range (len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break

        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        ally_color = 'w' if self.white_to_move else 'b'
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally_color: # can't capture an ally
                        moves.append(Move((r,c), (end_row, end_col), self.board))

    # get all the bishop moves for the bishop located at row, col and add these moves to the list
    def get_bishop_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range (len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1,-1), (-1, 1), (1,-1),(1,1)) # 4 diagonals
        enemy_color = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8: # on board
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]): # bishop can move in direction of pin or opposite direction without causing check
                        end_piece = self.board[end_row][end_col]
                        if end_piece == '--': # empty space valid
                            moves.append(Move((r,c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color: # enemy piece valid
                            moves.append(Move((r,c), (end_row, end_col), self.board))
                            break
                        else: # friendly piece invalid
                            break
                else: # off board
                    break

    # get all the queen moves for the queen located at row, col and add these moves to the list
    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    # get all the king moves for the king located at row, col and add these moves to the list
    def get_king_moves(self, r, c, moves):
        king_moves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        ally_color = 'w' if self.white_to_move else 'b'
        if self.white_to_move:
            king_row, king_col = self.white_king_location[0], self.white_king_location[1]
        else:
            king_row, king_col = self.black_king_location[0], self.black_king_location[1]
        for i in range(8):
            end_row = r + king_moves[i][0]
            end_col = c + king_moves[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color: # can't capture an ally
                    if ally_color == 'w':
                        self.white_king_location = (end_row, end_col)
                    else:
                        self.black_king_location = (end_row, end_col)

                    in_check, pins, checks = self.check_for_pins_and_checks()

                    if not in_check:
                        moves.append(Move((r,c), (end_row, end_col), self.board))
                    # place king back on original location
                    if ally_color == 'w':
                        self.white_king_location = (r, c)
                    else:
                        self.black_king_location = (r, c)
        

    def get_castle_moves(self, r, c, moves, allyColor):
        inCheck, _, _ = self.check_for_pins_and_checks()
        if inCheck:
            return # can't castle while we are in check
        if (self.white_to_move and self.current_castling_right.wks) or (not self.white_to_move and self.current_castling_right.bks):
            self.get_kingside_castle_moves(r, c, moves, allyColor)
        if (self.white_to_move and self.current_castling_right.wqs) or (not self.white_to_move and self.current_castling_right.bqs):
            self.get_queenside_castle_moves(r, c, moves, allyColor)
        
    def get_kingside_castle_moves(self, r, c, moves, allyColor):
        if self.board[r][c+1] == self.board[r][c+2] == '--':
            if not self.square_under_attack(r, c+1) and not self.square_under_attack(r, c+2):
                moves.append(Move((r,c), (r, c+2), self.board, pawn_promotion = False, is_castle_move = True))
    
    def get_queenside_castle_moves(self, r, c, moves, allyColor):
        if self.board[r][c-1] == self.board[r][c-2] == self.board[r][c-3] == '--':
            if not self.square_under_attack(r, c-1) and not self.square_under_attack(r, c-2):
                moves.append(Move((r,c), (r, c-2), self.board, pawn_promotion = False, is_castle_move = True))


# update the castle rights given the move       
    def update_castle_rights(self, move):
        if move.piece_moved == 'wK':
            self.current_castling_right.wks = False
            self.current_castling_right.wqs = False
        elif move.piece_moved == 'bK':
            self.current_castling_right.bks = False
            self.current_castling_right.bqs = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0: # left rook
                    self.current_castling_right.wqs = False
                elif move.start_col == 7: # right rook
                    self.current_castling_right.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0: # left rook
                    self.current_castling_right.bqs = False
                elif move.start_col == 7: # right rook
                    self.current_castling_right.bks = False   
    
        # if a rook is captured
        if move.piece_captured == 'wR':
            if move.end_row == 7:
                if move.end_col == 0:
                    self.current_castling_right.wqs = False
                elif move.end_col == 7:
                    self.current_castling_right.wks = False
        elif move.piece_captured == 'bR':
            if move.end_row == 0:
                if move.end_col == 0:
                    self.current_castling_right.bqs = False
                elif move.end_col == 7:
                    self.current_castling_right.bks = False














