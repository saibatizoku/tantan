from pprint import pprint

def handle_factory_db(factory, response, topicUrl):
    pprint(response, depth=2)
    evt = response
    factory.dispatch(topicUrl, evt) 
