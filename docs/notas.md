Acerca de el sistema TanTán
===========================

El sistema TanTán está hecho para ser una herramienta libre y gratuita, cuyo
propósito es el de automatizar tareas cotidianas en el cultivo de peces.

Es un sistema con múltiples componentes de software libre, principalmente
utilizando Python, HTML, CSS y JavaScript como lenguajes de programación.

Funcionalidad
-------------
* Servicios de publicación web
  - Utilizando HTTP, WebSockets

* Servicios de captura de datos de sensores
  - Servicios de comunicación con redes de dispositivos ZigBee

En esta versión del sistema TanTán, está construída sobre la plataforma
para redes [Twisted](http://www.twistedmatrix.com).


Modularidad del sistema
-----------------------

Los módulos principales del sistema son:

1. Módulo de comunicaciones
  1. Módulo de servicios web
2. Módulo de bases de datos
3. Módulo de sensores inalámbricos
  1. Módulo de comunicaciones seriales


.question



# Instalaciones con virtualenv activado
_Creado por saibatizoku. 19/sep/2013_


## Para _Twisted_

*    __Twisted__
    pip install zope.interface
    pip install pyOpenSSL
    src/Twisted/python setup.py develop

*    __PyCrypto__
    pip install pyasn1
    src/PyCrypto/python setup.py build
    src/PyCrypto/python setup.py develop

*    __CouchDB__
    src/paisley/python setup.py develop

## Para _IPython con [zmq,qtconsole,notebook,test]_

*   __IPython__
    pip install ipython[zmq,qtconsole,notebook,test]


## Para XBee
*   __PySerial__
    pip install pySerial

*   __XBee__
    hg clone https://code.google.com/p/python-xbee/
    cd python-xbee
    python setup.py install


## Para WebSockets

*   __AutobahnPython__
    git clone git://github.com/tavendo/AutobahnPython.git
    cd AutobahnPython
    git checkout v0.5.2
    cd autobahn
    python setup.py install


## zeroMQ & txZMQ

    pip install pyzmq
    #para twisted
    pip install txZMQ

## NumPy

    pip install numpy