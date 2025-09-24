#!/usr/bin/env python

import base64
from websockets.sync.client import connect


def main():
    with connect("ws://192.168.1.165:8080") as websocket:
        try:
            while True:
                websocket.send(base64.b64encode(("_req=" + input("_req=")).encode("utf-8")).decode("utf-8"))
                print(base64.b64decode(websocket.recv().encode("utf-8")).decode("utf-8"))
        except KeyboardInterrupt:
            print("STOP")


main()
