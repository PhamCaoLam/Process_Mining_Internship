import graphviz
import pm4py
import itertools
from itertools import chain, combinations
from pm4py.objects.petri_net.obj import PetriNet, Marking



class AlphaMiner(object):

    def __init__(self, FILE_PATH):
        self.filename_without_extension = FILE_PATH.removeprefix('uploads/').removesuffix('.xes')
        self.event_log = pm4py.read_xes(FILE_PATH)
        self.event_name_list = self.step_1_TL()
        self.follow_pairs = self.give_follow_pairs()
        self.causal_pairs = self.give_causal_pairs()
        self.independent_pairs = self.give_independent_pairs()
        self.relations = self.give_relation_matrix()



    # Step1 : print out all the present activity names in the event log
    def step_1_TL(self):
        # empty list holding names of all present event.
        TL = []
        # take every trace from the event log
        for trace in self.event_log:
            # traverse every event within a trace
            for i in range(len(trace)):
                # in each event, get access to the activity name
                name = trace[i]['concept:name']
                # add the activity name to the list if not yet present
                if name not in TL:
                    TL.append(name)
        return TL


    # Step 2: return the start activity names
    def step_2_TI(self):
        # create an empty set for start activities name
        start_acts = []
        # for every trace in the event log
        for trace in self.event_log:
            # take the first event from each trace out and get its activity name
            first_act = trace[0]['concept:name']
            if first_act not in start_acts:
                start_acts.append(first_act)
        return start_acts



    # Step 3: returns names of final activity nodes:
    def step_3_TO(self):
        # create an empty set for final activities name
        final_acts = []
        # for every trace in the event log
        for trace in self.event_log:
            # take the final event from each trace out and get its activity name
            final_act = trace[len(trace) - 1]['concept:name']
            if final_act not in final_acts:
                final_acts.append(final_act)
        return final_acts

    # create a list of element pairs with follow relations
    def give_follow_pairs(self):
        follow_pairs = []
        # take every trace from the event log
        for trace in self.event_log:
            # traverse every event within a trace
            for i in range(len(trace) - 1):
                # in each event, get access to the activity name
                event_name1 = trace[i]['concept:name']
                event_name2 = trace[i + 1]['concept:name']
                if (event_name1, event_name2) not in follow_pairs:
                    follow_pairs.append((event_name1, event_name2))
        return follow_pairs


    # create a relation matrix storing relation status between all event pairs
    def give_relation_matrix(self):
        event_name_list = self.event_name_list
        relations = dict()
        # create keys using event names as matrix rows
        for event_name in event_name_list:
            # each column is an empty dict
            relations[event_name] = dict()
            # in each column, define keys as event names again, and values as None
            for e in event_name_list:
                relations[event_name][e] = None
        # Now record the event relations to according matrix elements
        # traverse matrix rows
        for row in relations.keys():
            # traverse matrix column
            # print(f"row: {row}")
            for col in relations[row].keys():
                # if this matrix element is not yet filled with any value
                # print(f"col: {col}")
                if relations[row][col] == None:
                    if row == col:
                        # relation between any event with itself is independent
                        relations[row][col] = "independent"
                    else:
                        # if (row,col) and (col,row) are both None
                        # print(f"row = {row}, col = {col}")
                        pair = (row, col)
                        follow_list = self.follow_pairs
                        if relations[row][col] == None and relations[col][row] == None:
                            # if the pair shows causal relation
                            # if pair in follow_list and pair[::-1] not in follow_list:
                            if pair in self.causal_pairs:
                                relations[row][col] = "causal"
                                relations[col][row] = "reverse-causal"
                            # if the pair shows reverse-causal relation
                            # elif pair not in follow_list and pair[::-1] in follow_list:
                            elif pair[::-1] in self.causal_pairs:
                                relations[row][col] = "reverse-causal"
                                relations[col][row] = "causal"
                            # if the pair shows independence relation
                            # elif pair in follow_list and pair[::-1] in follow_list:
                            elif pair in self.independent_pairs:
                                relations[row][col] = "independent"
                                relations[col][row] = "independent"
                            # the pair must be in parallel relation
                            else:
                                relations[row][col] = "parallel"
                                relations[col][row] = "parallel"
                #else:
                    #print(f"row = {row}, col = {col} : {relations[row][col]}")
        return relations


    # Step4
    # This function returns the relation status between 2 events
    def get_relation_status_of(self, event_name1, event_name2):
        return self.relations[event_name1][event_name2]

    # This function returns a list of independent pairs
    def give_independent_pairs(self):
        pairs = list()
        follows = self.follow_pairs
        # create a list of combinations
        combinations = list(itertools.combinations(self.step_1_TL(), 2))
        for x, y in combinations:
            if (x,y) not in follows and (y,x) not in follows:
                if (x,y) not in pairs and (y,x) not in pairs:
                    pairs.append((x, y))
        return pairs

    # This function returns a list of causal pairs
    def give_causal_pairs(self):
        pairs = list()
        follows = self.follow_pairs
        # create a list of permutations
        permutations = itertools.permutations(self.step_1_TL(), 2)
        for x, y in permutations:
            if (x,y) in follows and (y,x) not in follows:
                pairs.append((x,y))
        return pairs

    # This function returns left-causal elements of a certain event
    def give_left_causal_elements(self, event_name):
        result = list()
        for x,y in self.causal_pairs:
            if y == event_name:
                list.append(x)
        return result

    # This function returns right-causal elements of a certain event
    def give_right_causal_elements(self, event_name):
        result = list()
        for x,y in self.causal_pairs:
            if x == event_name:
                result.append(y)
        #print(f"so, the list of right causal elements of {event_name} is {result}")
        return result

    # This function can check if an element can be added to an independent list, keeping
    # the list still remaining independent afterwards.

    def can_add_keep_independent(self,event_name, list):
        if list == None:
            list = list()
        if event_name in list:
            #print("event name already in list")
            return False
        else:
            for other_event_name in list:
                if self.get_relation_status_of(event_name, other_event_name) != "independent":
                    return False
        return True
    # this function returns a power set of a given set of elements
    def powerset(self, iterable):
        result = list(chain.from_iterable(list(itertools.combinations(iterable, r) for r in range(len(iterable) + 1))))
        for tuple in result[:]:
            if len(tuple) < 2:
                result.remove(tuple)
        return result

    # this function checks if a given set of elements is independent (only holding elements independent from each other)
    def check_independence_set(self, iterable):
        # iterable is pretty likely a tuple
        l = iterable
        # if iterable has 2 elements
        if len(l) == 2:
            return self.get_relation_status_of(l[0], l[-1]) == "independent"
        # else, iterable has more than 2 elements.
        pairs = itertools.combinations(l, r=2)
        for pair in pairs:
            if self.get_relation_status_of(pair[0],pair[-1]) != "independent":
                return False
        return True


# step 4, responsible for building up XL, which contains pairs of sets like (A,B), meeting 2 requirements:
        # 1. All event names in one set (A or B) must be independent from each other.
        # 2. Each event name in A must be in causal relation to each event name in B.
    # step 4 is divided into 3 substeps:
    # Substep a: builds pairs (A,B) with A and B having only one element.
    # e.g: ({a},{c})
    def step_4_a(self):
        result = []
        causals = self.causal_pairs
        for pair in causals:
            A = []
            B = []
            A.append(pair[0])
            B.append(pair[-1])
            result.append((A,B))
        return result

    # Substep b: builds pairs (A,B) with A has only one element, while B has multiple elements.
    # e.g: ({a},{c,e})
    def step_4_b(self):
        result = []
        # take every event name from the log
        for x in self.event_name_list:
            B = []
            # we build a set holding all right-causal elements of x
            right_causals = self.give_right_causal_elements(x)
            # we build a power set of the right-causals set (without the empty subset
            # and subsets that have only one element)
            powerset = self.powerset(right_causals)
            # traverse every subset in powerset:
            for subset in powerset:
                # if all elements in the tuple are independent from each other:
                if self.check_independence_set(subset) and subset not in B:
                    result.append(([x],list(subset)))
        return result

    # Substep c: builds pairs (A,B), with A containing multiple elements.
    # e.g: ({a,b},{c}), ({a,b},{c,d})
    def step_4_c(self):
        # create the result variable for storing pairs of A,B set
        result = []
        independents = self.independent_pairs
        # for every independent pair
        for x, y in independents:
            # print(f"no_name: consider independent pair ({x},{y})")
            A = []
            B = []
            # for every right-causal element of x
            for x_right in self.give_right_causal_elements(x):
                # print(f"no_name: right_causal of {x} is {x_right}")
                # if y -> x_right (causal)
                if self.get_relation_status_of(y, x_right) == "causal":
                    # print(f"{y} is also in causal relation with x_right = {x_right}")
                    # and if x_right not yet added to B as well as can be added to B, keeping B independent
                    if self.can_add_keep_independent(x_right, B):
                        B.append(x_right)
                        # print(f"so, {x_right} has just been added to B")
                # else:
                # print(f"{y} and {x_right} not in causality")
                # print(f"so now, B is {B}")
            # ultimately, we only add A,B to the result, if B is not empty
            if B:
                # print(f"B is not empty: {B}")
                # add x,y to A
                A += [x, y]
                # print("A is extended")
                # add tuple of (A,B) to the result
                result.append((A, B))
                # print(f"(A,B) were added to the result. A = {A}, B = {B}")
        return result

    # this function merges all results from the 3 substeps above:
    def step_4_XL(self):
        # result from substep a
        A = self.step_4_a()
        # result from substep b
        B = self.step_4_b()
        # result from substep c
        C = self.step_4_c()

        return A + B + C


    # Step5
    # This function simplifies XL by removing not yet maximal elements.
    def step_5_YL(self):
        result = self.step_4_XL()
        # traverse each pair (A,B)
        for A,B in result[:]:
            # consider only the pair where A or B has more than 1 elements
            if len(A) > 1 or len(B) > 1:
                #print(f"(A,B) = {(A,B)} is considered: ")
                # turn lists A,B into sets for easier handling
                set_A = set(A)
                set_B = set(B)
                #print(f"set_A = {set_A}")
                #print(f"set_B = {set_B}")
                # traverse the list again and consider elements different from the above pair (A,B)
                for _A,_B in result[:]:
                    # turn lists into sets
                    set__A = set(_A)
                    set__B = set(_B)
                    #print(f"set__A = {set__A}")
                    #print(f"set__B = {set__B}")
                    #print(f"from current_result = {result}")
                    # if the same element is being traversed
                    if _A == A and _B == B:
                        #print(f"the same element just traversed: {(_A,_B)} = {(A,B)} -> continue")
                        continue
                    else:
                        if set__A.issubset(set_A) and set__B.issubset(set_B):
                            #print(f"set__A = {set__A} is considered and is subset of set_A.")
                            #print(f"set__B = {set__B} is considered and is subset of set_B.")
                            result.remove((_A,_B))
                            #print(f"result after removing {_A} and {_B}: {result}")
        return result


    # Step6: create and add places into between pairs of nodes.
    def create_name_for_place_of(self, tuple_of_nodes):
        # the left side
        A = tuple_of_nodes[0]
        # the right side
        B = tuple_of_nodes[-1]
        left_name = ""
        right_name = ""

        left_name = "{" + ','.join(A) + "}"
        right_name = "{" + ','.join(B) + "}"
        name = "P(" + left_name + "," + right_name + ")"
        return name

    # return a list of all present place nodes consisting of initial and finishing places too.
    def step_6_PL (self):
        step_5_result = self.step_5_YL()
        # an empty list holding all place nodes present
        PL = []
        # traverse over result of step 5:
        for tuple in step_5_result:
            # for each tuple, create a place node
            place = self.create_name_for_place_of(tuple)
            PL.append(place)
        # finally, adding initial and final places:
        PL.append('iL')
        PL.append('oL')
        return PL

    # this functions maps each place name to a sign for easier specifications later
    def map_place_names(self, places):
        i = 1
        modified_place_names = []
        # traverse over each place name
        for place in places:
            if place[0] != 'i' and place[0] != 'o':
                new_name = place[0] + str(i)
                modified_place_names.append(new_name)
                i = i + 1
        return modified_place_names


    # Step7
    # now, we want to create pairs of event nodes and place nodes connected.
    def step_7_FL(self):
        FL = []
        step_5_result = self.step_5_YL()
        print(f" step 5 result: {step_5_result}")
        i = 1
        # traverse over list
        for tuple in step_5_result:
            # the place
            #place = self.create_name_for_place_of(tuple)
            place = f"p{i}"
            i = i + 1
            # left element
            for ele in tuple[0]:
                FL.append((ele, place))
            # right element
            for ele in tuple[-1]:
                FL.append((place, ele))
        # adding places connected with source and sink nodes
        source_nodes = self.step_2_TI()
        sink_nodes = self.step_3_TO()
        for source in source_nodes:
            FL.append(('iL', source))
        for sink in sink_nodes:
            FL.append((sink, 'oL'))
        return FL


    # adding all TL, PL and FL together
    # Step8
    def step_8(self):
        # all transitions
        TL = self.step_1_TL()
        # all places
        PL = self.step_6_PL()
        # all flows (arcs)
        FL = self.step_7_FL()
        return (PL, TL, FL)

    # we want to write a function that create pairs of event node and place node
    def draw_diagram(self):
        # create a graph object with name of the file containing the diagram.
        g = graphviz.Digraph(filename='Petri_net_model', graph_attr={'rankdir': 'LR'})

        # now, we create the edges between transition and place nodes:
        # set of all present flows (arcs):
        flows = self.step_7_FL()
        # traverse over each flow
        for flow in flows:
            # if the left element in flow is a place node (its name starts with the character 'p')
            print(f"for the flow {flow}:")
            # if one of 2 nodes of the flow is a source or sink node
            if flow[0] == 'iL':
                # the left node is a source node, hence holds a circle shape
                g.node(name=flow[0], shape='circle')
                # the right node is a transition node, hence holds a square shape
                g.node(name=flow[-1], shape='square')
            elif flow[-1] == 'oL':
                # the right node is a sink node, hence holds a circle shape
                g.node(name=flow[-1], shape='circle')
                # the left node is a transition node, hence holds a square shape
                g.node(name=flow[0], shape='square')
            elif flow[0][0] == 'p' and len(flow[0]) == 2:
                print(f"the left node is circle, the right is square.")
                # the left node is a place node, hence holds a circle shape
                g.node(name=flow[0], shape='circle')
                # the right node is a transition node, hence holds a square shape
                g.node(name=flow[-1], shape='square')
            else:
                print(f"the left node is square, the right is circle.")
                # the left node is a transition node, hence holds a square shape
                g.node(name=flow[0], shape='square')
                # the right node is a place node, hence holds a circle shape
                g.node(name=flow[-1], shape='circle')
            # relate 2 nodes above via an edge
            g.edge(tail_name=f"{flow[0]}", head_name=f'{flow[-1]}')

        # output the diagram to a file called filename and specify the directory where it is located.
        g.render(view=True, directory='graph-output', format='png', outfile=f'graph-output/{self.filename_without_extension}.png')




FILE_PATH = 'uploads/L1.xes'
#FILE_PATH = 'uploads/L2.xes'
#FILE_PATH = 'uploads/L3.xes'
#FILE_PATH = 'uploads/L4.xes'
#FILE_PATH = 'uploads/L5.xes'
#FILE_PATH = 'uploads/L6.xes'
FILE_PATH = 'uploads/L7.xes'
#FILE_PATH = 'uploads/billinstances.xes'
#FILE_PATH = 'uploads/flyerinstances.xes'
#FILE_PATH = 'uploads/posterinstances.xes'
#FILE_PATH = 'uploads/running-example.xes'


al_miner = AlphaMiner(FILE_PATH)

#print(al_miner.step_4_XL())
#print(al_miner.step_5_YL())

print(f"step 7: {al_miner.step_7_FL()}")
al_miner.draw_diagram()
