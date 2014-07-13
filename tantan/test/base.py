# -*- coding: utf-8 -*-

CLIENT_CONFIG = {   
    "info": {
        "name": "Physical-Area-Network System Client",
        "description": "Data publishing and control of physical devices. Establishes connections to the specified serial ports and echoes the data to the main server."
    },
    "networks": {
        "aabb": {
            "baud": 9600,
            "port": "/dev/ttyUSB0",
            "name": "ZigBee PAN"
        }
    },
    "server": {
        "host": "localhost",
        "port": 7789
    }
}

SERVER_CONFIG = {   
    "info": {
        "name": "Physical-Area-Network System Server",
        "description": "Data publishing and control of physical devices."
    },
    "server": {
        "host": "localhost",
        "port": 7789
    }
}
