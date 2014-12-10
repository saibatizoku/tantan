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


def handle_rx(self, packet):
    resp = {}
    #resp['name'] = ZB_reverse.get(packet["source_addr_long"], "Unknown")
    resp = get_zb_node_info(self, packet)
    print "pak: {}".format(repr(packet))
    rout = "RX:"
    for (key, item) in resp.items():
        rout += "{0}-{1}:".format(key, item)
    msg = "{0}:{1}:RX:".format(resp['id'], resp['addr'], resp['data']) + repr(resp['data'])
    #print 'Evt id: {0}\nVal: {1}'.format(str(resp['name']), resp['data'].decode('utf8'))
    evt = {'id': resp['id'],
            'type': 'rx',
            'data': resp['data'],
            }
    node_id = resp['id']
    data = resp['data']
    data_lines = data.splitlines()
    #print "VAL LINES", val_lines
    for l in data_lines:
        try:
            node_type, pin, sensor, value = l.split(":")
            reading = {
                    'node_id': node_id,
                    'node_type': node_type,
                    'pin': pin,
                    'sensor': sensor,
                    'value': float(value),
                    }
            print reading
            #self.wsMcuFactory.dispatch("http://www.tantan.org/api/sensores#amb-rx", reading)
            #uri = "/".join(["http://www.tantan.org/api/sensores/nodos#", node_id])
            #self.wsMcuFactory.dispatch(uri, {'node_id': node_id, 'msg': l})
        except:
            topic_id = u"mx.neutro.energia.api.nodos"
            topic = u".".join(["mx.neutro.energia.api.nodos", node_id])
            vals = V1, PA1, FP1, P1, P2, P3, P4 = [float(val) for val in l.rstrip(' \0').split() ]
            sensores = { 'v1': V1, 'pa1': PA1, 'fp1': FP1, 'p1': P1, 'p2': P2, 'p3': P3, 'p4': P4 }
            print topic_id, repr(vals), sensores
            self.session.publish(topic_id, {'node_id': node_id, 'msg': vals, 'sensores': sensores})
            if not self.pan_id:
                self.getPanId()
            else:
                topic_pan_id = u"mx.neutro.energia.api.redes"
                print topic_pan_id, self.pan_id
                self.session.publish(topic_pan_id, {'pan_id': self.pan_id, 'node_id': node_id})

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

