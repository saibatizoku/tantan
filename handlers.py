# -*- coding: utf-8 -*-
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


def parse_line(line):
    values = [float(val) for val in line.rstrip(' \0').split() ]
    if len(values) == 9:
        return parse_water(values)
    elif len(values) == 2:
        return parse_ambient(values)
    elif len(values) == 21:
        return parse_energy(values)
    else:
        return values

def sensor_dict(keys, values, units, titles):
    def make_dict(i):
        return {'value': values[i], 'units': units[i], 'title': titles[i]}
    parsed = {keys[i]: make_dict(i) for i in range(len(keys))}
    return parsed


def parse_water(values):
    # T0, T1, T2, T3, T4, OD1, OD2, OD3, OD4 = values

    sensor_keys = [ 't0', 't1', 't2', 't3', 't4', 'od1', 'od2', 'od3', 'od4' ]

    units = [u"°C", u"°C", u"°C", u"°C", u"°C", u'mg/l', u'mg/l', \
             u'mg/l', u'mg/l']

    titles = [ 'Temperatura 0', 'Temperatura 1', 'Temperatura 2', \
               'Temperatura 3', 'Temperatura 4', 'OD 1', 'OD 2', \
               'OD 3', 'OD 4' ]
    return sensor_dict(sensor_keys, values, units, titles)


def parse_ambient(values):
    # H, To = values
    sensor_keys = [ 'h', 'to' ]

    units = [u"%", u"°C"]

    titles = [u"Humedad", u"Temperatura ambiente"]

    return sensor_dict(sensor_keys, values, units, titles)


def parse_energy(values):
    # V0, V1, V2, V3, V4, I1, I2, I3, I4, P1, P2, P3, P4, LD0, LD1, LD2, LD3, BT0,
    # BT1, BT2, BT3, SMF = values

    sensor_keys = [ "v0", "v1", "v2", "v3", "v4", "i1", "i2", "i3", "i4", "p1",\
                    "p2", "p3", "p4", "ld0", "ld1", "ld2", "ld3", "bt0", "bt1",\
                    "bt2", "bt3", "smf" ]

    units = [u"V", u"V", u"V", u"V", u"V", u'A', u'A', u'A', u'A', u'kW', \
             u'kW', u'kW', u'kW', u'', u'', u'', u'', u'', u'', u'', u'', u'']

    titles = [ "Voltaje 0", "Voltaje 1", "Voltaje 2", "Voltaje 3", "Voltaje 4",\
               "Corriente 1", "Corriente 2", "Corriente 3", "Corriente 4", \
               "Potencia 1", "Potencia 2", "Potencia 3", "Potencia 4", "LD0", \
               "LD1", "LD2", "LD3", "BT0", "BT1", "BT2", "BT3", "SMF" ]

    return sensor_dict(sensor_keys, values, units, titles)


def publish_node_data(session, topic, data, debug=False):
    if debug:
        print "PUBLICANDO NODO {}".format(data['node_id'])
        print "PUBLICANDO canales {}".format(topic)
        print "PUBLICANDO DATA {}".format(data['json'])
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
            parsed = parse_line(l)
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
