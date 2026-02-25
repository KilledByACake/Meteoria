import pgzrun # imports pygame zero module

#Constant Settings for size
WIDTH = 480
HEIGHT = 720

TITLE = "Endless Biker in Finland Tester"

# Rectangle = Rect((x, y), (width, heigth))
# rectangle = Rect ((0, 0), (10, 10))
# Creates a rectangle object whose topleft corner begins at (x, y) ad has the defined width and heighth.

# Background rectangles
sky = Rect (0,0 800, 400)
ground = Rect (0, 400, 800, 200)


# Draw a rectangle
def draw():
    screen.clear()
    screen.draw.filled_rect(sky, "skyblue")
    screen.draw.filled_rect(ground, "mediumspringgreen")
    runner.draw()

# Actor setup - Bicycler
runner = Actor ("cyclist")
runner.pos = (100, 400
)

#List of all frames 
runner_frames = ["cycler1", "cycler2", "cycler3"]
current_frame = 0
frame_counter = 0 # counts number of update-cycles which has passed


pgrung.go() # executes the game loop