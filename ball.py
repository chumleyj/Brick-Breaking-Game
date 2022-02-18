from arcade import Sprite

class Ball(Sprite):
    """
    This class is an extension of the sprite class for a ball
    """
    def update(self):
        """
        Updates the position of the sprite
        """
        self.center_x += self.change_x
        self.center_y += self.change_y