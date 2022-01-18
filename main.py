import itertools
from itertools import chain
import graphviz
import pm4py


class AlphaMiner(object):

    def __init__(self, FILE_PATH):
        self.filename_without_extension = FILE_PATH.removeprefix('uploads/').removesuffix('.xes')
        self.event_log = pm4py.read_xes(FILE_PATH)
        self.event_name_list = self.step_1_TL()
        self.follow_pairs = self.give_follow_pairs()
        self.causal_pairs = self.give_causal_pairs()
        self.independent_pairs = self.give_independent_pairs()
        self.relations = self.give_relation_matrix()



    # Step1 : returns all present activity names in the event log
    def step_1_TL(self):
        # empty list holding all present event names.
        TL = []
        # take every trace from the event log
        for trace in self.event_log:
            # traverse every event within a trace
            for i in range(len(trace)):
                # in each event, get access to its activity name
                name = trace[i]['concept:name']
                # add the activity name to the list if not yet present
                if name not in TL:
                    TL.append(name)
        return TL

    # Step 2: returns names of all start nodes
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

    # Step 3: returns names of all final activity nodes
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

    # create a list of all pairs of event names with follow relations
    def give_follow_pairs(self):
        follow_pairs = []
        # take every trace from the event log
        for trace in self.event_log:
            # traverse every event within a trace
            for i in range(len(trace) - 1):
                # in each event, get access to the activity name
                event_name1 = trace[i]['concept:name']
                event_name2 = trace[i + 1]['concept:name']
                # we consider only pairs with event_name1 != event_name2 (event transition ignored)
                # (for ex: flyerinstances.xes have events of the same activity but of different transitions.
                if (event_name1, event_name2) not in follow_pairs and event_name1 != event_name2:
                    follow_pairs.append((event_name1, event_name2))
        return follow_pairs

    # This function returns the relation status between 2 certain event names
    def get_relation_status_of(self, event_name1, event_name2):
        return self.relations[event_name1][event_name2]

    # This function returns a list of all independent pairs
    def give_independent_pairs(self):
        pairs = list()
        follows = self.follow_pairs
        # create a list of combinations holding all pairs of event names.
        combinations = list(itertools.combinations(self.step_1_TL(), 2))
        for x, y in combinations:
            # x and y don't follow each other
            if (x, y) not in follows and (y, x) not in follows:
                # both (x,y) and (y,x) not added
                if (x, y) not in pairs and (y, x) not in pairs:
                    pairs.append((x, y))
        return pairs

        # This function returns a list of all causal pairs

    # This function returns a list of all causal pairs
    def give_causal_pairs(self):
        pairs = list()
        follows = self.follow_pairs
        # create a list of permutations of all pairs of event names
        permutations = list(itertools.permutations(self.step_1_TL(), 2))
        for x, y in permutations:
            if (x, y) in follows and (y, x) not in follows:
                pairs.append((x, y))
        return pairs

    # create a relation matrix storing relation status between all event pairs
    def give_relation_matrix(self):
        event_name_list = self.event_name_list
        relations = dict()
        # create keys using event names as matrix rows
        for event_name in event_name_list:
            # the value of each key is again a dictionary
            relations[event_name] = dict()
            # at first, assign each record of matrix a none value.
            for e in event_name_list:
                relations[event_name][e] = None
        # traverse matrix rows
        for row in relations.keys():
            # traverse matrix column
            for col in relations[row].keys():
                # we handle only records with none values
                if relations[row][col] == None:
                    if row == col:
                        # relation between any event with itself is independent
                        relations[row][col] = "independent"
                    else:
                        pair = (row, col)
                        # if for this pair no relations determined yet.
                        if relations[col][row] == None:

                            # if the pair is of causal relation
                            if pair in self.causal_pairs:
                                relations[row][col] = "causal"
                                relations[col][row] = "reverse-causal"
                            # if the pair is of reverse-causal relation
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
        return relations

    # This function returns all event names as second element in a follow relation to a certain event name
    def give_right_causal_elements(self, event_name):
        right_causals = list()
        for x,y in self.causal_pairs:
            if x == event_name:
                right_causals.append(y)
        return right_causals

    # This function can check if an element can be added to an independent list, keeping
    # the list still remaining independent afterwards.
    def can_add_keep_independent(self, event_name, list):
        if list == None:
            list = list()
        # return false if event name already contained in list
        if event_name in list:
            return False
        else:
            for other_event_name in list:
                # if other_event_name not in independent relation to a certain element in list.
                if self.get_relation_status_of(event_name, other_event_name) != "independent":
                    return False
        return True

    # this function returns a power set of a given set of elements (set of subsets)
    def powerset(self, iterable):
        result = list(chain.from_iterable(list(itertools.combinations(iterable, r) for r in range(len(iterable) + 1))))
        # result is modified during loops
        for tuple in result[:]:
        # filter out subsets with only one single element and the empty subset
            if len(tuple) < 2:
               result.remove(tuple)
        return result

    # this function checks if a given set of elements is independent (only holding elements independent from each other)
    def check_independence_set(self, l):
        # if iterable l has only 2 elements
        if len(l) == 2:
            return self.get_relation_status_of(l[0], l[-1]) == "independent"
        # else, l has more than 2 elements:
        pairs = itertools.combinations(l, r=2)
        for pair in pairs:
            if self.get_relation_status_of(pair[0],pair[-1]) != "independent":
                return False
        return True


# step 4, responsible for building up XL, which contains pairs of sets like (A,B), meeting 2 requirements:
        # 1. All event names within a set (A or B) must be independent from each other.
        # 2. Every event name in A must be in causal relation to any event name in B.
    # step 4 is divided into 3 substeps:
    # Substep a: builds pairs (A,B) with A and B each having only one element.
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
            # we build a set holding all right-causal elements of x
            right_causals = self.give_right_causal_elements(x)
            # we build a power set of the right-causals set
            powerset = self.powerset(right_causals)
            # traverse every subset in powerset:
            for subset in powerset:
                # if all elements in the tuple are independent from each other:
                if self.check_independence_set(subset):
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
            A = []
            B = []
            # for every right-causal element of x
            for x_right in self.give_right_causal_elements(x):
                # if y -> x_right (causal)
                if self.get_relation_status_of(y, x_right) == "causal":
                    # and if x_right not yet added to B as well as can be added to B, keeping B independent
                    if self.can_add_keep_independent(x_right, B):
                        B.append(x_right)
            # ultimately, we only add A,B to the result, if B is not empty
            if B:
                A += [x, y]
                # add tuple of (A,B) to the result
                result.append((A, B))
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
            # consider only pairs in which A or B has at least 2 elements
            if len(A) > 1 or len(B) > 1:
                # turn lists A,B into sets for easier handling
                set_A = set(A)
                set_B = set(B)
                # traverse the list again and consider elements different from the above pair (A,B)
                for _A,_B in result[:]:
                    # turn lists into sets
                    set__A = set(_A)
                    set__B = set(_B)
                    # if the same element is being traversed, then skip to the next loop
                    if _A == A and _B == B:
                        continue
                    # if a subset is traversed, then remove it as not-maximal element
                    else:
                        if set__A.issubset(set_A) and set__B.issubset(set_B):
                            result.remove((_A,_B))
        return result


    # create names for place nodes
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

    # Step6: create and add places into between pairs of nodes.
    # return a list of all present place nodes consisting of initial and final place too.
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

    # Step7
    # now, we want to create pairs of event nodes and place nodes connected.
    def step_7_FL(self):
        FL = []
        step_5_result = self.step_5_YL()
        i = 1
        # traverse over list
        for tuple in step_5_result:
            # the place
            place = f"p{i}"
            # left element
            for ele in tuple[0]:
                FL.append((ele, place))
            # right element
            for ele in tuple[-1]:
                FL.append((place, ele))
            i = i + 1
        # adding places connected with source and sink nodes
        source_nodes = self.step_2_TI()
        sink_nodes = self.step_3_TO()
        # link start place with each source node
        for source in source_nodes:
            FL.append(('start', source))
        # link end place with each sink node
        for sink in sink_nodes:
            FL.append((sink, 'end'))
        return FL


    # gather TL, PL and FL together
    # Step8
    def step_8(self):
        # all transitions
        TL = self.step_1_TL
        # all places
        PL = self.step_6_PL()
        # all flows (arcs)
        FL = self.step_7_FL()
        return (PL, TL, FL)

    # This function draws and returns a Petri net diagram
    def draw_diagram(self):
        # create a graph object with name of the file containing the diagram.
        g = graphviz.Digraph(filename='Petri_net_model', graph_attr={'rankdir': 'LR'})

        # now, we create the edges between transition and place nodes
        # set of all present flows (arcs):
        flows = self.step_7_FL()
        # traverse over each flow
        for flow in flows:
            # if the first node of the flow is a source node
            if flow[0] == 'start':
                # the left node is a source node, hence has a circle shape
                g.node(name=flow[0], shape='circle')
                # the right node is therefore a transition node, and has a rectangle shape
                g.node(name=flow[-1], shape='rect')
            # if the right node of the flow is a sink node
            elif flow[-1] == 'end':
                # the right node is a sink node, hence has a circle shape
                g.node(name=flow[-1], shape='circle')
                # the left node is therefore a transition node, hence has a rectangle shape
                g.node(name=flow[0], shape='rect')
            # if the left element in a flow is a normal place node
            # (its name must start with the character 'p' and have only 2 characters)
            elif flow[0][0] == 'p' and len(flow[0]) == 2:
                # the left node is a place node, hence holds a circle shape
                g.node(name=flow[0], shape='circle')
                # the right node is a transition node, hence holds a rectangle shape
                g.node(name=flow[-1], shape='rect')
            else:
                # the left node is a transition node, hence holds a rectangle shape
                g.node(name=flow[0], shape='rect')
                # the right node is a place node, hence holds a circle shape
                g.node(name=flow[-1], shape='circle')
            # relate 2 nodes above via an edge
            g.edge(tail_name=f"{flow[0]}", head_name=f'{flow[-1]}')

        # output the diagram to a file called filename and specify the directory where it is located.
        g.render(directory='graph-output', format='pdf', outfile=f'graph-output/{self.filename_without_extension}.pdf')


FILE_PATH = 'uploads/L1.xes'
#FILE_PATH = 'uploads/L2.xes'
#FILE_PATH = 'uploads/L3.xes'
#FILE_PATH = 'uploads/L4.xes'
#FILE_PATH = 'uploads/L5.xes'
#FILE_PATH = 'uploads/L6.xes'
#FILE_PATH = 'uploads/L7.xes'
#FILE_PATH = 'uploads/billinstances.xes'
#FILE_PATH = 'uploads/flyerinstances.xes'
#FILE_PATH = 'uploads/posterinstances.xes'
#FILE_PATH = 'uploads/running-example.xes'


al_miner = AlphaMiner(FILE_PATH)
al_miner.draw_diagram()
