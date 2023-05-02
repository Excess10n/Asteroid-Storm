import pygame
import math
import random
import sqlite3

pygame.init()

connect = sqlite3.connect("save data.db")
db = connect.cursor()

try:
    db.execute("CREATE TABLE SaveFile (saveID INTAGER PRIMARY KEY, currentID INTAGER, credits INTAGER, posx INTAGER, posy INTAGER, fuel INTAGER, health INTAGER, ammo1 INTAGER, ammo2 INTAGER, ammo3 INTAGER)")
except:
    pass
try:
    db.execute("CREATE TABLE OwnedShips (shipID INTAGER PRIMARY KEY, saveID INTAGER, weapon1 INTAGER, weapon2 INTAGER, weapon3 INTAGER)")
except:
    pass
try:
    db.execute("CREATE TABLE Inventory (itemID INTAGER PRIMARY KEY, saveID INTAGER, quantity INTAGER)")
except:
    pass
try:
    db.execute("CREATE TABLE Weapons (weaponID INTAGER PRIMARY KEY, saveID INTAGER, owned BOOLEAN)")
except:
    pass
try:
    # when adding new config values delete the table and write the new one here, and change the following:
    # the initial config
    # the format in the settings menu
    # the values that are writen to the table at the end
    db.execute("CREATE TABLE Config (thrust STRING, weapon1 STRING, weapon2 STRING, weapon3 STRING, pause STRING, scroll BOOLEAN, scrollfire STRING, ui BOOLEAN, backdrop BOOLEAN)")
except:
    pass

db.execute("SELECT * FROM SaveFile INNER JOIN OwnedShips ON SaveFile.saveID = OwnedShips.saveID")
db.execute("SELECT * FROM SaveFile INNER JOIN Inventory ON SaveFile.saveID = Inventory.saveID")
db.execute("SELECT * FROM SaveFile INNER JOIN Weapons ON SaveFile.saveID = Weapons.saveID")

#config array defined
try:
    db.execute("SELECT * FROM Config")
    array = db.fetchall()[0]
    config = []
    for i in range(len(array)):
        if i == 5 or i == 7 or i == 8:
            config.append(bool(array[i]))
        else:
            config.append(str(array[i]))
except:
    config = ["MOUSE1", "1", "2", "3", "escape", True, "MOUSE2", True, True]

display = pygame.display.set_mode()
SCREEN = display.get_size()
FRAME_RATE = 120
#frame rate affects the game loop speed, not display speed
MESSAGE_TIME = 100
SHIELD_REGEN = 500
IFRAME_NUM = 10
CHARGE_TIME = 50
LASER_STEP = 5
DAMAGE_MULTIPLIER = 5
ALIEN_RANDOM = 300
ALIEN_RANDOM_AGRO = 50
ALIEN_AGRO = 700
#the point the alien travels to when in radius of the ship (on screen)
THRUST_CONSUMPTION = 0.1
LASER_CONSUMPTION = 0.05
LASER_DIFFERENCE = 0.8
#the difference between size 1 and 2/3 laser consumptions
REFUEL_MULTIPLIER = 0.25
REPAIR_MULTIPLIER = 0.25
RESTOCK_MULTIPLIER = 0.5
BACKDROP_MOVEMENT = 0.02
BACKDROP_ZOOM = 1.5
STARTING_CREDITS = 100

def load_image(file_name, size):
    def remove_green(surface):
        pygame.Surface.set_colorkey(surface, [0,255,0])
        return surface.convert()
    return remove_green(pygame.transform.scale(pygame.image.load(file_name), size))

class ships:
    def __init__(self, ID, name, cost, speed, accel, health, shield, inventory, slots, hitbox, sprite, thrust_sprite):
        self.ID = ID
        self.name = name
        self.cost = cost
        self.speed = speed
        self.accel = accel
        self.health = health
        self.shield = shield
        self.inventory = inventory
        self.slots = slots
        self.hitbox = hitbox
        self.sprite = sprite
        self.thrust_sprite = thrust_sprite

ship0 = ships(0, "Delta wing",0 ,35 ,0.15 ,100 ,100 ,10 ,[1, 0, 0] ,35 ,load_image("ship0.png", (30, 40)), load_image("ship0thrust.png", (30, 40)))
ship1 = ships(1, "Alpha wing",100 ,20 ,0.1 ,150 ,200 ,30 ,[1, 1, 1] ,45 ,load_image("ship1.png", (40, 50)), load_image("ship1thrust.png", (40, 50)))
ship2 = ships(2, "Condor",200 ,40 ,0.21 ,50 ,100 ,20 ,[1, 1, 0] ,50 ,load_image("ship2.png", (40, 60)), load_image("ship2thrust.png", (40, 60)))
ship3 = ships(3, "Speeder",200 ,50 ,0.25 ,50 ,50 ,10 ,[1, 0, 0] ,50 ,load_image("ship3.png", (40, 60)), load_image("ship3thrust.png", (40, 60)))
ship4 = ships(4, "Lancer I",300 ,20 ,0.08 ,150 ,150 ,40 ,[-1, 1, 1] ,65 ,load_image("ship4.png", (50, 80)), load_image("ship4thrust.png", (50, 80)))
ship5 = ships(5, "Viper",500 ,30 ,0.1 ,200 ,200 ,30 ,[2, 2, 0] ,110 ,load_image("ship5.png", (80, 140)), load_image("ship5thrust.png", (80, 140)))
ship6 = ships(6, "Gunship",600 ,20 ,0.07 ,300 ,250 ,40,[2, 2, 2] ,130 ,load_image("ship6.png", (110, 150)), load_image("ship6thrust.png", (110, 150)))
ship7 = ships(7, "Class 1 hauler",500 ,15 ,0.05 ,300 ,200 ,100 ,[1, 1, 0] ,150 ,load_image("ship8.png", (150, 150)), load_image("ship8thrust.png", (150, 150)))
ship8 = ships(8, "Lancer II",600 ,15 ,0.06 ,200 ,250 ,50 ,[-2, 2, 2] ,155 ,load_image("ship7.png", (130, 180)), load_image("ship7thrust.png", (130, 180)))
ship9 = ships(9, "Vulture",1500 ,20 ,0.07 ,250 ,350 ,40 ,[3, 3, 0] ,160 ,load_image("ship9.png", (140, 180)), load_image("ship9thrust.png", (140, 180)))
ship10 = ships(10, "Clipper",1700 ,15 ,0.04 ,350,450 ,50 ,[3, 3, 3] ,250 ,load_image("ship10.png", (250, 250)), load_image("ship10thrust.png", (250, 250)))
ship11 = ships(11, "Class 2 hauler",1000 ,10 ,0.03 ,400 ,300 ,150 ,[2, 2, 0] ,245 ,load_image("ship11.png", (240, 250)), load_image("ship11thrust.png", (240, 250)))
ship12 = ships(12, "Lancer III",2000 ,10 ,0.04 ,350 ,350 ,100 ,[-3, 3, 3] ,210 ,load_image("ship12.png", (180, 240)), load_image("ship12thrust.png", (180, 240)))

class weapons:
    def __init__(self, ID, name, size, cost, ammo, delay, damage, asteroid, velocity, restock, sprite):
        self.ID = ID
        self.name = name
        self.size = size
        self.cost = cost
        self.ammo = ammo
        self.delay = delay
        self.damage = damage
        self.asteroid = asteroid
        self.velocity = velocity
        self.restock = restock
        self.sprite = sprite

weapon1 = weapons(1, "Plasma blaster S", 1, 0, 100, 20, 10, 3, 10, 0.1, load_image("bullet1.png", (16, 16)))
weapon7 = weapons(7, "Plasma blaster M", 2, 150, 150, 20, 40, 5, 10, 0.2, load_image("bullet1.png", (16, 16)))
weapon13 = weapons(13, "Plasma blaster L", 3, 300, 200, 20, 80, 7, 10, 0.4, load_image("bullet1.png", (16, 16)))
weapon2 = weapons(2, "Machine Gun S", 1, 50, 300, 5, 10, 1, 10, 0.1, load_image("bullet2.png", (6, 6)))
weapon8 = weapons(8, "Machine Gun M", 2, 200, 400, 5, 20, 2, 15, 0.1, load_image("bullet2.png", (6, 6)))
weapon14 = weapons(14, "Machine Gun L", 3, 400, 500, 5, 30, 3, 20, 0.2, load_image("bullet2.png", (6, 6)))
weapon3 = weapons(3, "Laser S", 1, 100, 1, 0, 0.5, 0, -1, 0, 5)
weapon9 = weapons(9, "Laser M", 2, 400, 1, 0, 1, 0, -1, 0, 10)
weapon15 = weapons(15, "Laser L", 3, 800, 1, 0, 3, 0, -1, 0, 15)
weapon4 = weapons(4, "Railgun S", 1, 200, 50, -50, 30, 5, 40, 1, load_image("bullet3.png", (50, 50)))
weapon10 = weapons(10, "Railgun M", 2, 500, 70, -50, 50, 7, 60, 1, load_image("bullet3.png", (50, 50)))
weapon16 = weapons(16, "Railgun L", 3, 1000, 100, -50, 100, 9, 80, 1, load_image("bullet3.png", (50, 50)))
weapon5 = weapons(5, "Explosive Launcher S", 1, 200, 20, 100, 50, 4, 5, 2, load_image("bullet4.png", (20, 20)))
weapon11 = weapons(11, "Explosive Launcher M", 2, 500, 40, 100, 100, 6, 4, 2, load_image("bullet4.png", (36, 36)))
weapon17 = weapons(17, "Explosive Launcher L", 3, 1000, 60, 100, 200, 8, 2, 2, load_image("bullet4.png", (50, 50)))
weapon6 = weapons(6, "Mining Laser S", 1, 0, 1, 0, 0, 3, -1, 0, 5)
weapon12 = weapons(12, "Mining Laser M", 2, 0, 1, 0, 0, 5, -1, 0, 10)
weapon18 = weapons(18, "Mining Laser L", 3, 0, 1, 0, 0, 7, -1, 0, 15)

class asteroids:
    def __init__(self, size, hitbox, speed, frequency, item, sprite):
        self.size = size
        self.hitbox = hitbox
        self.speed = speed
        self.frequency = frequency
        self.item = item
        self.sprite = sprite
        
asteroid0 = asteroids(1, 20, 4, 0, [0, 0, 0], load_image("asteroid0.png", (40, 40)))
asteroid1 = asteroids(2, 40, 3, 0, [0, 1, 1], load_image("asteroid1.png", (80, 80)))
asteroid2 = asteroids(3, 65, 2, 50, [0, 1, 2], load_image("asteroid2.png", (130, 130)))
asteroid3 = asteroids(4, 95, 1.5, 40, [1, 2, 3], load_image("asteroid3.png", (190, 190)))
asteroid4 = asteroids(5, 130, 1, 30, [2, 3, 4], load_image("asteroid4.png", (260, 260)))
asteroid5 = asteroids(6, 170, 0.75, 20, [4, 5, 6], load_image("asteroid5.png", (340, 340)))
asteroid6 = asteroids(7, 215, 0.5, 10, [6, 7, 8], load_image("asteroid6.png", (430, 430)))
asteroid7 = asteroids(8, 265, 0.25, 5, [7, 8, 9], load_image("asteroid7.png", (530, 530)))

class aliens:
    def __init__(self, ID, speed, health, damage, delay, velocity, hitbox, frequency, item, sprite):
        self.ID = ID
        self.speed = speed
        self.health = health
        self.damage = damage
        self.delay = delay
        self.velocity = velocity
        self.hitbox = hitbox
        self.frequency = frequency
        self.item = item
        self.sprite = sprite

alien0 = aliens(0, 2, 100, 10, 60, 10, 60, 10, [1, 2, 3], load_image("alien0.png", (60, 60)))
alien1 = aliens(1, 1, 150, 20, 40, 10, 100, 10, [3, 4, 5], load_image("alien1.png", (100, 100)))
alien2 = aliens(2, 1, 200, 20, 10, 30, 200, 5, [6, 7, 8], load_image("alien2.png", (200, 200)))
alien3 = aliens(3, 0.5, 400, 200, 60, 80, 400, 2, [8, 9, 9], load_image("alien3.png", (400, 400)))

ALIEN_BULLET_SPRITE = load_image("bullet1.png", (10, 10))

class items:
    def __init__(self, ID, name, value, colour):
        self.ID = ID
        self.name = name
        self.value = value
        self.colour = colour

item0 = items(0, "Stone", 10, [127, 127, 127])
item1 = items(1, "Copper", 20, [255, 127, 0])
item2 = items(2, "Iron", 40, [255, 255, 255])
item3 = items(3, "Lead", 70, [128, 0, 128])
item4 = items(4, "Tungsten", 100, [165, 42, 42])
item5 = items(5, "Aluminium", 150, [200, 200, 200])
item6 = items(6, "Lithium", 200, [231, 84, 128])
item7 = items(7, "Titanium", 250, [0, 150, 0])
item8 = items(8, "Gold", 300, [255, 211, 0])
item9 = items(9, "Diamond", 500, [0, 255, 255])

ARROW = load_image("arrow.png", (15, 20))
SPACE_STATION_SPRITE = load_image("Space Station.png", (2000, 1500))
BACKDROP = load_image("Back Drop.png", (SCREEN[0] * BACKDROP_ZOOM, SCREEN[1] * BACKDROP_ZOOM))

def print_text(string, pos, size):
    font = pygame.font.Font("VT323-Regular.ttf", size)
    text = font.render(string, False, (255, 255, 255))
    display.blit(text, pos)

def print_button(string, pos, size, invert):
    font = pygame.font.Font("VT323-Regular.ttf", size)
    if invert:
        text = font.render(string, False, (255, 255, 255), (0, 0, 0))
    else:
        text = font.render(string, False, (0, 0, 0), (255, 255, 255))
    display.blit(text, pos)

def check_position(posx, posy, x1, x2, y1, y2):
    if posx > x1 and posx < x2 and posy > y1 and posy < y2:
        return True
    else:
        return False

def main_menu():
    global state, held, temp_message, settings, submenu
    if settings == False:
        temp_message = ""
    print_text("ASTEROID STORM", (0, 0), 200)
    #update UI for main menu

    if held:
        if mouse[0] == False:
            held = False

    isnull = False
    db.execute("SELECT saveID FROM SaveFile")
    if db.fetchall() == []:
        isnull = True

    if settings:
        settings_menu()
    
    if check_position(mousex, mousey, 100, 325, 300, 370):
        print_button("NEW GAME", (100, 285), 100, True)
        if isnull:
            temp_message = "start a new game"
        else:
            temp_message = "start a new game (this will delete the existing one)"
        if mouse[0] and held == False:
            temp_message = ""
            new_game()
            settings = False
            state = 1.1
    else:
        print_button("NEW GAME", (100, 300), 70, True)
        
    if check_position(mousex, mousey, 100, 350, 400, 470):
        print_button("LOAD GAME", (100, 385), 100, True)
        if isnull:
            temp_message = "no save file found (try NEW GAME)"
        else:
            temp_message = "load an existing save file"
        if mouse[0] and held == False:
            if isnull == False:
                success = load_game(0)
                if success:
                    temp_message = ""
                    settings = False
                    state = 1.1
                else:
                    temp_message = "load failed"
    else:
        print_button("LOAD GAME", (100, 400), 70, True)

    if check_position(mousex, mousey, 100, 325, 500, 570):
        print_button("SETTINGS", (100, 485), 100, True)
        temp_message = "view and change the settings"
        if mouse[0] and held == False:
            settings = True
            submenu = 0
    else:
        print_button("SETTINGS", (100, 500), 70, True)
        
    if check_position(mousex, mousey, 100, 210, 600, 670):
        print_button("QUIT", (100, 585), 100, True)
        temp_message = "exit the game"
        if mouse[0] and held == False:
            state = -1
    else:
        print_button("QUIT", (100, 600), 70, True)

def new_game():
    global owned_ships, current_ship, ship_position, ship_inventory, ship_fuel, ship_health, ship_shield, ship_ammo, owned_weapons, total_credits
    owned_ships = [[0, 1, 0, 0]]
    current_ship = owned_ships[0]
    ship_position = [0, 0]
    ship_inventory = []
    ship_fuel = 100
    ship_health = ship0.health
    ship_ammo = [weapon1.ammo, 0, 0]
    owned_weapons = [True]
    for i in range(17):
        owned_weapons.append(False)
    total_credits = STARTING_CREDITS

def load_game(saveID):
    global owned_ships, current_ship, ship_position, ship_inventory, ship_fuel, ship_health, ship_shield, ship_ammo, owned_weapons, total_credits
    try:
        db.execute("SELECT * FROM SaveFile WHERE saveID = ?", (saveID, ))
        save = db.fetchall()
        current_shipID = save[0][1]
        total_credits = save[0][2]
        ship_position = [save[0][3], save[0][4]]
        ship_fuel = save[0][5]
        ship_health = save[0][6]
        ship_ammo = [save[0][7], save[0][8], save[0][9]]
        
        db.execute("SELECT * FROM OwnedShips WHERE saveID = ?", (saveID, ))
        save = db.fetchall()
        owned_ships = []
        for i in range(len(save)):
            owned_ships.append([save[i][0], save[i][2], save[i][3], save[i][4]])
        for i in range(len(owned_ships)):
            if owned_ships[i][0] == current_shipID:
                current_ship = owned_ships[i]

        db.execute("SELECT * FROM Inventory WHERE saveID = ?", (saveID, ))
        save = db.fetchall()
        ship_inventory = []
        for i in range(10):
            for j in range(save[i][2]):
                ship_inventory.append(i)

        db.execute("SELECT * FROM Weapons WHERE saveID = ?", (saveID, ))
        save = db.fetchall()
        owned_weapons = []
        for i in range(18):
            owned_weapons.append(save[i][2])
        return True
    except:
        return False

def save_game(saveID):
    db.execute("DELETE FROM SaveFile WHERE saveID = ?", (saveID, ))
    db.execute("DELETE FROM OwnedShips WHERE saveID = ?", (saveID, ))
    db.execute("DELETE FROM Inventory WHERE saveID = ?", (saveID, ))
    db.execute("DELETE FROM Weapons WHERE saveID = ?", (saveID, ))

    db.execute("INSERT INTO SaveFile (saveID, currentID, credits, posx, posy, fuel, health, ammo1, ammo2, ammo3) VALUES (?,?,?,?,?,?,?,?,?,?)",
               (saveID, current_ship[0], total_credits, ship_position[0], ship_position[1], ship_fuel, ship_health, ship_ammo[0], ship_ammo[1], ship_ammo[2]))

    for i in range(len(owned_ships)):
        db.execute("INSERT INTO OwnedShips (shipID, saveID, weapon1, weapon2, weapon3) VALUES (?,?,?,?,?)",
                   (owned_ships[i][0], saveID, owned_ships[i][1], owned_ships[i][2], owned_ships[i][3]))

    quantity = get_inventory_quantities()
    for i in range(10):
        db.execute("INSERT INTO Inventory (itemID, saveID, quantity) VALUES (?,?,?)", (i, saveID, quantity[i]))

    for i in range(18):
        db.execute("INSERT INTO Weapons (weaponID, saveID, owned) VALUES (?,?,?)", (i, saveID, owned_weapons[i]))

def settings_menu():
    global settings, config, submenu, changing, temp_message, held2
    if state == 0:
        offx = 100
        offy = 150
        pygame.draw.line(display, (255, 255, 255), (500, 200), (500, 800), 10)
        pygame.draw.line(display, (255, 255, 255), (900, 200), (900, 800), 10)
    if state == 1.5 or state == 1.6:
        offx = 0
        offy = 0
        pygame.draw.rect(display, (0, 0, 0), (405, 0, 395, SCREEN[1]))
        pygame.draw.line(display, (255, 255, 255), (800, 0), (800, 800), 10)
    print_text("SETTINGS", (450 + offx, 50 + offy), 100)
    print_text("BACK", (450 + offx, 150 + offy), 50)
    print_text("CONTROLS", (450 + offx, 250 + offy), 50)
    print_text("UI", (450 + offx, 350 + offy), 50)

    if check_position(mousex, mousey, 450 + offx, 525 + offx, 150 + offy, 200 + offy):
        print_button("BACK", (450 + offx, 140 + offy), 70, True)
        if mouse[0]:
            settings = False
            submenu = 0

    if check_position(mousex, mousey, 450 + offx, 610 + offx, 250 + offy, 300 + offy):
        print_button("CONTROLS", (450 + offx, 240 + offy), 70, True)
        if mouse[0]:
            submenu = 1
            changing = -1

    if check_position(mousex, mousey, 450 + offx, 480 + offx, 350 + offy, 400 + offy):
        print_button("UI", (450 + offx, 340 + offy), 70, True)
        if mouse[0]:
            submenu = 2

    if submenu > 0:
        if state == 0:
            pygame.draw.line(display, (255, 255, 255), (1300, 200), (1300, 800), 10)
        if state == 1.5 or state == 1.6:
            pygame.draw.rect(display, (0, 0, 0), (805, 0, 395, SCREEN[1]))
            pygame.draw.line(display, (255, 255, 255), (1200, 0), (1200, 800), 10)

    if submenu == 1:
        print_text("CONTROLS", (850 + offx, 50 + offy), 100)
        print_text("BACK", (850 + offx, 150 + offy), 50)
        print_text("Thrust Key", (850 + offx, 250 + offy), 30)
        if changing == 0:
            print_button(config[0], (850 + offx, 285 + offy), 20, False)
        else:
            print_button(config[0], (850 + offx, 285 + offy), 20, True)
        print_text("Weapon 1 key", (850 + offx, 320 + offy), 30)
        if changing == 1:
            print_button(config[1], (850 + offx, 355 + offy), 20, False)
        else:
            print_button(config[1], (850 + offx, 355 + offy), 20, True)
        print_text("Weapon 2 key", (850 + offx, 390 + offy), 30)
        if changing == 2:
            print_button(config[2], (850 + offx, 425 + offy), 20, False)
        else:
            print_button(config[2], (850 + offx, 425 + offy), 20, True)
        print_text("Weapon 3 key", (850 + offx, 460 + offy), 30)
        if changing == 3:
            print_button(config[3], (850 + offx, 495 + offy), 20, False)
        else:
            print_button(config[3], (850 + offx, 495 + offy), 20, True)
        print_text("Pause key", (850 + offx, 530 + offy), 30)
        if changing == 4:
            print_button(config[4], (850 + offx, 565 + offy), 20, False)
        else:
            print_button(config[4], (850 + offx, 565 + offy), 20, True)

        if config[5]:
            print_text("Scroll weapon key", (850 + offx, 600 + offy), 30)
            if changing == 5:
                print_button(config[6], (850 + offx, 635 + offy), 20, False)
            else:
                print_button(config[6], (850 + offx, 635 + offy), 20, True)
            
        for i in range(6):
            if i != 5 or config[5]:
                print_text("CHANGE", (950 + offx, 285 + offy + (i * 70)), 20)
                if check_position(mousex, mousey, 950 + offx, 995 + offx, 285 + offy + (i * 70), 305 + offy + (i * 70)) and changing == -1:
                    print_button("CHANGE", (950 + offx, 280 + offy + (i * 70)), 30, True)
                    if mouse[0]:
                        changing = i

        if changing != -1:
            index = changing
            if changing == 5:
                index = 6
            old = config[index]
            if get_pressed_string(True) != "NULL":
                config[index] = get_pressed_string(True)
                changing = -1
            elif check_position(mousex, mousey, 850 + offx, 895 + offx, 285 + offy + (changing * 70), 305 + offy + (changing * 70)):
                if mouse[0]:
                    config[index] = "MOUSE1"
                    changing = -1
                elif mouse[1]:
                    config[index] = "MOUSE3"
                    changing = -1
                elif mouse[2]:
                    config[index] = "MOUSE2"
                    changing = -1

            if changing == -1:
                exist = False
                for i in range(len(config)):
                    if i != index:
                        if config[index] == config[i]:
                            exist = True
                if exist:
                    config[index] = old
                    temp_message = "key already in use"

        print_text("Scroll weapon", (1030 + offx, 250 + offy), 30)
        print_text("select", (1030 + offx, 280 + offy), 30)
        pygame.draw.line(display, (255, 255, 255), (1050 + offx, 330 + offy), (1080 + offx, 330 + offy), 5)
        pygame.draw.line(display, (255, 255, 255), (1080 + offx, 330 + offy), (1080 + offx, 360 + offy), 5)
        pygame.draw.line(display, (255, 255, 255), (1050 + offx, 360 + offy), (1080 + offx, 360 + offy), 5)
        pygame.draw.line(display, (255, 255, 255), (1050 + offx, 330 + offy), (1050 + offx, 360 + offy), 5)
        if config[5]:
            pygame.draw.line(display, (255, 255, 255), (1050 + offx, 330 + offy), (1080 + offx, 360 + offy), 5)
            pygame.draw.line(display, (255, 255, 255), (1080 + offx, 330 + offy), (1050 + offx, 360 + offy), 5)
        if check_position(mousex, mousey, 1050 + offx, 1080 + offx, 330 + offy, 360 + offy):
            if mouse[0] and held2 == False:
                config[5] = not config[5]
                held2 = True

        if held2:
            if mouse[0] == False:
                held2 = False

        if check_position(mousex, mousey, 850 + offx, 925 + offx, 150 + offy, 200 + offy):
            print_button("BACK", (850 + offx, 140 + offy), 70, True)
            if mouse[0]:
                submenu = 0

    if submenu == 2:
        print_text("UI", (850 + offx, 50 + offy), 100)
        print_text("BACK", (850 + offx, 150 + offy), 50)

        if check_position(mousex, mousey, 850 + offx, 925 + offx, 150 + offy, 200 + offy):
            print_button("BACK", (850 + offx, 140 + offy), 70, True)
            if mouse[0]:
                submenu = 0

        print_text("Advanced UI", (850 + offx, 250 + offy), 30)
        pygame.draw.line(display, (255, 255, 255), (850 + offx, 300 + offy), (880 + offx, 300 + offy), 5)
        pygame.draw.line(display, (255, 255, 255), (880 + offx, 300 + offy), (880 + offx, 330 + offy), 5)
        pygame.draw.line(display, (255, 255, 255), (850 + offx, 330 + offy), (880 + offx, 330 + offy), 5)
        pygame.draw.line(display, (255, 255, 255), (850 + offx, 300 + offy), (850 + offx, 330 + offy), 5)
        if config[7]:
            pygame.draw.line(display, (255, 255, 255), (850 + offx, 300 + offy), (880 + offx, 330 + offy), 5)
            pygame.draw.line(display, (255, 255, 255), (880 + offx, 300 + offy), (850 + offx, 330 + offy), 5)
        if check_position(mousex, mousey, 850 + offx, 880 + offx, 300 + offy, 330 + offy):
            if mouse[0] and held2 == False:
                config[7] = not config[7]
                held2 = True

        print_text("Backdrop", (850 + offx, 400 + offy), 30)
        pygame.draw.line(display, (255, 255, 255), (850 + offx, 450 + offy), (880 + offx, 450 + offy), 5)
        pygame.draw.line(display, (255, 255, 255), (880 + offx, 450 + offy), (880 + offx, 480 + offy), 5)
        pygame.draw.line(display, (255, 255, 255), (850 + offx, 480 + offy), (880 + offx, 480 + offy), 5)
        pygame.draw.line(display, (255, 255, 255), (850 + offx, 450 + offy), (850 + offx, 480 + offy), 5)
        if config[8]:
            pygame.draw.line(display, (255, 255, 255), (850 + offx, 450 + offy), (880 + offx, 480 + offy), 5)
            pygame.draw.line(display, (255, 255, 255), (880 + offx, 450 + offy), (850 + offx, 480 + offy), 5)
        if check_position(mousex, mousey, 850 + offx, 880 + offx, 450 + offy, 480 + offy):
            if mouse[0] and held2 == False:
                config[8] = not config[8]
                held2 = True

        if held2:
            if mouse[0] == False:
                held2 = False

def pause_menu(ingame):
    global state, held, temp_message, saved, menu_button, settings, submenu

    if held:
        if get_control(4) == False:
            held = False
    
    if ingame:
        gameplay_UI()
    pygame.draw.rect(display, (0, 0, 0), (0, 0, 400, SCREEN[1]))
    pygame.draw.line(display, (255, 255, 255), (400, 0), (400, 800), 10)
    print_text("PAUSE", (50, 50), 100)
    print_text("BACK", (50, 200), 50)
    print_text("SETTINGS", (50, 300), 50)
    print_text("SAVE GAME", (50, 400), 50)
    print_text("MAIN MENU", (50, 500), 50)

    if settings:
        settings_menu()
    
    if get_control(4) and held == False:
        held = True
        settings = False
        if ingame:
            state = 1
        else:
            state = 2
    if check_position(mousex, mousey, 50, 125, 200, 250):
        print_button("BACK", (50, 190), 70, True)
        if mouse[0]:
            settings = False
            if ingame:
                state = 1
            else:
                state = 2
    if check_position(mousex, mousey, 50, 210, 300, 350):
        print_button("SETTINGS", (50, 290), 70, True)
        if mouse[0]:
            settings = True
            submenu = 0
        
    if check_position(mousex, mousey, 50, 225, 400, 450):
        print_button("SAVE GAME", (50, 390), 70, True)
        if mouse[0]:
            save_game(0)
            temp_message = "game saved"
            saved = True
            menu_button = False

    if menu_button:
        print_text("YOUR GAME WILL NOT SAVE", (0, 560), 40)
        print_text("ARE YOU SURE?", (50, 600), 40)
        print_text("YES", (90, 650), 40)
        print_text("NO", (170, 650), 40)
    if check_position(mousex, mousey, 90, 135, 650, 690) and menu_button:
        print_button("YES", (90, 645), 50, True)
        if mouse[0]:
            held = True
            settings = False
            state = 0
            
    if check_position(mousex, mousey, 170, 200, 650, 690) and menu_button:
        print_button("NO", (170, 645), 50, True)
        if mouse[0]:
            menu_button = False
        
    if check_position(mousex, mousey, 50, 225, 500, 550):
        print_button("MAIN MENU", (50, 490), 70, True)
        if mouse[0]:
            if saved == False:
                menu_button = True
            else:
                held = True
                settings = False
                state = 0

def get_inventory_quantities():
    quantity = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for i in range(len(ship_inventory)):
        value = ship_inventory[i]
        quantity[value] = quantity[value] + 1
    return quantity

def get_pressed_string(first):
    array = []
    for i in range(len(keys)):
        if keys[i] and i != 8 and i != 9 and i != 13 and i != 27:
            array.append(chr(i))
    if keys[8]:
        array.append("backspace")
    if keys[9]:
        array.append("tab")
    if keys[13]:
        array.append("enter")
    if keys[27]:
        array.append("escape")

    if keys[pygame.K_UP]:
        array.append("up")
    if keys[pygame.K_DOWN]:
        array.append("down")
    if keys[pygame.K_RIGHT]:
        array.append("right")
    if keys[pygame.K_LEFT]:
        array.append("left")
    if keys[pygame.K_CAPSLOCK]:
        array.append("capslock")
    if keys[pygame.K_LCTRL]:
        array.append("lctrl")
    if keys[pygame.K_LSHIFT]:
        array.append("lshift")
    if keys[pygame.K_LALT]:
        array.append("lalt")
        
    if first:
        try:
            return array[0]
        except:
            return "NULL"
    else:
        return array

def assign_ship(shipID):
    if shipID == 0:
        ship = ship0
    elif shipID == 1:
        ship = ship1
    elif shipID == 2:
        ship = ship2
    elif shipID == 3:
        ship = ship3
    elif shipID == 4:
        ship = ship4
    elif shipID == 5:
        ship = ship5
    elif shipID == 6:
        ship = ship6
    elif shipID == 7:
        ship = ship7
    elif shipID == 8:
        ship = ship8
    elif shipID == 9:
        ship = ship9
    elif shipID == 10:
        ship = ship10
    elif shipID == 11:
        ship = ship11
    elif shipID == 12:
        ship = ship12
    return ship

def assign_weapon(value):
    if value == 1:
        weap = weapon1
    elif value == 2:
        weap = weapon2
    elif value == 3:
        weap = weapon3
    elif value == 4:
        weap = weapon4
    elif value == 5:
        weap = weapon5
    elif value == 6:
        weap = weapon6
    elif value == 7:
        weap = weapon7
    elif value == 8:
        weap = weapon8
    elif value == 9:
        weap = weapon9
    elif value == 10:
        weap = weapon10
    elif value == 11:
        weap = weapon11
    elif value == 12:
        weap = weapon12
    elif value == 13:
        weap = weapon13
    elif value == 14:
        weap = weapon14
    elif value == 15:
        weap = weapon15
    elif value == 16:
        weap = weapon16
    elif value == 17:
        weap = weapon17
    elif value == 18:
        weap = weapon18
    return weap

def assign_asteroid(num):
    if num == 0:
        asteroid = asteroid0
    if num == 1:
        asteroid = asteroid1
    if num == 2:
        asteroid = asteroid2
    if num == 3:
        asteroid = asteroid3
    if num == 4:
        asteroid = asteroid4
    if num == 5:
        asteroid = asteroid5
    if num == 6:
        asteroid = asteroid6
    if num == 7:
        asteroid = asteroid7
    return asteroid

def assign_alien(num):
    if num == 0:
        alien = alien0
    if num == 1:
        alien = alien1
    if num == 2:
        alien = alien2
    if num == 3:
        alien = alien3
    return alien

def assign_item(num):
    if num == 0:
        item = item0
    if num == 1:
        item = item1
    if num == 2:
        item = item2
    if num == 3:
        item = item3
    if num == 4:
        item = item4
    if num == 5:
        item = item5
    if num == 6:
        item = item6
    if num == 7:
        item = item7
    if num == 8:
        item = item8
    if num == 9:
        item = item9
    return item

def define_loop():
    global state, ship, direction_vect, move_vect, thrust_vect, change, ship_shield, laser, laser_position, astent, alient, projent, aprojent, itement, index, shield_delay, iframes, weapon_delay, weapon_charge, weapon_select, weapon_1, weapon_2, weapon_3

    ship = assign_ship(current_ship[0])
    for i in range(1, 4):
        value = current_ship[i]
        if value == 0:
            weap = 0
        else:
            weap = assign_weapon(value)

        if i == 1:
            if weap != 0:
                weapon_1 = weap
            else:
                weapon_1 = 0
        if i == 2:
            if weap != 0:
                weapon_2 = weap
            else:
                weapon_2 = 0
        if i == 3:
            if weap != 0:
                weapon_3 = weap
            else:
                weapon_3 = 0
                
    
    if ship_position == [0, 0]:
        define_station()
        state = 2
    else:
        direction_vect = [0, 0]
        try:
            if move_vect != [0, 1]:
                move_vect = [0, 0]
        except:
            move_vect = [0, 0]
        thrust_vect = [0, 0]
        change = [0, 0]
        ship_shield = ship.shield
        shield_delay = 0
        iframes = 0
        state = 1
        laser = [False, False, False]
        laser_position = [0, 0]

        astent = []
        loop = True
        index = 0
        num = 0
        while loop:
            index = index + 1
            asteroid = assign_asteroid(num)
            if index <= asteroid.frequency:
                pos = [random.randint(-5000, 5000), random.randint(1000, 11000)]
                randx = random.randint(-100, 100)
                randy = random.randint(-100, 100)
                if randx == 0:
                    randx = 1
                if randy == 0:
                    randy = 1
                vect = get_thrust([randx, randy], asteroid.speed)
                astent.append([pos, vect, asteroid])
            else:
                index = 0
                num = num + 1
                if num == 8:
                    loop = False
            
        alient = []
        for i in range(alien0.frequency):
            pos = [random.randint(-5000, 5000), random.randint(1000, 11000)]
            randx = random.randint(-100, 100)
            randy = random.randint(-100, 100)
            if randx == 0:
                randx = 1
            if randy == 0:
                randy = 1
            vect = get_thrust([randx, randy], alien0.speed)
            alient.append([pos, vect, alien0, alien0.health, 0])
        for i in range(alien1.frequency + alien2.frequency + alien3.frequency):
            if i <= alien1.frequency:
                alien = alien1
            elif i <= alien1.frequency + alien2.frequency:
                alien = alien2
            else:
                alien = alien3
            pos = [random.randint(-5000, 5000), random.randint(11000, 21000)]
            randx = random.randint(-100, 100)
            randy = random.randint(-100, 100)
            if randx == 0:
                randx = 1
            if randy == 0:
                randy = 1
            vect = get_thrust([randx, randy], alien.speed)
            alient.append([pos, vect, alien, alien.health, 0])
            
        projent = []
        aprojent = []
        itement = []
        index = 0
        weapon_delay = [0, 0, 0]
        weapon_charge = [0, 0, 0]
        if config[5]:
            weapon_select = 1
        else:
            weapon_select = 0
        
def get_magnitude(vect):
    return math.sqrt((vect[0]**2) + (vect[1]**2))

def angle_calc(vect1, vect2, negative):
    try:
        top = (vect1[0] * vect2[0]) + (vect1[1] * vect2[1])
        bottom = (get_magnitude(vect1) * get_magnitude(vect2))
        angle = round(math.degrees(math.acos(top / bottom)))
        if vect1[0] > 0 and negative:
            angle = -angle
    except:
        angle = 0
    return angle

def get_thrust(vect, speed):
    length = get_magnitude(vect)
    length = length / speed
    thrust = [vect[0] / length, vect[1] / length]
    return thrust

def calc_vect(vectA, vectB, step):
    vectC = [0, 0]
    leng = math.sqrt((vectA[0] - vectB[0])**2 + (vectA[1] - vectB[1])**2)
    if leng <= 1:
        vectC = vectB
    else:
        vectC[0] = (vectA[0] * ((leng - step) / leng)) + (vectB[0] * (step / leng))
        vectC[1] = (vectA[1] * ((leng - step) / leng)) + (vectB[1] * (step / leng))
    return vectC

def ship_damage(damage, regen):
    global ship_health, ship_shield, iframes
    if regen:
        ship_shield = ship.shield
    else:
        if iframes <= index:
            if ship_shield > 0:
                ship_shield = ship_shield - damage
                if ship_shield < 0:
                    ship_shield = 0
            else:
                ship_health = ship_health - damage
                if ship_health <= 0:
                    return 0, True
                
    if damage > 0 and ship_health > 0:
        iframes = index + IFRAME_NUM
        return index + SHIELD_REGEN, False
    
def get_control(x):
    if config[x] == "MOUSE1":
        return mouse[0]
    elif config[x] == "MOUSE2":
        return mouse[2]
    elif config[x] == "MOUSE3":
        return mouse[1]
    else:
        try:
            return keys[pygame.key.key_code(config[x])]
        except:
            return keys[pygame.K_RETURN]
        

def game_loop():
    global index, state, temp_message, ship, thrust, direction_vect, move_vect, thrust_vect, change, ship_ammo, ship_fuel, ship_position, ship_sprite, ship_thrust_sprite, weapon_delay, weapon_charge, weapon_select, shield_delay, held, held2, saved, menu_button

    index = index + 1
    
    direction_vect = [mousex - ship_position[0] + change[0], mousey - ship_position[1] + change[1]]

    #ship movement
    thrust = False
    if get_control(0) and ship_fuel > 0:
        thrust_vect = get_thrust(direction_vect, ship.speed)
        move_vect = calc_vect(move_vect, thrust_vect, ship.accel)
        thrust = True
        ship_fuel = ship_fuel - (THRUST_CONSUMPTION * ship.accel)

    #fire weapons
    if (config[5] == False and get_control(1)) or (weapon_select == 1 and get_control(6)) and current_ship[1] != 0:
        if(weapon_delay[0] <= index or weapon_charge[0] > index) and (weapon_1.velocity != -1 or ship_fuel > 0):
            if weapon_1.delay < 0 and (weapon_charge[0] > index or weapon_charge[0] == 0):
                fire = False
                if weapon_charge[0] == 0:
                    weapon_charge[0] = index + CHARGE_TIME
            else:
                fire = True
                
            if fire:
                delay = fire_weapon(weapon_1, 0, False)
                weapon_delay[0] = delay + index
                if weapon_1.delay < 0:
                    weapon_charge[0] = 1000000000
    else:
        laser[0] = False
        weapon_charge[0] = 0
        
    if (config[5] == False and get_control(2)) or (weapon_select == 2 and get_control(6)) and current_ship[2] != 0:
        if(weapon_delay[1] <= index or weapon_charge[1] > index) and (weapon_2.velocity != -1 or ship_fuel > 0):
            if weapon_2.delay < 0 and (weapon_charge[1] > index or weapon_charge[1] == 0):
                fire = False
                if weapon_charge[1] == 0:
                    weapon_charge[1] = index + CHARGE_TIME
            else:
                fire = True
            if fire:
                delay = fire_weapon(weapon_2, 1, False)
                weapon_delay[1] = delay + index
                if weapon_2.delay < 0:
                    weapon_charge[1] = 1000000000
    else:
        laser[1] = False
        weapon_charge[1] = 0
        
    if (config[5] == False and get_control(3)) or (weapon_select == 3 and get_control(6)) and current_ship[3] != 0:
        if(weapon_delay[2] <= index or weapon_charge[2] > index) and (weapon_3.velocity != -1 or ship_fuel > 0):
            if weapon_3.delay < 0 and (weapon_charge[2] > index or weapon_charge[2] == 0):
                fire = False
                if weapon_charge[2] == 0:
                    weapon_charge[2] = index + CHARGE_TIME
            else:
                fire = True
            if fire:
                delay = fire_weapon(weapon_3, 2, False)
                weapon_delay[2] = delay + index
                if weapon_3.delay < 0:
                    weapon_charge[2] = 1000000000
    else:
        laser[2] = False
        weapon_charge[2] = 0

    #laser consume fuel
    if laser[0]:
        if weapon_1.size != 1:
            size = weapon_1.size * 0.7
        else:
            size = weapon_1.size
        ship_fuel = ship_fuel - (LASER_CONSUMPTION * size)
    if laser[1]:
        if weapon_2.size != 1:
            size = weapon_2.size * 0.7
        else:
            size = weapon_2.size
        ship_fuel = ship_fuel - (LASER_CONSUMPTION * size)
    if laser[2]:
        if weapon_3.size != 1:
            size = weapon_3.size * 0.7
        else:
            size = weapon_3.size
        ship_fuel = ship_fuel - (LASER_CONSUMPTION * size)

    if ship_fuel < 0:
        ship_fuel = 0

    #scroll wheel change weapons
    if config[5]:
        old = weapon_select
        weapon_select = weapon_select - scroll
        if weapon_select > 3:
            weapon_select = 1
        if weapon_select < 1:
            weapon_select = 3
        if ship_ammo[weapon_select - 1] == 0:
            weapon_select = old

    #ship sprite rotated and changed if thrust
    angle = angle_calc(direction_vect, [0, -100], True)
    ship_sprite = pygame.transform.rotate(ship.sprite, angle)
    ship_thrust_sprite = pygame.transform.rotate(ship.thrust_sprite, angle)

    #ship_position updated
    ship_position = [ship_position[0] + move_vect[0], ship_position[1] + move_vect[1]]
    
    #CHANGE
    change = [ship_position[0] - (SCREEN[0] / 2), ship_position[1] - (SCREEN[1] / 2)]

    #space station menu
    if check_position(ship_position[0], ship_position[1], -200, 200, -500, 0):
        define_station()
        display = pygame.display.set_mode()
        print_text("SPACE STATION", (50, 0), 100)
        print_text("DOCKING...", (100, 200), 50)
        pygame.display.update()
        display = pygame.display.set_mode()
        pygame.time.delay(1000)
        state = 2

    #self destruct
    if ship_fuel == 0:
        temp_message = "///Out of fuel - press ESC to self destruct///"
        if keys[pygame.K_ESCAPE]:
            state = 3

    #pause menu
    if held:
        if get_control(4) == False:
            held = False

    if ((get_control(4) and held == False) or (check_position(mousex, mousey, 10, 200, 10, 100) and mouse[0])) and state != 3:
        state = 1.5
        held = True
        saved = False
        menu_button = False

    #shield regen
    if shield_delay == index:
        ship_damage(0, True)

    #other processes
    move_entities()

    dead = collision_detection()
    if dead:
        state = 3

    gameplay_UI()

    if mousex < 200 and config[7]:
        manage_inventory()

def fire_weapon(weapon, i, isAlien):
    global projent, laser, aprojent
    if isAlien:
        bullet_vect = get_thrust([ship_position[0] - alient[i][0][0], ship_position[1] - alient[i][0][1]], weapon.velocity)
        bullet_position = alient[i][0]
        aprojent.append([bullet_position, bullet_vect, weapon])
        return weapon.delay
    else:
        if weapon != 0 and ship_ammo[i] > 0:
            if weapon.velocity == -1:
                laser[i] = True
                return 0
            else:
                bullet_vect = get_thrust(direction_vect, weapon.velocity)
                bullet_position = ship_position
                projent.append([bullet_position, bullet_vect, weapon])
                ship_ammo[i] = ship_ammo[i] - 1
                if weapon.delay < 0:
                    return -weapon.delay
                else:
                    return weapon.delay
        else:
            return 0
        
def move_entities():
    global astent, projent, alient
    #move asteroids
    for i in range(len(astent)):
        pos = astent[i][0]
        vect = astent[i][1]
        pos = [pos[0] + vect[0], pos[1] + vect[1]]
        if pos[0] >= -5000:
            vect[0] = -vect[0]
        if pos[0] <= 5000:
            vect[0] = -vect[0]
        if pos[1] >= 1000:
            vect[1] = -vect[1]
        if pos[1] <= 11000:
            vect[1] = -vect[1]
        astent[i] = [pos, vect, astent[i][2]]

    #move aliens
    for i in range(len(alient)):
        pos = alient[i][0]
        vect = alient[i][1]
        pos = [pos[0] + vect[0], pos[1] + vect[1]]
        if check_position(pos[0] - change[0], pos[1] - change[1], -200, SCREEN[0] + 200, -200, SCREEN[1] + 200) == False and index % ALIEN_RANDOM == 0:
            randx = random.randint(-100, 100)
            randy = random.randint(-100, 100)
            if randx == 0:
                randx = 1
            if randy == 0:
                randy = 1
            vect = get_thrust([randx, randy], alient[i][2].speed)
        
        elif check_position(pos[0] - change[0], pos[1] - change[1], 0, SCREEN[0], 0, SCREEN[1]):
            if index % ALIEN_RANDOM_AGRO == 0:
                x1 = round(ship_position[0] - ALIEN_AGRO / 2)
                x2 = round(ship_position[0] + ALIEN_AGRO / 2)
                y1 = round(ship_position[1] - ALIEN_AGRO / 2)
                y2 = round(ship_position[1] + ALIEN_AGRO / 2)
                new_pos = [random.randint(x1, x2), random.randint(y1, y2)]
                vect = get_thrust([new_pos[0] - pos[0], new_pos[1] - pos[1]], alient[i][2].speed)
            if alient[i][4] <= index:
                delay = fire_weapon(alient[i][2], i, True)
                alient[i][4] = delay + index

        if alient[i][2].ID == 0:
            if pos[0] >= -5000:
                vect[0] = -vect[0]
            if pos[0] <= 5000:
                vect[0] = -vect[0]
            if pos[1] >= 1000:
                vect[1] = -vect[1]
            if pos[1] <= 11000:
                vect[1] = -vect[1]
        elif alient[i][2].ID == 1:
            if pos[0] >= -5000:
                vect[0] = -vect[0]
            if pos[0] <= 5000:
                vect[0] = -vect[0]
            if pos[1] >= 1000:
                vect[1] = -vect[1]
            if pos[1] <= 21000:
                vect[1] = -vect[1]
        else:
            if pos[0] >= -5000:
                vect[0] = -vect[0]
            if pos[0] <= 5000:
                vect[0] = -vect[0]
            if pos[1] >= 11000:
                vect[1] = -vect[1]
            if pos[1] <= 21000:
                vect[1] = -vect[1]   

        alient[i][0] = pos
        alient[i][1] = vect

    #move ship and alien projectiles
    for j in range(2):
        if j == 0:
            array = projent
        elif j == 1:
            array = aprojent
        remove = []
        for i in range(len(array)):
            try:
                pos = array[i][0]
                vect = array[i][1]
                pos = [pos[0] + vect[0], pos[1] + vect[1]]
                if check_position(pos[0] - change[0], pos[1] - change[1], 0, SCREEN[0], 0, SCREEN[1]):
                    array[i][0] = pos
                else:
                    array.pop(i)
            except:
                pass

def collision_detection():
    global astent, projent, aprojent, itement, ship_inventory, move_vect, shield_delay, laser_position
    
    dead = False

    def spawn_items(pos, item_list):
        global itement
        for i in range(random.randint(1, 3)):
            num = random.randint(1, 6)
            if num < 4:
                index = 0
            elif num == 4 or num == 5:
                index = 1
            else:
                index = 2
            itement.append([[pos[0] + random.randint(-50, 50), pos[1] + random.randint(-50, 50)], assign_item(item_list[index])])

    def ss_hitbox(x1, x2, y1, y2):
        collide = False
        if check_position(ship_position[0] - (ship.hitbox / 2), ship_position[1] - (ship.hitbox / 2), x1, x2, y1, y2):
            collide = True
        elif check_position(ship_position[0] + (ship.hitbox / 2), ship_position[1] - (ship.hitbox / 2), x1, x2, y1, y2):
            collide = True
        elif check_position(ship_position[0] - (ship.hitbox / 2), ship_position[1] + (ship.hitbox / 2), x1, x2, y1, y2):
            collide = True
        elif check_position(ship_position[0] + (ship.hitbox / 2), ship_position[1] + (ship.hitbox / 2), x1, x2, y1, y2):
            collide = True
        return collide

    def ss_hitbox_invert(x1, x2, y1, y2):
        collide = False
        if check_position(x1, y1, ship_position[0] - (ship.hitbox / 2), ship_position[0] + (ship.hitbox / 2), ship_position[1] - (ship.hitbox / 2), ship_position[1] + (ship.hitbox / 2)):
            collide = True
        elif check_position(x1, y2, ship_position[0] - (ship.hitbox / 2), ship_position[0] + (ship.hitbox / 2), ship_position[1] - (ship.hitbox / 2), ship_position[1] + (ship.hitbox / 2)):
            collide = True
        elif check_position(x2, y1, ship_position[0] - (ship.hitbox / 2), ship_position[0] + (ship.hitbox / 2), ship_position[1] - (ship.hitbox / 2), ship_position[1] + (ship.hitbox / 2)):
            collide = True
        elif check_position(x2, y2, ship_position[0] - (ship.hitbox / 2), ship_position[0] + (ship.hitbox / 2), ship_position[1] - (ship.hitbox / 2), ship_position[1] + (ship.hitbox / 2)):
            collide = True
        return collide
            
    #check ship with space station
    if check_position(ship_position[0], ship_position[1], -750, 750, -1450, 500):
        hitbox_size = 10
        right = 480
        left = -480
        top = -1200
        bottom = 130
        bottom_image = 300
        entry_width = 400
        entry_depth = 500
        #left
        if ss_hitbox(left, left + hitbox_size, top, bottom):
            move_vect = [-move_vect[0], move_vect[1]]
        #right
        if ss_hitbox(right - hitbox_size, right, top, bottom):
            move_vect = [-move_vect[0], move_vect[1]]
        #top
        if ss_hitbox(left, right, top, top + hitbox_size):
            move_vect = [move_vect[0], -move_vect[1]]
        #left bottom
        if ss_hitbox(left, -(entry_width / 2), bottom - hitbox_size, bottom):
            move_vect = [move_vect[0], -move_vect[1]]
        #right bottom
        if ss_hitbox((entry_width / 2), right, bottom - hitbox_size, bottom):
            move_vect = [move_vect[0], -move_vect[1]]
        #entry left
        if ss_hitbox(-(entry_width / 2) - hitbox_size, -(entry_width / 2), bottom_image - entry_depth, bottom_image):
            move_vect = [-move_vect[0], move_vect[1]]
        #entry right
        if ss_hitbox((entry_width / 2), (entry_width / 2) + hitbox_size, bottom_image - entry_depth, bottom_image):
            move_vect = [-move_vect[0], move_vect[1]]
        #entry back
        if ss_hitbox(-(entry_width / 2), (entry_width / 2), bottom_image - entry_depth - hitbox_size, bottom_image - entry_depth):
            move_vect = [move_vect[0], -move_vect[1]]
        #left front
        if ss_hitbox_invert(-(entry_width / 2) - hitbox_size, -(entry_width / 2), bottom_image, bottom_image + hitbox_size):
            move_vect = [move_vect[0], -move_vect[1]]
        #right front
        if ss_hitbox_invert((entry_width / 2), (entry_width / 2) + hitbox_size, bottom_image, bottom_image + hitbox_size):
            move_vect = [move_vect[0], -move_vect[1]]

        
        
    #check ship with asteroid
    for i in range(len(astent)):
        try:
            if check_position(astent[i][0][0] - change[0], astent[i][0][1] - change[1], -265, SCREEN[0] + 265, -265, SCREEN[1] + 265):
                radius_vect = get_thrust([astent[i][0][0] - ship_position[0], astent[i][0][1] - ship_position[1]], astent[i][2].hitbox)
                point = [astent[i][0][0] - radius_vect[0], astent[i][0][1] - radius_vect[1]]
                x1 = ship_position[0] - (ship.hitbox / 2)
                x2 = ship_position[0] + (ship.hitbox / 2)
                y1 = ship_position[1] - (ship.hitbox / 2)
                y2 = ship_position[1] + (ship.hitbox / 2)
                if check_position(point[0], point[1], x1, x2, y1, y2):
                    magnitude = get_magnitude(move_vect)
                    normal_vect = [ship_position[0] - astent[i][0][0], ship_position[1] - astent[i][0][1]]
                    angle1 = angle_calc(normal_vect, move_vect, False)
                    angle2 = angle_calc(normal_vect, [0, -100], False)
                    angle3 = angle2 - angle1
                    if normal_vect[0] > 0:
                        angle3 = -angle3
                    angle3 = math.radians(angle3)
                    heading_vect = [math.sin(angle3), -(math.cos(angle3))]
                    move_vect = get_thrust(heading_vect, magnitude / 2)
                    astent[i][1] = get_thrust([-normal_vect[0], -normal_vect[1]], astent[i][2].speed)

                    shield_delay, dead = ship_damage(round(magnitude * DAMAGE_MULTIPLIER), False)           
        except:
            pass

    #check ships with alien
    for i in range(len(alient)):
        try:
            if check_position(alient[i][0][0] - change[0], alient[i][0][1] - change[1], -200, SCREEN[0] + 200, -200, SCREEN[1] + 200):
                collide = False
                x1 = alient[i][0][0] - (alient[i][2].hitbox / 2)
                x2 = alient[i][0][0] + (alient[i][2].hitbox / 2)
                y1 = alient[i][0][1] - (alient[i][2].hitbox / 2)
                y2 = alient[i][0][1] + (alient[i][2].hitbox / 2)
                if check_position(ship_position[0] - (ship.hitbox / 2), ship_position[1] - (ship.hitbox / 2), x1, x2, y1, y2):
                    collide = True
                elif check_position(ship_position[0] + (ship.hitbox / 2), ship_position[1] - (ship.hitbox / 2), x1, x2, y1, y2):
                    collide = True
                elif check_position(ship_position[0] - (ship.hitbox / 2), ship_position[1] + (ship.hitbox / 2), x1, x2, y1, y2):
                    collide = True
                elif check_position(ship_position[0] + (ship.hitbox / 2), ship_position[1] + (ship.hitbox / 2), x1, x2, y1, y2):
                    collide = True

                if collide == False:
                    x1 = ship_position[0] - (ship.hitbox / 2)
                    x2 = ship_position[0] + (ship.hitbox / 2)
                    y1 = ship_position[1] - (ship.hitbox / 2)
                    y2 = ship_position[1] + (ship.hitbox / 2)
                    if check_position(alient[i][0][0] - (alient[i][2].hitbox / 2), alient[i][0][1] - (alient[i][2].hitbox / 2), x1, x2, y1, y2):
                        collide = True
                    elif check_position(alient[i][0][0] + (alient[i][2].hitbox / 2), alient[i][0][1] - (alient[i][2].hitbox / 2), x1, x2, y1, y2):
                        collide = True
                    elif check_position(alient[i][0][0] - (alient[i][2].hitbox / 2), alient[i][0][1] + (alient[i][2].hitbox / 2), x1, x2, y1, y2):
                        collide = True
                    elif check_position(alient[i][0][0] + (alient[i][2].hitbox / 2), alient[i][0][1] + (alient[i][2].hitbox / 2), x1, x2, y1, y2):
                        collide = True

                if collide:
                    magnitude = get_magnitude(move_vect)
                    normal_vect = [ship_position[0] - alient[i][0][0], ship_position[1] - alient[i][0][1]]
                    angle1 = angle_calc(normal_vect, move_vect, False)
                    angle2 = angle_calc(normal_vect, [0, 100], False)
                    angle3 = angle2 - angle1
                    if normal_vect[0] > 0:
                        angle3 = -angle3
                    angle3 = math.radians(angle3)
                    heading_vect = [math.sin(angle3), -(math.cos(angle3))]
                    move_vect = get_thrust(heading_vect, magnitude / 2)
                    alient[i][1] = get_thrust([-normal_vect[0], -normal_vect[1]], astent[i][2].speed)

                    shield_delay, dead = ship_damage(round(magnitude * DAMAGE_MULTIPLIER), False)
        except:
            pass

    #check ship projectiles with asteroids
    for i in range(len(astent)):
        try:
            if check_position(astent[i][0][0] - change[0], astent[i][0][1] - change[1], -265, SCREEN[0] + 265, -265, SCREEN[1] + 265):
                for j in range(len(projent)):
                    try:
                        if get_magnitude([projent[j][0][0] - astent[i][0][0], projent[j][0][1] - astent[i][0][1]]) <= astent[i][2].hitbox:
                            if astent[i][2].size <= projent[j][2].asteroid:
                                if astent[i][2].size != 1:
                                    asteroid = assign_asteroid(astent[i][2].size - 2)
                                    angle1 = angle_calc(projent[j][1], [0, -100], False)
                                    angle2 = angle1 - 90
                                    angle2 = math.radians(angle2)
                                    heading_vect = [math.sin(angle2), -(math.cos(angle2))]
                                    astent.append([astent[i][0], get_thrust(heading_vect, asteroid.speed), asteroid])
                                    astent.append([astent[i][0], get_thrust([-heading_vect[0], -heading_vect[1]], asteroid.speed), asteroid])
                                spawn_items(astent[i][0], astent[i][2].item)
                                astent.pop(i)
                            projent.pop(j)
                    except:
                        pass
        except:
            pass

    #check ship projectiles with aliens
    for i in range(len(alient)):
        try:
            if check_position(alient[i][0][0] - change[0], alient[i][0][1] - change[1], -200, SCREEN[0] + 200, -200, SCREEN[1] + 200):
                for j in range(len(projent)):
                    try:
                        if check_position(projent[j][0][0], projent[j][0][1], alient[i][0][0] - (alient[i][2].hitbox) / 2, alient[i][0][0] + (alient[i][2].hitbox) / 2, alient[i][0][1] - (alient[i][2].hitbox) / 2, alient[i][0][1] + (alient[i][2].hitbox) / 2):
                            alient[i][3] = alient[i][3] - projent[j][2].damage
                            if alient[i][3] <= 0:
                                spawn_items(alient[i][0], alient[i][2].item)
                                alient.pop(i)
                            projent.pop(j)
                    except:
                        pass
        except:
            pass

    #check alien projectiles with asteroids
    for i in range(len(astent)):
        try:
            if check_position(astent[i][0][0] - change[0], astent[i][0][1] - change[1], -265, SCREEN[0] + 265, -265, SCREEN[1] + 265):
                for j in range(len(aprojent)):
                    try:
                        if get_magnitude([aprojent[j][0][0] - astent[i][0][0], aprojent[j][0][1] - astent[i][0][1]]) <= astent[i][2].hitbox:
                            aprojent.pop(j)
                    except:
                        pass
        except:
            pass

    #check alien projectiles with ship
    for i in range(len(aprojent)):
        try:
            if check_position(aprojent[i][0][0], aprojent[i][0][1], ship_position[0] - (ship.hitbox / 2), ship_position[0] + (ship.hitbox / 2), ship_position[1] - (ship.hitbox / 2), ship_position[1] + (ship.hitbox / 2)):
                shield_delay, dead = ship_damage(aprojent[i][2].damage, False)
                aprojent.pop(i)
        except:
            pass

    #check ship with items
    for i in range(len(itement)):
        try:
            if check_position(itement[i][0][0], itement[i][0][1], ship_position[0] - (ship.hitbox / 2), ship_position[0] + (ship.hitbox / 2), ship_position[1] - (ship.hitbox / 2), ship_position[1] + (ship.hitbox / 2)):
                if ship.inventory > len(ship_inventory):
                    ship_inventory.append(itement[i][1].ID)
                    itement.pop(i)
        except:
            pass

    #check laser with asteroids and aliens
    if laser[0] or laser[1] or laser[2]:
        collide = False
        if laser[2]:
            weapon = weapon_3
        if laser[1]:
            weapon = weapon_2
        if laser[0]:
            weapon = weapon_1
        laser_position = [mousex, mousey]
        laser_vect = get_thrust(direction_vect, LASER_STEP)
        pos = [SCREEN[0] / 2, SCREEN[1] / 2]
        length = get_magnitude(direction_vect)
        for j in range(round(length / LASER_STEP)):
            pos = [pos[0] + laser_vect[0], pos[1] + laser_vect[1]]
            for i in range(len(astent)):
                try:
                    if check_position(astent[i][0][0] - change[0], astent[i][0][1] - change[1], -265, SCREEN[0] + 265, -265, SCREEN[1] + 265):
                        if get_magnitude([pos[0] - (astent[i][0][0] - change[0]), pos[1] - (astent[i][0][1] - change[1])]) <= astent[i][2].hitbox:
                            if weapon.asteroid >= astent[i][2].size:
                                if astent[i][2].size != 1:
                                    asteroid = assign_asteroid(astent[i][2].size - 2)
                                    angle1 = angle_calc(direction_vect, [0, -100], False)
                                    angle2 = angle1 - 90
                                    angle2 = math.radians(angle2)
                                    heading_vect = [math.sin(angle2), -(math.cos(angle2))]
                                    astent.append([astent[i][0], get_thrust(heading_vect, asteroid.speed), asteroid])
                                    astent.append([astent[i][0], get_thrust([-heading_vect[0], -heading_vect[1]], asteroid.speed), asteroid])
                                spawn_items(astent[i][0], astent[i][2].item)
                                astent.pop(i)
                            laser_position = pos
                            collide = True
                except:
                    pass
                if collide:
                    break

            if collide == False:
                for i in range(len(alient)):
                    try:
                        if check_position(alient[i][0][0] - change[0], alient[i][0][1] - change[1], -200, SCREEN[0] + 200, -200, SCREEN[1] + 200):
                            if check_position(pos[0] + change[0], pos[1] + change[1], alient[i][0][0] - (alient[i][2].hitbox) / 2, alient[i][0][0] + (alient[i][2].hitbox) / 2, alient[i][0][1] - (alient[i][2].hitbox) / 2, alient[i][0][1] + (alient[i][2].hitbox) / 2):
                                alient[i][3] = alient[i][3] - weapon.damage
                                if alient[i][3] <= 0:
                                    spawn_items(alient[i][0], alient[i][2].item)
                                    alient.pop(i)
                                laser_position = pos
                                collide = True
                    except:
                        pass
                    if collide:
                        break
                                          
            if collide:
                break

    return dead


def gameplay_UI():
    #display backdrop
    if config[8]:
        display.blit(BACKDROP, (0 - (SCREEN[0] / 4) - (ship_position[0] * BACKDROP_MOVEMENT), 0 - (ship_position[1] * BACKDROP_MOVEMENT)))
    
    #display items
    for i in range(len(itement)):
        pygame.draw.circle(display, itement[i][1].colour, (round(itement[i][0][0] - change[0]), round(itement[i][0][1] - change[1])), 5)
    
    #display asteroids
    for i in range(len(astent)):
        display.blit(astent[i][2].sprite, (round(astent[i][0][0] - change[0] - (astent[i][2].hitbox)), round(astent[i][0][1] - change[1] - (astent[i][2].hitbox))))

    #aliens
    for i in range(len(alient)):
        display.blit(alient[i][2].sprite, (round(alient[i][0][0] - change[0] - (alient[i][2].hitbox / 2)), round(alient[i][0][1] - change[1] - (alient[i][2].hitbox / 2))))
        
    #display projectiles
    for i in range(len(projent)):
        angle = angle_calc(projent[i][1], [0, -100], True)
        display.blit(pygame.transform.rotate(projent[i][2].sprite, angle), (round(projent[i][0][0] - change[0] - (projent[i][2].sprite.get_width() / 2)), round(projent[i][0][1] - change[1] - (projent[i][2].sprite.get_height() / 2))))

    #display alien projectiles
    for i in range(len(aprojent)):
        display.blit(ALIEN_BULLET_SPRITE, (round(aprojent[i][0][0] - change[0] - (ALIEN_BULLET_SPRITE.get_width() / 2)), round(aprojent[i][0][1] - change[1] - (ALIEN_BULLET_SPRITE.get_height() / 2))))

    #display laser
    width = 0
    if laser[0]:
        width = width + weapon_1.sprite
    if laser[1]:
        width = width + weapon_2.sprite
    if laser[2]:
        width = width + weapon_3.sprite
    pygame.draw.line(display, (255, 255, 255), (round(SCREEN[0] / 2), round(SCREEN[1] / 2)), laser_position, width)

    #display ship
    if thrust:
        display.blit(ship_thrust_sprite, (round(ship_position[0] - change[0] - (ship.hitbox / 2)), round(ship_position[1] - change[1] - (ship.hitbox / 2))))
    else:
        display.blit(ship_sprite, (round(ship_position[0] - change[0] - (ship.hitbox / 2)), round(ship_position[1] - change[1] - (ship.hitbox / 2))))

    #display station
    display.blit(SPACE_STATION_SPRITE, (-1000 - change[0], -1200 - change[1]))

    #display HUD
    #put HUD config condition below
    if config[7] == False:
        print_text("health: " + str(ship_health), (0, 0), 30)
        print_text("shield: " + str(ship_shield), (0, 30), 30)
        if config[5] and weapon_select == 1:
            print_button("ammo1: " + str(ship_ammo[0]), (0, 60), 30, False)
        else:
            print_button("ammo1: " + str(ship_ammo[0]), (0, 60), 30, True)
        if config[5] and weapon_select == 2:
            print_button("ammo2: " + str(ship_ammo[1]), (0, 90), 30, False)
        else:
            print_button("ammo2: " + str(ship_ammo[1]), (0, 90), 30, True)
        if config[5] and weapon_select == 3:
            print_button("ammo3: " + str(ship_ammo[2]), (0, 120), 30, False)
        else:
            print_button("ammo3: " + str(ship_ammo[2]), (0, 120), 30, True)
        print_text("fuel: " + str(round(ship_fuel)), (0, 150), 30)
        print_text("position: " + str(round(ship_position[0])) + ", " + str(round(ship_position[1])), (0, 180), 30)
    else:
        #rects
        pygame.draw.rect(display, (0, 0, 0), (SCREEN[0] - 200, 305, 200, SCREEN[1] - 500))
        pygame.draw.rect(display, (0, 0, 0), (SCREEN[0] - 305, SCREEN[1] - 305, 300, 300))

        #weapon ammo
        offset = SCREEN[0] - 190
        for i in range(3):
            if current_ship[i + 1] != 0:
                if config[5] and weapon_select == i + 1:
                    invert = False
                else:
                    invert = True
                print_button(assign_weapon(current_ship[i + 1]).name, (offset, 320 + (i * 70)), 20, invert)
                if assign_weapon(current_ship[i + 1]).velocity == -1:
                    print_button("N/A", (offset, 340 + (i * 70)), 40, True)
                else:
                    string = (str(ship_ammo[i]) + " / " + str(assign_weapon(current_ship[i + 1]).ammo))
                    print_button(string, (offset, 340 + (i * 70)), 40, True)

        #ship stats
        display.blit(pygame.transform.scale(ship.sprite, (80, 120)), (SCREEN[0] - 200, SCREEN[1] - 210))

        #shield
        if ship_shield == 0:
            colour = (0, 255, 255)
            shield_percent = 1 - ((shield_delay - index) / SHIELD_REGEN)
        else:
            colour = (0, 100, 255)
            shield_percent = (ship_shield / ship.shield)

        if shield_percent > 0.5:
            shield_percent1 = (shield_percent - 0.5) * 2
            shield_percent2 = 1
        else:
            shield_percent1 = 0
            shield_percent2 = shield_percent * 2
        
        if shield_percent1 != 0:
            pygame.draw.line(display, colour, (SCREEN[0] - 255, SCREEN[1] - 275), (SCREEN[0] - 255 + (190 * shield_percent1), SCREEN[1] - 275), 50)

        if shield_percent2 != 0:
            pygame.draw.line(display, colour, (SCREEN[0] - 280, SCREEN[1] - 60), (SCREEN[0] - 280, SCREEN[1] - 60 - (240 * shield_percent2)), 50)

        #health
        health_percent = (ship_health / ship.health)
        pygame.draw.line(display, (255, 0, 0), (SCREEN[0] - 305, SCREEN[1] - 30), (SCREEN[0] - 305 + (300 * health_percent), SCREEN[1] - 30), 50)

        #fuel
        fuel_percent = (ship_fuel / 100)
        pygame.draw.line(display, (255, 127, 0), (SCREEN[0] - 35, SCREEN[1] - 60), (SCREEN[0] - 35, SCREEN[1] - 60 - (240 * fuel_percent)), 50)

        #left - right of weapons column
        pygame.draw.line(display, (255, 255, 255), (SCREEN[0] - 200, 305), (SCREEN[0] - 200, SCREEN[1] - 300), 10)
        pygame.draw.line(display, (255, 255, 255), (SCREEN[0] - 5, 0), (SCREEN[0] - 5, SCREEN[1]), 10)
        #top - left - bottom of ship stats
        pygame.draw.line(display, (255, 255, 255), (SCREEN[0] - 305, SCREEN[1] - 300), (SCREEN[0] - 5, SCREEN[1] - 300), 10)
        pygame.draw.line(display, (255, 255, 255), (SCREEN[0] - 305, SCREEN[1] - 300), (SCREEN[0] - 305, SCREEN[1] - 5), 10)
        pygame.draw.line(display, (255, 255, 255), (SCREEN[0] - 305, SCREEN[1] - 5), (SCREEN[0], SCREEN[1] - 5), 10)
        #top - left - bottom - right of secondary square
        pygame.draw.line(display, (255, 255, 255), (SCREEN[0] - 255, SCREEN[1] - 250), (SCREEN[0] - 65, SCREEN[1] - 250), 10)
        pygame.draw.line(display, (255, 255, 255), (SCREEN[0] - 255, SCREEN[1] - 250), (SCREEN[0] - 255, SCREEN[1] - 60), 10)
        pygame.draw.line(display, (255, 255, 255), (SCREEN[0] - 305, SCREEN[1] - 60), (SCREEN[0] - 5, SCREEN[1] - 60), 10)
        pygame.draw.line(display, (255, 255, 255), (SCREEN[0] - 65, SCREEN[1] - 300), (SCREEN[0] - 65, SCREEN[1] - 60), 10)

        #left HUD
        pygame.draw.rect(display, (0, 0, 0), (0, 0, 205, SCREEN[1]))
        #left - right of column
        pygame.draw.line(display, (255, 255, 255), (5, 0), (5, SCREEN[1]), 10)
        pygame.draw.line(display, (255, 255, 255), (205, 5), (205, SCREEN[1] - 5), 10)
        #top - middle - bottom of rows
        pygame.draw.line(display, (255, 255, 255), (0, 5), (205, 5), 10)
        pygame.draw.line(display, (255, 255, 255), (0, 105), (205, 105), 10)
        pygame.draw.line(display, (255, 255, 255), (0, SCREEN[1] - 5), (205, SCREEN[1] - 5), 10)

        #pause
        pygame.draw.line(display, (255, 255, 255), (20, 30), (70, 30), 10)
        pygame.draw.line(display, (255, 255, 255), (20, 50), (70, 50), 10)
        pygame.draw.line(display, (255, 255, 255), (20, 70), (70, 70), 10)
        print_text("PAUSE", (80, 20), 60)

        #inventory
        print_text("INVENTORY", (20, 120), 47)
        quantity = get_inventory_quantities()
        j = 0
        for i in range(10):
            if quantity[i] != 0:
                print_text(assign_item(i).name, (20, 170 + (j * 70)), 30)
                print_text(str(quantity[i]), (20, 205 + (j * 70)), 20)
                print_text("REMOVE", (50, 205 + (j * 70)), 20)
                j = j + 1
        
        mini_map()

def manage_inventory():
    global held2

    if held2:
        if mouse[0] == False:
            held2 = False
    
    quantity = get_inventory_quantities()
    j = 0
    for i in range(10):
        if quantity[i] != 0:
            if check_position(mousex, mousey, 50, 100, 205 + (j * 70), 225 + (j * 70)):
                print_button("REMOVE", (50, 200 + (j * 70)), 30, True)
                if mouse[0] and held2 == False:
                    l = 0
                    for k in range(len(ship_inventory)):
                        try:
                            if i == ship_inventory[k + l]:
                                ship_inventory.pop(k + l)
                                l = l - 1
                        except:
                            pass
                    held2 = True
            j = j + 1

def mini_map():
    pygame.draw.rect(display, (0, 0, 0), (SCREEN[0] - 305, 5, 300, 300))
    pygame.draw.rect(display, (255, 255, 255), (SCREEN[0] - 165, 150, 10, 10))
    offset = SCREEN[0] - 350
    for j in range(2):
        if j == 0:
            entities = astent
        elif j == 1:
            entities = alient
        for i in range(len(entities)):
            if check_position(entities[i][0][0], entities[i][0][1], ship_position[0] - 2400, ship_position[0] + 2400, ship_position[1] - 2400, ship_position[1] + 2400):
                pos = [round((entities[i][0][0] - change[0]) / 16), round((entities[i][0][1] - change[1]) / 16)]
                if j == 0:
                    size = astent[i][2].size + 2
                    pygame.draw.rect(display, (127, 127, 127), (pos[0] + offset + 150 - size, pos[1] + 130 - size, size * 2, size * 2))
                elif j == 1:
                    pygame.draw.rect(display, (0, 255, 0), (pos[0] + offset + 145, pos[1] + 125, 10, 10))

    if check_position(0, 0, ship_position[0] - 2400, ship_position[0] + 2400, ship_position[1] - 2400, ship_position[1] + 2400):
        pygame.draw.circle(display, (255, 255, 255), (offset + 150 - round(change[0] / 16), 125 - round(change[1] / 16)), 10)
    else:
        vect = [(offset + 140 - round(change[0] / 16)) - (SCREEN[0] - 165), (115 - round(change[1] / 16)) - 150]
        vect = get_thrust(vect, 140)
        angle = angle_calc(vect, [0, -100], True)
        display.blit(pygame.transform.rotate(ARROW, angle), (SCREEN[0] - 165 + vect[0], 150 + vect[1]))
           
    pygame.draw.line(display, (255, 255, 255), (SCREEN[0] - 305, 5), (SCREEN[0] - 5, 5), 10)
    pygame.draw.line(display, (255, 255, 255), (SCREEN[0] - 305, 305), (SCREEN[0] - 5, 305), 10)
    pygame.draw.line(display, (255, 255, 255), (SCREEN[0] - 305, 5), (SCREEN[0] - 305, 305), 10)
    pygame.draw.line(display, (255, 255, 255), (SCREEN[0] - 5, 5), (SCREEN[0] - 5, 305), 10)

def define_station():
    global restock, restock_cost, repair, repair_cost, refuel, refuel_cost, owned
    restock = False
    restock_cost = round((weapon_1.ammo - ship_ammo[0]) * weapon_1.restock)
    try:
        restock_cost = restock_cost + round((weapon_2.ammo - ship_ammo[1]) * weapon_2.restock)
    except:
        pass
    try:
        restock_cost = restock_cost + round((weapon_3.ammo - ship_ammo[2]) * weapon_3.restock)
    except:
        pass
    restock_cost = round(restock_cost * RESTOCK_MULTIPLIER)
    if restock_cost == 0:
        restock = True

    repair = False
    repair_cost = round((ship.health - ship_health) * REPAIR_MULTIPLIER)
    if repair_cost == 0:
        repair = True

    refuel = False
    refuel_cost = round((100 - ship_fuel) * REFUEL_MULTIPLIER)
    if refuel_cost == 0:
        refuel = True
    
    owned = []
    for i in range(13):
        x = False
        for j in range(len(owned_ships)):
            if owned_ships[j][0] == i:
                x = True
        owned.append(x)

def space_station():
    global state, ship_position, move_vect, ship_ammo, ship_health, ship_fuel, restock, repair, refuel, ship_inventory, total_credits, owned_ships, current_ship, owned_weapons, temp_message, held, saved, menu_button
    display = pygame.display.set_mode()
    print_text("SPACE STATION MENU", (50, 0), 100)
    print_text(str(total_credits) + " C", (1000, 50), 50)
    
    if check_position(mousex, mousey, 100, 220, 200, 250):
        print_button("LAUNCH", (100, 190), 70, True)
        if mouse[0]:
            print_button("LAUNCHING...", (100, 190), 70, True)
            pygame.display.update()
            display = pygame.display.set_mode()
            pygame.time.delay(1000)
            ship_position = [0, 1]
            move_vect = [0, 1]
            state = 1.1
    else:
        print_button("LAUNCH", (100, 200), 50, True)

    if True:
        pygame.draw.line(display, (255, 255, 255), (480, 200), (480, 800), 20)
        pygame.draw.line(display, (255, 255, 255), (780, 200), (780, 800), 20)
        pygame.draw.line(display, (255, 255, 255), (1190, 200), (1190, 800), 20)
        
        if check_position(mousex, mousey, 100, 335, 300, 350) and restock == False:
            print_button("RESTOCK AMMO", (100, 290), 70, True)
            print_text(str(restock_cost) + " C", (100, 340), 50)
            if mouse[0] and total_credits >= restock_cost:
                try:
                    ship_ammo = [weapon_1.ammo, weapon_2.ammo, weapon_3.ammo]
                except:
                    try:
                        ship_ammo = [weapon_1.ammo, weapon_2.ammo, 0]
                    except:
                        ship_ammo = [weapon_1.ammo, 0, 0]
                total_credits = total_credits - restock_cost
                restock = True
                            
        elif restock:
            print_button("AMMO RESTOCKED", (100, 300), 50, True)
        else:
            print_button("RESTOCK AMMO", (100, 300), 50, True)
            print_text(str(restock_cost) + " C", (100, 340), 50)

        if check_position(mousex, mousey, 100, 215, 400, 450) and repair == False:
            print_button("REPAIR", (100, 390), 70, True)
            print_text(str(repair_cost) + " C", (100, 440), 50)
            if mouse[0] and total_credits >= repair_cost:
                ship_health = ship.health
                total_credits = total_credits - repair_cost
                repair = True

        elif repair:
            print_button("REPAIRED", (100, 400), 50, True)
        else:
            print_button("REPAIR", (100, 400), 50, True)
            print_text(str(repair_cost) + " C", (100, 440), 50)

        if check_position(mousex, mousey, 100, 215, 500, 550) and refuel == False:
            print_button("REFUEL", (100, 490), 70, True)
            print_text(str(refuel_cost) + " C", (100, 540), 50)
            if mouse[0] and total_credits >= refuel_cost:
                ship_fuel = 100
                total_credits = total_credits - refuel_cost
                refuel = True
        elif refuel:
            print_button("REFUELED", (100, 500), 50, True)
        else:
            print_button("REFUEL", (100, 500), 50, True)
            print_text(str(refuel_cost) + " C", (100, 540), 50)

        if held:
            if keys[pygame.K_ESCAPE] == False:
                held = False

        if keys[pygame.K_ESCAPE] and held == False:
            state = 1.6
            held = True
            saved = False
            menu_button = False

        print_text("INVENTORY", (500, 200), 50)
        order = []
        row = 0
        for i in range(10):
            num = 0
            for j in range(len(ship_inventory)):
                if ship_inventory[j] == i:
                    num = num + 1
            if num != 0:
                print_text(assign_item(i).name + ": " + str(num), (500, 250 + row), 20)
                row = row + 20
        if row != 0:
            if check_position(mousex, mousey, 500, 825, 255 + row, 295 + row):
                print_text("SELL ALL", (500, 250 + row), 50)
                if mouse[0]:
                    for i in range(len(ship_inventory)):
                        total_credits = total_credits + assign_item(ship_inventory[i]).value
                    ship_inventory = []
            else:
                print_text("SELL ALL", (500, 255 + row), 40)
        else:
            print_text("EMPTY", (500, 255), 40)

        print_text("SHIPS", (800, 200), 50)
        print_text(ship0.name, (800, 250), 30)
        print_text(ship1.name, (800, 290), 30)
        print_text(ship2.name, (800, 330), 30)
        print_text(ship3.name, (800, 370), 30)
        print_text(ship4.name, (800, 410), 30)
        print_text(ship5.name, (800, 450), 30)
        print_text(ship6.name, (800, 490), 30)
        print_text(ship7.name, (800, 530), 30)
        print_text(ship8.name, (800, 570), 30)
        print_text(ship9.name, (800, 610), 30)
        print_text(ship10.name, (800, 650), 30)
        print_text(ship11.name, (800, 690), 30)
        print_text(ship12.name, (800, 730), 30)
        for i in range(13):
            if owned[i]:
                if current_ship[0] == i:
                    print_text("EQUIPED", (1000, (250 + (40 * i))), 30)
                else:
                    print_text("EQUIP", (1000, (250 + (40 * i))), 30)
            else:
                print_text("BUY", (1000, (250 + (40 * i))), 30)
                print_text(str(assign_ship(i).cost) + " C", (1100, (250 + (40 * i))), 30)
        for i in range(13):
            if check_position(mousex, mousey, 1000, 1060, (250 + (40 * i)), (280 + (40 * i))):
                if owned[i] and current_ship[0] != i:
                    print_button("EQUIP", (1000, (245 + (40 * i))), 40, True)
                    if mouse[0] and repair and restock:
                        for j in range(len(owned_ships)):
                            if owned_ships[j][0] == i:
                                current_ship = owned_ships[j]
                        ship_health = assign_ship(current_ship[0]).health
                        ship_ammo = [0, 0, 0]
                        for j in range(3):
                            try:
                                ship_ammo[j] = assign_weapon(current_ship[j + 1]).ammo
                            except:
                                pass
                    elif mouse[0]:
                        temp_message = "repair/restock first before changing ships"
                elif owned[i] == False:
                    if total_credits >= assign_ship(i).cost:
                        print_button("BUY", (1000, (245 + (40 * i))), 40, True)
                        if mouse[0] and repair and restock:
                            weapon_slot = assign_ship(i).slots[0]
                            if weapon_slot < 0:
                                if weapon_slot == -1:
                                    owned_ships.append([i, 6, 0, 0])
                                if weapon_slot == -2:
                                    owned_ships.append([i, 12, 0, 0])
                                if weapon_slot == -3:
                                    owned_ships.append([i, 18, 0, 0])
                            else:
                                owned_ships.append([i, 1, 0, 0])
                            total_credits = total_credits - assign_ship(i).cost
                            owned[i] = True
                        elif mouse[0]:
                            temp_message = "repair/restock first before buying new ships"

        display.blit(pygame.transform.scale(assign_ship(current_ship[0]).sprite, (100, 150)), (1210, 20))
        print_text("WEAPONS", (1210, 200), 50)
        print_text("1: " + assign_weapon(current_ship[1]).name, (1210, 250), 30)
        if current_ship[2] != 0:
            print_text("2: " + assign_weapon(current_ship[2]).name, (1210, 280), 30)
        else:
            if assign_ship(current_ship[0]).slots[1] == 0:
                print_text("2: UNAVAILIBLE", (1210, 280), 30)
            else:
                print_text("2: EMPTY", (1210, 280), 30)
        if current_ship[3] != 0:
            print_text("3: " + assign_weapon(current_ship[3]).name, (1210, 310), 30)
        else:
            if assign_ship(current_ship[0]).slots[2] == 0:
                print_text("3: UNAVAILIBLE", (1210, 310), 30)
            else:
                print_text("3: EMPTY", (1210, 310), 30)
        if assign_ship(current_ship[0]).slots[0] == 1 or assign_ship(current_ship[0]).slots[0] == -1:
            size = 1
        if assign_ship(current_ship[0]).slots[0] == 2 or assign_ship(current_ship[0]).slots[0] == -2:
            size = 2
        if assign_ship(current_ship[0]).slots[0] == 3 or assign_ship(current_ship[0]).slots[0] == -3:
            size = 3
        amount = 0
        for i in range(3):
            if assign_ship(current_ship[0]).slots[i] != 0:
                amount = amount + 1
            
        for i in range(1, 6):
            has_weapon = False
            if size == 1:
                j = i
                print_text(assign_weapon(j).name, (1210, 280 + (i * 90)), 30)
                has_weapon = owned_weapons[j - 1]
            if size == 2:
                j = i + 6
                print_text(assign_weapon(j).name, (1210, 280 + (i * 90)), 30)
                has_weapon = owned_weapons[j - 1]
            if size == 3:
                j = i + 12
                print_text(assign_weapon(j).name, (1210, 280 + (i * 90)), 30)
                has_weapon = owned_weapons[j - 1]
            if has_weapon == False:
                print_text("BUY", (1210, 320 + (i * 90)), 30)
                print_text(str(assign_weapon(j).cost) + " C", (1270, 320 + (i * 90)), 30)
                if check_position(mousex, mousey, 1210, 1250, 320 + (i * 90), 350 + (i * 90)) and total_credits >= assign_weapon(j).cost:
                    print_button("BUY", (1210, 315 + (i * 90)), 40, True)
                    if mouse[0]:
                        owned_weapons[j - 1] = True
                        total_credits = total_credits - assign_weapon(j).cost
            else:
                print_text("EQUIP TO:", (1210, 320 + (i * 90)), 30)
                print_text("1", (1330, 320 + (i * 90)), 30)
                if amount > 1:
                    print_text("2", (1360, 320 + (i * 90)), 30)
                if amount == 3:
                    print_text("3", (1390, 320 + (i * 90)), 30)
                for k in range(amount):
                    if check_position(mousex, mousey, 1330 + (k * 30), 1345 + (k * 30), 320 + (i * 90), 350 + (i * 90)) and (assign_ship(current_ship[0]).slots[0] > 0 or k > 0):
                        print_button(str(k + 1), (1330 + (k * 30), 315 + (i * 90)), 40, True)
                        if mouse[0] and restock:
                            for l in range(len(owned_ships)):
                                if owned_ships[l][0] == current_ship[0]:
                                    owned_ships[l][k + 1] = j
                                    ship_ammo[k] = assign_weapon(j).ammo
                        elif mouse[0]:
                            temp_message = "restock first before changing weapons"

def game_over():
    global state, temp_message, ship_position, ship_health, ship_inventory, held
    print_text("GAME OVER", (100, 100), 100)
    print_text("RETURN TO SPACE STATION", (100, 250), 50)
    print_text("RETURN TO MAIN MENU", (100, 300), 50)

    temp_message = ""
    
    if check_position(mousex, mousey, 100, 560, 250, 300):
        print_button("RETURN TO SPACE STATION", (100, 240), 70, True)
        temp_message = "Return to the space station"
        if mouse[0]:
            temp_message = ""
            ship_position = [0, 0]
            ship_health = round(ship.health / 2)
            ship_inventory = []
            define_station()
            held = True
            state = 2

    if check_position(mousex, mousey, 100, 470, 300, 350):
        print_button("RETURN TO MAIN MENU", (100, 290), 70, True)
        temp_message = "Quit to the main menu (this will save the game)"
        if mouse[0]:
            temp_message = ""
            ship_position = [0, 0]
            ship_health = round(ship.health / 2)
            ship_inventory = []
            save_game(0)
            held = True
            state = 0 

state = 0
run = True
held = False
held2 = False
settings = False
temp_message = ""
temp_index = -1

while run:
    
    for event in pygame.event.get():
        (mousex, mousey) = pygame.mouse.get_pos()
        if event.type == pygame.QUIT:  
           run = False
        if event.type == pygame.MOUSEWHEEL:
            scroll = event.y
        else:
            scroll = 0
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()

    if state == -1:
        run = False

    if state == 0:
        main_menu()

    if state == 1.1:
        define_loop()

    if state == 1:
        game_loop()

    if state == 1.5:
        pause_menu(True)

    if state == 1.6:
        pause_menu(False)

    if state == 2:
        space_station()
        
    if state == 3:
        game_over()

    if temp_message != "" and temp_index != 0:
        print_text(temp_message, (300, 800), 50)
        if temp_index == -1:
            temp_index = MESSAGE_TIME
        else:
            temp_index = temp_index - 1
    else:
        print_text(temp_message, (300, 800), 50)
        temp_message = ""
        temp_index = -1   

    pygame.display.update()
    display = pygame.display.set_mode()

    pygame.time.Clock().tick_busy_loop(FRAME_RATE)

pygame.quit()

db.execute("DELETE FROM Config")
db.execute("INSERT INTO Config (thrust, weapon1, weapon2, weapon3, pause, scroll, scrollfire, ui, backdrop) VALUES (?,?,?,?,?,?,?,?,?)", config)

connect.commit()
connect.close()

#code archive:

#old collision detection for ship -> asteroid
                #collide = False
                #x1 = astent[i][0][0] - astent[i][2].hitbox
                #x2 = astent[i][0][0] + astent[i][2].hitbox
                #y1 = astent[i][0][1] - astent[i][2].hitbox
                #y2 = astent[i][0][1] + astent[i][2].hitbox
                #if check_position(ship_position[0] - (ship.hitbox / 2), ship_position[1] - (ship.hitbox / 2), x1, x2, y1, y2):
                    #collide = True
                #elif check_position(ship_position[0] + (ship.hitbox / 2), ship_position[1] - (ship.hitbox / 2), x1, x2, y1, y2):
                    #collide = True
                #elif check_position(ship_position[0] - (ship.hitbox / 2), ship_position[1] + (ship.hitbox / 2), x1, x2, y1, y2):
                    #collide = True
                #elif check_position(ship_position[0] + (ship.hitbox / 2), ship_position[1] + (ship.hitbox / 2), x1, x2, y1, y2):
                    #collide = True

                #if collide == False:
                    #x1 = ship_position[0] - (ship.hitbox / 2)
                    #x2 = ship_position[0] + (ship.hitbox / 2)
                    #y1 = ship_position[1] - (ship.hitbox / 2)
                    #y2 = ship_position[1] + (ship.hitbox / 2)
                    #if check_position(astent[i][0][0] - astent[i][2].hitbox, astent[i][0][1] - astent[i][2].hitbox, x1, x2, y1, y2):
                        #collide = True
                    #elif check_position(astent[i][0][0] + astent[i][2].hitbox, astent[i][0][1] - astent[i][2].hitbox, x1, x2, y1, y2):
                        #collide = True
                    #elif check_position(astent[i][0][0] - astent[i][2].hitbox, astent[i][0][1] + astent[i][2].hitbox, x1, x2, y1, y2):
                        #collide = True
                    #elif check_position(astent[i][0][0] + astent[i][2].hitbox, astent[i][0][1] + astent[i][2].hitbox, x1, x2, y1, y2):
                        #collide = True
