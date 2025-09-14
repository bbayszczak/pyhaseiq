#!/usr/bin/env python

from websockets.sync.client import connect


def hello():
    with connect("ws://192.168.1.165:8080") as websocket:
        websocket.send("X3JlcT1hcHBQaGFzZQ==")
        message = websocket.recv()
        print(f"Received: {message}")


hello()
