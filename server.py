import os
import json

import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver


class ValidationError(Exception):
    pass


class PermissionDenied(Exception):
    pass


class SessionHandler(tornado.web.RequestHandler):
    def get_token(self):
        return os.urandom(16).hex()

    async def post(self):
        token = self.get_token()
        self.application.tokens.add(token)
        self.finish(token)


class VoteHandler(tornado.web.RequestHandler):
    async def vote(self):
        if 'x-token' not in self.request.headers or self.request.headers['x-token'] not in self.application.tokens:
            raise PermissionDenied
        try:
            data = json.loads(self.request.body)
        except json.JSONDecodeError:
            raise ValidationError

        if 'number' not in data or not isinstance(data['number'], int) or not 1 <= data['number'] <= 10:
            raise ValidationError

        self.application.total_votes_sum += data['number']

        for client in self.application.clients:
            await client.notify()

        self.application.tokens.remove(self.request.headers['x-token'])

    async def post(self):
        try:
            await self.vote()
        except ValidationError:
            self.send_error(400)
        except PermissionDenied:
            self.send_error(403)
        else:
            self.finish('OK')


class RootHandler(tornado.web.RequestHandler):
    async def get(self):
        self.render('index.html')


class OnlineHandler(tornado.websocket.WebSocketHandler):
    async def notify(self):
        await self.write_message(str(self.application.total_votes_sum))

    def open(self):
        self.application.clients.add(self)
        self.write_message(str(self.application.total_votes_sum))

    def on_close(self):
        self.application.clients.remove(self)


class Application(tornado.web.Application):
    def __init__(self):
        self.clients = set()
        self.tokens = set()
        self.total_votes_sum = 0

        settings = {
            'static_path': os.path.join(os.path.dirname(__file__), 'static'),
            'handlers': [
                (r'/session', SessionHandler),
                (r'/vote', VoteHandler),
                (r'/online', OnlineHandler),
                (r'/', RootHandler),
            ]
        }

        super().__init__(**settings)


if __name__ == '__main__':
    app = Application()
    try:
        app.listen(8080)
        print('Listening...')
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        print('\nBye')
