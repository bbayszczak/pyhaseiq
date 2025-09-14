#!/usr/bin/env python

import time
import base64
from rich.live import Live
from rich.table import Table
from websockets.sync.client import connect
from websockets.sync.connection import Connection


def main():
    table = Table()
    table.add_column("parameter")
    table.add_column("value")
    with connect("ws://192.168.1.165:8080") as websocket:
        with Live(table, refresh_per_second=4) as _:
            try:
                while True:
                    table.rows.clear()
                    for m in ["appAufheiz", "appP", "appPhase", "appT"]:
                        table.add_row(m, send_and_receive(websocket, m).split("=")[1])
                    time.sleep(1)
            except KeyboardInterrupt:
                print("STOP")


def send_and_receive(websocket: Connection, message: str) -> str:
    websocket.send(to_base64_str(f"_req={message}"))
    recv = websocket.recv()
    return base64.b64decode(recv.encode("utf-8")).decode("utf-8")


def to_base64_str(base: str) -> str:
    return base64.b64encode(base.encode("utf-8")).decode("utf-8")


main()
