from __future__ import annotations

import asyncio
import json
import secrets
import uuid
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.api.games import router as games_router
from backend.api.health import router as health_router
from backend.config import settings
from backend.game.service import choose_language, create_game, get_game_state, join_game, ready_game, submit_guess

app = FastAPI(title="Multi Wordle")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(games_router)

connected_clients: dict[str, WebSocket] = {}


async def _broadcast_to_game(game: Any, payload: dict[str, Any]) -> None:
    for player in game.players:
        websocket = connected_clients.get(player.session_token)
        if websocket is not None:
            await websocket.send_json(payload)


def _player_payload(game: Any) -> dict[str, Any]:
    return {
        "code": game.code,
        "status": game.status.value,
        "winner_id": game.winner_id,
        "winner_decided_at": game.winner_decided_at,
        "players": [
            {
                "id": player.id,
                "name": player.name,
                "session_token": player.session_token,
                "language": player.language.value if player.language else None,
                "ready": player.ready,
                "connected": player.is_connected,
                "guesses": player.guesses,
                "total_guesses": player.total_guesses,
                "best_progress": player.best_progress,
            }
            for player in game.players
        ],
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    session_token = secrets.token_urlsafe(24)
    active_tokens = {session_token}
    connected_clients[session_token] = websocket
    try:
        while True:
            payload = await websocket.receive_json()
            message_type = payload.get("type")
            if message_type == "join_game":
                code = payload.get("code")
                player_name = payload.get("player_name") or "Player"
                session = payload.get("session_token") or session_token
                active_tokens.add(session)
                connected_clients[session] = websocket
                try:
                    selected_language = payload.get("language")
                    if code:
                        game = join_game(code.upper(), player_name, session, selected_language)
                    else:
                        game = create_game(player_name, session, selected_language)
                except Exception as exc:  # noqa: BLE001
                    await websocket.send_json({"type": "error", "message": str(exc)})
                    continue
                await _broadcast_to_game(game, {"type": "game_state", **_player_payload(game)})
            elif message_type == "ready":
                code = payload.get("code")
                player_id = payload.get("player_id")
                if not code or not player_id:
                    await websocket.send_json({"type": "error", "message": "code and player_id are required"})
                    continue
                try:
                    game = ready_game(code.upper(), player_id)
                except Exception as exc:  # noqa: BLE001
                    await websocket.send_json({"type": "error", "message": str(exc)})
                    continue
                await _broadcast_to_game(game, {"type": "game_state", **_player_payload(game)})
            elif message_type == "guess":
                code = payload.get("code")
                player_id = payload.get("player_id")
                guess_value = payload.get("value")
                if not code or not player_id or not guess_value:
                    await websocket.send_json({"type": "error", "message": "code, player_id and value are required"})
                    continue
                try:
                    result = submit_guess(code.upper(), player_id, str(guess_value))
                except Exception as exc:  # noqa: BLE001
                    await websocket.send_json({"type": "error", "message": str(exc)})
                    continue
                game = get_game_state(code.upper())
                if game is not None:
                    await _broadcast_to_game(game, {"type": "guess_result", **result})
                    await _broadcast_to_game(game, {"type": "game_state", **_player_payload(game)})
                else:
                    await websocket.send_json({"type": "guess_result", **result})
            elif message_type == "leave":
                break
            else:
                await websocket.send_json({"type": "error", "message": "Unsupported message type"})
    except WebSocketDisconnect:
        pass
    finally:
        for token in active_tokens:
            connected_clients.pop(token, None)
