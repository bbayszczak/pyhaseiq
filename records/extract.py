#!/usr/bin/env python

import sys
import json
import base64

with open(sys.argv[1], "r") as fd:
    content = fd.read()

loaded = json.loads(content)

out = []

for elem in loaded:
    new = {}
    new["src"] = elem["_source"]["layers"]["ip"]["ip.src"]
    new["dst"] = elem["_source"]["layers"]["ip"]["ip.dst"]
    new["ts"] = elem["_source"]["layers"]["frame"]["frame.time_utc"]
    new["payload"] = [
        base64.b64decode(e).decode("utf-8")
        for e in elem["_source"]["layers"]["websocket"]["websocket.payload"]["websocket.payload.text"].split("\r")
        if e != ""
    ]
    out.append(new)

with open(sys.argv[1] + ".parsed.json", "w") as fd:
    fd.write(json.dumps(out, indent=2))
