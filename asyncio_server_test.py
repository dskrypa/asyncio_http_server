#!/usr/bin/env python3

import asyncio
import logging
from aiohttp import web
from collections import defaultdict, OrderedDict
from html import escape as html_escape

from lib.log_handling import LogManager

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style type="text/css">
    table, tr, td {{
        border: 1px solid black;
    }}
    </style>
</head>
<body>
{body}
</body>
</html>
"""


def route_registry(method):
    class Registry(defaultdict):
        pass

    registry = Registry(dict)

    def register(method, uri):
        def decorate(func):
            registry[uri][method] = func.__name__
            return func
        return decorate

    registry.register = register
    return registry


class TestServer(object):
    def __init__(self, loop, address="127.0.0.1", port=8888):
        self.counter = 0
        self.loop = loop
        self.address = address
        self.port = port
        self.app = web.Application(loop=self.loop)
        for uri, actions in self.web_routes.items():
            for http_method, server_method in actions.items():
                logging.debug("Adding route: {} {} -> {}.{}()".format(http_method, uri, self.__class__.__name__, server_method))
                self.app.router.add_route(http_method, uri, getattr(self, server_method))
        self.handler = self.app.make_handler()
        self.server = None

    @asyncio.coroutine
    def start(self):
        self.server = yield from self.loop.create_server(self.handler, self.address, self.port)
        return self.server.sockets[0].getsockname()

    @route_registry
    def web_routes(self):
        pass

    @web_routes.register("GET", "/")
    def get_root(self, req):
        print("{} {} on {}; cookies: {}; headers: {}".format(req.method, req.path, req.host, req.cookies, req.headers))
        self.counter += 1
        content = {"title": "Request Info", "body": "Information about your request:<br/>"}
        row_content = OrderedDict()
        for k in sorted(req.__dict__.keys()):
            row_content[html_escape(k)] = html_escape(str(req.__dict__[k]))
        rows = ["<tr><td>{}</td><td>{}</td></tr>".format(k, v) for k, v in row_content.items()]
        content["body"] += "<table>{}</table>".format("\n".join(rows))
        html = html_template.format(**content)
        return web.Response(content_type="text/html", text=html)


def main():
    LogManager.create_default_stream_logger(True)
    loop = asyncio.get_event_loop()
    host = loop.run_until_complete(TestServer(loop).start())
    print("Running server on {}".format(host))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    print("Server stopped.")
    loop.close()


if __name__ == "__main__":
    main()
