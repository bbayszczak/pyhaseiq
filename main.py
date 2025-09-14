#!/usr/bin/env python

import base64
from websockets.sync.client import connect


def main():
    with connect("ws://192.168.1.165:8080") as websocket:
        try:
            while True:
                in_str = input("_req=")
                websocket.send(base64.b64encode(("_req=" + in_str).encode("utf-8")).decode("utf-8"))
                recv = websocket.recv()
                print(base64.b64decode(recv.encode("utf-8")).decode("utf-8"))
        except KeyboardInterrupt:
            print("STOP")


main()
