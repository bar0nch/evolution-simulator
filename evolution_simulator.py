import pygame, time, random, pickle, json, os
from particle_related_classes import * #classes Particle, Element and Compound
from world_manager import * #saving and loading functions + Version class and methods
pygame.init()
temp = None #general multipurpose variable
minimum_version_required = 'v0.2.1'

#================================================TODO================================================
'''
update reactions in the mainloop
create reactions and compounds data automatically
'''
#===============================================BUGLOG===============================================

'''
reaction request system is completely broken
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
missing_by_obsolescence = {'v0.2.1': "ratios json file"}
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
''' 
world_data = {"version":VERSION.String,
              "elements":elements,
              "compounds":compounds,
              "reactions":reactions,
              "ratios":ratios,
              "w":w,
              "h":h,
              "side":side,
              "spacing":spacing,
              "max particle ratio":max_particle_ratio,
              "world":world[:]}
'''
win = pygame.display.set_mode((w*side,h*side))
pygame.display.set_caption("evolution simulator") #generates the grid


#=======================================WORLD RELATED CLASSES========================================

class ReacRequest: #the request an unit sends to another to make a reaction together
    def __init__(self, start_unit, reaction):
        self.units = {start_unit: False}
        self.accepted = False
        self.reaction = reaction

    def close_unit(self,unit):
        self.units[unit] = True
        if not bool([i for i in self.units.values() if i == False]): #if there are no False values in self.units
            total_particles = 0
            for req in self.reaction["requirements"]:
                total_particles += req[0]
            if len(self.units) == total_particles:
                self.accepted = True
        

class Unit: #the floor units where cells will be standing
    def __init__(self,particle,x,y,terr_matrix,X,Y):
        self.x = x #win coords
        self.y = y
        self.X = X #matrix coords
        self.Y = Y
        self.particle = particle
        self.color = self.particle.color
        self.terrain_matrix = terr_matrix
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
            raise Exception("max particle ratio is set to neither 4 or 8")
    
        
    def update(self, update_neighbours=False):
        if update_neighbours:
            self.calc_neighbours()

        if self.particle in ratios.keys():
            possible_reactions = []
            for reac in reactions:
                if is_in_reac_requirements(self.particle,reac):
                    possible_reactions.append(reac)
            target_reaction = possible_reactions[random.randint(0,len(possible_reactions))]
            
            self.rr = ReacRequest(self,target_reaction)
            for neg in self.neighbours:
                if neg.rr != None and is_in_reac_requirements(neg.particle,target_reaction):
                    max_particle_amount = None
                    for req in target_reaction["requirement"]:
                        if req[1] == neg.particle:
                            max_particle_amount = req[0]
                    current_particle_amount = 0
                    for unit in self.rr.units.keys():
                        if unit.particle == neg.particle:
                            current_particle_amount += 1
                    if max_particle_amount > current_particle_amount:
                        neg.rr = self.rr
                        self.rr[neg] = False
            self.rr.close_unit(self)
        

    def draw(self,win):
        pygame.draw.rect(win,self.color,(self.x,self.y,side,side))


#==============================================PROGRAM===============================================

print("generating the terrain matrix...")
terrain = [] #the actual world chemical composition matrix
for y in range(0,len(world)):
    row = []
    #gets the element from the world matrix and sets it in to the correspondent unit in the terrain matrix
    for x in range(0,len(world[0])):
        row.append(Unit(world[x][y], x*side, y*side, terrain, x,y))
    terrain.append(row)

for y in range(0,len(world)):
    for x in range(0,len(world[0])):
        terrain[x][y].calc_neighbours()
print("done generating the terrain matrix")

    
def updateGFX():
    for row in terrain:
        for unit in row:
            unit.draw(win)
    pygame.display.update()


print("starting the mainloop...\n\n\nTABLE OF ELEMENTS:\n")
print_elem_list(elements)

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    updateGFX()

print("\n\nexited the mainloop")
print("exiting code sequence...")
pygame.quit()

