'''
Produce slice from pdg.
'''
import re
import copy
import bitarray

import parseutility2 as pu
import config

class nodes:
    def __init__(self, line_number):
        self.node_id = line_number
        self.from_node = []                     #in
        self.to_node = []                       #out

def fnv1a_hash(string):
    '''
    FNV-1a 32bit hash (http://isthe.com/chongo/tech/comp/fnv/)
    '''
    hash = 2166136261
    for c in string:
        hash ^= ord(c)
        hash *= 16777619
        hash &= 0xFFFFFFFF
    hash = hash & (config.bloomfilter_size-1)
    return hash

def produce_slice_hash(FileName, slice_content):
    '''
    slice_content: String. original slice.
    FileName: String
    return the hash value of abstracted and normalized function slice.
    '''
    function = pu.parseFile_deep(FileName)
    if len(function) == 0:
        print "The file <", FileName, "> has ", len(function), " funcitons."
        return ""
    if len(function) != 1:
        print "The file <", FileName, "> has ", len(function), " funcitons."
    absSlice = pu.removeComment(absSlice)
    absSlice = pu.abstract_slice(slice_content, function[0].variableList)
    absSlice = pu.normalize(absSlice)
    hash_value = fnv1a_hash(absSlice)
    
    return [hash_value, absSlice]

def produce_funcBody_hash(FileName):
    '''
    return the hash value of abstracted and normalized function Body.
    '''
    function = pu.parseFile_deep(FileName)
    if len(function) == 0:
        print "The file <", FileName, "> has ", len(function), " funcitons."
        return ""
    if len(function) != 1:
        print "The file <", FileName, "> has ", len(function), " funcitons."
    absBody = pu.abstract(function[0], 4)[1]
    absBody = pu.normalize(absBody)
    hash_value = fnv1a_hash(absBody)
    
    #print "hash_value:", hash_value
    #print "absBody", absBody
    return [hash_value, absBody]

def get_nodes(line_pair, nodes_id):
    '''
    return a dictory of nodes.
    {node_id1: nodes1, nodes_id2: nodes2, ...}
    '''
    node_list = []
    for node in nodes_id:
        temp = nodes(node)
        for pair in line_pair:
            if pair[0] == node:
                temp.to_node.append(pair[1])
            elif pair[1] == node:
                temp.from_node.append(pair[0])
        temp.from_node = list(set(temp.from_node))
        temp.to_node = list(set(temp.to_node))
        node_list.append(temp)
    result = {}
    for i in node_list:
        result[i.node_id] = i
    return result

def get_slice_of_node(nodes_dict, node_id):
    '''
    nodes_dict: {node_id1: nodes1, nodes_id2: nodes2, ...}
    node_id: return the slice about node with node_id
    
    return type: list. eg: [node_id1, node_id2, ... ,node_idn]
    '''
    queue_out = [node_id]
    queue_in = [node_id]
    result = []
    
    copy_nodeDict = copy.deepcopy(nodes_dict)    
    while queue_out:
        current_node = queue_out[0]
        queue_out = queue_out[1:]
        result.append(current_node)
        queue_out.extend(copy_nodeDict[current_node].to_node)
        copy_nodeDict[current_node].to_node = []
        
    while queue_in:
        current_node = queue_in[0]
        queue_in = queue_in[1:]
        result.append(current_node)
        queue_in.extend(copy_nodeDict[current_node].from_node)
        copy_nodeDict[current_node].from_node = []
    
    result = list(set(result))
    return result

def slice_from_project(lines_numbers):
    '''
    lines_numbers(String) looks like: (29,30)(32,41)(41,42)(37,37)(32,55)
    return a dictory record each lines_numbers' slice.
    '''
    pattern = r"(\d+,\d+)"
    line_pair = []
    for i in re.findall(pattern, lines_numbers):
        temp = []
        temp.append(int(i.split(',')[0]))
        temp.append(int(i.split(',')[1]))
        if temp[0] == temp[1]:
            continue
        line_pair.append(temp)
    nodes_id = [i for j in line_pair for i in j]
    nodes_id = list(set(nodes_id))
    
    #print "1-1111111"
    nodes_dic = get_nodes(line_pair, nodes_id)
    #print "1-2222222"
    result = {}
    #print "1-33333333"
    for node in nodes_id:
        tmp = get_slice_of_node(nodes_dic, node)
        result[node] = tmp
    #print "1-44444444"
    return result

def get_slice_content(func_content, line_numbers):
    '''
    return the slice content corresponding to the line_number(that is 'node_id')
    return type: String
    '''
    content = ""
    line_numbers.sort()
    for num in line_numbers:
        try:
            content += func_content[num-1]   #two functions have same name is posible, need to be processed.
        except IndexError:
            print "[Error] list index out of range."
            return ""
    return content