from tidal import *
from app import MenuApp
from buttons import Buttons
from textwindow import TextWindow
import accelerometer
import random

import vga2_bold_16x32

class EightBall(MenuApp):
    TITLE = "Get Me Answers"
    timer = None
    last_y = 0

    def on_start(self):
        super().on_start()
        choices = (
            ("Magic 8 Ball", self.do_8_ball),
            ("Roll dice", self.do_dice),
            ("Toss a coin", self.do_coin),
            ("Meaning of life", self.do_life),
        )
        self.window.set_choices(choices)

        self.new_buttons = Buttons()
        self.new_buttons.on_press(BUTTON_FRONT, self.pop_window)

    def on_activate(self):
        super().on_activate()
        self.timer = self.periodic(500, self.check_for_shake)

    def on_deactivate(self):
        if self.timer:
            self.timer.cancel()
        super().on_deactivate()

    def do_8_ball(self):
        window = EightBallWindow(buttons=self.new_buttons)
        self.push_window(window, activate=True)

    def do_dice(self):
        window = DiceWindow(buttons=self.new_buttons)
        self.push_window(window, activate=True)

    def do_coin(self):
        window = CoinWindow(buttons=self.new_buttons)
        self.push_window(window, activate=True)

    def do_life(self):
        window = LifeWindow(buttons=self.new_buttons)
        self.push_window(window, activate=True)


    def check_for_shake(self):
        if len(self.windows) < 2:
            return
        (x, y, z) = accelerometer.get_xyz()
        if self.last_y < 0.0 and y > 0.0:
            self.windows[-1].on_shake()
        self.last_y = y


class ShakeyWindow(TextWindow):

    ANSWER_FONT = vga2_bold_16x32
    COLOURS = ((RED,WHITE),
                (MAGENTA,BLACK),
                (BLUE,WHITE),
                (CYAN,BLACK),
                (GREEN,BLACK),
                (YELLOW,BLACK),
            )

    def __init__(self, bg=None, fg=None, title=None, font=None, buttons=None):
        super().__init__(bg, fg, title, font, buttons)

        if title is None:
            self.set_title(self.default_title, redraw=False)

        self.bg = self.COLOURS[self.colour_index][0]
        self.fg = self.COLOURS[self.colour_index][1]

    def redraw(self):
        self.cls()
        self.println("")
        for line in self.flow_lines(self.intro_text):
            self.println(line)

    def on_shake(self):
        self.bg = self.COLOURS[self.colour_index][0]
        self.fg = self.COLOURS[self.colour_index][1]
        self.cls()
        self.colour_index = (self.colour_index +1)%len(self.COLOURS)
        self.println("")
        for line in self.flow_lines(self.answer_intro_text):
            self.println(line)

        lines = self.flow_lines(self.get_answer(), self.ANSWER_FONT)
        texty = 50
        for (i, line) in enumerate(lines):
            textw = len(line) * self.ANSWER_FONT.WIDTH
            linex = (self.width() - textw) // 2
            liney = texty + (i * self.ANSWER_FONT.HEIGHT)
            self.draw_text(line, linex, liney, self.bg, self.fg, self.ANSWER_FONT)

    def get_answer(self):
        return random.choice(self.choices)


class EightBallWindow(ShakeyWindow):
    default_title = "Magic 8 Ball"
    intro_text = "Ask me a\nquestion\nthen shake me!"
    answer_intro_text = "The 8 ball\nanswers:"
    # Source: https://en.wikipedia.org/wiki/Magic_8_Ball
    choices = ['It is\ncertain',
        'It is\ndecided-\nly so',
        'Without\na doubt',
        'Yes\ndefin-\nitely',
        'You may\nrely\non it',
        'As I see\nit,\nyes',
        'Most\nlikely',
        'Outlook\ngood',
        'Yes',
        'Signs\npoint to\nyes',
        'Reply\nhazy,\ntry\nagain',
        'Ask\nagain\nlater',
        'Better\nnot tell\nyou now',
        'Cannot\npredict\nnow',
        'Concen-\ntrate\nand ask\nagain',
        'Don\'t\ncount\non it',
        'My reply\nis no',
        'My\nsources\nsay no',
        'Outlook\nnot so\ngood',
        'Very\ndoubtful'
    ]
    colour_index = 2


class DiceWindow(ShakeyWindow):
    default_title = "Roll 1D6"
    intro_text = "Up/Down\nto change number;\nLeft/Right to\nchange\Shake me!"
    answer_intro_text = "You rolled"
    colour_index = 0
    num = 1
    faces = 6

    def __init__(self, bg=None, fg=None, title=None, font=None, buttons=None):
        super().__init__(bg, fg, title, font, buttons)

        self.buttons.on_press(JOY_UP, lambda:self.update_numbers(1,0))
        self.buttons.on_press(JOY_DOWN, lambda:self.update_numbers(-1,0))
        self.buttons.on_press(JOY_LEFT, lambda:self.update_numbers(0,-1))
        self.buttons.on_press(JOY_RIGHT, lambda:self.update_numbers(0,1))

    def update_numbers(self, num_delta, faces_delta):
        self.num += num_delta
        self.num = max(self.num, 1)
        self.num = min(self.num, 5)

        self.faces += faces_delta
        self.faces = max(self.faces, 1)

        self.set_title(f"Roll {self.num:d}D{self.faces:d}", redraw=False)
        self.redraw()

    @property
    def intro_text(self):
        return f"""Up/Down to
change number
of dice.

Left/Right to
change faces.

Shake me to
roll {self.num:d}D{self.faces:d}!"""

    def get_answer(self):
        answers = []
        for _ in range(0, self.num):
            answers.append(str(random.randint(1, self.faces)))
        return "\n".join(answers)

class CoinWindow(ShakeyWindow):
    default_title = "Toss a Coin"
    intro_text = "Shake me!"
    answer_intro_text = "You got:"
    choices = ['HEADS','TAILS']
    colour_index = 4

class LifeWindow(ShakeyWindow):
    default_title = "Meaning of life"
    intro_text = "Shake me to\nfind out the\nAnswer to the\nUltimate\nQuestion\nof Life,\nthe Universe,\nand Everything."
    answer_intro_text = "The answer is:"
    choices = ['42',]
    colour_index = 4

main = EightBall