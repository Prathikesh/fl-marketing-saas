from __future__ import annotations


class FederatedServer:
    def __init__(self, clients: list, rounds: int) -> None:
        self.clients = clients
        self.rounds = rounds

    def run(self):
        raise NotImplementedError
