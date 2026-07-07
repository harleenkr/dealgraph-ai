$env:PATH = "$HOME\.local\bin;$env:PATH"
Set-Location $HOME\secure-agent-lab
git init
git config user.name "Harleen Kaur Kaggle Participant"
git config user.email "harleen.kaur212@gmail.com"
uv venv
$env:VIRTUAL_ENV="$HOME\secure-agent-lab\.venv"
$env:PATH="$HOME\secure-agent-lab\.venv\Scripts;$env:PATH"
uv tool install google-agents-cli
uvx google-agents-cli setup
agents-cli info
