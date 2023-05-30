# import Library
from pettingzoo.classic import connect_four_v3
import random
import math
import time


ROW_COUNT = 6
COLUMN_COUNT = 7
PLAYER_NUMBER = 2
AI_NUMBER = 1
EMPTY = 0
WINDOW_LENGTH = 4
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
    # Check horizontal locations for win
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if game_matrix[r][c] == agent and game_matrix[r][c + 1] == agent and game_matrix[r][c + 2] == agent and game_matrix[r][
                c + 3] == agent:
                return True

    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if game_matrix[r][c] == agent and game_matrix[r + 1][c] == agent and game_matrix[r + 2][c] == agent and game_matrix[r + 3][
                c] == agent:
                return True

    # Check positively sloped diaganols
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if game_matrix[r][c] == agent and game_matrix[r + 1][c + 1] == agent and game_matrix[r + 2][c + 2] == agent and game_matrix[r + 3][
                c + 3] == agent:
                return True

    # Check negatively sloped diaganols
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if game_matrix[r][c] == agent and game_matrix[r - 1][c + 1] == agent and game_matrix[r - 2][c + 2] == agent and game_matrix[r - 3][
                c + 3] == agent:
                return True


def evaluate_window(window, agent, mode = None):
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
            score-= THREE_SAME_COLOR_OPP_SCORE*2
        else: score -= THREE_SAME_COLOR_OPP_SCORE

    return score


def score_position(game_matrix, agent):
    score = 0

    ## Score center column
    center_array = [int(i) for i in list(game_matrix[:, COLUMN_COUNT // 2])]
    center_array =[]
    for i in range(5,-1,-1):
        center_array.append(game_matrix[i][COLUMN_COUNT // 2])
    # center_count = center_array.count(0)
    center_count = center_array.count(agent)
    score += center_count * 3
    # if center_count >= 4 :
    #     score += center_count * 3
    # else :
    #      center_count = center_array.count(agent)
    #      score += center_count * 2


    ## Score Horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(game_matrix[r, :])]
        for c in range(COLUMN_COUNT - 3):
            alpha = 1
            window = row_array[c:c + WINDOW_LENGTH]
            if r<4 :
                row_array2 = [int(i) for i in list(game_matrix[r+1, :])]
                window2= row_array2[c:c + WINDOW_LENGTH]
                score_window2 = evaluate_window(window2, agent)
                if score_window2 == THREE_SAME_COLOR_SCORE:
                    alpha = 0.6
                elif score_window2 == TWO_SAME_COLOR_SCORE:
                    alpha = 0.4
                
        score+= evaluate_window(window, agent)*alpha

    ## Score Vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(game_matrix[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r + WINDOW_LENGTH]
            score += evaluate_window(window, agent, "vertical")

    ## Score posiive sloped diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [game_matrix[r + i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, agent)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [game_matrix[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, agent)

    return score


def valid_columns_to_drop(game_matrix):
    valid_cols = []
    for col in range(COLUMN_COUNT):
        if game_matrix[0][col] == 0:
            valid_cols.append(col)
    return valid_cols


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
            print("draw")
        time.sleep(30)
        env.reset()
        break

    else:
        if agent == 'player_0':
            game_matrix = generate_map(env)
            col, minimax_score = minimax(game_matrix, 5, -math.inf, math.inf, True)
            if game_matrix[0][col] == 0:
                env.step(col)
        else : 
            col =  int(input())
            if game_matrix[0][col] == 0:
                env.step(col)
            else:
                print("Invalid action!")


env.close()



