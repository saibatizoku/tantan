###############################################################################
##
##  Copyright (C) 2012-2014 Tavendo GmbH, 
##  Modified 2014 saibatizoku
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################


def parse_water(line):
    values = [float(val) for val in line.rstrip(' \0').split() ]
    # T0, T1, T2, T3, T4, OD1, OD2, OD3, OD4 = values
    sensor_keys = [ 't0', 't1', 't2', 't3', 't4', 'od1', 'od2', 'od3', 'od4' ]
    sensors = dict(zip(sensor_keys, values))
    return sensors

def publish_node_data(session, topic, data, debug=False):
    if debug:
        print "PUBLICANDO NODO {}".format(data['node_id'])
        print "PUBLICANDO canales {}".format(topic)
    session.publish(topic['pan_id'], {'pan_id': data['pan_id'], 'node_id': data['node_id']})
    session.publish(topic['id'], {'pan_id': data['pan_id'], 'node_id': data['node_id'], 'sensores': data['json']})
    session.publish(topic['nodo'], {'pan_id': data['pan_id'], 'node_id': data['node_id'], 'sensores': data['json']})
    for k, v in data['json'].items():
        topic_sensor = u".".join([topic['nodo'], k])
        if (k.startswith("t") and v == -127.0) :
            print "{} no PUBLICADO".format(k)
        elif (k.startswith("od") and v > 100.0) :
            print "{} no PUBLICADO".format(k)
        else:
            session.publish(topic_sensor, {'pan_id': data['pan_id'], 'node_id': data['node_id'], 'sensor': k, 'value': v})
            if debug:
                print "PUBLICANDO sensor {}: {}".format(topic_sensor, v)


def handle_rx(self, packet):
    resp = {}
    resp = get_zb_node_info(self, packet)
    print "pak: {}".format(repr(packet))
    rout = "RX:"

    for (key, item) in resp.items():
        rout += "{0}-{1}:".format(key, item)
    msg = "{0}:{1}:RX:".format(resp['id'], resp['addr'], resp['data']) + repr(resp['data'])

    evt = {'id': resp['id'],
            'type': 'rx',
            'data': resp['data'],
            }

    node_id = resp['id']
    data = resp['data']
    data_lines = data.splitlines()

    for l in data_lines:
        topic = {}
        topic['id'] = u"mx.ejeacuicola.api.nodos"
        topic['nodo'] = u".".join(["mx.ejeacuicola.api.nodos", node_id])
        topic['pan_id'] = u"mx.ejeacuicola.api.redes"
        try:
            parsed = parse_water(l)
            if self.debug:
                print "PARSED: {}".format(parsed)
                print "Publicando a:\n\t{}\n\t{}\n\t{}".format(topic['pan_id'], topic['id'], topic['nodo'])
                print "Sensores: {}".format(parsed)
            if self.pan_id:
                data = {'pan_id': self.pan_id, 'node_id': node_id, 'json': parsed}
                publish_node_data(self.session, topic, data, self.debug)
            else:
                self.getPanId()
        except:
            print "FORMATO MALO: {}".format(l)

def is_target_type(self, packet, field, target):
    if field in packet and packet[field].lower() == target:
        return True
    return False

def is_AT_RESPONSE(self, packet):
    return is_target_type(self, packet, 'id', 'at_response')

def is_PANID(self, packet):
    is_atresp = is_AT_RESPONSE(self, packet)
    is_nd = is_target_type(self, packet, 'command', 'id')
    return is_atresp and is_nd

def is_RX(self, packet):
    return is_target_type(self, packet, 'id', 'rx')

def get_zb_node_info(self, packet):
    try:
        resp = {}
        resp['id'] = packet["source_addr_long"].encode('hex')
        resp['laddr'] = packet["source_addr_long"].encode('hex')
        resp['addr'] = packet["source_addr"].encode('hex')
        resp['data'] = packet["rf_data"] or ''
        return resp
    except:
        return None
