#!/usr/bin/env python

import time
import base64
from datetime import datetime
from rich.live import Live
from rich.table import Table
from websockets.sync.client import connect
from websockets.sync.connection import Connection


def generate_table() -> Table:
    table = Table()
    table.add_column("parameter")
    table.add_column("value")
    with connect("ws://192.168.1.165:8080") as websocket:
        table.rows.clear()
        table.add_row("Last update", datetime.now().strftime("%x - %X"))
        for m in ["appAufheiz", "appP", "appPhase", "appT"]:
            table.add_row(m, send_and_receive(websocket, m).split("=")[1])
        return table


def main():
    with Live(generate_table(), refresh_per_second=1) as live:
        while True:
            try:
                time.sleep(1)
                live.update(generate_table())
            except KeyboardInterrupt:
                print("STOP")
                exit(0)


def send_and_receive(websocket: Connection, message: str) -> str:
    websocket.send(to_base64_str(f"_req={message}"))
    recv = websocket.recv()
    return base64.b64decode(recv.encode("utf-8")).decode("utf-8")


def to_base64_str(base: str) -> str:
    return base64.b64encode(base.encode("utf-8")).decode("utf-8")


if __name__ == "__main__":
    main()
