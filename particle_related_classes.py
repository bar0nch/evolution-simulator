class Particle:
    def __init__(self, name, color):
        self.name = name
        self.color = tuple(color)
        self.lean_form = {"name":self.name, "color":self.color}

class Element(Particle):
    def __init__(self,*args):
        if type(args[0]) == dict: #args passed in lean form
            super().__init__(args[0]["name"],args[0]["color"])
            self.shorthand = args[0]["shorthand"]
            self.perc_num = args[0]["perc num"]
            self.distribution = args[0]["distribution"]
            self.lean_form = args[0]
        else:
            super().__init__(args[0],args[1])
            self.shorthand = args[2]
            self.perc_num = args[3]
            self.distribution = args[4]
            self.lean_form["shorthand"] = args[2]
            self.lean_form["perc num"] = args[3]
            self.lean_form["distribution"] = args[4]

    def __str__(self):
        return "name: " + self.name + " ("+self.shorthand+")  color: " + str(self.color) + "  distribution:" + self.distribution

class Compound(Particle):
    def __init__(self,*args):
        if type(args[0]) == dict: #args passed in lean form
            super().__init__(args[0]["name"],args[0]["color"])
            self.density = args[0]["density"]
            self.lean_form["density"] = self.density
        else:
            super().__init__(args[0],args[1])
            self.density = args[2]
            self.lean_form["density"] = self.density
            
    def __str__(self):
        return "name: " + self.name + "  color: " + str(self.color) + "  density: "+str(self.density)


def make_particle(particle,elem_list=None,comp_list=None):
    if elem_list == None and comp_list == None:
        if "perc num" in particle.keys():
            return Element(particle)
        else:
            return Compound(particle)
    elif not (elem_list == None and comp_list == None):
        if "perc num" in particle.keys():
            for elem in elem_list:
                if elem.name == particle["name"]:
                    return elem
        else:
            for comp in comp_list:
                if comp.name == particle["name"]:
                    return comp
