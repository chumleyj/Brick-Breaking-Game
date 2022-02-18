import arcade
from PIL import Image

"""This class holds the wall elements for a game - extension of SpriteList class"""
class Wall(arcade.SpriteList):
    """initializer"""
    def __init__(self, game_width, game_height, image_width, image_height, segment_image='images\wall.png', x_start=0, y_start=0):
        super().__init__()
        self.wall_list = None
        self.board_width = game_width
        self.board_height = game_height
        self.x_start = x_start
        self.y_start = y_start
        self.segment_image = segment_image
        self.wall_segment_width = image_width
        self.wall_segment_height = image_height        

    """setup the sprites for each segment of the wall"""
    def setup(self):
        
        # starting x,y coordinates for constructing the wall
        left_x = self.x_start + (self.wall_segment_width / 2)
        right_x = self.board_width - (self.wall_segment_width / 2)
        current_y = self.y_start + (self.wall_segment_height / 2)

        # create sprites along left and right edges of the game board
        while current_y < self.board_height:
            # left edge
            new_segment = arcade.Sprite(filename=self.segment_image,
                                        image_height=self.wall_segment_height,
                                        image_width=self.wall_segment_width,
                                        center_x=left_x,
                                        center_y=current_y
            )
            self.append(new_segment)
            
            # right edge
            new_segment = arcade.Sprite(filename=self.segment_image,
                                        image_height=self.wall_segment_height,
                                        image_width=self.wall_segment_width,
                                        center_x=right_x,
                                        center_y=current_y
            )
            self.append(new_segment)
            # update y coordinate
            current_y += self.wall_segment_height
        
        # reset x,y coordinates to top edge of game board
        left_x +=self.wall_segment_width
        current_y -= self.wall_segment_height

        # create sprites along top edge of the game board
        while left_x < (self.board_width - self.wall_segment_width):
            new_segment = arcade.Sprite(filename=self.segment_image,
                                        image_height=self.wall_segment_height,
                                        image_width=self.wall_segment_width,
                                        center_x=left_x,
                                        center_y=current_y
            )
            self.append(new_segment)
            left_x += self.wall_segment_width
