from pettingzoo.classic import connect_four_v3
import random
import math
import time


ROW_COUNT = 6
COLUMN_COUNT = 7
PLAYER_NUMBER = 2
AI_NUMBER = 1
EMPTY = 0
WINING_LEN = 4
FOUR_SAME_COLOR_SCORE = 100
THREE_SAME_COLOR_SCORE = 10
TWO_SAME_COLOR_SCORE = 3
THREE_SAME_COLOR_OPP_SCORE = -15

# Create Environment
env = connect_four_v3.env(render_mode="human")
env.reset()


def generate_map(env):
    observation, reward, termination, truncation, info = env.last()
    # print(observation['observation'][:, :, 1])
    mat = observation['observation'][:, :, AI_NUMBER-1]
    mat2 = observation['observation'][:, :, PLAYER_NUMBER-1]
    for i in range(6):
        for j in range(7):
            if mat2[i][j] == 1:
                mat[i][j] = 2
    return mat


def minimax(game_matrix, depth, alpha, beta, maximizingPlayer):
    end = check_end(game_matrix)
    valid_cols = valid_columns_to_drop(game_matrix)
    if end :
        if has_won(game_matrix, AI_NUMBER):
                return (None, 1000000000)
        elif has_won(game_matrix, PLAYER_NUMBER):
                return (None, -1000000000)
        else:
                return (None, 0)

    if depth == 0 :
            return (None, score_position(game_matrix, AI_NUMBER))
        
    if maximizingPlayer: 
        max_score = -math.inf
        column = random.choice(valid_cols)
        for col in valid_cols:
            row = first_empty_row(game_matrix, col)
            mat_copy = game_matrix.copy()
            mat_copy[row][col] = AI_NUMBER
            new_score = minimax(mat_copy, depth - 1, alpha, beta, False)[1]
            if new_score > max_score:
                max_score = new_score
                column = col
            alpha = max(alpha, max_score)
            if alpha >= beta:
                break
        return column, max_score

    else:  # Minimizing player
        max_score = math.inf
        column = random.choice(valid_cols)
        for col in valid_cols:
            row = first_empty_row(game_matrix, col)
            mat_copy = game_matrix.copy()
            mat_copy[row][col] = PLAYER_NUMBER
            new_score = minimax(mat_copy, depth - 1, alpha, beta, True)[1]
            if new_score < max_score:
                max_score = new_score
                column = col
            beta = min(beta, max_score)
            if alpha >= beta:
                break
        return column, max_score


def check_end(game_matrix):
    if has_won(game_matrix, PLAYER_NUMBER) or has_won(game_matrix, AI_NUMBER) or len(valid_columns_to_drop(game_matrix)) == 0:
        return 1
    return 0


def first_empty_row(game_matrix, col):
    for row in range(ROW_COUNT-1,-1,-1):
        if game_matrix[row][col] == 0:
            return row


def has_won(game_matrix, agent):

    # Check horizontal for win
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(game_matrix[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c + WINING_LEN]
            if window.count(agent) == 4:
                return True

    # Check vertical for win
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(game_matrix[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r + WINING_LEN]
            if window.count(agent) == 4:
                return True

    # Check positively sloped diaganols
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [game_matrix[r + i][c + i] for i in range(WINING_LEN)]
            if window.count(agent) == 4:
                return True
            
    # Score negative sloped diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [game_matrix[r + 3 - i][c + i] for i in range(WINING_LEN)]
            if window.count(agent) == 4:
                return True

    return False


def window_score(window, agent, mode = None):
    score = 0
    opp_agent = PLAYER_NUMBER
    if agent == PLAYER_NUMBER:
        opp_agent = AI_NUMBER

    if window.count(agent) == 4:
        score +=  FOUR_SAME_COLOR_SCORE
    elif window.count(agent) == 3 and window.count(EMPTY) == 1:
        score +=  THREE_SAME_COLOR_SCORE
    elif window.count(agent) == 2 and window.count(EMPTY) == 2:
        score += TWO_SAME_COLOR_SCORE

    if window.count(opp_agent) == 3 and window.count(EMPTY) == 1:
        if mode == "vertical":
            # should have more effect because we can be sure all the place beneath are filled
            score-= THREE_SAME_COLOR_OPP_SCORE*2
        else: score -= THREE_SAME_COLOR_OPP_SCORE

    return score


def score_position(game_matrix, agent):
    score = 0
    # center column is a good move to take
    center_array =[]
    for i in range(5,-1,-1):
        center_array.append(game_matrix[i][COLUMN_COUNT // 2])
    center_count = center_array.count(agent)
    # the more agent piece is in center column, the more possible to prevent the opponent from wining
    score += center_count * 4

    # Horizontal score
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(game_matrix[r, :])]
        for c in range(COLUMN_COUNT - 3):
            alpha = 1
            window = row_array[c:c + WINING_LEN]
            # in horizontal wondow it is possible that the below row is not filled and you may need a piece to firts
            # fill the row below so that you could place your piece
            if r<4 :
                row_array2 = [int(i) for i in list(game_matrix[r+1, :])]
                window2= row_array2[c:c + WINING_LEN]
                score_window2 = window_score(window2, agent)
                if score_window2 == THREE_SAME_COLOR_SCORE:
                    alpha = 0.6
                elif score_window2 == TWO_SAME_COLOR_SCORE:
                    alpha = 0.4
                
        score+= window_score(window, agent)*alpha

    # Vertical score
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(game_matrix[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r + WINING_LEN]
            score += window_score(window, agent, "vertical")

    # positive sloped diagonal score
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [game_matrix[r + i][c + i] for i in range(WINING_LEN)]
            score += window_score(window, agent)

    # negative sloped diagonal score
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [game_matrix[r + 3 - i][c + i] for i in range(WINING_LEN)]
            score += window_score(window, agent)

    return score


def valid_columns_to_drop(game_matrix):
    valid_cols = []
    for col in range(COLUMN_COUNT):
        if game_matrix[0][col] == EMPTY:
            valid_cols.append(col)
    return valid_cols

print("Choose what game you want to play:")
print("1. AI AGENT with HUMAN")
print("2. AI AGENT with AI AGENT")
print("3. AI AGENT with RANDOM AGENT")

game = int(input())
while not (game == 1 or game == 2 or game ==3 ) :
    print("Wrong entry, choose a valid number")
    game = int(input())

if game == 1 :
    # AI WITH HUMAN
    for agent in env.agent_iter():
        # if agent == 'player_1':
        #     PLAYER_NUMBER = 1
        #     AI_NUMBER = 2
        # else:
        #     PLAYER_NUMBER = 2
        #     AI_NUMBER = 1
        observation, reward, termination, truncation, info = env.last()

        if termination or truncation:
            action = None
            if reward == 1:
                print("AI AGENT HAS WON")
            elif reward == -1:
                print("YOU WON")
            else:
                print("DRAW")
            time.sleep(30)
            env.reset()
            break

        else:
            if agent == 'player_0':
                game_matrix = generate_map(env)
                col, minimax_score = minimax(game_matrix, 5, -math.inf, math.inf, True)
                if game_matrix[0][col] == EMPTY:
                    env.step(col)
            else : 
                col =  int(input())
                if game_matrix[0][col] == EMPTY:
                    env.step(col)
                else:
                    print("INVALID ACTION")

    env.close()
elif game == 2 :
    # AI WITH AI
    for agent in env.agent_iter():
        if agent == 'player_1':
            PLAYER_PIECE = 1
            AI_PIECE = 2
        else:
            PLAYER_PIECE = 2
            AI_PIECE = 1
        observation, reward, termination, truncation, info = env.last()

        if termination or truncation:

            action = None
            if reward == 1:
                print("THE FIRST AGENT HAS WON")
            elif reward == -1:
                print("THE SECOND AGENT HAS WON")
            else:
                print("DRAW")
            time.sleep(30)
            env.reset()
            break
        else:
            game_matrix = generate_map(env)
            col, minimax_score = minimax(game_matrix, 6, -math.inf, math.inf, True)
            if game_matrix[0][col] == EMPTY:
                env.step(col)

    env.close()

elif game == 3 :
    # AI WITH RANDOM

    for agent in env.agent_iter():
        observation, reward, termination, truncation, info = env.last()

        if termination or truncation:
            action = None
            if reward == 1:
                print("THE AI AGENT HAS WON")
            elif reward == -1:
                print("THE RANDOM AGENT HAS WON")
            else:
                print("DRAW")
            time.sleep(30)
            env.reset()
            break
        else:
            if agent == 'player_0':
                action = env.action_space(agent).sample()
                env.step(action)
            else : 
                game_matrix = generate_map(env)
                col, minimax_score = minimax(game_matrix, 5, -math.inf, math.inf, True)
                if game_matrix[0][col] == EMPTY:
                    env.step(col)

    env.close()