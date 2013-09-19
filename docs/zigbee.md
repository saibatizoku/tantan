tantan.zb
=========

Éste módulo permite conectarse a un dispositivo mediante un puerto serial de
la computadora.

Para ejecutar el servicio desde la línea de comando:

    $ python ttxbee.py

Por defecto, al ejecutar el script de esta manera, se imprimirán en la conso-
la (**sys.stdout**) los registros del log.

El servicio iniciará un servidor web accesible desde

    http://localhost:8080/zb.html

El servicio también iniciará un servidor websockets WAMP accesible desde

    http://localhost:8080/ws

Para obtener información acerca de las opciones de ejecución, se debe invocar
el siguiente comando desde la línea de comando:

    $ python ttxbee.py --help

