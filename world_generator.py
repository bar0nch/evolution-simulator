import random
from particle_related_classes import *
from world_manager import *

curveY1 = '(1000-10*x)/(10+x)'     #different curves control the variability of element percentages order
curveY2 = '(3850-38.5*x)/(38.5+x)' #it is mainly to prevent or cause a regular decreascence between the percentages
curveY3 = '(10000-100*x)/(100+x)'
curveY4 = '-x+100'
perc_curveY = curveY3 #the curve used


def y_in_curve_for_x(x, curveY_eq=perc_curveY):
    return eval(curveY_eq,{"x":x})


def create_element_list(names, shorthands, colors, melting_points):
    global element_perc_affinity
    
    #first element getting called in the loop by [i-1]
    elements = [{"name":names[0], "shorthand":shorthands[0], "color":colors[0], "perc num":0, "melting point":melting_points[0]}]
    
    for i in range(1, len(names)):
        prec_percnum = elements[i-1]["perc num"]
        new_perc_num = random.uniform(prec_percnum, 100 - (100 - prec_percnum) / element_perc_affinity)
        elements.append({"name":names[i],"shorthand":shorthands[i], "color":colors[i], "perc num":new_perc_num, "melting point":melting_points[i]})
        
    elements.append(elements.pop(0)) #moving the first element at the top and filling the
    elements[-1]["perc num"] = 100   #last percentage gap assigning his perc num to 100
    '''
    The perc num is just a random point in the x axys that will return the y value of the point of
    intersection between the curve equation and x = perc num. The interval in which the y value
    stands represents the element selected by the Unit when it needs to assign one to itself.
    '''

    point0x = 0 #calculating the interval in the graph to get the element distribution percentage in the world
    for elem in elements:
        pointFx = elem["perc num"]
        point0y = y_in_curve_for_x(point0x)
        pointFy = y_in_curve_for_x(pointFx)

        elem["distribution"] =  str(point0y - pointFy) + '%'
        
        point0x = elem["perc num"]
    
    return [Element(elem) for elem in elements] #the function is old so operations are done in
                                                #lean form and converted after

def create_reactionsRatiosCompounds_data(element_list):
    pass


def generate_world(w, h, element_list=None, output="indirect"):
    '''
    generates a world matrix of width w and height h
    

    element list   -  [ element_data structure ]
    is the list containing the elements to fill the matrix cells

    output         -  "direct" ; "indirect"
    select direct mode if the output will be displayed in the console
    '''
    world = []
    if element_list == None:
        elements = create_element_list()
    else:
        elements = element_list
    
    for i in range(0,w): #assigns the elements to the cells
        raw = []
        for j in range(0,h):
            generator = random.uniform(0,100) #a random value that stands in an element interval
            element = None
            for element in elements:
                if y_in_curve_for_x(generator) < element.perc_num:
                    if output == "direct": #ideal for console output
                        raw.append(element.shorthand) #fills the matrix with the elements shorthand
                    elif output == "indirect": #ideal for the other calculations
                        raw.append(element) #fills the matrix with the elements themselves
                    break
                    
        world.append(raw)

    return world


if __name__ == '__main__':
    V = (0,2,2) #version of the world (just for priming, to get the WorldVersion object use VERSION)
    element_perc_affinity = 4 #lower this value (>1) to prevent very common and very rare elements
    
    if len(V) < 3:
        VERSION = WorldVersion(str(V[0]),str(V[1]))
    else:
        VERSION = WorldVersion(str(V[0]),str(V[1]),str(V[2]))
    names = []
    shorthands = []
    colors = []
    melting_points = []

    w = int(input("\n\ninsert grid width: "))
    h = w
    side = int(input("insert unit size: "))
    spacing = int(input("insert spacing beetween cells: "))

    max_particle_ratio = int(input("\ninsert max amount of particles in a compound (must be either 4 or 8): "))
    elem_num = int(input("\ninsert the number of elements in this world: "))
    
    for elem in range(0,elem_num):
        names.append(input("insert an element name: "))
        shorthands.append(input("insert the element's shorthand: "))
        print()
    print("")

    if input("\ndo you want to choose elements color? (y if you do): ") == "y": #sets the color of every element
        for i in range(0,elem_num):
            exec("colors.append((" + input('insert color of the element '+names[i]+' red,green,blue: ') + "))")
    else:
        for i in range(0,elem_num):
            colors.append((random.randint(0,255),random.randint(0,255),random.randint(0,255)))

    if input("\ndo you want to choose elements melting point? (y if you do): ") == "y": #sets the melting point of every element
        for i in range(0,elem_num):
            exec("melting_points.append((" + input('insert melting point of the element '+names[i]+' int: ') + "))")
    else:
        for i in range(0,elem_num):
            melting_points.append(random.randint(-200,2000))

    elements = create_element_list(names, shorthands, colors, melting_points)
    world = generate_world(w, h, elements) #*just to be saved in world_data otherwise if the same list is used for
                                           # both processing and saving a bug causing their overlap will occour
    temperatures = []
    for y in range(0,len(world)):
        row = []
        for x in range(0,len(world[0])):
            row.append(0)
        temperatures.append(row)

    world_data = {"version":VERSION.String,
                  "elements":elements,
                  "compounds":None, #these NoneType factors must be modified in the respective json file
                  "reactions":None, #until the function create_reactionsRatiosCompounds_data is created
                  "ratios":None,
                  "w":w,
                  "h":h,
                  "side":side,
                  "spacing":spacing,
                  "max particle ratio":max_particle_ratio,
                  "world":world[:],
                  "temperature":temperatures}

    save_progress(world_data,input("\n\ntype the world name: "))
