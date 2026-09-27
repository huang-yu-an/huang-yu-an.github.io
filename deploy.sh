#!/usr/bin/env bash
# deploy.sh — 一键推送个人学术网站到 GitHub Pages
# 用法: ./deploy.sh "commit message"   (commit message 可选)
#
# 前提 (二选一):
#   - 已配 HTTPS + token (git credential.helper 已缓存), 或
#   - 已配 SSH key (ssh -T git@github.com 返回 "successfully authenticated")

set -e

SITE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SITE_DIR"

GITHUB_USER="huang-yu-an"
REPO_NAME="${GITHUB_USER}.github.io"

# --- 颜色输出 -----------------------------------------------------------
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'
info() { printf "${GREEN}[deploy]${NC} %s\n" "$*"; }
warn() { printf "${YELLOW}[warn]${NC} %s\n" "$*"; }
err()  { printf "${RED}[error]${NC} %s\n" "$*"; }

# --- 1. 校验 git 身份 --------------------------------------------------
if [ -z "$(git config --global user.name)" ] || [ -z "$(git config --global user.email)" ]; then
    err "git user.name / user.email 未配置"
    echo "    请先运行:"
    echo "      git config --global user.name  \"Yu-An Huang\""
    echo "      git config --global user.email \"your-email@example.com\""
    exit 1
fi

# --- 2. 选 remote URL ---------------------------------------------------
if ssh -T -o ConnectTimeout=5 -o BatchMode=yes git@github.com 2>&1 | grep -qi "successfully authenticated"; then
    REMOTE_URL="git@github.com:${GITHUB_USER}/${REPO_NAME}.git"
    AUTH_MODE="SSH"
elif gh auth status >/dev/null 2>&1; then
    REMOTE_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}.git"
    AUTH_MODE="HTTPS (gh CLI)"
elif [ -n "$(git config --global credential.helper)" ]; then
    REMOTE_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}.git"
    AUTH_MODE="HTTPS (credential helper)"
else
    warn "SSH 和 HTTPS 都没检测到凭据。"
    warn "将默认使用 HTTPS。请确保已配置 Personal Access Token 并通过 credential.helper 缓存。"
    echo "    快速配置: gh auth login (推荐) 或参考 README.md 的 HTTPS token 方案"
    REMOTE_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}.git"
    AUTH_MODE="HTTPS (未检测到凭据)"
fi
info "认证方式: $AUTH_MODE"
info "远程地址: $REMOTE_URL"

# --- 3. 添加 remote (如果还没) ------------------------------------------
if ! git remote get-url origin >/dev/null 2>&1; then
    git remote add origin "$REMOTE_URL"
    info "已添加 origin → $REMOTE_URL"
else
    CURRENT=$(git remote get-url origin)
    if [ "$CURRENT" != "$REMOTE_URL" ]; then
        warn "现有 origin: $CURRENT"
        warn "本次计算:   $REMOTE_URL"
        read -p "要替换吗? [y/N] " ans
        if [[ "$ans" =~ ^[Yy]$ ]]; then
            git remote set-url origin "$REMOTE_URL"
            info "已更新 origin"
        fi
    fi
fi

# --- 4. 校验 GitHub 仓库存在 -------------------------------------------
info "检查 GitHub 仓库是否存在..."
if command -v gh >/dev/null 2>&1; then
    if ! gh repo view "${GITHUB_USER}/${REPO_NAME}" >/dev/null 2>&1; then
        err "仓库 https://github.com/${GITHUB_USER}/${REPO_NAME} 不存在或不可访问"
        echo "    请先在 https://github.com/new 创建空仓库 (Public, 不要勾选任何初始化选项)"
        exit 1
    fi
else
    warn "未安装 gh CLI, 跳过仓库存在性检查"
fi

# --- 5. 提交改动 (如果有) ----------------------------------------------
if [ -n "$(git status --porcelain)" ]; then
    MSG="${1:-Update site}"
    info "有未提交的改动, 将以 commit message: \"$MSG\""
    git add -A
    git commit -m "$MSG"
else
    info "工作区干净, 无需 commit"
fi

# --- 6. 推送 -------------------------------------------------------------
info "推送到 origin/main ..."
git push -u origin main

# --- 7. 提示 Pages 配置 -------------------------------------------------
info "推送完成!"
echo ""
echo "========================================================================"
echo "  下一步: 打开 https://github.com/${GITHUB_USER}/${REPO_NAME}/settings/pages"
echo "         Source 选 'Deploy from a branch'"
echo "         Branch 选 'main' / '(root)'"
echo "         点 Save, 等 1~2 分钟访问 https://${GITHUB_USER}.github.io"
echo "========================================================================"
