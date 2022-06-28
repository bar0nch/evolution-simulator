import pygame, time, random, pickle, json, os, copy
from particle_related_classes import * #classes Particle, Element and Compound
from world_manager import * #saving and loading functions + Version class and methods
import world_generator #functions to automatically generate world files
pygame.init()
temp = None #general multipurpose variable
optional_prints = False
temperatures_map_alpha = 230
simulation_slowness_multiplier = 0
control_sensibility_slowness_multiplier = 0
minimum_version_required = 'v0.2.2'

#================================================TODO================================================
'''
create compound unit class
update reactions in the mainloop
create reactions and compounds data automatically
'''
#===============================================BUGLOG===============================================

'''
liquids only move in the middle of the world
'''

#=============================================FUNCTIONS==============================================

def check_inf_loop(initial_time,safe_time=10):
    '''
    checks if a certain amount of time has passed. (used for infinite loops)
    '''
    if time.time() - initial_time > safe_time:
        return True
    else:
        return False

def is_in_reac_requirements(particle,reaction):
    '''
    checks if a particle is required in a reaction (is in requirements list of said reaction)
    '''
    for req in reaction["requirements"]:
        if particle in req:
            return True
    return False

#functions to quickly get an element from the element list

def find_by_param_in_elem_list(param, elem_list):
    for elem in elem_list:
        if elem.name == param:
            return elem_list.index(elem)
        elif elem.shorthand == param:
            return elem_list.index(elem)
        elif elem.color == param:
            return elem_list.index(elem)
        elif elem.perc_num == param:
            return elem_list.index(elem)
        elif elem.distribution == param:
            return elem_list.index(elem)
    return -1

def get_by_param_in_elem_list(param, elem_list):
    for elem in elem_list:
        if elem.name == param:
            return elem
        elif elem.shorthand == param:
            return elem
        elif elem.color == param:
            return elem
        elif elem.perc_num == param:
            return elem
        elif elem.distribution == param:
            return elem
    return None

def find_by_param_in_comp_list(param, comp_list):
    for comp in comp_list:
        if comp.name == param:
            return comp_list.index(comp)
        elif comp.color == param:
            return comp_list.index(comp)
        elif comp.density == param:
            return comp_list.index(comp)
    return -1

def get_by_param_in_comp_list(param, comp_list):
    for comp in comp_list:
        if comp.name == param:
            return comp
        elif comp.color == param:
            return comp
        elif comp.density == param:
            return comp
    return None

def print_elem_list(elem_list):
    for elem in elem_list:
        print(elem.name.ljust(14),' (',elem.shorthand, ') ',str(elem.color).ljust(15),' : ',elem.distribution,'\n')

def print_comp_list(comp_list):
    for comp in comp_list:
        print(comp.name.ljust(30),str(comp.color).ljust(16),comp.density)

def print_terrain_matrix(terr_matrix):
    for row in terr_matrix:
        for unit in row:
            print("(X): ",unit.x,"  (Y): ",unit.y,"  ",str(unit.particle))
        print()
    print('\n\n\n')



#setting world parameters to use later
filename = input("insert a full filename or press backspace: ")
temp = open('saves/'+filename+'/version.txt','r')
VERSION = WorldVersion() #version of the world loaded
extracted_temp_data = temp.read()
if extracted_temp_data:
    VERSION.override(extracted_temp_data)
temp.close()
missing_by_obsolescence = {'v0.2.1': "ratios json file",
                           'v0.2.2': "melting point key in particles, temperature matrix, movement (for single units)"
                           }
current_missing = [] #checks if the version is obsolete
for v, feature in missing_by_obsolescence.items():
    ver = WorldVersion()
    ver.override(v)
    if ver > VERSION:
        current_missing.append(feature)
temp = WorldVersion()
temp.override(minimum_version_required)
assert VERSION >= temp, "version outdated. missing: " + ", ".join(current_missing)

if filename != "": #loads progress from a world folder
    world_data = load_progress(filename)
else:
    world_data = load_progress()

elements = world_data["elements"] #world parameters
w = world_data["w"]
h = world_data["h"]
side = world_data["side"]
spacing = world_data["spacing"]
max_particle_ratio = world_data["max particle ratio"]
world = world_data["world"]
compounds = world_data["compounds"]
reactions = world_data["reactions"]
ratios = world_data["ratios"]
temperatures = world_data["temperature"]

win = pygame.display.set_mode((w*side,h*side))
pygame.display.set_caption("evolution simulator") #generates the grid


#=======================================WORLD RELATED CLASSES========================================

class MoveRequest:
    def __init__(self, requester, direction=None):
        self.requester = requester
        self.subject = None
        self.direction = direction
        self.accepted = False

    def set_direction(self, direction=None):
        if direction:
            self.direction = direction
            return
        
        if not self.direction: #not to waste resources
            directions = {"up":False, "down":False, "left":False, "right":False} #dict to check the available directions
            units_available = {"up":None, "down":None, "left":None, "right":None} #binds the directions to the proper units
            
            for neg in self.requester.neighbours: #checks every neighbour of the requester unit and sets their direction to available if it is
                if neg.state_of_matter == "liquid":
                    if neg.Y == self.requester.Y - 1 and neg.X == self.requester.X:
                        directions["up"] = True
                        units_available["up"] = neg
                    elif neg.Y == self.requester.Y + 1 and neg.X == self.requester.X:
                        directions["down"] = True
                        units_available["down"] = neg
                    elif neg.X == self.requester.X - 1 and neg.Y == self.requester.Y:
                        directions["left"] = True
                        units_available["left"] = neg
                    elif neg.X == self.requester.X + 1 and neg.Y == self.requester.Y:
                        directions["right"] = True
                        units_available["right"] = neg
                  
            directions_list = [key for key, value in directions.items() if value] #a list is made to be shuffled and so to randomise the direction chosen
            if directions_list:
                random.shuffle(directions_list)
                self.direction = directions_list[0]
                self.subject = units_available[self.direction] #select the other unit subject to the movement with the direction bind

    def cancel(self):
        self.requester.mr = None
        if self.subject:
            self.subject.mr = None
        

class ReacRequest: #wip
    def __init__(self):
        pass

class Unit: #the floor units where cells will be standing
    def __init__(self,particle,x,y,terr_matrix,X,Y):
        self.x = x #win coords
        self.y = y
        self.X = X #matrix coords
        self.Y = Y
        self.particle = particle
        self.color = self.particle.color
        self.terrain_matrix = terr_matrix
        self.state_of_matter = "solid"
        self.mr = None #MoveRequest
        self.rr = None #ReacRequest

    def __str__(self):
        if self.rr:
            has_rr = "yes"
        else:
            has_rr = "no"
        return "particle: {"+str(self.particle)+"} coords: "+str(self.x)+","+str(self.y)+" matrix coords: "+str(self.X)+","+str(self.Y)+" has ReacRequest: "+has_rr

    def set_particle(self,new_particle):
        self.particle = new_particle
        self.color = new_particle.color
        
    def calc_neighbours(self):
        '''
        saves the 4 or 8 adiacent units ignoring the ones that don't exist due to their corner position
        '''
        if world_data["max particle ratio"] == 8:
            self.neighbours = [self.terrain_matrix[self.X+x][self.Y+y] for x in range(-1,2) for y in range(-1,2) if self.X+x >= 0 and self.X+x < len(self.terrain_matrix[0]) and self.Y+y >= 0 and self.Y+y < len(self.terrain_matrix)]
        elif world_data["max particle ratio"] == 4:
            self.neighbours = [self.terrain_matrix[self.X+x][self.Y+y] for x, y in ((-1,0),(0,-1),(0,1),(1,0)) if self.X+x >= 0 and self.X+x < len(self.terrain_matrix[0]) and self.Y+y >= 0 and self.Y+y < len(self.terrain_matrix)]
        else:
            raise ValueError("max particle ratio is set to neither 4 or 8")
    
        
    def update(self, update_neighbours=False):
        if update_neighbours:
            self.calc_neighbours()

        if temperatures[self.X][self.Y] > self.particle.melting_point: #temperature variability leads to a change in the state of matter of the unit
            if optional_prints and self.state_of_matter == "solid": #prints the change of state
                print(self.particle.name, "turned to liquid")
            self.state_of_matter = "liquid"
        else:
            if optional_prints and self.state_of_matter == "liquid": #prints the change of state
                print(self.particle.name, "turned to solid")
            self.state_of_matter = "solid"

        if not self.mr: #moves the unit
            if self.state_of_matter == "liquid": #only moves liquids
                if random.randint(0,40) == 0:
                    self.mr = MoveRequest(self)
                    self.mr.set_direction()
                    if self.mr.subject:
                        self.mr.subject.mr = self.mr
                        self.mr.accepted = True

    def late_update(self):
        if self.mr:
            if self.mr.accepted:
                self.mr.requester.particle, self.mr.subject.particle = self.mr.subject.particle, self.mr.requester.particle
                self.mr.requester.color, self.mr.subject.color = self.mr.subject.color, self.mr.requester.color
                self.mr.cancel()
            else:
                self.mr.cancel()
        

    def draw(self, win, draw_temperature=False):
        global temperatures_map_alpha
        global temperatures
        
        pygame.draw.rect(win,self.color,(self.x,self.y,side,side))
        if draw_temperature:
            unit_tempr = temperatures[self.Y][self.X]
            tempr_color = {"R":0, "G":0, "B":0} #colors displayed in temperatures map
            if unit_tempr > 0:
                if unit_tempr > 255:
                    tempr_color["R"] = 255
                    tempr_color["G"] += unit_tempr - 255
                    tempr_color["B"] += unit_tempr - 255
                    if tempr_color["B"] > 255:
                        tempr_color["G"] = 255
                        tempr_color["B"] = 255
                else:
                    tempr_color["R"] = unit_tempr
            else:
                if unit_tempr < -255:
                    tempr_color["B"] = 255
                    tempr_color["G"] += -unit_tempr - 255
                    tempr_color["R"] += -unit_tempr - 255
                    if tempr_color["R"] > 255:
                        tempr_color["G"] = 255
                        tempr_color["R"] = 255
                else:
                    tempr_color["B"] = -unit_tempr

            tempr_color["R"] = (self.particle.color[0] * (255 - temperatures_map_alpha) + tempr_color["R"] * temperatures_map_alpha) / 255
            tempr_color["G"] = (self.particle.color[1] * (255 - temperatures_map_alpha) + tempr_color["G"] * temperatures_map_alpha) / 255
            tempr_color["B"] = (self.particle.color[2] * (255 - temperatures_map_alpha) + tempr_color["B"] * temperatures_map_alpha) / 255
            #it calculates the alpha value with a ponderated average
                    
            pygame.draw.rect(win,(tempr_color["R"], tempr_color["G"], tempr_color["B"]),(self.x,self.y,side,side))


#==============================================PROGRAM===============================================

print("generating the terrain matrix...")
terrain = [] #the actual world chemical composition matrix
for y in range(0,len(world)):
    row = []
    #gets the element from the world matrix and sets it in to the correspondent unit in the terrain matrix
    for x in range(0,len(world[0])):
        row.append(Unit(world[x][y], x*side, y*side, terrain, x,y))
    terrain.append(row)

for y in range(0,len(world)): #just to get all the neighbours of the units before execution
    for x in range(0,len(world[0])):
        terrain[x][y].calc_neighbours()
print("done generating the terrain matrix")

   
def updateGFX(temperatures_map=False):
    for row in terrain:
        for unit in row:
            if temperatures_map:
                unit.draw(win, True)
            else:
                unit.draw(win)
    pygame.display.update()

def update():
    for row in terrain:
        for unit in row:
            unit.update()
            
def late_update():
    global temperatures
    
    for row in terrain:
        for unit in row:
            unit.late_update()

    if random.randint(0,10) == 0:
        temperatures = [[tempr + random.randint(-1,3) for tempr in row] for row in temperatures]


print("starting the mainloop...\n\n\nTABLE OF ELEMENTS:\n")
print_elem_list(elements)

run = True
simulation_update_time = 0
controls_update_time = 0
while run:
    temperatures_map = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    keys = pygame.key.get_pressed()

    if keys[pygame.K_p]: #shows additional infos in the console
        if optional_prints == True:
            optional_prints = False
        else:
            optional_prints = True
        time.sleep(0.8)

    if keys[pygame.K_t]: #shows the temperatures map
        temperatures_map = True
        if controls_update_time == 0:
            if keys[pygame.K_KP_PLUS]: #adjusts the alpha value of the temperatures map
                temperatures_map_alpha += 1
                if temperatures_map_alpha > 255:
                    temperatures_map_alpha = 255
            if keys[pygame.K_KP_MINUS]:
                temperatures_map_alpha -= 1
                if temperatures_map_alpha < 0:
                    temperatures_map_alpha = 0

    if keys[pygame.K_d]:
        for row in terrain:
            for unit in row:
                    print(unit)
        print()
        time.sleep(0.8)

    if simulation_update_time == 0:
        update()
        late_update()
        updateGFX(temperatures_map)

    simulation_update_time += 1
    if simulation_update_time > simulation_slowness_multiplier:
        simulation_update_time = 0
    controls_update_time += 1
    if controls_update_time > control_sensibility_slowness_multiplier:
        controls_update_time = 0


print("\n\nexited the mainloop")
print("exiting code sequence...")
pygame.quit()

