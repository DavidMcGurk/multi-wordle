import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import './App.css'

type Language = 'en' | 'hu'
type Screen = 'home' | 'lobby' | 'game'

type Player = {
  id: string
  name: string
  session_token: string
  language: Language | null
  ready: boolean
  connected: boolean
  total_guesses: number
  best_progress: number[]
  guesses: string[]
}

type GuessResults = Record<number, number[]>

type GameState = {
  code: string
  status: string
  winner_id?: string | null
  winner_decided_at?: number | null
  players: Player[]
}

type ServerMessage =
  | { type: 'game_state'; code: string; status: string; winner_id?: string | null; winner_decided_at?: number | null; players: Player[] }
  | { type: 'guess_result'; correct: boolean; result: number[]; guess_count: number; winner_id?: string | null; winner_decided_at?: number | null; player_id?: string; target_word?: string }
  | { type: 'error'; message: string }

const keyboardRows: Record<Language, string[][]> = {
  en: [
    ['q','w','e','r','t','y','u','i','o','p'],
    ['a','s','d','f','g','h','j','k','l'],
    ['z','x','c','v','b','n','m'],
  ],
  hu: [
    ['q','w','e','r','t','z','u','i','o','p'],
    ['a','s','d','f','g','h','j','k','l'],
    ['y','x','c','v','b','n','m'],
  ],
}

const hungarianAccentKeys = ['á', 'é', 'í', 'ó', 'ö', 'ő', 'ú', 'ü', 'ű']

function normalizeGuess(value: string) {
  return value.normalize('NFC').trim().toLowerCase()
}

function App() {
  const [screen, setScreen] = useState<Screen>('home')
  const [language, setLanguage] = useState<Language>('en')
  const [joinCode, setJoinCode] = useState('')
  const [game, setGame] = useState<GameState | null>(null)
  const [currentGuess, setCurrentGuess] = useState('')
  const [, setConnected] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [guessResults, setGuessResults] = useState<GuessResults>({})
  const [ws, setWs] = useState<WebSocket | null>(null)
  const lastNoticeRef = useRef<{ message: string; at: number }>({ message: '', at: 0 })
  const lastSubmittedGuessRef = useRef('')
  const lastGameCodeRef = useRef<string | null>(null)
  const gameRef = useRef<GameState | null>(null)
  const playerIdRef = useRef('')

  const setInlineNotice = (message: string | ((current: string) => string)) => {
    const resolvedMessage = typeof message === 'function' ? message(lastNoticeRef.current.message) : message
    if (!resolvedMessage) {
      setNotice('')
      lastNoticeRef.current = { message: '', at: 0 }
      return
    }

    const now = Date.now()
    if (resolvedMessage === lastNoticeRef.current.message && now - lastNoticeRef.current.at < 250) {
      return
    }

    lastNoticeRef.current = { message: resolvedMessage, at: now }
    setNotice(resolvedMessage)
  }
  const [sessionToken] = useState<string>(() => {
    const key = 'wordle-session'
    const saved = window.sessionStorage.getItem(key)
    if (saved) {
      return saved
    }
    const created = globalThis.crypto?.randomUUID?.() ?? `session-${Date.now()}`
    window.sessionStorage.setItem(key, created)
    return created
  })
  const [playerId, setPlayerId] = useState('')

  const resetToHome = useCallback(() => {
    setGame(null)
    setScreen('home')
    setCurrentGuess('')
    setGuessResults({})
    lastGameCodeRef.current = null
    setError('')
    setNotice('')
    setPlayerId('')
  }, [])

  useEffect(() => {
    window.sessionStorage.setItem('wordle-session', sessionToken)
  }, [sessionToken])

  useEffect(() => {
    gameRef.current = game
  }, [game])

  useEffect(() => {
    playerIdRef.current = playerId
  }, [playerId])

  useEffect(() => {
    if (typeof WebSocket === 'undefined') {
      return
    }

    const socket = new WebSocket('ws://localhost:8000/ws')
    socket.onopen = () => setConnected(true)
    socket.onclose = () => setConnected(false)
    socket.onmessage = (event) => {
      const previousGameCode = lastGameCodeRef.current
      const message = JSON.parse(event.data) as ServerMessage
      if (message.type === 'game_state') {
        const players = message.players.map((player) => ({
          ...player,
          name: player.name || 'You',
          best_progress: Array.isArray(player.best_progress) ? player.best_progress : [0, 0, 0, 0, 0],
        }))
        const nextGame: GameState = {
          code: message.code,
          status: message.status,
          winner_id: message.winner_id ?? null,
          winner_decided_at: message.winner_decided_at ?? null,
          players,
        }
        gameRef.current = nextGame
        setGame(nextGame)
        if (previousGameCode !== message.code) {
          setGuessResults({})
        }
        lastGameCodeRef.current = message.code

        const self = players.find((player) => player.session_token === sessionToken)
        if (self) {
          playerIdRef.current = self.id
          setPlayerId(self.id)
        } else if (players.length > 0) {
          playerIdRef.current = players[0].id
          setPlayerId(players[0].id)
        }

        if (message.winner_id) {
          const winNotice = self && message.winner_id === self.id ? 'You win!' : 'You lose!'
          setInlineNotice(winNotice)
        } else if (!message.winner_id && !gameRef.current?.winner_id && !hasPersistentTerminalNotice) {
          setInlineNotice('')
        }

        setScreen(message.status === 'IN_PROGRESS' || message.status === 'FINISHED' ? 'game' : 'lobby')
        setError('')
      }
      if (message.type === 'guess_result') {
        const selfIdFromGame = gameRef.current?.players.find((player) => player.session_token === sessionToken)?.id ?? playerIdRef.current
        const isOwnGuess = !message.player_id || message.player_id === selfIdFromGame
        if (isOwnGuess) {
          const guessIndex = Math.max(0, message.guess_count - 1)
          setGuessResults((previous) => ({
            ...previous,
            [guessIndex]: message.result,
          }))
          setCurrentGuess('')
        }

        const winnerId = message.winner_id ?? gameRef.current?.winner_id ?? null
        const currentPlayerId = selfIdFromGame || null
        if (winnerId && winnerId === currentPlayerId) {
          setInlineNotice('You win!')
          return
        }
        if (winnerId && winnerId !== currentPlayerId) {
          setInlineNotice('You lose!')
          return
        }
        if (message.target_word) {
          setInlineNotice(`Answer: ${message.target_word.toUpperCase()}`)
          return
        }
        if (!isOwnGuess) {
          return
        }
        if (!winnerId && !hasTerminalWinner && !hasPersistentTerminalNotice) {
          setInlineNotice('')
        }
      }
      if (message.type === 'error') {
        setError(message.message)
        setInlineNotice(message.message)
      }
    }
    setWs(socket)
    return () => socket.close()
  }, [sessionToken])

  const send = (payload: Record<string, unknown>) => {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      setError('Connection is not available.')
      return
    }
    ws.send(JSON.stringify(payload))
  }

  const createGame = () => {
    setError('')
    setNotice('')
    send({ type: 'join_game', player_name: 'You', session_token: sessionToken, language })
  }

  const joinGame = () => {
    setError('')
    setNotice('')
    send({ type: 'join_game', code: joinCode, player_name: 'You', session_token: sessionToken, language })
  }

  const leaveLobby = () => {
    resetToHome()
    send({ type: 'leave' })
  }

  const currentPlayer = useMemo(() => game?.players.find((player) => player.id === playerId) ?? null, [game, playerId])
  const opponent = useMemo(() => game?.players.find((player) => player.id !== playerId) ?? null, [game, playerId])
  const hasTerminalWinner = !!game?.winner_id
  const hasPersistentTerminalNotice = notice === 'You win!' || notice === 'You lose!'

  const submitGuess = useCallback(() => {
    if (!game) return
    if ((currentPlayer?.guesses.length ?? 0) >= 6) {
      setInlineNotice('You have used all 6 guesses.')
      return
    }
    if (currentGuess.length !== 5) {
      setInlineNotice('Your guess must be exactly 5 letters.')
      return
    }
    if (currentPlayer?.guesses.includes(currentGuess)) {
      setInlineNotice('You already tried that guess.')
      return
    }
    if (!hasPersistentTerminalNotice) {
      setInlineNotice('')
    }
    lastSubmittedGuessRef.current = currentGuess
    send({ type: 'guess', code: game.code, player_id: playerId, value: currentGuess })
  }, [currentGuess, currentPlayer, game, hasPersistentTerminalNotice, playerId])

  const rows = Array.from({ length: 6 }, (_, rowIndex) => {
    const submittedGuess = currentPlayer?.guesses[rowIndex] ?? ''
    const isActiveRow = rowIndex === (currentPlayer?.guesses.length ?? 0)
    const guess = submittedGuess || (isActiveRow ? currentGuess : '')
    const result = guessResults[rowIndex] ?? []
    return Array.from({ length: 5 }, (_, columnIndex) => {
      const letter = guess[columnIndex] ?? ''
      const tone = result[columnIndex]
      const tileClass = tone === 2 ? 'tile correct' : tone === 1 ? 'tile almost' : 'tile'
      return (
        <div key={`${rowIndex}-${columnIndex}`} className={tileClass}>
          {letter.toUpperCase()}
        </div>
      )
    })
  })

  const opponentProgressSequence = Array.from({ length: 5 }, (_, index) => {
    const tone = opponent?.best_progress?.[index] ?? 0
    return tone
  })
  const opponentProgressTiles = Array.from({ length: 5 }, (_, index) => {
    const tone = opponentProgressSequence[index] ?? 0
    const filled = tone !== 0
    const tileClass = tone === 2 ? 'progress-tile correct' : tone === 1 ? 'progress-tile almost' : 'progress-tile empty'
    return <div key={`opponent-progress-${index}`} className={tileClass} aria-label={filled ? 'Opponent progress tile' : 'Empty progress tile'} />
  })

  const addLetter = useCallback((key: string) => {
    const rawKey = key.trim()
    if (!rawKey) {
      return
    }

    const normalizedKey = normalizeGuess(rawKey)
    if (!normalizedKey) {
      return
    }

    setCurrentGuess((value) => {
      if (value.length >= 5) {
        return value
      }
      const next = normalizeGuess(`${value}${normalizedKey}`)
      return next.slice(0, 5)
    })
    if (!hasTerminalWinner && !hasPersistentTerminalNotice) {
      setInlineNotice('')
    }
  }, [hasPersistentTerminalNotice, hasTerminalWinner])

  const removeLetter = useCallback(() => {
    if (!hasTerminalWinner && !hasPersistentTerminalNotice) {
      setInlineNotice('')
    }
    setCurrentGuess((value) => value.slice(0, -1))
  }, [hasPersistentTerminalNotice, hasTerminalWinner])

  useEffect(() => {
    if (screen !== 'game') {
      return
    }

    const onKeyDown = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null
      const isTypingInField = !!target && ['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName)

      if (event.key === 'Enter') {
        event.preventDefault()
        submitGuess()
        return
      }

      if (event.key === 'Backspace') {
        event.preventDefault()
        removeLetter()
        return
      }

      if (event.key.length !== 1 || !/[a-zA-ZáéíóöőúüűÁÉÍÓÖŐÚÜŰ]/.test(event.key)) {
        return
      }

      if (isTypingInField && target?.getAttribute('aria-label') === 'Guess') {
        return
      }

      event.preventDefault()
      addLetter(event.key)
    }

    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [screen, addLetter, removeLetter, submitGuess])

  return (
    <div className="app-shell">
      <header className="topbar">
        <button type="button" className="brand-button" onClick={resetToHome} aria-label="Multi Wordle">
          Multi Wordle
        </button>
      </header>

      {screen !== 'game' && error ? <div className="error-banner">{error}</div> : null}

      {screen === 'home' && (
       <main className="panel home-panel">
         <h2 className="panel-heading">Choose your language</h2>
         <div className="language-picker" role="group" aria-label="Choose language">
           <button type="button" className={language === 'en' ? 'selected' : ''} onClick={() => setLanguage('en')}>
             English
           </button>
           <button type="button" className={language === 'hu' ? 'selected' : ''} onClick={() => setLanguage('hu')}>
             Hungarian
           </button>
         </div>

         <div className="entry-stack">
           <div className="split-action">
             <button type="button" className="primary-button" onClick={createGame}>Start lobby</button>
           </div>

           <form className="field-group inline-join" onSubmit={(event) => {
             event.preventDefault()
             joinGame()
           }}>
             <label htmlFor="join-code">Join lobby</label>
             <div className="join-row">
               <input
                 id="join-code"
                 aria-label="Join code"
                 value={joinCode}
                 onChange={(event) => setJoinCode(event.target.value.toUpperCase())}
                 placeholder="K7P2"
               />
               <button type="submit" className="secondary-button">Join lobby</button>
             </div>
           </form>
         </div>
       </main>
      )}

      {screen === 'lobby' && game && (
        <main className="panel lobby-panel waiting-panel">
          <div className="waiting-content">
            <p className="waiting-label">Waiting for opponent</p>
            <h2 className="lobby-header">Room code: <span className="lobby-code">{game.code}</span></h2>
            <p className="lobby-note">Your game will begin as soon as the other player joins and selects a language.</p>
            <button type="button" className="ghost-button" onClick={leaveLobby}>Back to start</button>
          </div>
        </main>
      )}

      {screen === 'game' && game && (
        <main className="panel">
          <div className="board-grid">{rows}</div>
          {notice ? <div className="inline-notice">{notice}</div> : null}
          <div className="keyboard" aria-label="Wordle keyboard">
            {(keyboardRows[language] ?? keyboardRows.en).map((row, rowIndex) => (
              <div key={`keyboard-row-${rowIndex}`} className="keyboard-row">
                {row.map((key) => (
                  <button key={key} type="button" className="key-button" onClick={() => addLetter(key)}>
                    {key.toUpperCase()}
                  </button>
                ))}
              </div>
            ))}
            {language === 'hu' ? (
              <div className="keyboard-row keyboard-row-accent">
                {hungarianAccentKeys.map((key) => (
                  <button key={key} type="button" className="key-button" onClick={() => addLetter(key)}>
                    {key.toUpperCase()}
                  </button>
                ))}
              </div>
            ) : null}
            <div className="keyboard-row keyboard-row-actions">
              <button type="button" className="key-button key-action" onClick={submitGuess}>
                Enter
              </button>
              <button type="button" className="key-button key-action" onClick={removeLetter}>
                Delete
              </button>
            </div>
          </div>
          <div className="status-strip">
            <div className="opponent-progress" aria-label="Opponent progress">
              <span className="opponent-progress-label">Opponent progress</span>
              <div className="opponent-progress-bar">
                {opponentProgressTiles}
              </div>
            </div>
          </div>
        </main>
      )}
    </div>
  )
}

export default App
