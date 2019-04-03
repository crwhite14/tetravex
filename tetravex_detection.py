
import imutils
import cv2
import numpy as np
import pyautogui
from scipy.spatial import distance as dist


class TetravexDetection:

    def __init__(self, n):	
        self.n = n
        self.board_coordinates = None
        self.tiles_coordinates = None
        self.board_width = None

    def detect_puzzle_from_screen(self):

        #take a screenshot of the screen and convert it to the cv2 format
        screen = pyautogui.screenshot()
        screen_array = np.array(screen) 
        screen = screen_array[:, :, ::-1].copy()

        # pre-process the image by converting it to
        # graycale, blurring it, and computing an edge map
        gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 50, 200, 255)		

        #find all contours and sort them by area
        cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

        self.tiles = []
        tiles_dimensions = None
        w_tiles, h_tiles = 0,0

        #find the two largest squares in the screenshot
        for c in cnts:
            perimeter = cv2.arcLength(c, True)
            num_vertices = cv2.approxPolyDP(c, 0.02 * perimeter, True)
            x,y,w,h = cv2.boundingRect(c)

            #if the contour has four vertices, and length =~ width, then it is a square
            if len(num_vertices) == 4 and .9 * w < h < 1.1 * w:

                #the first square must be the set of tiles
                if len(self.tiles) == 0:
                    self.tiles = screen[y:y+h, x:x+w]
                    self.tiles_coordinates = (x, y)
                    tiles_dimensions = (w, h)

                #the second square must be the board
                else:
                    self.board_coordinates = (x, y)
                    self.board_width = w
                    break

        #determine the four colors on every tile
        return self.process_tiles(tiles_dimensions)

    def process_tiles(self, tiles_dimensions):

        #set the width of each tile, and the width of the border to remove
        w_tile = int(tiles_dimensions[0] / self.n)
        h_tile = int(tiles_dimensions[1] / self.n)
        count = 0
        colors = []
        tiles_array = np.zeros([self.n,self.n,4])

        #for every tile, compute its four colors
        for i in range(self.n):
            for j in range(self.n):

                #crop out an individual tile and scale it to 300 pixels				
                tile_original_size = self.tiles[h_tile*i:h_tile*(i+1), w_tile*j:w_tile*(j+1)]
                tile = imutils.resize(tile_original_size.copy(), width=300)		
                ratio = tile_original_size.shape[0] / float(tile.shape[0])

                h,w = tile.shape[:2]
                short_offset = int(.15*h)
                long_offset = int(.3*h)
                count = count + 1
                mean = None	

                #sample colors from each of the four sides of the tile
                #e.g., for each side of the tile (top, bottom, left, right), sample a 4x4 square of pixels
                for k in range(4):
                    if k == 0:
                        mean = cv2.mean(tile[short_offset-2:short_offset+2,w-long_offset-2:w-long_offset+2])[:3]
                    elif k == 1:
                        mean = cv2.mean(tile[h-long_offset-2:h-long_offset+2,short_offset-2:short_offset+2])[:3]					
                    elif k == 2:
                        mean = cv2.mean(tile[h-long_offset-2:h-long_offset+2,w-short_offset-2:w-short_offset+2])[:3]
                    else:
                        mean = cv2.mean(tile[h-short_offset-2:h-short_offset+2,w-long_offset-2:w-long_offset+2])[:3]				

                    #find the closest color among the colors we've seen so far
                    minDist = (np.inf, None) 
                    for (index, row) in enumerate(colors):
                        d = dist.euclidean(row[0], mean)
                        if d < minDist[0]:
                            minDist = (d, index)				

                    #if the RGB triplet is within 20 of an existing color, it must be a match
                    if minDist[0] < 20:
                        tiles_array[i][j][k] = minDist[1]
                    else:
                        colors.append([mean])
                        tiles_array[i][j][k] = len(colors) - 1

        return tiles_array

    def get_board_coordinates(self):
        return self.board_coordinates

    def get_tiles_coordinates(self):
        return self.tiles_coordinates

    def get_board_width(self):
        return self.board_width
