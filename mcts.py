from __future__ import absolute_import, division, print_function
import math
import random
import time
import copy
import heapq
#Feel free to add extra classes and functions

class State:
    def __init__(self, grid, player):
        self.grid = grid
        self.type = player
        self.visits = 1
        self.wins = 0
        self.parent = None
        self.children = []
        self.move = None
        self.won = False
        self.options = []

    # A method to set a piece in the grid of state class
    def set_piece(self, player, r, c):
        if self.grid[r][c] == '.':
            self.grid[r][c] = player
            return True
        return False
class MCTS:
    def __init__(self, grid, player):
        self.root = State(grid, player)
        self.maxrc = len(grid) - 1
        self.grid_count = 11
        self.simulations = 0
        self.root.options = self.optimal_move(grid, player)

    # A method to call the primary search method
    def uct_search(self):
        start_time = time.time()
        # Limiting the computational budget
        while time.time()-start_time <= 7:

            # Selection and expansion
            s = self.selection(self.root)

            # Simulation
            winner = self.simulation(s)

            # Backpropogation
            self.backpropagation(s, winner)
        ma_x = -math.inf
        move = None
        for child in self.root.children:
            if (child.wins/child.visits) > ma_x:
                ma_x = child.wins/child.visits
                move = child.move

        # Debug Statements
        # print(self.root.type)
        # print(self.simulations)
        # print(self.root.grid)
        # print(len(self.root.children))
        # for child in self.root.children:
        #     print(child.wins, '/', child.visits, ' ', child.move, child.type)
        # print('Returning move ', move)

        return move

    # Selecting the node that we will need to run simulation on
    # If a node is not fully expanded, we will call expansion
    def selection(self, state):
        while state.won == False:
            if len(state.children) < 5:
                # Expand if the state is not fully expanded
                return self.expansion(state)
            else:
                # If fully expanded, pick the best child
                state = state.children[self.best_child(state)]
        return state

    # Expanding the state if it is not fully expanded
    def expansion(self, state):
        new_state = copy.deepcopy(state)
        if new_state.type == self.root.type:
            r, c = heapq.heappop(state.options)[1]
        else:
            r, c = self.make_move(new_state)
        if state.type == 'w':
            new_type = 'b'
        else:
            new_type = 'w'
        child_node = State(new_state.grid, new_type)
        child_node.parent = state
        state.children.append(child_node)
        child_node.move = (r, c)

        if child_node.type == 'w':
            child_node.set_piece('b', r, c)
        else:
            child_node.set_piece('w', r, c)

        if self.check_win(child_node.grid, r, c):
            # if child_node.parent == self.root:
                # print('Move ', r, ',', c, ' set with win')
                # print(len(child_node.children))
            child_node.won = True
        else:
            child_node.won = False
        child_node.options = self.optimal_move(child_node.grid, child_node.type)
        return child_node

    # If a state is fully expanded, we pick its best child to traverse down the tree
    def best_child(self, state):
        ma_x = -math.inf
        best_child_index = 0
        for i in range(0, len(state.children)):
            if (state.children[i].wins/state.children[i].visits) + math.sqrt(math.log(state.visits, math.exp(1))/state.children[i].visits) > ma_x:
                ma_x = (state.children[i].wins/state.children[i].visits) + math.sqrt(math.log(state.visits, math.exp(1))/state.children[i].visits)
                best_child_index = i
        return best_child_index

    # After selection, we run simulation on the state, to see it on a random simulation,
    # this state has the potential to win
    def simulation(self, state):
        new_state = copy.deepcopy(state)
        # if new_state.won:
        #     print('Won at the beginning')
        while new_state.won is False:
            # new_state.options = self.optimal_move(new_state.grid, new_state.type)
            if new_state.type == self.root.type:
                r, c = heapq.heappop(new_state.options)[1]
            else:
                r, c = self.make_move(new_state)
            if new_state.type == 'w':
                new_type = 'b'
            else:
                new_type = 'w'
            child_node = State(new_state.grid, new_type)
            child_node.move = (r, c)
            if child_node.type == 'w':
                child_node.set_piece('b', r, c)
            else:
                child_node.set_piece('w', r, c)
            if self.check_win(child_node.grid, r, c):
                # print('Simulation won')
                child_node.won = True
            else:
                child_node.won = False
            child_node.options = self.optimal_move(child_node.grid, child_node.type)
            new_state = child_node
            # if new_state.won == True:
            #     print('Returning with won')
        simReward = {}
        if new_state.type == 'w':
            simReward['b'] = 0
            simReward['w'] = 1
        elif new_state.type == 'b':
            simReward['b'] = 1
            simReward['w'] = 0
        return simReward

    # We propogate the result of the simulation to all the
    # parents nodes from the state uptil the root
    def backpropagation(self, state, result):
        # while state is not None:
        # i = 0
        while state is not None:
            state.visits += 1
            state.wins = state.wins + result[state.type]
            state = state.parent
            # i += 1
        #print('Backpropogated ', i, ' times with', result )

    # Check if the given move would be a winning move for the grid
    def check_win(self, grid, r, c):
        #north direction (up)
        n_count = self.get_continuous_count(grid, r, c, -1, 0)
        #south direction (down)
        s_count = self.get_continuous_count(grid, r, c, 1, 0)
        #east direction (right)
        e_count = self.get_continuous_count(grid, r, c, 0, 1)
        #west direction (left)
        w_count = self.get_continuous_count(grid, r, c, 0, -1)
        #south_east diagonal (down right)
        se_count = self.get_continuous_count(grid, r, c, 1, 1)
        #north_west diagonal (up left)
        nw_count = self.get_continuous_count(grid, r, c, -1, -1)
        #north_east diagonal (up right)
        ne_count = self.get_continuous_count(grid, r, c, -1, 1)
        #south_west diagonal (down left)
        sw_count = self.get_continuous_count(grid, r, c, 1, -1)
        if (n_count + s_count + 1 >= 5) or (e_count + w_count + 1 >= 5) or \
                (se_count + nw_count + 1 >= 5) or (ne_count + sw_count + 1 >= 5):
            #print('Checking a returning true')
            return True
        else:
            return False

    # Helper function to to get continuous count of the player pieces
    def get_continuous_count(self, grid, r, c, dr, dc):
        piece = grid[r][c]
        result = 0
        i = 1
        while True:
            new_r = r + dr * i
            new_c = c + dc * i
            if 0 <= new_r < self.grid_count and 0 <= new_c < self.grid_count:
                if grid[new_r][new_c] == piece:
                    result += 1
                else:
                    break
            else:
                break
            i += 1
        return result

    # Function to get all possible options for the next move
    def get_options(self, grid):
        #collect all occupied spots
        current_pcs = []
        for r in range(len(grid)):
            for c in range(len(grid)):
                if not grid[r][c] == '.':
                    current_pcs.append((r,c))
        #At the beginning of the game, curernt_pcs is empty
        if not current_pcs:
            return [(self.maxrc//2, self.maxrc//2)]
        #Reasonable moves should be close to where the current pieces are
        #Think about what these calculations are doing
        #Note: min(list, key=lambda x: x[0]) picks the element with the min value on the first dimension
        min_r = max(0, min(current_pcs, key=lambda x: x[0])[0]-1)
        max_r = min(self.maxrc, max(current_pcs, key=lambda x: x[0])[0]+1)
        min_c = max(0, min(current_pcs, key=lambda x: x[1])[1]-1)
        max_c = min(self.maxrc, max(current_pcs, key=lambda x: x[1])[1]+1)
        #Options of reasonable next step moves
        options = []
        for i in range(min_r, max_r+1):
            for j in range(min_c, max_c+1):
                if not (i, j) in current_pcs:
                    options.append((i,j))
        return options

    # Function to make a random move
    def make_move(self,state):
        return random.choice(self.get_options(state.grid))

    # Check if the grid is full
    # Primarily used to check if the game ends in draw
    def check_full(self, grid):
        current_pcs = []
        for r in range(len(grid)):
            for c in range(len(grid)):
                if grid[r][c] == '.':
                    current_pcs.append((r, c))
        if not current_pcs:
            return True
        else:
            return False

    # Function to create a priority queue of possible moves
    # Sorted by their priority as ranked by heuristics
    def optimal_move(self, grid, player):
        new_grid = copy.deepcopy(grid)
        new_player = copy.deepcopy(player)
        optimal_moves = []
        options = self.get_options(new_grid)
        if new_player == 'w':
            opponent = 'b'
        else:
            opponent = 'b'
        for option in options:
            # opposition heuristics
            on_count = self.get_optimal_continuous_count(opponent, new_grid, option[0], option[1], -1, 0)
            # south direction (down)
            os_count = self.get_optimal_continuous_count(opponent, new_grid, option[0], option[1], 1, 0)
            # east direction (right)
            oe_count = self.get_optimal_continuous_count(opponent, new_grid, option[0], option[1], 0, 1)
            # west direction (left)
            ow_count = self.get_optimal_continuous_count(opponent, new_grid, option[0], option[1], 0, -1)
            # south_east diagonal (down right)
            ose_count = self.get_optimal_continuous_count(opponent, new_grid, option[0], option[1], 1, 1)
            # north_west diagonal (up left)
            onw_count = self.get_optimal_continuous_count(opponent, new_grid, option[0], option[1], -1, -1)
            # north_east diagonal (up right)
            one_count = self.get_optimal_continuous_count(opponent, new_grid, option[0], option[1], -1, 1)
            # south_west diagonal (down left)
            osw_count = self.get_optimal_continuous_count(opponent, new_grid, option[0], option[1], 1, -1)

            # MCTS player heuristics
            n_count = self.get_optimal_continuous_count(new_player, new_grid, option[0], option[1], -1, 0)
            # south direction (down)
            s_count = self.get_optimal_continuous_count(new_player, new_grid, option[0], option[1], 1, 0)
            # east direction (right)
            e_count = self.get_optimal_continuous_count(new_player, new_grid, option[0], option[1], 0, 1)
            # west direction (left)
            w_count = self.get_optimal_continuous_count(new_player, new_grid, option[0], option[1], 0, -1)
            # south_east diagonal (down right)
            se_count = self.get_optimal_continuous_count(new_player, new_grid, option[0], option[1], 1, 1)
            # north_west diagonal (up left)
            nw_count = self.get_optimal_continuous_count(new_player, new_grid, option[0], option[1], -1, -1)
            # north_east diagonal (up right)
            ne_count = self.get_optimal_continuous_count(new_player, new_grid, option[0], option[1], -1, 1)
            # south_west diagonal (down left)
            sw_count = self.get_optimal_continuous_count(new_player, new_grid, option[0], option[1], 1, -1)

            # The way this heuristic ranks moves is the following
            # Moves below are ranked in descending order of rank
            # 1) Moves for MCTS player to win
            # 2) Moves to block opposition win
            # 3) Moves for MCTS player to get above 3 consecutive
            # 4) Moves to block opposition player from getting above 3 consecutive
            # And this goes on in a sequential manner
            if (n_count + s_count + 1 >= 5) or (e_count + w_count + 1 >= 5) or \
                    (se_count + nw_count + 1 >= 5) or (ne_count + sw_count + 1 >= 5):
                heapq.heappush(optimal_moves, (15, (option[0], option[1])))
            elif (on_count + os_count + 1 >= 5) or (oe_count + ow_count + 1 >= 5) or \
                    (ose_count + onw_count + 1 >= 4) or (one_count + osw_count + 1 >= 4):
                heapq.heappush(optimal_moves, (13, (option[0], option[1])))
            elif (n_count + s_count + 1 >= 4) or (e_count + w_count + 1 >= 4) or \
                    (se_count + nw_count + 1 >= 4) or (ne_count + sw_count + 1 >= 4):
                heapq.heappush(optimal_moves, (10, (option[0], option[1])))
            elif (on_count + os_count + 1 >= 4) or (oe_count + ow_count + 1 >= 4) or \
                    (ose_count + onw_count + 1 >= 4) or (one_count + osw_count + 1 >= 4):
                heapq.heappush(optimal_moves, (7, (option[0], option[1])))
            elif (n_count + s_count + 1 >= 3) or (e_count + w_count + 1 >= 3) or \
                    (se_count + nw_count + 1 >= 3) or (ne_count + sw_count + 1 >= 3):
                heapq.heappush(optimal_moves, (4, (option[0], option[1])))
            elif (on_count + os_count + 1 >= 3) or (oe_count + ow_count + 1 >= 3) or \
                    (ose_count + onw_count + 1 >= 3) or (one_count + osw_count + 1 >= 3):
                heapq.heappush(optimal_moves, (3, (option[0], option[1])))
            elif (n_count + s_count + 1 >= 2) or (e_count + w_count + 1 >= 2) or \
                    (se_count + nw_count + 1 >= 2) or (ne_count + sw_count + 1 >= 2):
                heapq.heappush(optimal_moves, (2, (option[0], option[1])))
            else:
                heapq.heappush(optimal_moves, (1, (option[0], option[1])))

        # Using heapq, make into a priority queue which is descending in priority
        heapq._heapify_max(optimal_moves)
        return optimal_moves

    # Helper function to get continuous count for a particular piece
    def get_optimal_continuous_count(self, player, grid, r, c, dr, dc):
        piece = player
        result = 0
        i = 1
        while True:
            new_r = r + dr * i
            new_c = c + dc * i
            if 0 <= new_r < self.grid_count and 0 <= new_c < self.grid_count:
                if grid[new_r][new_c] == piece:
                    result += 1
                else:
                    break
            else:
                break
            i += 1
        return result