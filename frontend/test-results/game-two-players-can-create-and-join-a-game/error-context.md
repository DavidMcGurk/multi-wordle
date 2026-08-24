# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: game.spec.ts >> two players can create and join a game
- Location: tests/game.spec.ts:3:1

# Error details

```
Test timeout of 30000ms exceeded.
```

# Page snapshot

```yaml
- generic [ref=e3]:
  - banner [ref=e4]:
    - heading "Multi Wordle" [level=1] [ref=e5]
  - main [ref=e6]:
    - 'heading "Lobby: VRSJ8" [level=2] [ref=e7]'
    - generic [ref=e9]:
      - strong [ref=e10]: Alice
      - generic [ref=e11]: en
      - generic [ref=e12]: Waiting for opponent
    - paragraph [ref=e13]: The room starts as soon as both players are connected and have selected a language.
```