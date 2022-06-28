import pickle, json, os, copy, shutil
from particle_related_classes import *

def save_progress(data,dirname='world saves',safe=[2,3]):
    '''
    Saves a world into a directory data structure, in the saves folder, using the variable world_data (to be put in the data parameter).

    Safe parameter activates various procedures to avoid losing important data:
        0 - no safe measures
        1 - print the data in the console
        2 - create a backup of the folder if possible
        3 - in case of error prints the unsaved data

    Saving the data makes the data dictionary unusable, if the dictionary needs to be used more in the code use the syntax:
        world_data = save_progress(world_data, dirname)
    '''
    if 2 in safe:
        try:
            shutil.copytree('saves/' + dirname, 'saves/' + dirname + ' - backup')
        except FileNotFoundError:
            print("a backup of the world could not be created")

    backup_data = copy.deepcopy(data)
    if 1 in safe:
        for key, value in backup_data.items():
            print(key)
            print(value)
            print()
            
    if not os.path.exists('saves/'+dirname): #makes the world folder
        os.makedirs('saves/'+dirname)

    safe_test = True
    try:
        V_file = open('saves/'+dirname+'/version.txt','w') #saves the version in txt format
        V_file.write(data["version"])
        V_file.close()
        data.pop("version")
        safe_test = False
    finally:
        if 3 in safe and safe_test:
            print(data)
        safe_test = True

    try:
        elems_file = open('saves/'+dirname+'/elements.json','w') #saves the element list in json format
        data["elements"] = [elem.lean_form for elem in data["elements"]] #converts everything into lean form
        elems_file.write(json.dumps(data["elements"]))
        elems_file.close()
        data.pop("elements")
        safe_test = False
    finally:
        if 3 in safe and safe_test:
            print(data)
        safe_test = True

    try:
        comps_file = open('saves/'+dirname+'/compounds.json','w') #saves the compound list in json format
        if data["compounds"]:
            data["compounds"] = [comp.lean_form for comp in data["compounds"]] #converts everything into lean form
        comps_file.write(json.dumps(data["compounds"]))
        comps_file.close()
        data.pop("compounds")
        safe_test = False
    finally:
        if 3 in safe and safe_test:
            print(data)
        safe_test = True

    try:
        reacs_file = open('saves/'+dirname+'/reactions.json','w') #saves the reaction list in json format
        if data["reactions"]:
            for reac in data["reactions"]:
                for prod in reac["product"]: #prod is in form of [int,compound in lean form]
                    prod[1] = prod[1].lean_form
                for req in reac["requirements"]: #req too
                    req[1] = req[1].lean_form
        reacs_file.write(json.dumps(data["reactions"]))
        reacs_file.close()
        data.pop("reactions")
        safe_test = False
    finally:
        if 3 in safe and safe_test:
            print(data)
        safe_test = True

    try:
        ratios_file = open('saves/'+dirname+'/ratios.json','w') #saves the ratios list in json format
        data["ratios"] = [[rt[0],rt[1].lean_form] for rt in data["ratios"]]
        ratios_file.write(json.dumps(data["ratios"]))
        ratios_file.close()
        data.pop("ratios")
        safe_test = False
    finally:
        if 3 in safe and safe_test:
            print(data)
        safe_test = True

    try:
        terrain_file = open('saves/'+dirname+'/terrain.json','w') #saves the world matrix in json format
        if data["world"]:
            for row,particles in enumerate(data["world"]):
                for col,particle in enumerate(particles):
                    data["world"][row][col] = particle.lean_form
        terrain_file.write(json.dumps(data["world"]))
        terrain_file.close()
        data.pop("world")
        safe_test = False
    finally:
        if 3 in safe and safe_test:
            print(data)
        safe_test = True

    try:
        temperature_file = open('saves/'+dirname+'/temperatures.json','w') #saves the temperature matrix in json format
        temperature_file.write(json.dumps(data["temperature"]))
        temperature_file.close()
        data.pop("temperature")
        safe_test = False
    finally:
        if 3 in safe and safe_test:
            print(data)
        safe_test = True

    save_file = open('saves/'+dirname+'/general data.p','wb') #saves the rest with pickle
    pickle.dump(data,save_file)
    save_file.close()

    print("\n\nsaved progress in: saves/"+dirname+"\n\n")
    return backup_data

def load_progress(dirname='world saves'):
    '''
    Loads some world data from a world directory speciied in dirname.
    '''
    load_file = open('saves/'+dirname+'/general data.p','rb') #loads the general data first
    data = pickle.load(load_file)
    load_file.close()

    V_file = open('saves/'+dirname+'/version.txt','r') #loads the version
    data["version"] = V_file.read()
    V_file.close()
    
    elems_file = open('saves/'+dirname+'/elements.json','r') #loads the element list
    data["elements"] = json.loads(elems_file.read())
    elems_file.close()
    data["elements"] = [Element(elem) for elem in data["elements"]] #converts from lean form to class

    comps_file = open('saves/'+dirname+'/compounds.json','r') #loads the compound list
    data["compounds"] = json.loads(comps_file.read())
    comps_file.close()
    if data["compounds"]:
        data["compounds"] = [Compound(comp) for comp in data["compounds"]] #converts from lean form to class
    else:
        print('warning: the compounds list is missing')

    reacs_file = open('saves/'+dirname+'/reactions.json','r') #loads the reaction list
    data["reactions"] = json.loads(reacs_file.read())
    reacs_file.close()
    if data["reactions"] != None:
        for reac in data["reactions"]:
            for prod in reac["product"]: #prod is in form of [int,compound in lean form]
                prod[1] = make_particle(prod[1],data["elements"],data["compounds"])
            for req in reac["requirements"]:
                req[1] = make_particle(req[1],data["elements"],data["compounds"])
    else:
        print('warning: the reactions list is missing')

    ratios_file = open('saves/'+dirname+'/ratios.json','r') #loads the ratios dict
    data["ratios"] = json.loads(ratios_file.read())
    ratios_file.close()
    if data["ratios"]: #converts the colors of the compounds in tuples and converts the ratio list into a dict {particle:amount}
        for ratio in data["ratios"]:
            ratio[1]["color"] = tuple(ratio[1]["color"])
        data["ratios"] = [[ratio[0], make_particle(ratio[1],data["elements"],data["compounds"])] for ratio in data["ratios"]]
    else:
        print('warning: the ratio list is missing')

    terrain_file = open('saves/'+dirname+'/terrain.json','r') #loads the world matrix
    data["world"] = json.loads(terrain_file.read())
    terrain_file.close()
    if data["world"]:
        for row,particles in enumerate(data["world"]):
            for col,particle in enumerate(particles):
                data["world"][row][col] = make_particle(particle,data["elements"],data["compounds"])
    else:
        print('warning: the world matrix is missing')

    temperature_file = open('saves/'+dirname+'/temperatures.json','r') #loads the temperature matrix
    data["temperature"] = json.loads(temperature_file.read())
    temperature_file.close()

    print("\n\nloaded progress from: saves/"+dirname+" in version "+data["version"]+"\n\n")
    return data


class WorldVersion: #just to ordinately write the world version and compare it to other world versions
    def __init__(self, main='0', secondary='0', third='0'):
        self.main = main
        self.secondary = secondary
        self.third = third

        if third == '0':
            self.String = 'v' + main + '.' + secondary
        else:
            self.String = 'v' + main + '.' + secondary + '.' + third

        self.List = self.String.split('.')

    def __eq__(self,other):
        if self.main == other.main and self.secondary == other.secondary and self.third == other.third:
            return True
        else:
            return False

    def __ne__(self,other):
        if self == other:
            return False
        else:
            return True

    def __gt__(self,other):
        if self.main > other.main:
            return True        
        elif self.main == other.main:
            if self.secondary > other.secondary:
                return True            
            elif self.secondary == other.secondary:
                if self.third > other.third:
                    return True
                else:
                    return False               
            else:
                return False           
        else:
            return False

    def __lt__(self,other):
        if (not self > other) and (not self == other):
            return True
        else:
            return False

    def __ge__(self,other):
        if self > other or self == other:
            return True
        else:
            return False

    def __le__(self,other):
        if self < other or self == other:
            return True
        else:
            return False

    def override(self, string):
        self.List = string[1:].split('.')
        
        assert_mess = "".join(["WorldVersion class cannot have the string  ",
                       string,
                       " as parameter. String is not correspondent to a version number of type main.secondary.third"])
        assert len(self.List) <= 3, assert_mess

        self.main = self.List[0]
        self.secondary = self.List[1]
        if len(self.List) == 3:
            self.third = self.List[2]
        else:
            self.third = '0'

        if self.third == '0':
            self.String = 'v' + self.main + '.' + self.secondary
        else:
            self.String = 'v' + self.main + '.' + self.secondary + '.' + self.third

def toWorldVersion(string): #converts a string to a WorldVersion object
    version = WorldVersion()
    version.override(string)
    if string[0] != 'v':
        version.override('v'+string)
    return version
