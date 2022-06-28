import pickle, json, os
from world_manager import *


#FUNCTIONS FOR GENERAL UTILITY
def find_by_param_in_elem_list(param, elem_list):
    for elem in elem_list:
        if elem["name"] == param:
            return elem_list.index(elem)
        elif elem["shorthand"] == param:
            return elem_list.index(elem)
        elif elem["color"] == param:
            return elem_list.index(elem)
        elif elem["perc num"] == param:
            return elem_list.index(elem)
        elif elem["distribution"] == param:
            return elem_list.index(elem)
    return -1

def get_by_param_in_elem_list(param, elem_list):
    for elem in elem_list:
        if elem["name"] == param:
            return elem
        elif elem["shorthand"] == param:
            return elem
        elif elem["color"] == param:
            return elem
        elif elem["perc num"] == param:
            return elem
        elif elem["distribution"] == param:
            return elem
    return None

def find_by_param_in_comp_list(param, comp_list):
    for comp in comp_list:
        if comp["name"] == param:
            return comp_list.index(comp)
        elif comp["color"] == param:
            return comp_list.index(comp)
    return -1

def get_by_param_in_comp_list(param, comp_list):
    for comp in comp_list:
        if comp["name"] == param:
            return comp
        elif comp["color"] == param:
            return comp
    return None


#FUNCTIONS TO CREATE/EDIT WORLD PARAMETERS
def calculate_compound_color(compound,elem_list=None,comp_list=None):
    ratio = {}
    denominator = 0
    
    if compound["name"][0] != '(': #if the name is not a tuple inside a string
        for elem in elem_list:
            if compound["name"].find(elem["shorthand"]) == -1:
                continue
            denominator += int(compound["name"][compound["name"].find(elem["shorthand"]) + len(elem["shorthand"])])
            ratio.setdefault(elem["shorthand"],int(compound["name"][compound["name"].find(elem["shorthand"]) +  + len(elem["shorthand"])]))
        print(ratio)

        R = 0
        for elem in ratio:
            for i in range(0,ratio[elem]):
                R += get_by_param_in_elem_list(elem,elem_list)["color"][0]
        R //= denominator

        G = 0
        for elem in ratio:
            for i in range(0,ratio[elem]):
                G += get_by_param_in_elem_list(elem,elem_list)["color"][1]
        G //= denominator

        B = 0
        for elem in ratio:
            for i in range(0,ratio[elem]):
                B += get_by_param_in_elem_list(elem,elem_list)["color"][2]
        B //= denominator

        return R,G,B

    else:
        for comp in comp_list:
            for i in eval(compound["name"]):
                if comp["name"] in i:
                    denominator += i[0]
                    ratio.setdefault(comp["name"],i[0])

        R = 0
        for comp in ratio:
            for i in range(0,ratio[comp]):
                R += get_by_param_in_comp_list(comp,comp_list)["color"][0]
        R //= denominator

        G = 0
        for comp in ratio:
            for i in range(0,ratio[comp]):
                G += get_by_param_in_comp_list(comp,comp_list)["color"][1]
        G //= denominator

        B = 0
        for comp in ratio:
            for i in range(0,ratio[comp]):
                B += get_by_param_in_comp_list(comp,comp_list)["color"][2]
        B //= denominator

        return R,G,B
            
def create_ratios_from_reactions(reactions):
    ratios = []
    for reac in reactions:
        for req in reac["requirements"]:
            if req not in ratios:
                ratios.append(req)
    return ratios


#FUNCTIONS FOR FILE MANAGEMENT  
def clean_reaction_list(dirname, safe=True):
    load_file = open('saves/'+dirname+'/reactions.json','r')
    data = load_file.read()
    load_file.close()
    if safe:
        print("PREVIOUS DATA".center(70,'.'))
        print(data)

    data = data[: data.rfind(']')] + '\n' + data[data.rfind(']') :]

    copy = data
    while "product" in copy:
        ind = copy.find('"product"')
        data = data[:ind-1] + '\n' + data[ind-1:]
        data = data[:ind+1] + '\n' + data[ind+1:]
        copy = data
        ind += 2
        copy = ' ' * len(copy[:ind+len('"product"')]) + copy[ind+len('"product"'):]

    copy = data
    while "requirements" in copy:
        ind = copy.find('"requirements"')
        data = data[:ind] + '\n' + data[ind:]
        copy = data
        ind += 1
        copy = ' ' * len(copy[:ind+len('"requirements"')]) + copy[ind+len('"requirements"'):]

    copy = data
    while "probability" in copy:
        ind = copy.find('"probability"')
        data = data[:ind] + '\n' + data[ind:]
        copy = data
        ind += 1
        copy = ' ' * len(copy[:ind+len('"probability"')]) + copy[ind+len('"probability"'):]

    if safe:
        print("\n\n\n" + "CLEANED DATA".center(70,'.'))
        print(data)

    print("\n\ndata cleaned\n\n")
    save_file = open('saves/'+dirname+'/reactions.json','w')
    save_file.write(data)
    save_file.close()
 
def clean_compound_list(dirname, safe=True):
    load_file = open('saves/'+dirname+'/compounds.json','r')
    data = load_file.read()
    load_file.close()
    if safe:
        print("PREVIOUS DATA".center(70,'.'))
        print(data)

    evaluated = eval(data)
    data = '['
    for comp in evaluated:
        data += '\n' + str(comp) + ','
    data = data[:-2]
    data += '}\n]'
    
    if safe:
        print("\n\n\n" + "CLEANED DATA".center(70,'.'))
        print(data)

    if data == '[]':
        raise Exception("error in the function: wasn't able to decode the data. exception raised as a safety measure")

    print("\n\ndata cleaned\n\n")
    save_file = open('saves/'+dirname+'/compounds.json','w')
    save_file.write(data)
    save_file.close()

    

