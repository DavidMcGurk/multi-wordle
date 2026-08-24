from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.game.service import create_game, get_game_state, join_game, ready_game, submit_guess

router = APIRouter(prefix="/api", tags=["games"])


class CreateGameRequest(BaseModel):
    player_name: str = Field(..., min_length=1, max_length=32)
    session_token: str = Field(..., min_length=8, max_length=64)


class JoinGameRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=16)
    player_name: str = Field(..., min_length=1, max_length=32)
    session_token: str = Field(..., min_length=8, max_length=64)


class GuessRequest(BaseModel):
    guess: str = Field(..., min_length=1, max_length=8)


@router.post("/games")
def create_game_route(payload: CreateGameRequest) -> dict[str, str]:
    game = create_game(payload.player_name, payload.session_token)
    return {"code": game.code, "player_id": game.players[0].id}


@router.post("/games/join")
def join_game_route(payload: JoinGameRequest) -> dict[str, str]:
    try:
        game = join_game(payload.code.upper(), payload.player_name, payload.session_token)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"code": game.code, "player_id": game.players[-1].id}


@router.post("/games/{code}/ready")
def ready_game_route(code: str, player_id: str) -> dict[str, str]:
    try:
        game = ready_game(code.upper(), player_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": game.status.value, "code": game.code}


@router.post("/games/{code}/guess")
def submit_guess_route(code: str, player_id: str, payload: GuessRequest) -> dict[str, object]:
    try:
        result = submit_guess(code.upper(), player_id, payload.guess)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"result": result}


@router.get("/games/{code}")
def get_game_route(code: str) -> dict[str, object]:
    game = get_game_state(code.upper())
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return {
        "code": game.code,
        "status": game.status.value,
        "players": [{"name": player.name, "language": player.language.value if player.language else None, "ready": player.ready, "guesses": player.guesses, "won": player.won} for player in game.players],
    }
