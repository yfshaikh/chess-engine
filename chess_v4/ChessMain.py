"""
Responsible for storing all the information about the current state of a chess game, as well as determining the valid moves at the current state. 
It will also keep a move log
"""
import pygame as p
from Chess import GameState, AI



BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 300
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
MENU_WIDTH = BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH
MENU_HEIGHT = BOARD_HEIGHT
MENU_ITEM_HEIGHT = 50
MENU_ITEM_WIDTH = 300
DIMENSION = 8 # dimensions of a chess board are 8x8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

# initialize a global dictionary of images
def load_images():
    pieces = ['wP', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bP', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
         IMAGES[piece] = p.transform.scale(p.image.load('Chess/images/' + piece + '.svg'), (SQ_SIZE, SQ_SIZE))


# main driver; will handle user input and updating graphics
#TODO: condense/tidy up main()
def main():

    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    move_log_font = p.font.SysFont('Lustria', 20, False, False)
    menu_font = p.font.SysFont('Lustria', 40, False, False)
    gs = GameState.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False # flag variable for when a move is made
    animate = False # flag variable for when we shoud animate a move
    load_images()
    sq_selected = () # no square is selected, keep track of the last click of the user (tuple: (row, col))
    player_clicks = [] # keep track of player clicks (two tuples: first click, second click)
    game_over = False
    global player_one # True if a human is playing white, False if AI is playing white
    global player_two # True if a human is playing black, False if AI is playing black
    menu_open = True
    game_open = True
    global max_depth
    max_depth = 3
    
    
    # menu loop
    while game_open and menu_open:
        for event in p.event.get():
            if event.type == p.QUIT:
                game_open = False

        menu_open = display_menu(screen, menu_font)
        p.display.flip()
    
        

    # game loop
    while game_open and not menu_open:

        human_turn  = (gs.white_to_move and player_one) or (not gs.white_to_move and player_two)
        for e in p.event.get():
            if e.type == p.QUIT:
                game_open = False



            # mouse handlers
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over and human_turn:
                    location = p.mouse.get_pos() # (x, y) location of the mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sq_selected == (row, col) or col >= 8: # user clicked the same square twice or user clicked move log
                        sq_selected = () # deselect
                        player_clicks = [] # clear player clicks
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected) # append for both first and second clicks
                    if len(player_clicks) == 2: # after the second click
                        move = GameState.Move(player_clicks[0], player_clicks[1], gs.board)
                        for i in range (len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(move) # switches turn
                                if gs.check_pawn_promotion(move):
                                        piece = display_promotion_popup(screen)
                                        if gs.white_to_move: # white turn now => black promoted before
                                                gs.board[move.end_row][move.end_col] = 'b' + str(piece) # replace pawn with promotion
                                        else:
                                                gs.board[move.end_row][move.end_col] = 'w' + str(piece)
                                        p.display.flip()
                        
                                move_made = True
                                animate = True
                                sq_selected = () # reset user clicks
                                player_clicks = []
                        if not move_made:
                            player_clicks = [sq_selected]



            # key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: # undo when 'z' is pressed
                    if player_two is False: # if playing against AI, reverse the AI's move as well (call undo_move twice)
                        gs.undo_move()
                    gs.undo_move()
                    move_made = True
                    animate = False
                    game_over = False
                if e.key == p.K_r: # reset the biard when 'r' is pressed
                    gs = GameState.GameState()
                    valid_moves = gs.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False

                    
                    


        # AI move finder
        if not game_over and not human_turn:
            ai_move = AI.find_best_move(gs, valid_moves, max_depth)
            if ai_move is None:
                ai_move = AI.find_random_move(valid_moves)
            gs.make_move(ai_move)
            if ai_move.piece_moved == 'bP' and gs.check_pawn_promotion(ai_move):
                print('test')
                # AI should always pick queen
                gs.board[ai_move.end_row][ai_move.end_col] = 'bQ' # replace pawn with promotion
                p.display.flip()
            move_made = True
            animate = True


        # make move
        if move_made:
            if animate:
                animate_move(gs.move_log[-1], screen, gs.board, clock)
            valid_moves = gs.get_valid_moves()
            animate = False
            move_made = False
        if gs.checkmate:
            game_over = True
            if gs.white_to_move:
                draw_end_game_text(screen, "Black wins by checkmate")
            else:
                draw_end_game_text(screen, "White wins by checkmate")
        if gs.stalemate:
            game_over = True
            draw_end_game_text(screen, "Stalemate")




        draw_game_state(screen, gs, valid_moves, sq_selected, move_log_font, menu_font, menu_open)
        clock.tick(MAX_FPS)
        p.display.flip()
    

# if a pawn is promoting, ask user what to promote to
def display_promotion_popup(screen):
    font = p.font.SysFont('Lustria', 30)
    popup_rect = p.Rect((BOARD_WIDTH // 2 - 100, BOARD_HEIGHT // 2 - 100, 200, 200))
    p.draw.rect(screen, p.Color('gray'), popup_rect)
    options = ['Q', 'R', 'B', 'N']
    option_rects = []

    for i, option in enumerate(options):
        option_text = font.render(option, True, p.Color('black'))
        option_rect = option_text.get_rect(center=(BOARD_WIDTH // 2, BOARD_HEIGHT // 2 - 60 + i * 40))
        option_rects.append((option_rect, option))
        screen.blit(option_text, option_rect)

    p.display.flip()

    while True:
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                exit()
            elif event.type == p.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                for option_rect, option in option_rects:
                    if option_rect.collidepoint(mouse_x, mouse_y):
                        return option  # Return the chosen promotion piece

# highlight the square selected and moves for the piece selected
def highlight_squares(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b'): # sqSelected is a piece that can be moved
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) # transparency value
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            # highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col*SQ_SIZE, move.end_row*SQ_SIZE))




# responsible for all the graphics in a current game state
def draw_game_state(screen, gs, valid_moves, sq_selected, move_log_font, menu_font, menu_open):
    draw_board(screen) 
    highlight_squares(screen, gs, valid_moves, sq_selected)
    draw_pieces(screen, gs.board)
    draw_move_log(screen, gs, move_log_font)




# draw the squares on the board
def draw_board(screen):
    global colors
    colors = [p.Color('white'), p.Color('gray')]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))



# draw the pieces on the board using the current GameState.board
def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
             piece = board[r][c]
             if piece != '--': # not empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


# draw move log next to game
def draw_move_log(screen, gs, move_log_font):

    #TODO: menu that starts at x = 0
    move_log_rect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, (61, 60, 57), move_log_rect)
    move_log = gs.move_log
    move_texts = []
    for i in range (0, len(move_log), 2):
        move_string = str(i//2 + 1) + '. ' + str(move_log[i]) + ' '
        if i+1 < len(move_log): # make sure black made a move
            move_string += str(move_log[i+1])
        move_texts.append(move_string)

    moves_per_row = 3
    padding = 5
    text_y = padding
    line_spacing = 2
    for i in range(0, len(move_texts), moves_per_row):
        text = ''
        for j in range(moves_per_row):
            if i+j < len(move_texts):
                text += move_texts[i+j] + ' '
        text_object = move_log_font.render(text, True, p.Color('white'))
        text_location = move_log_rect.move(padding, text_y)
        screen.blit(text_object, text_location)
        text_y += text_object.get_height() + line_spacing


# display menu
def display_menu(screen, menu_font):
    global player_one
    global player_two
    global max_depth

    # Clear the menu area with a dark background
    menu_rect = p.Rect(0, 0, MENU_WIDTH, MENU_HEIGHT)
    p.draw.rect(screen, (61, 60, 57), menu_rect)

    # Render the title "Chess" and center it at the top
    title_text = menu_font.render('Chess', True, p.Color('white'))
    title_rect = title_text.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 8))
    screen.blit(title_text, title_rect)

    

    # menu options
    menu_options = ['Two Player', 'Computer (easy)', 'Computer (hard)', 'Quit']


    # Define the outline rectangles for each menu option
    spacing = 20
    start_y = title_rect.bottom + spacing
    start_x = (MENU_WIDTH - MENU_ITEM_WIDTH) // 2
    outline_rects = [
    p.Rect(start_x, start_y + i * (MENU_ITEM_HEIGHT + spacing), MENU_ITEM_WIDTH, MENU_ITEM_HEIGHT)
    for i in range(len(menu_options))
    ]   


    
    # Render each menu option text
    for i, option in enumerate(menu_options):
        text_object = menu_font.render(option, True, p.Color('white'))
        text_rect = text_object.get_rect(center=outline_rects[i].center)
        screen.blit(text_object, text_rect)
        
        # Draw outline rectangle
        p.draw.rect(screen, p.Color('white'), outline_rects[i], 3)

    # intstructions
    font = p.font.SysFont('Lustria', 30, False, False)
    instructions = ['z - undo move', 'r - restart game']
    instructions_start_y = start_y + len(menu_options) * (MENU_ITEM_HEIGHT + 10) + 50
    for j, instruction in enumerate(instructions):
        instruction_text = font.render(instruction, True, p.Color('white'))
        instruction_rect = instruction_text.get_rect(center=(MENU_WIDTH // 2, instructions_start_y + j * 40))
        screen.blit(instruction_text, instruction_rect)


    # Check for mouse input and perform actions
    mouse_x, mouse_y = p.mouse.get_pos()
    mouse_clicked = p.mouse.get_pressed()

    for i, rect in enumerate(outline_rects):
        if rect.collidepoint(mouse_x, mouse_y):
            if mouse_clicked[0]:  # Check for left mouse button click
                option = menu_options[i]
                if option == 'Two Player':
                    player_one = True
                    player_two = True
                    return False
                elif option == 'Computer (easy)':
                    max_depth = 1
                    player_one = True
                    player_two = False
                    return False
                elif option == 'Computer (hard)':
                    max_depth = 3
                    player_one = True
                    player_two = False
                    return False
                elif option == 'Quit':
                    return False  # Close the window
    return True  # Keep the menu open



# animating a move
def animate_move(move, screen, board, clock):
    global colors
    coords = [] # list of coords that the animation will move through
    dR = move.end_row - move.start_row
    dC = move.end_col - move.start_col
    frames_per_square = 10 # frames to move one square
    frame_count = (abs(dR) + abs(dC)) * frames_per_square


        
    for frame in range (frame_count + 1):
        r, c = (move.start_row + dR*frame/frame_count + 10, move.start_col + dC*frame/frame_count + 10)
        draw_board(screen)
        draw_pieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.end_row + move.end_col)%2]
        end_square = p.Rect(move.end_col*SQ_SIZE, move.end_row*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        # draw moving piece
        screen.blit(IMAGES[move.piece_moved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

# draw endgame text
def draw_end_game_text(screen, text):
    font = p.font.SysFont('Lustria', 32, False, False)
    text_object = font.render(text, 1, p.Color('White'))
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH/2 - text_object.get_width()/2, BOARD_HEIGHT/2 - text_object.get_height()/2)

    while True:
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                return
        p.draw.rect(screen, (217, 84, 61), ((BOARD_WIDTH - 300) // 2, (BOARD_HEIGHT - 45) // 2, 300, 45))
        screen.blit(text_object, text_location)
        p.display.flip()

   

main()

