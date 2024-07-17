import asyncio
import html
import random
from typing import Dict
import uuid
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route, WebSocketRoute
from starlette.websockets import WebSocket, WebSocketDisconnect


async def homepage(request):

    resp = """
<html>
    <head>
        <title>Example HTMX chat</title>
        <script src="https://unpkg.com/htmx.org@1.9.0"></script>
        <script src="https://unpkg.com/htmx-ext-ws@2.0.0/ws.js"></script>
    </head>
    <body>
        <main hx-ext="ws" ws-connect="/ws/chat">
            <div id="game-content"><i>Nothing to see here</i></div>
            <form ws-send="">
                <input name="game-input" id="game-input" placeholder="Type a message" />
                <button type="submit">Send</button>
            </form>
        </main>
    </body>
</html>
"""
    return HTMLResponse(resp)


_next_id = 0


def get_next_id():
    global _next_id
    _next_id += 1
    return _next_id


canned_responses = [
    "Yes, Hello, I am a bot",
    "Have you ever met a cat?",
    "I have never met a cat",
    "I am very smart",
]


async def websocket_endpoint(socket: WebSocket):
    try:
        await socket.accept()
        await socket.send_text(
            '<div id="game-content"><div class="msg-bot">Bot: Hello, I am bot</div></div>'
        )

        responses = canned_responses[:]
        while True:
            message: Dict[str, str] = await socket.receive_json()
            input: str = message.get("game-input", "").strip()
            await socket.send_text(
                '<input value="" name="game-input" id="game-input"/>'
            )
            if input:
                await socket.send_text(
                    '<div id="game-content" hx-swap-oob="beforeend"><div class="msg-human">Human: '
                    + html.escape(input)
                    + "</div></div>"
                )
                response = ["Bot:"] + random.choice(responses).split(" ")
                response_id = f"resp-{get_next_id()}"
                await socket.send_text(
                    f'<div id="game-content" hx-swap-oob="beforeend"><div id="{response_id}"></div></div>'
                )
                for word in response:
                    await asyncio.sleep(0.1)
                    await socket.send_text(
                        f'<div id="{response_id}" hx-swap-oob="beforeend">{word} </div>'
                    )

    except WebSocketDisconnect as e:
        pass


routes = [
    Route("/", homepage),
    WebSocketRoute("/ws/chat", websocket_endpoint),
]

app = Starlette(routes=routes)
