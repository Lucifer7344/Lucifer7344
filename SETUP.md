# Setup (about 5 minutes)

1. **Copy everything** from this zip into the root of your `Lucifer7344/Lucifer7344` repo, keeping the folders (`assets/`, `scripts/`, `games/`, `.github/workflows/`). Commit and push to `main`.
2. **Allow Actions to write:** Settings → Actions → General → Workflow permissions → **Read and write permissions** → Save.
3. **Turn on Issues** (needed for Tic-Tac-Toe): Settings → General → Features → tick **Issues**.
4. **Generate the Snake and Pac-Man animations:** Actions tab → *Contribution Games (Snake + Pac-Man)* → **Run workflow**. They refresh every 12 hours after that.
5. **Test the game:** click any numbered square on your profile, submit the issue, and refresh after about a minute.

## Optional
- **Logo:** save your Albero logo as `assets/albero-logo.png` and uncomment the logo line near the top of `README.md`.
- **Edit the banners:** `assets/*.svg` are plain text. Change names, products or colours (`#7DD3FC` is the accent) in any editor.
- **Reset the game stats:** delete `games/tictactoe.json`, then open an issue titled `ttt|new`.
