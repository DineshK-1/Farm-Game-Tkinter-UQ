import tkinter as tk
from tkinter import filedialog # For masters task
from typing import Callable, Union, Optional
from a3_support import *
from model import *
from constants import *

# Implement your classes here

class InfoBar(AbstractGrid):
    
    def __init__(self, master: tk.Tk | tk.Frame) -> None:
        super().__init__(master, (2,3), (FARM_WIDTH+INVENTORY_WIDTH, INFO_BAR_HEIGHT))
    
    def redraw(self, day: int, money: int, energy: int) -> None:
        self.clear()
        self.annotate_position((0,0), "Day:", HEADING_FONT)
        self.annotate_position((0,1), "Money:", HEADING_FONT)
        self.annotate_position((0,2), "Energy:", HEADING_FONT)
        self.annotate_position((1,0), day)
        self.annotate_position((1,1), f"${money}")
        self.annotate_position((1,2), energy)

class FarmView(AbstractGrid):

    def __init__(self, master: tk.Tk | tk.Frame, dimensions: tuple[int, int], size: tuple[int, int], **kwargs) -> None:
        super().__init__(master, dimensions, size)
        self.ImageCache = {}
        map = kwargs.get("map")
        self.redraw(map, {}, (0,0), DOWN)
        print(map)

    def redraw(self, ground: list[str], plants: dict[tuple[int, int], "Plant"], player_position: tuple[int, int], player_direction: str) -> None:
        self.clear()
        for i in range(0, len(ground)):
            for j in range(0, len(ground[i])):
                Type = ground[i][j]
                if Type == "G":
                    img = get_image("images/"+IMAGES[GRASS], (50,50), self.ImageCache)
                    pos = self.get_midpoint((i,j))
                    self.create_image(pos[0], pos[1], image=img)
                elif Type == "U":
                    img = get_image("images/"+IMAGES[UNTILLED], (50,50), self.ImageCache)
                    pos = self.get_midpoint((i,j))
                    self.create_image(pos[0], pos[1], image=img)
                elif Type == "S":
                    img = get_image("images/"+IMAGES[SOIL], (50,50), self.ImageCache)
                    pos = self.get_midpoint((i,j))
                    self.create_image(pos[0], pos[1], image=img)

        player_pos = self.get_midpoint((player_position[0], player_position[1]))
        if player_direction == DOWN:
            player_image = get_image("images/player_s.png", (50,50), self.ImageCache)
        elif player_direction == UP:
            player_image = get_image("images/player_w.png", (50,50), self.ImageCache)
        elif player_direction == LEFT:
            player_image = get_image("images/player_a.png", (50,50), self.ImageCache)
        elif player_direction == RIGHT:
            player_image = get_image("images/player_d.png", (50,50), self.ImageCache)
        
        self.create_image(player_pos[0], player_pos[1], image=player_image)

class ItemView(tk.Frame):

    def __init__ (self, master: tk.Frame, item_name: str, amount: int, select_command: Optional[Callable[[str], None]] = None, sell_command: Optional[Callable[[str],None]] = None, buy_command: Optional[Callable[[str], None]] = None) -> None:
        backgrondColor = INVENTORY_COLOUR
        if item_name in "Potato":
            backgrondColor = INVENTORY_COLOUR
        elif item_name in "Kale":
            backgrondColor = INVENTORY_COLOUR
        elif item_name in "Berry":
            backgrondColor = INVENTORY_EMPTY_COLOUR

        super().__init__(master, background=backgrondColor)
        
        seed_label = tk.Label(self, text=f"{item_name}: {amount}", background=backgrondColor).pack()
        if item_name in BUY_PRICES:
            buy_label = tk.Label(self, text=f"Buy price: ${BUY_PRICES[item_name]}", background=backgrondColor).pack()
        else:
            buy_label = tk.Label(self, text=f"Buy price: $N/A", background=backgrondColor).pack()
        sell_label = tk.Label(self, text=f"Sell price: ${SELL_PRICES[item_name]}", background=backgrondColor).pack()

        if item_name in BUY_PRICES:
            buy_button = tk.Button(self, text="Buy", command=lambda: buy_command(item_name))
            buy_button.pack(side="left")

        sell_button = tk.Button(self, text="Sell", command=lambda: sell_command(item_name))
        sell_button.pack(side="left")

class FarmGame():

    def __init__(self, master: tk.Tk, map_file: str) -> None:
        master.title("Farm Game")

        self.ImageCache = {}

        BannerLabel = tk.Label(master, image=get_image("images/header.png", (FARM_WIDTH+INVENTORY_WIDTH, BANNER_HEIGHT), self.ImageCache))
        BannerLabel.pack()

        self.Model = FarmModel(map_file)

        self.Farm = FarmView(master, self.Model.get_dimensions(), (FARM_WIDTH, FARM_WIDTH), map=self.Model.get_map())
        self.Farm.pack(side="left")

        Inventory_Frame = tk.Frame(master, width=INVENTORY_WIDTH)

        self.Player = self.Model.get_player()
        PlayerInv = self.Player.get_inventory()

        self.ItemPSeed = ItemView(Inventory_Frame, "Potato Seed", PlayerInv["Potato Seed"], None, None, None)
        self.ItemKSeed = ItemView(Inventory_Frame, "Kale Seed", PlayerInv["Kale Seed"], None, None, None)
        self.ItemKBSeed = ItemView(Inventory_Frame, "Berry Seed", 0, None, None, None)
        self.ItemPotato = ItemView(Inventory_Frame, "Potato", 0, None, None, None)
        self.ItemKale = ItemView(Inventory_Frame, "Kale", 0, None, None, None)
        self.ItemBerry = ItemView(Inventory_Frame, "Berry", 0, None, None, None)

        self.ItemPSeed.pack()
        self.ItemKSeed.pack()
        self.ItemKBSeed.pack()
        self.ItemPotato.pack()
        self.ItemKale.pack()
        self.ItemBerry.pack()

        Inventory_Frame.pack(side="right", fill="y")

        self.Info = InfoBar(master)
        self.redraw_info()
        self.Info.pack(side="bottom")
        def next_day_command():
            self.Model.new_day()
            self.redraw_info()

        NextButton = tk.Button(master, text="Next day", command=next_day_command).pack()

        master.bind("<KeyPress>", self.handle_keypress)

        master.mainloop()

    def redraw_info(self):
        self.Info.redraw(self.Model.get_days_elapsed(), self.Model.get_player().get_money(), self.Model.get_player().get_energy())

    def redraw(self) -> None:
        self.Farm.redraw(self.Model.get_map(), self.Model.get_plants(), self.Model.get_player_position(), self.Player.get_direction())
        self.redraw_info()

    def handle_keypress(self, event: tk.Event) -> None:
        if event.keysym in [UP, DOWN, LEFT, RIGHT]:
            pos = self.Player.get_position()

            if event.keysym == "w":
                self.Player.set_position((pos[0]-1, pos[1]))
            elif event.keysym == "s":
                self.Player.set_position((pos[0]+1, pos[1]))
            elif event.keysym == "a":
                self.Player.set_position((pos[0], pos[1]-1))
            elif event.keysym == "d":
                self.Player.set_position((pos[0], pos[1]+1))

            self.Player.set_direction(event.keysym)
            self.Player.reduce_energy(1)
            self.redraw()



def play_game(root: tk.Tk, map_file: str) -> None:
    # root.title("Farm Game")

    # BannerLabel = tk.Label(root, image=get_image("images/header.png", (FARM_WIDTH+INVENTORY_WIDTH, BANNER_HEIGHT), {}))
    # BannerLabel.pack(side="top")

    # Model = FarmModel(map_file)
    # print(Model.get_dimensions())

    # Farm = FarmView(root, Model.get_dimensions(), (FARM_WIDTH, FARM_WIDTH), map=Model.get_map())
    # Farm.pack(side="left", fill="y")

    # Inventory_Frame = tk.Frame(root, width=INVENTORY_WIDTH)

    # ItemPSeed = ItemView(Inventory_Frame, "Potato Seed", 5, None, None, None).pack()
    # ItemKSeed = ItemView(Inventory_Frame, "Kale Seed", 5, None, None, None).pack()
    # ItemKBSeed = ItemView(Inventory_Frame, "Berry Seed", 0, None, None, None).pack()
    # ItemPotato = ItemView(Inventory_Frame, "Potato", 0, None, None, None).pack()
    # ItemKale = ItemView(Inventory_Frame, "Kale", 0, None, None, None).pack()
    # ItemBerry = ItemView(Inventory_Frame, "Berry", 0, None, None, None).pack()

    # Inventory_Frame.pack(side="right", fill="y")

    # Info = InfoBar(root)
    # Info.redraw(Model.get_days_elapsed(), Model.get_player().get_money(), Model.get_player().get_energy())
    # Info.pack(side="bottom")
    # def next_day_command():
    #     Model.new_day()
    #     Info.redraw(Model.get_days_elapsed(), Model.get_player().get_money(), Model.get_player().get_energy())

    # NextButton = tk.Button(root, text="Next day", command=next_day_command)
    
    # root.mainloop()
    FarmGame(root, map_file)

def main() -> None:
    window = tk.Tk()

    play_game(window, "maps/map1.txt")

if __name__ == '__main__':
    main()
