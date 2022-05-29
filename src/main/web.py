from typing import Callable

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from src.web.resource import Resource
from src.web.resources.connected import StubResource


def resource_factory(resource: Resource) -> Callable[[Request], Response]:
    def view_adapter(request: Request) -> Response:
        return resource.on_get(request)

    return view_adapter


def create_app() -> Starlette:
    routes = [
        Route(
            "/connected/realtime/{first_developer_handle}/{second_developer_handle}",
            resource_factory(StubResource()),
        ),
    ]
    web_api = Starlette(routes=routes)
    return web_api