
class D2Punkt():


    def __init__(self,koordinaten,name):
        self.koordinaten = koordinaten
        self.nachbar = None
        self.avg_k_distanz = None
        self.name = name
        self.label = None
        self.nachbar_name = set([])

    def small_copy(self, d2Punkt):
        self.koordinaten = d2Punkt.koordinaten
        self.name = d2Punkt.name
        self.avg_k_distanz = d2Punkt.avg_k_distanz




