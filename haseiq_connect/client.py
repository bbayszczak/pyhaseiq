import base64
from typing import Dict
from websockets.sync.client import connect
from websockets.sync.connection import Connection

REQUESTS: Dict[str, str] = {
    "temperature": "appT",
    "phase": "appPhase",
    "performance": "appP",
    "minimal_temp_percent": "appAufheiz",
}


class Client:
    """
    Represent the connection interface to the wood stove
    """

    port: int
    ip: str
    ws_connection: Connection

    def __init__(self, ip: str, port: int = 8080) -> None:
        self.port = port
        self.ip = ip
        self.ws_connection = connect(f"ws://{self.ip}:{self.port}")

    def close(self) -> None:
        self.ws_connection.close_socket()

    def get_temperature(self) -> float:
        """
        Get the temperature inside the stove

        :return: The temperature inside the stove
        :rtype: float
        """
        return float(self.get(REQUESTS["temperature"]))

    def get_phase(self) -> int:
        """
        Get the current stove phase
        0: no fire
        1: temperature increasing
        2: nominal temperature
        3: need wood
        4: stop adding wood

        :return: The phase
        :rtype: int
        """
        return int(self.get(REQUESTS["phase"]))

    def get_performance(self) -> float:
        """
        Get the current performance percentage

        :return: performance percentage
        :rtype: float
        """
        return float(self.get(REQUESTS["performance"]))

    def get_minimal_temp_percent(self) -> float:
        """
        Get current percentage of minimal target temperature

        :return: current percentage of minimal temperature
        :rtype: float
        """
        return float(self.get(REQUESTS["minimal_temp_percent"]))

    def get(self, request: str) -> str:
        """
        Get a response from the websocket using specified request string

        :param request: request string
        :return: websocket response
        :rtype: str
        """
        self.ws_connection.send(base64.b64encode((f"_req={request}").encode("utf-8")).decode("utf-8"))
        recv = self.ws_connection.recv()
        return base64.b64decode(recv.encode("utf-8")).decode("utf-8").lstrip(f"{request}=")
