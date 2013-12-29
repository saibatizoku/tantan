# -*- coding: utf-8 -*-
import json


class Nodo(object):
    def __init__(self, nid=None):
        """ 
        """
        self.nid = nid

    def serialize(self):
        return {'node_id': self.nid}

class NodoSensor(Nodo):
    def __init__(self, nid, data=None, lpm=10):
        self.nid = nid
        self._data = data
        self._lpm = lpm
        if len(nid) == 16:
            self._dh = nid[:8]
            self._dl = nid[8:]

    def get_data(self):
        return self._data

    def parse_data(self, data):
        return u'Parsed data'


class NodoAmbiental(NodoSensor):
    def __init__(self, *args, **kwargs):
        Nodo.__init__(self, *args, **kwargs)
        self.tipo = u"Ambiental"

    @property
    def humedad(self):
        return self._doc.get('humedad', None)

    @humedad.setter
    def humedad(self, value):
        return self._doc.update({'humedad': value})

    @humedad.deleter
    def humedad(self):
        return self._doc.pop('humedad', None)

    @property
    def presion(self):
        return self._doc.get('presion', None)

    @presion.setter
    def presion(self, value):
        return self._doc.update({'presion': value})

    @presion.deleter
    def presion(self):
        return self._doc.pop('presion', None)

    @property
    def luz(self):
        return self._doc.get('luz', None)

    @luz.setter
    def luz(self, value):
        return self._doc.update({'luz': value})

    @luz.deleter
    def luz(self):
        return self._doc.pop('luz', None)

    @property
    def temperatura(self):
        return self._doc.get('temperatura', None)

    @temperatura.setter
    def temperatura(self, value):
        return self._doc.update({'temperatura': value})

    @temperatura.deleter
    def temperatura(self):
        return self._doc.pop('temperatura', None)
    

    def serialize(self):
        d = {
                'node_id': self.nid,
                'sensores': [
                    {
                        'tipo': 'humedad',
                        'valor': self.humedad,
                        'unidad': '%'
                        },
                    {
                        'tipo': u'presión',
                        'valor': self.presion,
                        'unidad': 'hPa'
                        },
                    {
                        'tipo': 'luz',
                        'valor': self.luz,
                        'unidad': ''
                        },
                    {
                        'tipo': 'temperatura',
                        'valor': self.temperatura,
                        'unidad': 'Celsius'
                        },
                    ],
                }
        return d

    def toJSON(self):
        return json.dumps(self.serialize())
