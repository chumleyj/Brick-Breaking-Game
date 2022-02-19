import arcade
import layouts
import wall
import ball

# Constants
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 400
WALL_THICKNESS = 20
BALL_SPEED = 3
BALL_MAX_X = 6
BRICK_SCORE = 10
PADDLE_SCORE_PENALTY = 1
LIFE_SCORE_PENALTY = 10
MAX_LEVEL = 4
BRICK_IMAGES = ['images/brick.png', 'images/brick2.png', 'images/brick3.png', 'images/brick4.png']

class BrickBraker(arcade.Window):
    """
    This class holds all the sprite, game processing, and display information
    """
    def __init__(self):
        """
        Initialize the game window and game variables
        """
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Brick Breaker")

        # Sprite list variables
        self.paddle_list = None
        self.brick_list = None
        self.ball_list = None
        self.wall_list = None

        # paddle and ball sprites
        self.paddle_sprite = None
        self.ball_sprite = None
        
        # score, level, lives variables
        self.score = None
        self.level = None
        self.lives = None
        self.game_over = None
        
        # variable for background music
        self.init_sounds()

        # set the background color
        arcade.set_background_color(arcade.color.PALE_COPPER)
    
    def init_sounds(self):
        """
        This function sets up the background music for the game
        """
        self.bg_music = arcade.load_sound('music-short.wav')
        self.bg_music.play(loop=True)
    
    def populate_bricks(self, image='images/brick.png'):
        """
        This function sets up the bricks for the current level of the game
        """
        # create bricks at each coordinate from layout for current level and add to brick_list
        for loc in layouts.brick_layouts[self.level]:
            brick = arcade.Sprite(filename=image, 
                                  center_x=loc[0],
                                  center_y=loc[1],
                                  scale=1,
                                  hit_box_algorithm='Simple'
            )
            self.brick_list.append(brick)

    def setup(self):
        """
        Create all game sprites
        """
        # sprite lists
        self.paddle_list = arcade.SpriteList()
        self.brick_list = arcade.SpriteList()
        self.ball_list = arcade.SpriteList()
        self.wall_list = wall.Wall(game_width=SCREEN_WIDTH, 
                                   game_height=SCREEN_HEIGHT, 
                                   image_height=WALL_THICKNESS, 
                                   image_width=WALL_THICKNESS, 
                                   segment_image='images/wall.png')
        self.wall_list.setup()

        # score, level, lives
        self.score = 0
        self.level = 1
        self.lives = 3
        self.game_over = False

        # setup paddle
        self.paddle_sprite = arcade.Sprite(filename='images/paddle.png', 
                                           center_x=SCREEN_WIDTH/2, 
                                           center_y=100,
                                           scale=1,
                                           hit_box_algorithm='Simple'
        )
        self.paddle_list.append(self.paddle_sprite)

        # adds bricks to brick_list
        self.populate_bricks()

        # create ball sprite
        self.ball_sprite = ball.Ball(filename='images/ball.png', 
                             center_x=self.paddle_sprite.center_x, 
                             #center_y=self.paddle_sprite.top + 1,
                             scale=0.3,
                             hit_box_algorithm='Detailed'
        )
        self.ball_sprite.bottom = self.paddle_sprite.top + 1
        self.ball_sprite.change_x = 0
        self.ball_sprite.change_y = 0
        self.ball_list.append(self.ball_sprite)

    def reset_ball(self):
        """
        This function places the ball at rest on top of the paddle
        """
        # reposition the ball on the paddle and stop its movement
        self.ball_sprite.bottom = self.paddle_sprite.top + 1
        self.ball_sprite.center_x = self.paddle_sprite.center_x
        self.ball_sprite.change_x = 0
        self.ball_sprite.change_y = 0

    def advance_levels(self):
        """
        Advances the level, including setting up the next brick layout
        and setting the ball back on the paddle
        """
        self.level += 1
        # setup next level's brick layout
        self.populate_bricks(BRICK_IMAGES[self.level - 1])

        # reset ball's speed to 0 and place on paddle
        self.reset_ball()


    def wall_collisions(self):
        """
        This function updates the ball's speed in the x,y directions
        based on collisions with the wall
        """
        # update ball's speed in x,y directions based on contact with the walls or ceiling
        if self.ball_sprite.left < WALL_THICKNESS:
            self.ball_sprite.left = WALL_THICKNESS
            self.ball_sprite.change_x *= -1
        elif self.ball_sprite.right > SCREEN_WIDTH - WALL_THICKNESS:
            self.ball_sprite.right = SCREEN_WIDTH - WALL_THICKNESS
            self.ball_sprite.change_x *= -1
        if self.ball_sprite.top > SCREEN_HEIGHT - WALL_THICKNESS:
            self.ball_sprite.top = SCREEN_HEIGHT - WALL_THICKNESS
            self.ball_sprite.change_y *= -1

    def paddle_collisions(self):
        """
        This function updates the ball's speed in the x,y directions
        based on collisions with the paddle
        """
        # change the ball's y direction if it collides with the paddle
        if arcade.check_for_collision(self.ball_sprite, self.paddle_sprite) and self.ball_sprite.center_y > self.paddle_sprite.top:
            self.ball_sprite.change_y *= -1
            self.ball_sprite.bottom = self.paddle_sprite.top

            # update magnitude of ball's speed in x direction based on paddle's x speed at contact, capping at BALL_MAX_X
            # this allows the player to impact the ball's trajectory based on how they move the paddle.
            self.ball_sprite.change_x += self.paddle_sprite.change_x
            if self.ball_sprite.change_x > BALL_MAX_X:
                self.ball_sprite.change_x = BALL_MAX_X
            elif self.ball_sprite.change_x < -BALL_MAX_X:
                self.ball_sprite.change_x = -BALL_MAX_X
        
            # lose points for each paddle contact
            if not self.game_over:
                self.score -= PADDLE_SCORE_PENALTY
        
        # reset paddle x-speed to 0
        self.paddle_sprite.change_x = 0

    def brick_collisions(self):
        """
        This function identifies bricks that the ball has collided with and determines the
        side the ball impacted first. Based on the side first impacted, the ball's direction
        is updated.
        """
        # get list of collisions between ball and bricks
        brick_collisions = arcade.check_for_collision_with_list(self.ball_sprite, self.brick_list)
        
        # variables to track whether ball should change its x,y direction based on a collision
        change_y = False
        change_x = False

        # determine what direction ball should rebound from brick collisions.
        # there are 12 ways the ball could impact the brick, which are accounted for in this if statement
        for brick in brick_collisions:
            # if contacting the brick from top left
            if self.ball_sprite.center_y > brick.top and self.ball_sprite.center_x < brick.left:
                # if ball impacted top of brick before the left side (center of ball is further from top 
                # than the side), reverse y-speed
                if abs(self.ball_sprite.center_y - brick.top) >= abs(self.ball_sprite.center_x - brick.left):
                    change_y = True
                # if ball impacted the left side before the top, reverse x-speed
                else:
                    change_x = True
            # if colliding from top right side
            elif self.ball_sprite.center_y > brick.top and self.ball_sprite.center_x > brick.right:
                # if ball impacted top of brick before the right side, reverse y-speed
                if abs(self.ball_sprite.center_y - brick.top) >= abs(self.ball_sprite.center_x - brick.right):
                    change_y = True
                # if ball impacted the left side before the top, reverse x-speed
                else:
                    change_x = True
            # if contacting the brick from bottom left
            elif self.ball_sprite.center_y < brick.bottom and self.ball_sprite.center_x < brick.left:
                # if ball impacted bottom of brick before the left side (center of ball is further from bottom 
                # than the side), reverse y-speed
                if abs(self.ball_sprite.center_y - brick.bottom) >= abs(self.ball_sprite.center_x - brick.left):
                    change_y = True
                # if ball impacted the left side before the bottom, reverse x-speed
                else:
                    change_x = True
            # if colliding from bottom right side
            elif self.ball_sprite.center_y < brick.bottom and self.ball_sprite.center_x > brick.right:
                # if ball impacted bottom of brick before the right side, reverse y-speed
                if abs(self.ball_sprite.center_y - brick.bottom) >= abs(self.ball_sprite.center_x - brick.right):
                    change_y = True
                # if ball impacted the right side before the bottom, reverse x-speed
                else:
                    change_x = True
            # if colliding with top or bottom in-between the sides, reverse y-speed
            elif self.ball_sprite.center_y > brick.top or self.ball_sprite.center_y < brick.bottom:
                change_y = True
            # if contacting the brick from the left or right, reverse x-speed
            else:
                change_x = True

            # remove all bricks the ball collided with
            brick.remove_from_sprite_lists()

            # gain points for each brick removed
            self.score += BRICK_SCORE

        # change the ball's direction based on the collisions
        if change_y:
            self.ball_sprite.change_y *= -1
        if change_x:
            self.ball_sprite.change_x *= -1

    def on_update(self, delta_time):
        """
        Update sprites movement and collisions if the game has started
        """
        # if ball has started movement
        if self.ball_sprite.change_y != 0:
            # update the ball's position
            self.ball_list.update()

            # update ball's speed in x,y directions based on collision with the walls or ceiling
            self.wall_collisions()

            # update the ball's speed in the x,y directions based on collision with the paddle
            self.paddle_collisions()

            # handle collisions between the ball and bricks
            self.brick_collisions()

            # if all bricks have been cleared, then advance levels
            if len(self.brick_list) == 0 and self.level < MAX_LEVEL:
                self.advance_levels()
            elif (len(self.brick_list) == 0):
                self.game_over = True
            
            # if ball has gone off the bottom of the screen
            if self.ball_sprite.top < 0:

                # lose points if ball goes off screen
                if not self.game_over:
                    self.score -= 10

                # decrement lives and reset ball if there are still lives remaining
                if self.lives > 1:
                    self.lives -= 1
                    self.reset_ball()
                # update game_over variable if no lives remaining
                elif self.lives == 1:
                    self.lives -= 1
                    self.game_over = True

    def on_draw(self):
        """
        Clears the screen and draws sprites
        """
        # clear the window
        arcade.start_render()
        
        # draw all sprites
        self.paddle_list.draw()
        self.brick_list.draw()
        self.ball_list.draw()
        self.wall_list.draw()

        arcade.draw_text(f'Score: {self.score}', 30, 15, arcade.color.BLACK, 12, font_name='arial')
        arcade.draw_text(f'Lives: {self.lives}', SCREEN_WIDTH-90, 15, arcade.color.BLACK, 12, font_name='arial')

        if self.game_over:
            arcade.draw_text('Game Over', SCREEN_WIDTH/2 - 115, 150, arcade.color.BLANCHED_ALMOND, 30, font_name='arial', bold=True)

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Click left mouse button to start the ball moving if it is at rest
        """
        if (button == arcade.MOUSE_BUTTON_LEFT and self.ball_sprite.change_y == 0):
            self.ball_sprite.change_y = BALL_SPEED
            self.ball_sprite.change_x = 0

    def on_mouse_motion(self, x, y, dx, dy):
        """
        Move the paddle based on the position of the mouse
        """
        # align paddle with the mouse and get x-axis rate of change
        self.paddle_sprite.center_x = x
        self.paddle_sprite.change_x = dx
        
        # prevent paddle from overlapping left or right wall
        if self.paddle_sprite.left < WALL_THICKNESS:
            self.paddle_sprite.left = WALL_THICKNESS
        elif self.paddle_sprite.right > SCREEN_WIDTH - WALL_THICKNESS:
            self.paddle_sprite.right = SCREEN_WIDTH - WALL_THICKNESS
        
        # if the ball hasn't started moving yet, match it's position to just above the center of the paddle
        if self.ball_sprite.change_y == 0:
            self.ball_sprite.bottom = self.paddle_sprite.top + 1
            self.ball_sprite.center_x = self.paddle_sprite.center_x

def main():
    """
    Create the game window and run the game
    """
    window = BrickBraker()
    window.setup()
    arcade.run()

if __name__ == '__main__':
    main()