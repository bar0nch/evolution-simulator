import pickle, json, os
from particle_related_classes import *

def save_progress(data,dirname='world saves'):
    '''
    Saves a world into a directory data structure, in the saves folder, using the variable world_data (to be put in the data parameter).
    '''
    backup_data = {i:n for i,n in data.items()}
    if not os.path.exists('saves/'+dirname): #makes the world folder
        os.makedirs('saves/'+dirname)

    V_file = open('saves/'+dirname+'/version.txt','w') #saves the version in txt format
    V_file.write(data["version"])
    V_file.close()
    data.pop("version")

    elems_file = open('saves/'+dirname+'/elements.json','w') #saves the element list in json format
    data["elements"] = [elem.lean_form for elem in data["elements"]] #converts everything into lean form
    elems_file.write(json.dumps(data["elements"]))
    elems_file.close()
    data.pop("elements")

    comps_file = open('saves/'+dirname+'/compounds.json','w') #saves the compound list in json format
    if data["compounds"]:
        data["compounds"] = [comp.lean_form for comp in data["compounds"]] #converts everything into lean form
    comps_file.write(json.dumps(data["compounds"]))
    comps_file.close()
    data.pop("compounds")

    reacs_file = open('saves/'+dirname+'/reactions.json','w') #saves the reaction list in json format
    if data["reactions"]:
        for reac in data["reactions"]:
            for prod in reac["product"]: #prod is in form of [int,compound in lean form]
                prod[1] = prod[1].lean_form
    reacs_file.write(json.dumps(data["reactions"]))
    reacs_file.close()
    data.pop("reactions")

    ratios_file = open('saves/'+dirname+'/ratios.json','w') #saves the ratios list in json format
    if data["ratios"]:
        data["ratios"] = [[val,key.lean_form] for key, val in data["ratios"].items()]
    ratios_file.write(json.dumps(data["ratios"]))
    ratios_file.close()
    data.pop("ratios")

    terrain_file = open('saves/'+dirname+'/terrain.json','w') #saves the world matrix in json format
    if data["world"]:
        for row,particles in enumerate(data["world"]):
            for col,particle in enumerate(particles):
                data["world"][row][col] = particle.lean_form
    terrain_file.write(json.dumps(data["world"]))
    terrain_file.close()
    data.pop("world")

    save_file = open('saves/'+dirname+'/general data.p','wb') #saves the rest with pickle
    pickle.dump(data,save_file)
    save_file.close()

    world_data = {i:n for i,n in backup_data.keys()}
    print("\n\nsaved progress in: saves/"+dirname+"\n\n")

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
    else:
        print('warning: the reactions list is missing')

    ratios_file = open('saves/'+dirname+'/ratios.json','r') #loads the ratios dict
    data["ratios"] = json.loads(ratios_file.read())
    ratios_file.close()
    if data["ratios"]: #converts the colors of the compounds in tuples and converts the ratio list into a dict {particle:amount}
        for ratio in data["ratios"]:
            ratio[1]["color"] = tuple(ratio[1]["color"])
        data["ratios"] = {make_particle(ratio[1],data["elements"],data["compounds"]):ratio[0] for ratio in data["ratios"]}
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
