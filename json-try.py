import json
import os

shallow_dict = {}
deep_dict = {}


def check_shallow_func(function_name):
        if function_name in shallow_dict:
            return True;

def check_deep_func(function_name):
        if function_name in deep_dict:
            return True;
    

def add_func(function_name, instrumentation_type):
    if instrumentation_type == 'deep':
        if check_deep_func(function_name) != True:
            deep_dict[function_name] = True

    if instrumentation_type == 'shallow':
        if check_shallow_func(function_name) != True:
            shallow_dict[function_name] = True

    return;



def init_json():
    global shallow_dict 
    global deep_dict
    if os.path.exists('shallow.json'):
        shallow_dict = json.load(open('shallow.json'))
    if os.path.exists('deep.json'):
        deep_dict = json.load(open('deep.json'))
    #for i in shallow_dict:
    #    print i
    #for i in deep_dict:
    #    print i
    

def finished_json():
    #for i in shallow_dict:
    #    print i
    #for i in deep_dict:
    #    print i
    with open('deep.json', 'w') as outfile:
          json.dump(deep_dict, outfile)
    with open('shallow.json', 'w') as outfile:
          json.dump(shallow_dict, outfile)



if name == '__main__' :
    init_json()
    add_func('main1','deep')
    add_func('main1','shallow')
    add_func('test1','deep')
    add_func('mytest1','shallow')
    add_func('foo1','deep')
    add_func('bar1','shallow')
    finished_json()

