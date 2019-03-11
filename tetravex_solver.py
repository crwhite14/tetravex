
import pyautogui, time
import copy

class TetravexSolver:

	def __init__(self, n):
		self.n = n
		self.tiles = []
		
	def input_solution(self):
		#get the coordinates of the tiles and the board
		x_tiles, y_tiles = self.tile_coordinates
		x_board, y_board = self.board_coordinates
		tile_length = self.board_width / self.n

		#for each tile, drag it to its correct location on the board
		for i in range(self.n):
			for j in range(self.n):
				[num] = self.solution[i][j]
				
				#get the (x,y) coordinate of the tile
				x = num // self.n
				y = num % self.n
				
				#move the mouse to the location of the tile
				pyautogui.moveTo(x_tiles + tile_length/2 + y*tile_length, y_tiles + tile_length/2 + x*tile_length)
				
				#move the mouse to its correct location on the board
				pyautogui.dragTo(x_board + tile_length/2 + j*tile_length, y_board + tile_length/2 + i*tile_length, 0.5, pyautogui.easeOutQuad) 
				
	def solve(self, tiles_array):
	#solve the tetravex puzzle
	
		self.n = len(tiles_array)
		partial_solution = []
		
		'''
		partial_solution is an array where partial_solution[i] contains all possible tiles that fit in board location i
		at the start, for all i, partial_solution[i] contains an array of every tile
		at the end, for all i, partial_solution[i] contains a single tile (i.e., we have solved the puzzle)
		'''
		
		#for each board location i, set up partial_solution[i]
		for i in range(self.n):
			partial_solution.append([])
			for j in range(self.n):
				self.tiles.append(tiles_array[i][j])
				partial_solution[i].append([k for k in range(self.n*self.n)])
		
		#use recursion to solve the puzzle
		self.solution = self.recur(partial_solution)[1]
		
		return self.solution
		
	def recur(self, partial_solution):

		#find the index of partial_solution containing the fewest elements
		#ie., we find the board location with the fewwest choices of tiles
		min = self.n * self.n + 1
		i,j = -1,-1
		for x in range(self.n):
			for y in range(self.n):
				if 1<len(partial_solution[x][y]) < min:
					min = len(partial_solution[i][j])
					i,j = x,y

		#if all board locations have just one possible tile,
		#then we have solved the puzzle
		if i == -1:
			return (True, partial_solution)

		#recur on each choice of tile
		for tile in partial_solution[i][j]:
			ps = copy.deepcopy(partial_solution)
			ps[i][j] = [tile]	
	
			#self.update() updates partial_solution, and returns false if there
			#is a logical contradiction
			if self.update(ps, i, j):
			
				solved, solution = self.recur(ps)
				if solved:
					return (True, solution)
				
		#if we tried all choices of the tile and none fit, return False
		return (False, [])
			
	def update(self, partial_solution, i, j):
		'''
		update is called immediately after we guess the tile that fits into location [i][j]
		update recursively prunes the potential tiles using two facts (let tile = partial_solution[i][j]):
		(1) No other board location can contain tile
		(2) each neighbor of [i][j] (above, below, left, right) must match the color of the side it shares with [i][j]
		e.g. if the top side of tile is red, then partial_solution[i-1][j] must only contain tiles whose bottom is red
		
		If, during these updates, we find a logical error (e.g., some location has no possible tiles), then return false
		If, during these updates, we find a new tile location (e.g., some location has one possible tile),
		then we must recursively prune the potential tiles using facts (1) and (2)
		'''
		
		#dirty is the list of locations that got set to a tile
		#initially, add (i,j) to dirty because we set partial_solution[i][j] = tile
		dirty = [(i,j)]
		
		while len(dirty) > 0:
			i,j = dirty.pop()
			[tile] = partial_solution[i][j]

			#remove tile from all other places in partial_solution
			for x in range(self.n):
				for y in range(self.n):
					for k,elt in enumerate(partial_solution[x][y]):
					
						#remove tile from location [x][y]
						if elt == tile and (i != x or j != y):
							partial_solution[x][y].pop(k)
							
							#if the number of possible tiles in location [x][y] is zero,
							#then this cannot be the solution to the puzzle
							if len(partial_solution[x][y]) == 0:
								return False
							
							#if the number of possible tiles in location [x][y] is one,
							#then we found a new tile location, so we later must update partial_solution accordingly
							#we do this by adding [x][y] to dirty
							elif len(partial_solution[x][y]) == 1:
								dirty.append((x,y))
			
			#compute the neighbors of location (i,j)
			neighbors = []
			if i > 0:
				neighbors.append(('above', i-1, j))
			if i < self.n - 1:
				neighbors.append(('below', i+1, j))
			if j > 0:
				neighbors.append(('left', i, j-1))
			if j < self.n - 1:
				neighbors.append(('right', i, j+1))
				
			tile_side = {'above':0, 'left':1, 'right':2, 'below':3}
			nbhr_side = {'above':3, 'left':2, 'right':1, 'below':0}
				
			#for each neighbor, update its list of possible tiles
			for neighbor in neighbors:
				updated = []
				for potential_neighboring_tile in partial_solution[neighbor[1]][neighbor[2]]:
				
					#if the colors don't match between tile and its potential neighboring tile,
					#the neighboring tile is removed from partial_solution[neighbor[0][neighbor[1]]
					if self.tiles[tile][tile_side[neighbor[0]]] == self.tiles[potential_neighboring_tile][nbhr_side[neighbor[0]]]:
						updated.append(potential_neighboring_tile)
				
				#if the number of possible tiles in location [x][y] is zero,
				#then this cannot be the solution to the puzzle		
				if len(updated) == 0:
					return False
					
				#if the number of possible tiles in location [x][y] is one,
				#then we found a new tile location, so we later must update partial_solution accordingly
				#we do this by adding [x][y] to dirty			
				if len(updated) == 1 and len(partial_solution[neighbor[1]][neighbor[2]]) > 1:
					dirty.append((neighbor[1],neighbor[2]))				
				
				partial_solution[neighbor[1]][neighbor[2]] = updated
			
		return True

	def set_tile_coordinates(self, tile_coordinates):
		self.tile_coordinates = tile_coordinates
	
	def set_board_coordinates(self, board_coordinates):
		self.board_coordinates = board_coordinates
		
	def set_board_width(self, board_width):
		self.board_width = board_width

	