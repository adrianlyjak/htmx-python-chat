from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route, WebSocketRoute
from starlette.websockets import WebSocket

async def homepage(request):
    return HTMLResponse('<html><body><h1>hello world</h1></body></html>')

async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.close()

routes = [
    Route("/", homepage),
    WebSocketRoute("/ws/chat", websocket_endpoint),
]

app = Starlette(routes=routes)
