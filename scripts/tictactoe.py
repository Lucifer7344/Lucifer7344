#!/usr/bin/env python3
"""Issue-driven Tic-Tac-Toe for a GitHub profile README.

Visitors click a square in the README, which opens an issue titled
``ttt|move|<1-9>``. The workflow runs this script, which plays the move,
lets the bot (O) answer, rewrites the board between the README markers,
and writes a reply to msg.txt for the workflow to post on the issue.
"""
import json
import os
import random
from urllib.parse import quote

STATE = "games/tictactoe.json"
README = "README.md"
START, END = "<!-- TTT_START -->", "<!-- TTT_END -->"
LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6),
         (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
KEYCAPS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

REPO = os.environ.get("REPO", "Lucifer7344/Lucifer7344")
TITLE = os.environ.get("ISSUE_TITLE", "ttt|new").strip()
USER = os.environ.get("ISSUE_USER", "someone").strip()


def fresh_board():
    return [" "] * 9


def load():
    try:
        with open(STATE, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"board": fresh_board(), "wins": 0, "losses": 0, "draws": 0,
                "status": "New game — you're ❌. Pick a square!",
                "recent": [], "players": {}}


def save(state):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def result(b):
    for a, c, d in LINES:
        if b[a] != " " and b[a] == b[c] == b[d]:
            return b[a]
    return "D" if " " not in b else None


def bot_move(b):
    empty = [i for i, v in enumerate(b) if v == " "]
    for mark in ("O", "X"):          # win if possible, otherwise block
        for i in empty:
            trial = b[:]
            trial[i] = mark
            if result(trial) == mark:
                return i
    if 4 in empty:
        return 4
    corners = [i for i in (0, 2, 6, 8) if i in empty]
    return random.choice(corners or empty)


def issue_link(title):
    body = "Just click **Submit new issue** — the board updates in about a minute. 🎮"
    return (f"https://github.com/{REPO}/issues/new"
            f"?title={quote(title)}&body={quote(body)}")


def render(state):
    b = state["board"]
    rows = []
    for r in range(3):
        cells = []
        for c in range(3):
            i = r * 3 + c
            if b[i] == "X":
                inner = "❌"
            elif b[i] == "O":
                inner = "⭕"
            else:
                inner = f'<a href="{issue_link(f"ttt|move|{i + 1}")}">{KEYCAPS[i]}</a>'
            cells.append(f'<td align="center" width="64" height="64">{inner}</td>')
        rows.append("<tr>" + "".join(cells) + "</tr>")

    recent = "<br/>".join(state["recent"]) or "<i>No moves yet — be the first!</i>"
    top = sorted(state["players"].items(), key=lambda kv: -kv[1])[:5]
    board_html = "<table>" + "".join(rows) + "</table>"
    leaders = " · ".join(f"<a href=\"https://github.com/{u}\">@{u}</a> ({n})" for u, n in top) \
        or "<i>Your name could be here</i>"

    return f"""{START}
<div align="center">

**{state['status']}**

{board_html}

<sub>🏆 Visitors {state['wins']} · 🤖 Bot {state['losses']} · 🤝 Draws {state['draws']}</sub>

<sub>Recent moves:<br/>{recent}</sub>

<sub>Top players: {leaders}</sub>

<a href="{issue_link('ttt|new')}"><img src="https://img.shields.io/badge/↻%20Reset%20game-0B1F3A?style=flat-square" /></a>

</div>
{END}"""


def update_readme(block):
    with open(README, encoding="utf-8") as f:
        text = f.read()
    s, e = text.find(START), text.find(END)
    if s == -1 or e == -1:
        raise SystemExit("Tic-Tac-Toe markers not found in README.md")
    text = text[:s] + block + text[e + len(END):]
    with open(README, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    state = load()
    parts = TITLE.split("|")
    board_url = f"https://github.com/{REPO}#-arcade"
    msg = ""

    if len(parts) >= 2 and parts[1] == "new":
        state["board"] = fresh_board()
        state["status"] = f"New game started by @{USER} — you're ❌. Pick a square!"
        msg = f"♻️ Fresh board is up. [Make your move →]({board_url})"

    elif len(parts) == 3 and parts[1] == "move" and parts[2].isdigit() and 1 <= int(parts[2]) <= 9:
        i = int(parts[2]) - 1
        b = state["board"]
        if b[i] != " ":
            msg = f"Square {i + 1} is already taken — [pick another one]({board_url})."
        else:
            state["players"][USER] = state["players"].get(USER, 0) + 1
            b[i] = "X"
            state["recent"].insert(0, f"@{USER} played ❌ on {i + 1}")
            r = result(b)
            j = None
            if r is None:
                j = bot_move(b)
                b[j] = "O"
                state["recent"].insert(0, f"🤖 bot answered ⭕ on {j + 1}")
                r = result(b)

            if r == "X":
                state["wins"] += 1
                state["status"] = f"🎉 @{USER} beat the bot! New board below."
                msg = "🎉 You won! The board has been reset for the next challenger."
            elif r == "O":
                state["losses"] += 1
                state["status"] = f"🤖 The bot won that one against @{USER}. Rematch?"
                msg = "🤖 The bot won this round. The board is reset — try again!"
            elif r == "D":
                state["draws"] += 1
                state["status"] = f"🤝 Draw between @{USER} and the bot. New board below."
                msg = "🤝 It's a draw! Fresh board is ready."
            else:
                state["status"] = f"Your turn! @{USER} played {i + 1}, bot answered {j + 1}."
                msg = f"✅ Move played. The bot answered on square {j + 1}. [Keep playing →]({board_url})"

            if r is not None:
                state["board"] = fresh_board()
            state["recent"] = state["recent"][:6]
    else:
        msg = "That doesn't look like a valid move. Click a square on the profile to play."

    save(state)
    update_readme(render(state))
    with open("msg.txt", "w", encoding="utf-8") as f:
        f.write(msg + f"\n\nThanks for playing, @{USER}! 👋")


if __name__ == "__main__":
    main()
