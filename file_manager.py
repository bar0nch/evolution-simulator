import pickle, json, os
from world_manager import *


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


def calculate_compound_color(compound,elem_list=None,comp_list=None):
    ratio = {}
    denominator = 0
    
    if compound["name"][0] != '(': #if the name is not a tuple inside a string
        for elem in elem_list:
            if compound["name"].find(elem["shorthand"]) == -1:
                continue
            denominator += int(compound["name"][compound["name"].find(elem["shorthand"]) + len(elem["shorthand"])])
            ratio.setdefault(elem["shorthand"],int(compound["name"][compound["name"].find(elem["shorthand"]) + 1]))
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
        
