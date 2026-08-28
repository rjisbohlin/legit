import tkinter as tk
import pygame
import time
import os


# ================= AUDIO =================

AUDIO_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "earrings.mp3"
)

pygame.mixer.init()
pygame.mixer.music.load(AUDIO_FILE)


# ================= LYRICS =================

LYRICS = [
    (1.03, "Her love is in your head"),
    (2.96, "You lost your earrings in her bed"),
    (6.36, "You couldn't tell her that you lost 'em"),
    (9.41, "'Cause you're scared and you're not talking"),
    (12.49, "So you think of what to say"),
    (15.33, "Then save it for another day"),
    (18.52, "'Cause you just never had the heart"),
    (21.57, "Now they just drift further apart"),
    (24.12, "From you, oh.........."),
]


# ================= DESIGN =================

BOX_W, BOX_H = 300, 250

FONT = ("Helvetica", 22, "bold")

BG_COLOR = "#fdfdf5"
FG_COLOR = "#111111"

RISE_SPEED = 67

BOTTOM_SPAWN_OFFSET = 150

# Typewriter speed
# Smaller number = faster typing
TYPE_SPEED = 50


# ================= LYRIC CARD =================

class LyricCard:

    def __init__(self, parent, text, x, y):

        self.win = tk.Toplevel(parent)

        self.win.overrideredirect(True)

        self.win.attributes("-topmost", True)

        self.win.configure(bg=BG_COLOR)

        self.win.geometry(
            f"{BOX_W}x{BOX_H}+{int(x)}+{int(y)}"
        )

        self.win.resizable(False, False)

        # Save the complete lyric
        self.full_text = text

        # Start with empty text
        self.label = tk.Label(
            self.win,
            text="",
            font=FONT,
            bg=BG_COLOR,
            fg=FG_COLOR,
            wraplength=BOX_W - 25,
            justify="center"
        )

        self.label.pack(
            expand=True,
            fill="both",
            padx=15,
            pady=15
        )

        # Typewriter starts immediately
        self.typewriter_index = 0

        self.typewriter()

        # Position
        self.x = x
        self.y = float(y)


    # ================= TYPEWRITER =================

    def typewriter(self):

        if self.typewriter_index <= len(self.full_text):

            # Write the lyric little by little
            self.label.config(
                text=self.full_text[
                    :self.typewriter_index
                ]
            )

            self.typewriter_index += 1

            # 20 milliseconds per character
            self.win.after(
                TYPE_SPEED,
                self.typewriter
            )


    # ================= RISING =================

    def rise(self, dy):

        self.y -= dy

        self.win.geometry(
            f"{BOX_W}x{BOX_H}+"
            f"{int(self.x)}+{int(self.y)}"
        )


    # ================= OFFSCREEN =================

    def is_offscreen(self):

        return self.y + BOX_H < -50


# ================= MAIN APP =================

class LyricFloatApp:

    def __init__(self, root):

        self.root = root

        self.screen_w = (
            root.winfo_screenwidth()
        )

        self.screen_h = (
            root.winfo_screenheight()
        )

        self.next_lyric_idx = 0

        self.boxes = []

        self.last_frame_time = None

        self.current_side = "left"

        # Start automatically
        self.start()


    # ================= CARD POSITION =================

    def random_safe_x(self):

        center_x = self.screen_w // 2

        spacing = BOX_W + 60

        left_x = center_x - spacing

        right_x = center_x + 60

        if self.current_side == "left":

            self.current_side = "right"

            return left_x

        else:

            self.current_side = "left"

            return right_x


    # ================= START =================

    def start(self):

        # Start the music
        pygame.mixer.music.play()

        # Start timer at the same time
        self.start_time = time.perf_counter()

        self.last_frame_time = (
            self.start_time
        )

        # Start animation immediately
        self.tick()


    # ================= MAIN LOOP =================

    def tick(self):

        now = time.perf_counter()

        elapsed = (
            now - self.start_time
        )

        dt = (
            now - self.last_frame_time
        )

        self.last_frame_time = now


        # Prevent huge movement if the program pauses
        if dt > 0.1:

            dt = 0.1


        # ================= SPAWN LYRICS =================

        while (
            self.next_lyric_idx
            < len(LYRICS)

            and
            LYRICS[
                self.next_lyric_idx
            ][0] <= elapsed
        ):

            _, text = LYRICS[
                self.next_lyric_idx
            ]


            # Alternate left/right
            x = self.random_safe_x()


            # Start near bottom
            y = (
                self.screen_h
                - BOX_H
                - BOTTOM_SPAWN_OFFSET
            )


            # Create floating card
            box = LyricCard(
                self.root,
                text,
                x,
                y
            )


            self.boxes.append(box)

            self.next_lyric_idx += 1


        # ================= MOVE CARDS =================

        dy = RISE_SPEED * dt


        for box in self.boxes:

            box.rise(dy)


        # ================= REMOVE OFFSCREEN =================

        still_visible = []


        for box in self.boxes:

            if box.is_offscreen():

                try:

                    box.win.destroy()

                except tk.TclError:

                    pass

            else:

                still_visible.append(box)


        self.boxes = still_visible


        # ================= CONTINUE =================

        if (
            self.next_lyric_idx
            < len(LYRICS)

            or self.boxes
        ):

            self.root.after(
                8,
                self.tick
            )

        else:

            # Close after all cards disappear
            self.root.after(
                100,
                self.root.destroy
            )


# ================= RUN =================

if __name__ == "__main__":

    root = tk.Tk()

    # No Start window
    root.withdraw()

    # Launch automatically
    app = LyricFloatApp(root)

    root.mainloop()