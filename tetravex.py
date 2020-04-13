
#USAGE
#"python tetravex.py n", where n is the length of the Tetravex board

'''
Given a Tetravex game with an n by n board and an n by n set of tiles
(e.g. http://smart-games.org/en/tetravex ),
this module will detect the tetravex game, find the solution, and automatically
input the solution by dragging the tiles to their correct location
'''

from tetravex_detection import TetravexDetection
from tetravex_solver import TetravexSolver
import argparse

#parse the input value of n
ap = argparse.ArgumentParser()
ap.add_argument("n", help="Length of board")
args = vars(ap.parse_args())
n = int(args["n"])

#detect the tiles, and get the coordinates of the board and the tiles
td = TetravexDetection(n)
tiles_array = td.detect_puzzle_from_screen()
tile_coordinates = td.get_tiles_coordinates()
board_coordinates = td.get_board_coordinates()
board_width = td.get_board_width()

if not tile_coordinates:
    print("tiles not found")
elif not board_coordinates:
    print("board not found")
else:

    #solve the puzzle
    ts = TetravexSolver(n)
    solution = ts.solve(tiles_array)

    mac = True
    if mac:
        tile_coordinates = [coord / 2 for coord in tile_coordinates]
        board_coordinates = [coord / 2 for coord in board_coordinates]
        board_width = board_width / 2

    #automatically input the solution
    ts.set_tile_coordinates(tile_coordinates)
    ts.set_board_coordinates(board_coordinates)
    ts.set_board_width(board_width)
    ts.input_solution()
