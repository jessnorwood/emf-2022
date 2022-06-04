from app import TextApp
from tidal import *
import accelerometer
import random
import time

COLOURS = [RED, GREEN, BLUE, YELLOW, MAGENTA, CYAN]
BACKGROUND_COLOUR = BLACK
CROSSHAIR_COLOUR = YELLOW
OBSTACLE_COLOUR = WHITE
SPEED = 20.0
BALL_COUNT = 10
BALL_RADIUS = 5
CROSSHAIR_LENGTH = 10
COLLISION_DISTANCE_SQUARED = (2*BALL_RADIUS)**2
REFRESH_INTERVAL = 10 # but actually refresh time increases with number of balls :/

class Jess(TextApp):
    TITLE = ""
    BG = BACKGROUND_COLOUR
    balls = []
    x_accel = 0.0
    y_accel = 0.0
    somewhere_low = {'x':0.0,'y':0.0}
    crosshair = {'x':0.0, 'y':0.0}
    last_run_time = 0
    redraw_static = False

    # I'm not using `periodic` because each refresh takes too long
    # and the async tasks end up backing up and the buttons stop working.
    # So only set a new timer when the last job ends.
    running = True

    def on_start(self):
        super().on_start()
        self.buttons.on_press(JOY_CENTRE, self.add_obstacle)
        self.buttons.on_press(BUTTON_A, self.delete_last_obstacle)
        self.buttons.on_press(JOY_UP, self.crosshair_up)
        self.buttons.on_press(JOY_DOWN, self.crosshair_down)
        self.buttons.on_press(JOY_LEFT, self.crosshair_left)
        self.buttons.on_press(JOY_RIGHT, self.crosshair_right)

        for idx in range(BALL_COUNT):
            x = random.uniform(0, display.width())
            y = random.uniform(0, display.height())
            self.balls.append({'id':idx,
                'x':x,
                'y':y,
                'has_collision':False,
                'colour':random.choice(COLOURS),
                'static':False,
            })

    def on_activate(self):
        super().on_activate()
        display.fill(BACKGROUND_COLOUR)
        self.crosshair = {'x':BALL_RADIUS, 'y':display.height()-BALL_RADIUS}
        self.running = True
        self.redraw_static = True
        self.refresh()

    def on_deactivate(self):
        self.running = False
        super().on_deactivate()

    def update_pos(self, ball):
        x_candidate = ball['x'] + (self.x_accel*SPEED)
        x_candidate = max(x_candidate, BALL_RADIUS)
        x_candidate = min(x_candidate, display.width() - BALL_RADIUS)
        x_candidate = float(x_candidate)

        y_candidate = ball['y'] - (self.y_accel*SPEED)
        y_candidate = max(y_candidate, BALL_RADIUS)
        y_candidate = min(y_candidate, display.height() - BALL_RADIUS)

        if self.has_collision(ball['id'], x_candidate, y_candidate):
            ball['has_collision'] = True
        else:
            ball['x'] = x_candidate
            ball['y'] = y_candidate
            ball['has_collision'] = False

    def has_collision(self, id, x, y):
        for other in self.lowest_first:
            if id == other['id']:
                return False # stop looking if there's nothing else lower than us
            if self.distance_squared(x, y, other['x'], other['y']) < COLLISION_DISTANCE_SQUARED:
                return True
        return False

    def distance_squared(self, x, y, other_x, other_y):
        return (x - other_x)**2 + (y - other_y)**2

    def height(self, ball):
        return self.distance_squared(ball['x'], ball['y'], self.somewhere_low['x'], self.somewhere_low['y'])

    def update_debug(self):
        win = self.window
        win.set_next_line(0)
        # win.println(f"accel X: {self.x_accel:0.3g}")
        # win.println(f"accel Y: {self.y_accel:0.3g}")
        # win.println(f"low X: {self.somewhere_low['x']:0.3g}")
        # win.println(f"low Y: {self.somewhere_low['y']:0.3g}")
        # win.println(f"height: {self.height(self.balls[0]):0.3g}")
        win.println(f"frame rate: {self.frame_rate:0.2g}")

    def crosshair_up(self):
        self.draw_crosshair(BACKGROUND_COLOUR)
        self.crosshair['y'] -= BALL_RADIUS*2
        self.draw_crosshair()
        self.redraw_static = True

    def crosshair_down(self):
        self.draw_crosshair(BACKGROUND_COLOUR)
        self.crosshair['y'] += BALL_RADIUS*2
        self.draw_crosshair()
        self.redraw_static = True

    def crosshair_left(self):
        self.draw_crosshair(BACKGROUND_COLOUR)
        self.crosshair['x'] -= BALL_RADIUS*2
        self.draw_crosshair()
        self.redraw_static = True

    def crosshair_right(self):
        self.draw_crosshair(BACKGROUND_COLOUR)
        self.crosshair['x'] += BALL_RADIUS*2
        self.draw_crosshair()
        self.redraw_static = True

    def draw_crosshair(self, colour=None):
        if colour is None:
            colour = CROSSHAIR_COLOUR
        x = int(self.crosshair['x'])
        y = int(self.crosshair['y'])
        display.line(x-CROSSHAIR_LENGTH, y, x+CROSSHAIR_LENGTH, y, colour)
        display.line(x, y-CROSSHAIR_LENGTH, x, y+CROSSHAIR_LENGTH, colour)
        display.circle(x, y, BALL_RADIUS, colour)

    def add_obstacle(self):
        self.balls.append({
            'id':len(self.balls),
            'x':self.crosshair['x'],
            'y':self.crosshair['y'],
            'has_collision':False,
            'colour': OBSTACLE_COLOUR,
            'static': True,
        })
        self.draw_ball(self.balls[-1])

    def delete_last_obstacle(self):
        """ or ball, if you delete enough """
        if len(self.balls):
            self.draw_ball(self.balls[-1], BACKGROUND_COLOUR)
            del self.balls[-1]

    def draw_ball(self, ball, colour=None):
        if colour is None:
            colour = ball['colour']
        display.fill_circle(int(ball['x']), int(ball['y']), BALL_RADIUS, colour)

    def refresh(self):
        if not self.running:
            return

        current = time.ticks_ms()
        self.frame_rate = 1000/float(current - self.last_run_time)
        self.last_run_time = time.ticks_ms()

        (x, y, z) = accelerometer.get_xyz()
        self.x_accel = x
        self.y_accel = y
        self.somewhere_low = {'x':10000.0*x,'y':-10000.0*y}

        self.lowest_first = sorted(self.balls, key=self.height, reverse=False)
        for ball in self.lowest_first:
            if not ball['static']:
                self.draw_ball(ball, BACKGROUND_COLOUR)
                self.update_pos(ball)
            if self.redraw_static or not ball['static']:
                self.draw_ball(ball)

        self.redraw_static = False
        self.draw_crosshair()
        #self.update_debug()
        self.after(REFRESH_INTERVAL, self.refresh)

main = Jess