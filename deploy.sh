#!/usr/bin/env bash
# deploy.sh — 一键推送 (token 存在 macOS 钥匙串里就不用 paste 了)
# 用法: ./deploy.sh "commit message"   (commit message 可选)

set -e

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
ok()   { printf "${GREEN}[deploy]${NC} %s\n" "$*"; }
warn() { printf "${YELLOW}[deploy]${NC} %s\n" "$*"; }
err()  { printf "${RED}[deploy]${NC} %s\n" "$*"; }

SITE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SITE_DIR"

USER="huang-yu-an"
REPO="${USER}.github.io"

# Load credentials from keychain (saved by push.sh)
TOKEN=""
if [ -f "$SITE_DIR/.deploy-credentials.sh" ]; then
    source "$SITE_DIR/.deploy-credentials.sh"
    TOKEN="$GITHUB_TOKEN"
fi
if [ -z "$TOKEN" ]; then
    TOKEN=$(security find-generic-password -s "github.com" -a "$USER" -w 2>/dev/null || true)
fi

if [ -z "$TOKEN" ]; then
    err "没找到 token, 请先跑一次 ./push.sh YOUR_TOKEN (或 ssh-add ~/.ssh/id_ed25519_huang_yu_an)"
    exit 1
fi

# Set remote
git remote remove origin 2>/dev/null || true
git remote add origin "https://${USER}:${TOKEN}@github.com/${USER}/${REPO}.git"

# Commit if needed
if [ -n "$(git status --porcelain)" ]; then
    MSG="${1:-Update site}"
    ok "改动将作为 commit: \"$MSG\""
    git add -A
    git commit -m "$MSG"
else
    ok "工作区干净"
fi

# Push
ok "推送到 origin/main ..."
git push -u origin main

# Clean token from remote URL
git remote set-url origin "https://github.com/${USER}/${REPO}.git"

echo ""
ok "推送完成! GitHub Pages 会自动重建 (~30 秒)"
ok "访问 https://${USER}.github.io 查看"
