import os
import json

import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver


clients = set()
tokens = set()
total_votes_sum = 0


class ValidationError(Exception):
    pass


class PermissionDenied(Exception):
    pass


class SessionHandler(tornado.web.RequestHandler):
    def get_token(self):
        return os.urandom(16).hex()

    async def post(self):
        token = self.get_token()
        tokens.add(token)
        self.finish(token)


class VoteHandler(tornado.web.RequestHandler):
    async def post(self):
        global total_votes_sum
        try:
            if 'x-token' not in self.request.headers or self.request.headers['x-token'] not in tokens:
                raise PermissionDenied
            try:
                data = json.loads(self.request.body)
            except json.JSONDecodeError:
                raise ValidationError

            if 'number' not in data or not isinstance(data['number'], int) or not 1 <= data['number'] <= 10:
                raise ValidationError
        except ValidationError:
            self.send_error(400)
        except PermissionDenied:
            self.send_error(403)
        else:
            total_votes_sum += data['number']

            for client in clients:
                await client.notify()

            tokens.remove(self.request.headers['x-token'])
            self.finish('OK')


class RootHandler(tornado.web.RequestHandler):
    async def get(self):
        self.render('index.html')


class OnlineHandler(tornado.websocket.WebSocketHandler):
    async def notify(self):
        await self.write_message(str(total_votes_sum))

    def open(self):
        clients.add(self)
        self.write_message(str(total_votes_sum))

    def on_close(self):
        clients.remove(self)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/session', SessionHandler),
            (r'/vote', VoteHandler),
            (r'/online', OnlineHandler),
            (r'/', RootHandler),
        ]
        settings = dict(
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
        )
        super().__init__(handlers, **settings)


if __name__ == '__main__':
    app = Application()
    app.listen(8080)
    print('Listening...')
    tornado.ioloop.IOLoop.current().start()
