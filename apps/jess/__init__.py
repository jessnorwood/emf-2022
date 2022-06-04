from app import TextApp
from tidal import *
import accelerometer
import random

COLOURS = [RED, GREEN, BLUE, YELLOW, MAGENTA, CYAN]
BACKGROUND_COLOUR = BLACK
SPEED = 20.0
BALL_COUNT = 10
STATIC_COUNT = 5
BALL_RADIUS = 5

class Jess(TextApp):
    TITLE = ""
    BG = BLACK
    timer = None
    balls = []
    x_accel = 0.0
    y_accel = 0.0
    somewhere_low = {'x':0.0,'y':0.0}

    def on_start(self):
        super().on_start()

    def on_activate(self):
        super().on_activate()
        self.balls = []
        for idx in range(BALL_COUNT + STATIC_COUNT):
            x = random.uniform(0, display.width())
            y = random.uniform(0, display.height())
            self.balls.append({'id':idx,
                'x':x,
                'y':y,
                'has_collision':False,
                'colour':idx < BALL_COUNT and random.choice(COLOURS) or WHITE,
                'static':idx >= BALL_COUNT,
            })
        self.update_screen()
        self.timer = self.periodic(100, self.update_screen)

    def on_deactivate(self):
        self.timer.cancel()
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
                continue
                #return False # stop looking if there's nothing else lower than us
            if self.distance_squared(x, y, other['x'], other['y']) <= (2*BALL_RADIUS)**2:
                return True
        return False

    def distance_squared(self, x, y, other_x, other_y):
        return (x - other_x)**2 + (y - other_y)**2

    def height(self, ball):
        return self.distance_squared(ball['x'], ball['y'], self.somewhere_low['x'], self.somewhere_low['y'])

    def update_debug(self):
        win = self.window
        win.set_next_line(0)
        win.println()
        win.println(f"accel X: {self.x_accel:0.3g}")
        win.println(f"accel Y: {self.y_accel:0.3g}")
        win.println(f"low X: {self.somewhere_low['x']:0.3g}")
        win.println(f"low Y: {self.somewhere_low['y']:0.3g}")
        win.println(f"height: {self.height(self.balls[0]):0.3g}")

    def update_screen(self):
        (x, y, z) = accelerometer.get_xyz()
        self.x_accel = x
        self.y_accel = y
        self.somewhere_low = {'x':10000.0*x,'y':-10000.0*y}

        self.lowest_first = sorted(self.balls, key=self.height, reverse=False)
        for ball in self.lowest_first:
            if not ball['static']:
                display.fill_circle(int(ball['x']), int(ball['y']), BALL_RADIUS, BACKGROUND_COLOUR)
                self.update_pos(ball)
            display.fill_circle(int(ball['x']), int(ball['y']), BALL_RADIUS, ball['colour'])

        # self.lowest_first = sorted(self.balls, key=self.height, reverse=False)
        # for (pos, ball) in enumerate(self.lowest_first):
        #     brightness = int(220/BALL_COUNT*(BALL_COUNT-pos))
        #     if ball['has_collision']:
        #         colour = color565(brightness, 0, 0)
        #     else:
        #         colour = color565(brightness, brightness, brightness)
        #     display.fill_circle(int(ball['x']), int(ball['y']), BALL_RADIUS, ball['colour'])

        #self.update_debug()

main = Jess