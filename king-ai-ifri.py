"""
Created on 26 oct. 16:01 2020

@author: Team:King
"""

from core import *
from seega.seega_rules import SeegaRules
from seega.seega_actions import *
from seega.seega_state import *
import numpy as np
import random

class AI(Player):

    in_hand = 12
    score = 0
                
    def __init__(self, color):
        super(AI, self).__init__(color)
        self.position = color.value
        
    def has_enemy_neighboor(self,board,cell,color):
        cells_to_verify = [ ( cell[0], cell[1] + 1 ) , ( cell[0] , cell[1] - 1 ) , ( cell[0] + 1 , cell[1] ) , ( cell[0] - 1 , cell[1] )]
        enemies = []
        for cell_to_verify in cells_to_verify:
            his_color = board.get_cell_color(cell_to_verify)
            if his_color != color and his_color != 0:
                enemies.append(cell_to_verify)
        return enemies
    
    def can_be_eaten(self,board,piece,with_enemy):
        place = []
        for enemy in with_enemy:
            condition = (piece[0] - enemy[0],piece[1]-enemy[1])
            if condition == (1,0):
                to_empty = (enemy[0]-1,enemy[0])
                if(board.get_cell_color(to_empty) == Color.empty):
                    place.append(to_empty)
            elif condition == (-1,0):
                to_empty = (enemy[0]+1,enemy[0])
                if(board.get_cell_color(to_empty) == Color.empty):
                    place.append(to_empty)
            elif condition == (0,1):
                to_empty = (enemy[0],enemy[0]-1)
                if(board.get_cell_color(to_empty) == Color.empty):
                    place.append(to_empty)
                print(board.get_cell_color(to_empty))
            elif condition == (0,-1):
                to_empty = (enemy[0],enemy[0]+1)
                if(board.get_cell_color(to_empty) == Color.empty):
                    place.append(to_empty)
                print(board.get_cell_color(to_empty))
        return place
            
    def go_to_place(self,movables,destinations,board):
        print(movables,destinations)
        if(len(movables)==0 or len(destinations)==0):
            return False
        while(True):
            max_value = 1;
            place = destinations[0]
            movable = movables
            for dest in destinations:
                if destinations.count(dest) >= max_value:
                    max_value = destinations.count(dest)
                    place = dest
            for piece in movable:
                block = False
                x = piece[0]
                y = piece[1]   
                while not block:
                    if(x==place[0] and y!=place[1]):
                        if(board.get_cell_color((x,y+1))==0):
                            ++y
                            return SeegaAction(action_type=SeegaActionType.MOVE,at=piece,to=(x,y))
                        else:
                            block==True
                    elif(x!=place[0] and y==place[1]):
                        if(board.get_cell_color((x+1,y))==0):
                            ++x
                            return SeegaAction(action_type=SeegaActionType.MOVE,at=piece,to=(x,y))
                        else:
                            block==True
                    elif x!=place[0] and y!=place[1]:
                        if(board.get_cell_color((x,y+1))==0):
                            ++y
                            return SeegaAction(action_type=SeegaActionType.MOVE,at=piece,to=(x,y))
                        elif(board.get_cell_color((x+1,y))==0):
                            ++x
                            return SeegaAction(action_type=SeegaActionType.MOVE,at=piece,to=(x,y))
                        else:
                            block==True
                if(block==True):
                    movable.remove(piece)
            if(len(movable)==0):
                destinations.remove(place)
            if (len(destinations)==0):
                return False;
            
            
    def make_move(self,state,all_lose_move,color,board):
        destinations = []
        movable = []
        with_enemy = {}
        for piece in all_lose_move:
            with_enemy[piece] = self.has_enemy_neighboor(state.board,piece,color)
            with_enemy[piece] = self.can_be_eaten(state.board,piece,with_enemy[piece])
            if len(with_enemy[piece]) != 0:
                destinations.extend(with_enemy[piece])
            else:
                movable.append(piece)
        target = self.go_to_place(movable,destinations,board)
        if(isinstance(target, SeegaActionType)):
            return target
        else:
            random_piece = [piece for piece in all_lose_move]
            random_piece = random.choice(random_piece)
            if len(all_lose_move[random_piece]) !=0:
                #self.moveWhenCantWon(state, self.color)
                choose = random.choice(all_lose_move[random_piece])
                return SeegaAction(action_type=SeegaActionType.MOVE,at=random_piece,to=choose)

            
    def empty_neighboor_cells(self, cell,empty_cells):
        cells_to_verify = [ ( cell[0], cell[1] + 1 ) , ( cell[0] , cell[1] - 1 ) , ( cell[0] + 1 , cell[1] ) , ( cell[0] - 1 , cell[1] )]
        valid_cells = []
        for i in range(len(cells_to_verify)):
            if cells_to_verify[i] in empty_cells:
                valid_cells.append(cells_to_verify[i])
        return valid_cells
    
    def matching(self,state,cell,color,x,y,a,b):
        is_oppenent = state.board.get_cell_color((cell[0]+x,cell[1]+y)) != color
        is_oppenent = is_oppenent and state.board.get_cell_color((cell[0]+x,cell[1]+y)) != 0
        is_friend = state.board.get_cell_color((cell[0]+a,cell[1]+b)) == color
        return (is_oppenent and is_friend)

    def general_matching(self,origin_cell,cell,condition,state,color,index):
        count = 0
        if (origin_cell[0]-cell[0],origin_cell[1]-cell[1]) == condition:
            if self.matching(state,cell,color,index[0][0],index[0][1],index[0][2],index[0][3]):
                count += 1
            if self.matching(state,cell,color,index[1][0],index[1][1],index[1][2],index[1][3]):
                count += 1
            if self.matching(state,cell,color,index[2][0],index[2][1],index[2][2],index[2][3]):
                    count += 1
        return count
    def can_eat(self,empty_cells,origin_cell,state,color):
        max_eat = []
        for cell in empty_cells:
            count = self.general_matching(origin_cell,cell,(-1,0),state,color,[[1,0,2,0],[0,1,0,2],[0,-1,0,-2]])
            count = self.general_matching(origin_cell,cell,(0,-1),state,color,[[1,0,2,0],[0,1,0,2],[-1,0,-2,0]])
            count = self.general_matching(origin_cell,cell,(1,0), state,color,[[0,1,0,2],[-1,0,-2,0],[0,-1,0,-2]])
            count = self.general_matching(origin_cell,cell,(0,1), state,color,[[1,0,2,0],[-1,0,-2,0],[0,-1,0,-2]])
            max_eat.append(count)
        return max_eat
    
    def main_phase2(self,state,color):
        pieces_onboard = state.board.get_player_pieces_on_board(color)
        empty_cells = state.board.get_all_empty_cells()
        all_win_move = {}
        all_lose_move = {}
        max_eat = 0
        move_one = None
        origin = None
        all_possibility = {}
        # recherche de toutes les possibilités de bouffes pour chaque piece et des pièces qui peuvent se déplacer mais ne peuvent pas bouffés
        for piece in pieces_onboard:
            all_possibility[piece] = self.empty_neighboor_cells(piece,empty_cells)
            """ 
                all_possibility{
                    (piece_position) : [all_his_empty_neighboor]
                }
            """
            if(len(all_possibility[piece])!=0):
                max_min = self.can_eat(all_possibility[piece],piece,state,color)
                max_value = max(max_min)
                if (max_value!=0):
                    all_win_move[piece] = [all_possibility[piece][max_min.index(max_value)],max_value]
                    max_value = 0
                else:
                    all_lose_move[piece] = all_possibility[piece]
        for moves in all_win_move:
            if(max_eat < all_win_move[moves][1]):
                max_eat = all_win_move[moves][1]
                move_one = all_win_move[moves][0]
                origin = moves
        if max_eat != 0:
            return SeegaAction(action_type=SeegaActionType.MOVE, at=origin,to=move_one)
        #else:
        #    return self.make_move(state,all_lose_move,self.color,state.board)
            
    def play(self, state, remain_time):

        print(f"Player {self.name} is playing.\n Time remain is ", remain_time, " seconds")
        phase =  1 if self.in_hand > 0 else 2
        
        if phase == 1:
            return SeegaRules.random_play(state, self.position)
        else:
            return self.main_phase2(state,self.color)
 #return SeegaAction(action_type=SeegaActionType.ADD,to=(1, 0))
    def set_score(self, new_score):
        self.score = new_score

    def update_player_infos(self, infos):
        self.in_hand = infos['in_hand']
        self.score = infos['score']
        
    def reset_player_informations(self):
        self.in_hand = 12
        self.score = 0
