
class Move:
    ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4,
                   '5': 3, '6': 2, '7': 1, '8': 0}
    rows_to_ranks = {v: k for k, v, in ranks_to_rows.items()}
    files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3,
                   'e': 4, 'f': 5, 'g': 6, 'h': 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, is_enpassant_move = False, pawn_promotion = False, is_castle_move = False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.is_pawn_promotion = pawn_promotion
        self.promoted_piece = None
        self.is_enpassant_move = is_enpassant_move
        if self.is_enpassant_move:
            self.piece_captured = 'wP' if self.piece_moved == 'bP' else 'bP'
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
        self.is_capture = self.piece_captured != '--'
        self.is_castle_move = is_castle_move
        
        

    # overriding the equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def get_rank_file(self, row, col):
        return self.cols_to_files[col] + self.rows_to_ranks[row]
    
    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)
    
    # overriding the string function
    def __str__(self):
        # castle move
        if self.is_castle_move:
            return 'O-O' if self.end_col == 6 else 'O-O-O'
        
        end_square = self.get_rank_file(self.end_row, self.end_col)
        # pawn moves
        if self.piece_moved[1] == 'P':
            if self.is_capture:
                return self.cols_to_files[self.start_col] + 'x' + end_square
            else:
                return end_square
            
            # TODO: pawn promotions
        
        #TODO: + for check move, # for checkmate

        # piece moves
        move_string = self.piece_moved[1]
        if self.is_capture:
            move_string += 'x'
        return move_string + end_square




    