# J.U.D.A.H.

Just Ur Dependable AI Helper

## How to Run

1. Set the `OPENAI_API_KEY` environment variable
2. `poetry init`
3. `poetry run python -m judah.main`

## Development Setup

Having a `.vscode/launch.json` is useful:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Run judah.main",
      "type": "debugpy",
      "request": "launch",
      "module": "judah.main",
      "cwd": "${workspaceFolder}",
      "console": "integratedTerminal",
      "env": {
        "PYTHONPATH": "${workspaceFolder}",
        "OPENAI_API_KEY": "YOUR_KEY_HERE"
      }
    }
  ]
}
```
