# -*- coding: utf-8 -*-
"""
Created on Sat May 30 22:36:43 2026

@author: sunil
"""
import os
import random
import tkinter as tk


CANVAS_WIDTH = 1000
CANVAS_HEIGHT = 650

TILE_SIZE = 48
ROWS = 8
COLS = 11

WORLD_LEFT = 55
WORLD_TOP = 120

UP_BUTTON = [760, 500, 820, 560]
LEFT_BUTTON = [695, 565, 755, 625]
DOWN_BUTTON = [760, 565, 820, 625]
RIGHT_BUTTON = [825, 565, 885, 625]
RESET_BUTTON = [55, 565, 190, 615]

START_ROW = 6
START_COL = 1

KAREL_IMAGE = "karel_sprite_white_body_44.png"

BATTERY_BOOST = 8
TRAP_PENALTY = 6
NUM_PORTALS = 2


class KarelQuestGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Karel Beeper Quest")

        self.canvas = tk.Canvas(
            self.root,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            bg="lightblue"
        )
        self.canvas.pack()

        self.font_title = ("Arial", 13, "bold")
        self.font_header = ("Arial", 11, "bold")
        self.font_normal = ("Arial", 10)
        self.font_small = ("Arial", 9)
        self.font_button = ("Arial", 11, "bold")

        self.karel_image = self.load_karel_image()

        self.level_number = 1
        self.start_level()

        self.canvas.bind("<Button-1>", self.handle_click)

    def load_karel_image(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            base_dir = os.getcwd()

        image_path = os.path.join(base_dir, KAREL_IMAGE)

        try:
            return tk.PhotoImage(file=image_path)
        except Exception:
            return None

    def run(self):
        self.root.mainloop()

    def start_level(self):
        self.level = self.create_random_level(self.level_number)

        self.karel_row = START_ROW
        self.karel_col = START_COL

        self.beepers_collected = 0
        self.total_beepers = self.count_total_beepers()

        self.energy = self.get_start_energy(self.level_number)
        self.moves = 0

        self.game_won = False
        self.game_over = False

        self.draw_game()

    def handle_click(self, event):
        action = self.get_clicked_action(event.x, event.y)

        if action is None:
            return

        if action == "reset":
            if self.game_won:
                self.level_number += 1

            self.start_level()
            return

        if self.game_won or self.game_over:
            return

        if action == "up":
            self.move_karel(-1, 0)

        elif action == "down":
            self.move_karel(1, 0)

        elif action == "left":
            self.move_karel(0, -1)

        elif action == "right":
            self.move_karel(0, 1)

        if self.energy <= 0:
            self.energy = 0
            self.game_over = True

        if self.reached_goal():
            if self.beepers_collected == self.total_beepers:
                self.game_won = True

        self.draw_game()

    def get_clicked_action(self, x, y):
        if self.point_in_button(x, y, UP_BUTTON):
            return "up"

        if self.point_in_button(x, y, LEFT_BUTTON):
            return "left"

        if self.point_in_button(x, y, DOWN_BUTTON):
            return "down"

        if self.point_in_button(x, y, RIGHT_BUTTON):
            return "right"

        if self.point_in_button(x, y, RESET_BUTTON):
            return "reset"

        return None

    def point_in_button(self, x, y, button):
        return (
            x >= button[0]
            and x <= button[2]
            and y >= button[1]
            and y <= button[3]
        )

    def create_random_level(self, level_number):
        num_beepers = self.get_num_beepers(level_number)
        num_traps = self.get_num_traps(level_number)
        num_batteries = self.get_num_batteries(level_number)
        wall_chance = self.get_wall_chance(level_number)

        while True:
            level = self.create_empty_level(wall_chance)
            reachable = self.get_reachable_cells(level)

            needed_cells = num_beepers + num_traps + num_batteries + NUM_PORTALS + 4

            if len(reachable) >= needed_cells:
                goal_cell = self.choose_far_cell(level, reachable)

                if goal_cell is not None:
                    level[goal_cell[0]][goal_cell[1]] = "G"

                    self.place_random_items(level, reachable, "B", num_beepers)
                    self.place_random_items(level, reachable, "E", num_batteries)
                    self.place_random_items(level, reachable, "T", num_traps)
                    self.place_random_items(level, reachable, "P", NUM_PORTALS)

                    return level

    def create_empty_level(self, wall_chance):
        level = []

        for row in range(ROWS):
            current_row = []

            for col in range(COLS):
                if row == 0 or row == ROWS - 1 or col == 0 or col == COLS - 1:
                    current_row.append("#")
                elif row == START_ROW and col == START_COL:
                    current_row.append(".")
                elif random.randint(1, 100) <= wall_chance:
                    current_row.append("#")
                else:
                    current_row.append(".")

            level.append(current_row)

        return level

    def get_num_beepers(self, level_number):
        if level_number == 1:
            return 3
        elif level_number == 2:
            return 4
        elif level_number == 3:
            return 5
        else:
            return 6

    def get_num_traps(self, level_number):
        if level_number == 1:
            return 1
        elif level_number == 2:
            return 2
        elif level_number == 3:
            return 3
        else:
            return 4

    def get_num_batteries(self, level_number):
        if level_number <= 2:
            return 1
        else:
            return 2

    def get_wall_chance(self, level_number):
        if level_number == 1:
            return 12
        elif level_number == 2:
            return 17
        elif level_number == 3:
            return 21
        else:
            return 24

    def get_start_energy(self, level_number):
        if level_number == 1:
            return 36
        elif level_number == 2:
            return 34
        elif level_number == 3:
            return 32
        else:
            return 30

    def get_reachable_cells(self, level):
        reachable = []
        queue = [[START_ROW, START_COL]]

        while len(queue) > 0:
            current = queue.pop(0)
            row = current[0]
            col = current[1]

            if not self.cell_in_list(reachable, row, col):
                reachable.append([row, col])

                self.add_open_neighbor(level, queue, reachable, row - 1, col)
                self.add_open_neighbor(level, queue, reachable, row + 1, col)
                self.add_open_neighbor(level, queue, reachable, row, col - 1)
                self.add_open_neighbor(level, queue, reachable, row, col + 1)

        return reachable

    def add_open_neighbor(self, level, queue, reachable, row, col):
        if self.can_move_to(level, row, col):
            if not self.cell_in_list(reachable, row, col):
                if not self.cell_in_list(queue, row, col):
                    queue.append([row, col])

    def cell_in_list(self, cells, row, col):
        for cell in cells:
            if cell[0] == row and cell[1] == col:
                return True

        return False

    def choose_far_cell(self, level, reachable):
        possible_cells = []

        for cell in reachable:
            row = cell[0]
            col = cell[1]
            distance = abs(row - START_ROW) + abs(col - START_COL)

            if level[row][col] == ".":
                if distance >= 7:
                    possible_cells.append(cell)

        if len(possible_cells) == 0:
            return None

        return random.choice(possible_cells)

    def place_random_items(self, level, reachable, symbol, count):
        possible_cells = []

        for cell in reachable:
            row = cell[0]
            col = cell[1]

            if level[row][col] == ".":
                if not (row == START_ROW and col == START_COL):
                    possible_cells.append(cell)

        for i in range(count):
            if len(possible_cells) > 0:
                chosen = random.choice(possible_cells)
                row = chosen[0]
                col = chosen[1]

                level[row][col] = symbol
                possible_cells.remove(chosen)

    def count_total_beepers(self):
        count = 0

        for row in range(ROWS):
            for col in range(COLS):
                if self.level[row][col] == "B":
                    count += 1

        return count

    def move_karel(self, row_change, col_change):
        next_row = self.karel_row + row_change
        next_col = self.karel_col + col_change

        if self.can_move_to(self.level, next_row, next_col):
            self.karel_row = next_row
            self.karel_col = next_col
            self.moves += 1
            self.energy -= 1

            current_tile = self.level[self.karel_row][self.karel_col]

            if current_tile == "B":
                self.level[self.karel_row][self.karel_col] = "."
                self.beepers_collected += 1

            elif current_tile == "E":
                self.level[self.karel_row][self.karel_col] = "."
                self.energy += BATTERY_BOOST

            elif current_tile == "T":
                self.level[self.karel_row][self.karel_col] = "."
                self.energy -= TRAP_PENALTY

            elif current_tile == "P":
                self.teleport_karel()

    def teleport_karel(self):
        for row in range(ROWS):
            for col in range(COLS):
                if self.level[row][col] == "P":
                    if row != self.karel_row or col != self.karel_col:
                        self.karel_row = row
                        self.karel_col = col
                        return

    def can_move_to(self, level, row, col):
        if row < 0:
            return False

        if row >= ROWS:
            return False

        if col < 0:
            return False

        if col >= COLS:
            return False

        return level[row][col] != "#"

    def reached_goal(self):
        return self.level[self.karel_row][self.karel_col] == "G"

    def draw_game(self):
        self.canvas.delete("all")

        goal_open = self.beepers_collected == self.total_beepers

        self.draw_background()
        self.draw_level(goal_open)
        self.draw_karel()
        self.draw_score_panel()
        self.draw_mission_panel()
        self.draw_controls()

        if self.game_won:
            self.draw_win_message()

        if self.game_over:
            self.draw_game_over_message()

    def draw_background(self):
        self.canvas.create_rectangle(
            0,
            0,
            CANVAS_WIDTH,
            CANVAS_HEIGHT,
            fill="lightblue",
            outline=""
        )

        self.canvas.create_rectangle(
            0,
            515,
            CANVAS_WIDTH,
            CANVAS_HEIGHT,
            fill="darkseagreen",
            outline=""
        )

        self.draw_cloud(100, 45)
        self.draw_cloud(390, 55)

        self.canvas.create_rectangle(
            WORLD_LEFT - 8,
            WORLD_TOP - 8,
            WORLD_LEFT + COLS * TILE_SIZE + 8,
            WORLD_TOP + ROWS * TILE_SIZE + 8,
            fill="darkolivegreen",
            outline="black"
        )

    def draw_level(self, goal_open):
        for row in range(ROWS):
            for col in range(COLS):
                x = self.get_x(col)
                y = self.get_y(row)
                tile = self.level[row][col]

                if tile == "#":
                    self.draw_wall_tile(x, y)
                elif tile == ".":
                    self.draw_floor_tile(x, y)
                elif tile == "B":
                    self.draw_floor_tile(x, y)
                    self.draw_beeper(x, y)
                elif tile == "E":
                    self.draw_floor_tile(x, y)
                    self.draw_battery(x, y)
                elif tile == "T":
                    self.draw_floor_tile(x, y)
                    self.draw_trap(x, y)
                elif tile == "P":
                    self.draw_floor_tile(x, y)
                    self.draw_portal(x, y)
                elif tile == "G":
                    self.draw_goal_tile(x, y, goal_open)

    def draw_floor_tile(self, x, y):
        self.canvas.create_rectangle(
            x,
            y,
            x + TILE_SIZE,
            y + TILE_SIZE,
            fill="palegreen",
            outline="white"
        )

    def draw_wall_tile(self, x, y):
        self.canvas.create_rectangle(
            x,
            y,
            x + TILE_SIZE,
            y + TILE_SIZE,
            fill="sienna",
            outline="black"
        )

        self.canvas.create_rectangle(
            x,
            y,
            x + TILE_SIZE,
            y + 9,
            fill="forestgreen",
            outline=""
        )

    def draw_goal_tile(self, x, y, goal_open):
        if goal_open:
            tile_color = "honeydew"
            flag_color = "green"
        else:
            tile_color = "lightgray"
            flag_color = "gray"

        self.canvas.create_rectangle(
            x,
            y,
            x + TILE_SIZE,
            y + TILE_SIZE,
            fill=tile_color,
            outline="black"
        )

        self.canvas.create_rectangle(
            x + 20,
            y + 8,
            x + 24,
            y + 38,
            fill="black",
            outline=""
        )

        self.canvas.create_rectangle(
            x + 24,
            y + 8,
            x + 42,
            y + 23,
            fill=flag_color,
            outline="black"
        )

    def draw_beeper(self, x, y):
        self.canvas.create_oval(
            x + 14,
            y + 11,
            x + 34,
            y + 32,
            fill="gold",
            outline="black"
        )

        self.canvas.create_rectangle(
            x + 22,
            y + 15,
            x + 26,
            y + 28,
            fill="orange",
            outline=""
        )

    def draw_battery(self, x, y):
        self.canvas.create_rectangle(
            x + 10,
            y + 15,
            x + 34,
            y + 31,
            fill="dodgerblue",
            outline="black"
        )

        self.canvas.create_rectangle(
            x + 34,
            y + 20,
            x + 39,
            y + 26,
            fill="dodgerblue",
            outline="black"
        )

        self.canvas.create_rectangle(
            x + 16,
            y + 20,
            x + 29,
            y + 26,
            fill="white",
            outline=""
        )

    def draw_trap(self, x, y):
        self.canvas.create_rectangle(
            x + 8,
            y + 8,
            x + 40,
            y + 40,
            fill="firebrick",
            outline="black"
        )

        self.canvas.create_rectangle(
            x + 14,
            y + 14,
            x + 34,
            y + 34,
            fill="black",
            outline=""
        )

        self.canvas.create_oval(
            x + 19,
            y + 19,
            x + 29,
            y + 29,
            fill="orange",
            outline="black"
        )

        self.canvas.create_rectangle(x + 10, y + 8, x + 14, y + 17, fill="black", outline="")
        self.canvas.create_rectangle(x + 34, y + 8, x + 38, y + 17, fill="black", outline="")
        self.canvas.create_rectangle(x + 10, y + 31, x + 14, y + 40, fill="black", outline="")
        self.canvas.create_rectangle(x + 34, y + 31, x + 38, y + 40, fill="black", outline="")

    def draw_portal(self, x, y):
        self.canvas.create_oval(
            x + 7,
            y + 7,
            x + 41,
            y + 41,
            fill="purple",
            outline="black"
        )

        self.canvas.create_oval(
            x + 14,
            y + 14,
            x + 34,
            y + 34,
            fill="violet",
            outline="black"
        )

        self.canvas.create_oval(
            x + 21,
            y + 21,
            x + 27,
            y + 27,
            fill="white",
            outline="black"
        )

    def draw_karel(self):
        x = self.get_x(self.karel_col)
        y = self.get_y(self.karel_row)

        if self.karel_image is not None:
            self.canvas.create_image(
                x + TILE_SIZE // 2,
                y + TILE_SIZE // 2,
                image=self.karel_image
            )
        else:
            self.draw_karel_fallback(x, y)

    def draw_karel_fallback(self, x, y):
        self.canvas.create_rectangle(x + 9, y + 5, x + 32, y + 36, fill="white", outline="black")
        self.canvas.create_rectangle(x + 15, y + 11, x + 26, y + 27, fill="lightskyblue", outline="black")
        self.canvas.create_rectangle(x + 3, y + 22, x + 11, y + 29, fill="black", outline="")
        self.canvas.create_rectangle(x + 32, y + 13, x + 38, y + 31, fill="white", outline="black")
        self.canvas.create_rectangle(x + 10, y + 36, x + 31, y + 41, fill="black", outline="")
        self.canvas.create_rectangle(x + 20, y + 40, x + 34, y + 44, fill="black", outline="")

    def draw_text(self, x, y, text, color="black", font=None, anchor="nw"):
        if font is None:
            font = self.font_normal

        self.canvas.create_text(
            x,
            y,
            text=text,
            fill=color,
            font=font,
            anchor=anchor
        )

    def draw_score_panel(self):
        panel_left = 55
        panel_top = 24
        panel_right = 585
        panel_bottom = 102

        self.canvas.create_rectangle(
            panel_left,
            panel_top,
            panel_right,
            panel_bottom,
            fill="white",
            outline="black"
        )

        self.canvas.create_rectangle(
            panel_left,
            panel_top,
            panel_right,
            panel_top + 28,
            fill="lightyellow",
            outline="black"
        )

        self.draw_text(
            panel_left + 16,
            panel_top + 6,
            "Karel Beeper Quest",
            "black",
            self.font_title
        )

        self.draw_text(
            panel_left + 16,
            panel_top + 38,
            "Level " + str(self.level_number),
            "black",
            self.font_normal
        )

        self.draw_text(
            panel_left + 120,
            panel_top + 38,
            "Moves: " + str(self.moves),
            "black",
            self.font_normal
        )

        self.draw_text(
            panel_left + 240,
            panel_top + 38,
            "Beepers: " + str(self.beepers_collected) + " of " + str(self.total_beepers),
            "black",
            self.font_normal
        )

        self.draw_text(
            panel_left + 16,
            panel_top + 62,
            "Energy",
            "black",
            self.font_normal
        )

        self.canvas.create_rectangle(
            panel_left + 85,
            panel_top + 60,
            panel_left + 265,
            panel_top + 76,
            fill="lightgray",
            outline="black"
        )

        energy_width = self.energy * 4

        if energy_width > 180:
            energy_width = 180

        if energy_width < 0:
            energy_width = 0

        if self.energy <= 8:
            energy_color = "firebrick"
        elif self.energy <= 18:
            energy_color = "goldenrod"
        else:
            energy_color = "forestgreen"

        self.canvas.create_rectangle(
            panel_left + 85,
            panel_top + 60,
            panel_left + 85 + energy_width,
            panel_top + 76,
            fill=energy_color,
            outline=""
        )

        self.draw_text(
            panel_left + 280,
            panel_top + 58,
            str(self.energy),
            "black",
            self.font_normal
        )

    def draw_mission_panel(self):
        panel_left = 625
        panel_top = 45
        panel_right = 955
        panel_bottom = 455

        self.canvas.create_rectangle(
            panel_left,
            panel_top,
            panel_right,
            panel_bottom,
            fill="white",
            outline="black"
        )

        self.canvas.create_rectangle(
            panel_left,
            panel_top,
            panel_right,
            panel_top + 36,
            fill="lightyellow",
            outline="black"
        )

        self.draw_text(
            panel_left + 18,
            panel_top + 10,
            "MISSION BRIEFING",
            "black",
            self.font_title
        )

        if self.game_won:
            status_text = "Level complete"
            detail_text = "Press NEXT to continue."
            status_color = "forestgreen"
        elif self.game_over:
            status_text = "Out of energy"
            detail_text = "Press RETRY to restart."
            status_color = "firebrick"
        elif self.beepers_collected == self.total_beepers:
            status_text = "Goal unlocked"
            detail_text = "Reach the green flag."
            status_color = "forestgreen"
        else:
            remaining = self.total_beepers - self.beepers_collected
            status_text = "Collect all beepers"
            detail_text = str(remaining) + " beeper(s) left."
            status_color = "black"

        self.canvas.create_rectangle(
            panel_left + 18,
            panel_top + 58,
            panel_right - 18,
            panel_top + 116,
            fill="honeydew",
            outline="black"
        )

        self.draw_text(
            panel_left + 34,
            panel_top + 68,
            status_text,
            status_color,
            self.font_header
        )

        self.draw_text(
            panel_left + 34,
            panel_top + 90,
            detail_text,
            "black",
            self.font_normal
        )

        self.draw_text(
            panel_left + 18,
            panel_top + 140,
            "Tile guide",
            "black",
            self.font_header
        )

        self.draw_legend_item(panel_left + 22, panel_top + 170, "beeper", "Beeper", "Collect all")
        self.draw_legend_item(panel_left + 22, panel_top + 210, "battery", "Battery", "Restores energy")
        self.draw_legend_item(panel_left + 22, panel_top + 250, "trap", "Trap", "Drains energy")
        self.draw_legend_item(panel_left + 22, panel_top + 290, "portal", "Portal", "Teleports Karel")
        self.draw_legend_item(panel_left + 22, panel_top + 330, "goal", "Goal flag", "Opens after beepers")

        self.canvas.create_rectangle(
            panel_left + 18,
            panel_top + 370,
            panel_right - 18,
            panel_top + 400,
            fill="aliceblue",
            outline="black"
        )

        self.draw_text(
            panel_left + 30,
            panel_top + 377,
            "Tip: portals are linked in pairs.",
            "black",
            self.font_small
        )

    def draw_legend_item(self, x, y, item_type, title, description):
        if item_type == "beeper":
            self.draw_mini_beeper(x, y)
        elif item_type == "battery":
            self.draw_mini_battery(x, y)
        elif item_type == "trap":
            self.draw_mini_trap(x, y)
        elif item_type == "portal":
            self.draw_mini_portal(x, y)
        elif item_type == "goal":
            self.draw_mini_goal(x, y)

        self.draw_text(x + 38, y - 3, title, "black", self.font_header)
        self.draw_text(x + 38, y + 15, description, "gray25", self.font_small)

    def draw_mini_beeper(self, x, y):
        self.canvas.create_oval(x, y, x + 18, y + 18, fill="gold", outline="black")
        self.canvas.create_rectangle(x + 8, y + 4, x + 11, y + 15, fill="orange", outline="")

    def draw_mini_battery(self, x, y):
        self.canvas.create_rectangle(x, y + 4, x + 20, y + 15, fill="dodgerblue", outline="black")
        self.canvas.create_rectangle(x + 20, y + 7, x + 24, y + 12, fill="dodgerblue", outline="black")
        self.canvas.create_rectangle(x + 6, y + 8, x + 15, y + 11, fill="white", outline="")

    def draw_mini_trap(self, x, y):
        self.canvas.create_rectangle(x, y, x + 20, y + 20, fill="firebrick", outline="black")
        self.canvas.create_rectangle(x + 5, y + 5, x + 15, y + 15, fill="black", outline="")
        self.canvas.create_oval(x + 8, y + 8, x + 12, y + 12, fill="orange", outline="")

    def draw_mini_portal(self, x, y):
        self.canvas.create_oval(x, y, x + 20, y + 20, fill="purple", outline="black")
        self.canvas.create_oval(x + 5, y + 5, x + 15, y + 15, fill="violet", outline="black")

    def draw_mini_goal(self, x, y):
        self.canvas.create_rectangle(x + 8, y, x + 11, y + 24, fill="black", outline="")
        self.canvas.create_rectangle(x + 11, y, x + 28, y + 13, fill="green", outline="black")

    def draw_controls(self):
        self.draw_button(UP_BUTTON, "UP", "darkslategray")
        self.draw_button(LEFT_BUTTON, "LEFT", "darkslategray")
        self.draw_button(DOWN_BUTTON, "DOWN", "darkslategray")
        self.draw_button(RIGHT_BUTTON, "RIGHT", "darkslategray")

        if self.game_won:
            self.draw_button(RESET_BUTTON, "NEXT", "darkgreen")
        elif self.game_over:
            self.draw_button(RESET_BUTTON, "RETRY", "firebrick")
        else:
            self.draw_button(RESET_BUTTON, "RESET", "firebrick")

    def draw_button(self, button, label, color):
        self.canvas.create_rectangle(
            button[0],
            button[1],
            button[2],
            button[3],
            fill=color,
            outline="white",
            width=2
        )

        self.canvas.create_text(
            (button[0] + button[2]) // 2,
            (button[1] + button[3]) // 2,
            text=label,
            fill="white",
            font=self.font_button
        )

    def draw_win_message(self):
        self.canvas.create_rectangle(
            310,
            240,
            620,
            330,
            fill="white",
            outline="black"
        )

        self.canvas.create_rectangle(
            310,
            240,
            620,
            270,
            fill="darkgreen",
            outline="black"
        )

        self.draw_text(335, 249, "LEVEL COMPLETE", "white", self.font_header)
        self.draw_text(335, 282, "Karel collected all beepers.", "black", self.font_normal)

        self.draw_text(
            335,
            304,
            "Level " + str(self.level_number) + " finished in " + str(self.moves) + " moves.",
            "black",
            self.font_normal
        )

    def draw_game_over_message(self):
        self.canvas.create_rectangle(
            310,
            240,
            620,
            330,
            fill="white",
            outline="black"
        )

        self.canvas.create_rectangle(
            310,
            240,
            620,
            270,
            fill="firebrick",
            outline="black"
        )

        self.draw_text(340, 249, "OUT OF ENERGY", "white", self.font_header)
        self.draw_text(340, 292, "Press RETRY to try again.", "black", self.font_normal)

    def draw_cloud(self, x, y):
        self.canvas.create_oval(x, y + 18, x + 65, y + 48, fill="white", outline="")
        self.canvas.create_oval(x + 30, y, x + 85, y + 45, fill="white", outline="")
        self.canvas.create_oval(x + 65, y + 20, x + 125, y + 50, fill="white", outline="")

    def get_x(self, col):
        return WORLD_LEFT + col * TILE_SIZE

    def get_y(self, row):
        return WORLD_TOP + row * TILE_SIZE


if __name__ == "__main__":
    game = KarelQuestGame()
    game.run()