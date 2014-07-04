import json
from pprint import pprint

def handle_factory_db(factory, response, topicUrl):
    pprint(response, depth=2)
    evt = response
    factory.dispatch(topicUrl, evt) 

def loadConfig(filepath):
    try:
        cfg = json.load(open(filepath, 'r'))
        pprint(cfg, depth=4)
    except:
        cfg = {}
    return cfg

def saveConfig(cfg, filepath):
    try:
        json.dump(cfg, open(filepath, 'w'), indent=4)
        pprint(cfg, depth=4)
    except:
        print "Could not save config"

def compDictKeys(a, b):
    set_a = set(a.keys())
    set_b = set(b.keys())
    return set_b.difference(set_a)
