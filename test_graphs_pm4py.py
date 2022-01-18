import graphviz
from main import AlphaMiner
import pm4py
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.objects.petri_net.utils import petri_utils

# in this file, we want to use pm4py module to draw Petri net for a given event log (consult youtube)
# Should i alternatively use ProM instead of pm4py ?

net = PetriNet("new_petri_net")
FILE_PATH = 'uploads/L1.xes'
event_log = pm4py.read_xes(FILE_PATH)
al = AlphaMiner(event_log)

# creating source, p_1 and sink place
source = PetriNet.Place("iL")
sink = PetriNet.Place("oL")
net.places.add(source)
net.places.add(sink)


# add the places to the Petri Net
# place = PetriNet.Place("place")
# net.places.add(place)

for _place in al.step_6_PL():
    place = PetriNet.Place(f"{_place}")
    net.places.add(place)

# Create transitions
# t_1 = PetriNet.Transition("name_1", "label_1")
for transition in al.step_1_TL:
    net.transitions.add(PetriNet.Transition(f"{transition}", f"{transition}"))


# Add arcs

#petri_utils.add_arc_from_to(source, t_1, net)

transition_place_connected = al.step_7_FL()
#for left, right in transition_place_connected:
    # if left is a transition (only one letter in name) and right is a place:


# Adding tokens
initial_marking = Marking()
initial_marking[source] = 1
final_marking = Marking()
final_marking[sink] = 1


gviz = pn_visualizer.apply(net, initial_marking, final_marking)
pn_visualizer.view(gviz)