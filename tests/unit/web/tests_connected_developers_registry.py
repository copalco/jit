import datetime
import unittest
from dataclasses import dataclass

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from src.domain.model.handle import Handle


@dataclass(frozen=True)
class ConnectedRegistryForDevelopersQuery:
    first: str
    second: str


@dataclass(frozen=True)
class Entry:
    registered_at: datetime.datetime
    connected: bool
    organizations: list[str]


@dataclass(frozen=True)
class RegisterFor:
    first: Handle
    second: Handle
    entries: list[Entry]


class ConnectedRegistryQueryHandler:
    def handle(self, query: ConnectedRegistryForDevelopersQuery) -> RegisterFor:
        return RegisterFor(Handle(""), Handle(""), [])


class FakeQueryHandler(ConnectedRegistryQueryHandler):
    def handle(self, query: ConnectedRegistryForDevelopersQuery) -> RegisterFor:
        if query.first != "dev1" or query.second != "dev2":
            return RegisterFor(Handle(query.first), Handle(query.second), entries=[])
        return RegisterFor(
            Handle("dev1"),
            Handle("dev2"),
            entries=[
                Entry(
                    registered_at=datetime.datetime(2022, 5, 30),
                    connected=False,
                    organizations=[],
                ),
                Entry(
                    registered_at=datetime.datetime(2022, 6, 1),
                    connected=True,
                    organizations=["org1", "org3"],
                ),
                Entry(
                    registered_at=datetime.datetime(2022, 6, 2),
                    connected=True,
                    organizations=["org1", "org2", "org3"],
                ),
            ],
        )


class ConnectedRegistryResource:
    def __init__(self, query_handler: ConnectedRegistryQueryHandler) -> None:
        self._query_handler = query_handler

    def on_get(self, request: Request) -> Response:
        register = self._query_handler.handle(
            ConnectedRegistryForDevelopersQuery(
                request.path_params["first_developer_handle"],
                request.path_params["second_developer_handle"],
            )
        )
        return JSONResponse(
            [self._serialize_entry(entry) for entry in register.entries]
        )

    def _serialize_entry(self, entry: Entry) -> dict[str, str | bool | list[str]]:
        serialized: dict[str, str | bool | list[str]] = {
            "registered_at": entry.registered_at.isoformat(),
            "connected": entry.connected,
        }
        if entry.connected:
            serialized["organisations"] = entry.organizations
        return serialized


class ConnectedResourceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.query_handler = FakeQueryHandler()  # type: ignore
        self.resource = ConnectedRegistryResource(self.query_handler)  # type: ignore

    def test_returns_registered_entries_for_developers(self) -> None:
        result = self.resource.on_get(
            Request(
                scope={
                    "type": "http",
                    "path_params": {
                        "first_developer_handle": "dev1",
                        "second_developer_handle": "dev2",
                    },
                }
            )
        )
        self.assertEqual(
            JSONResponse(
                [
                    {
                        "registered_at": datetime.datetime(2022, 5, 30).isoformat(),
                        "connected": False,
                    },
                    {
                        "registered_at": datetime.datetime(2022, 6, 1).isoformat(),
                        "connected": True,
                        "organisations": ["org1", "org3"],
                    },
                    {
                        "registered_at": datetime.datetime(2022, 6, 2).isoformat(),
                        "connected": True,
                        "organisations": ["org1", "org2", "org3"],
                    },
                ]
            ).body,
            result.body,
            result.body,
        )
