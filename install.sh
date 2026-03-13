#!/bin/bash
#
# TDD Pipeline Executor 安装脚本
# 支持 CodeFuse、Aone Copilot 和 Claude Code
# 支持本地安装和远程安装
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 技能名称
SKILL_NAME="tdd-pipeline-executor"
SKILL_REPO="https://github.com/your-username/tdd-executor.git"  # 替换为你的仓库地址

# 检测安装模式
if [ -f "$(dirname "${BASH_SOURCE[0]}")/SKILL.md" ]; then
    # 本地安装模式
    SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    INSTALL_MODE="local"
else
    # 远程安装模式
    SKILL_DIR=$(mktemp -d)
    INSTALL_MODE="remote"
fi

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# 清理临时文件
cleanup() {
    if [ "$INSTALL_MODE" = "remote" ] && [ -d "$SKILL_DIR" ]; then
        print_info "清理临时文件..."
        rm -rf "$SKILL_DIR"
    fi
}

# 注册清理函数
trap cleanup EXIT

# 下载技能文件（远程模式）
download_skill() {
    print_info "正在从远程仓库下载..."
    
    # 检查 git 是否可用
    if ! command -v git &> /dev/null; then
        print_error "未找到 git 命令，无法下载"
        exit 1
    fi
    
    # 克隆仓库到临时目录
    git clone --depth 1 "$SKILL_REPO" "$SKILL_DIR" || {
        print_error "克隆仓库失败"
        exit 1
    }
    
    print_success "下载完成"
}

# 检测平台
detect_platform() {
    if [ -d "$HOME/.aone_copilot/skills" ]; then
        echo "aone_copilot"
    elif [ -d "$HOME/.claude/skills" ]; then
        echo "claude_code"
    elif command -v codefuse &> /dev/null; then
        echo "codefuse"
    else
        echo "unknown"
    fi
}

# 安装到 Aone Copilot
install_aone_copilot() {
    print_info "安装到 Aone Copilot..."
    
    local target_dir="$HOME/.aone_copilot/skills/$SKILL_NAME"
    
    # 创建目录
    mkdir -p "$target_dir"
    
    # 复制文件
    cp -r "$SKILL_DIR"/* "$target_dir/"
    
    # 设置权限
    chmod +x "$target_dir"/*.py 2>/dev/null || true
    
    print_success "已安装到: $target_dir"
    print_info "Python 脚本位置: $target_dir"
    
    # 验证安装
    if [ -f "$target_dir/SKILL.md" ]; then
        print_success "SKILL.md 已就位"
    else
        print_error "SKILL.md 文件缺失"
        return 1
    fi
}

# 安装到 Claude Code
install_claude_code() {
    print_info "安装到 Claude Code..."
    
    local target_dir="$HOME/.claude/skills/$SKILL_NAME"
    
    # 创建目录
    mkdir -p "$target_dir"
    
    # 只复制 SKILL.md（Claude Code 只需要这个）
    cp "$SKILL_DIR/SKILL.md" "$target_dir/"
    
    print_success "已安装到: $target_dir"
    
    # 验证安装
    if [ -f "$target_dir/SKILL.md" ]; then
        print_success "SKILL.md 已就位"
    else
        print_error "SKILL.md 文件缺失"
        return 1
    fi
}

# 安装到 CodeFuse
install_codefuse() {
    print_info "安装到 CodeFuse..."
    
    local target_dir="$HOME/.codefuse/skills/$SKILL_NAME"
    
    # 创建目录
    mkdir -p "$target_dir"
    
    # 复制所有文件
    cp -r "$SKILL_DIR"/* "$target_dir/"
    
    # 创建 .skill 包（如果需要）
    if command -v codefuse &> /dev/null; then
        print_info "检测到 CodeFuse CLI，正在打包..."
        cd "$SKILL_DIR"
        codefuse package skill . -o "$target_dir/$SKILL_NAME.skill" || {
            print_warning "打包失败，跳过 .skill 文件创建"
        }
        cd - > /dev/null
    fi
    
    # 设置权限
    chmod +x "$target_dir"/*.py 2>/dev/null || true
    
    print_success "已安装到: $target_dir"
    
    # 验证安装
    if [ -f "$target_dir/SKILL.md" ]; then
        print_success "SKILL.md 已就位"
    else
        print_error "SKILL.md 文件缺失"
        return 1
    fi
}

# 手动安装
manual_install() {
    print_warning "未检测到已知平台，使用手动安装模式"
    echo ""
    echo "请选择目标平台:"
    echo "  1) Aone Copilot (~/.aone_copilot/skills/)"
    echo "  2) Claude Code (~/.claude/skills/)"
    echo "  3) CodeFuse (~/.codefuse/skills/)"
    echo "  4) 自定义路径"
    echo "  5) 退出"
    echo ""
    read -p "请输入选项 [1-5]: " choice
    
    case $choice in
        1)
            install_aone_copilot
            ;;
        2)
            install_claude_code
            ;;
        3)
            install_codefuse
            ;;
        4)
            read -p "请输入目标路径: " custom_path
            mkdir -p "$custom_path/$SKILL_NAME"
            cp -r "$SKILL_DIR"/* "$custom_path/$SKILL_NAME/"
            print_success "已安装到: $custom_path/$SKILL_NAME"
            ;;
        5)
            print_info "已取消安装"
            exit 0
            ;;
        *)
            print_error "无效选项"
            exit 1
            ;;
    esac
}

# 显示安装信息
show_install_info() {
    echo ""
    echo "======================================"
    echo "  TDD Pipeline Executor 安装完成"
    echo "======================================"
    echo ""
    echo "技能名称: $SKILL_NAME"
    echo "安装位置: $1"
    echo ""
    echo "使用方法:"
    echo "  1. 重启你的 AI 助手（Aone Copilot / Claude Code / CodeFuse）"
    echo "  2. 使用以下命令测试:"
    echo "     python -m tdd_toolkit init"
    echo ""
    echo "  3. 或者直接在对话中使用:"
    echo "     '使用 TDD Pipeline 实现一个功能'"
    echo ""
    echo "更多信息请查看: $1/SKILL.md"
    echo ""
}

# 主安装流程
main() {
    echo ""
    echo "╔════════════════════════════════════════╗"
    echo "║   TDD Pipeline Executor 安装程序        ║"
    echo "╚════════════════════════════════════════╝"
    echo ""
    
    # 如果是远程模式，先下载文件
    if [ "$INSTALL_MODE" = "remote" ]; then
        download_skill
    fi
    
    # 检查必要文件
    if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
        print_error "找不到 SKILL.md 文件"
        exit 1
    fi
    
    # 检测平台
    print_info "检测运行环境..."
    platform=$(detect_platform)
    
    case $platform in
        aone_copilot)
            print_success "检测到 Aone Copilot"
            install_aone_copilot
            show_install_info "$HOME/.aone_copilot/skills/$SKILL_NAME"
            ;;
        claude_code)
            print_success "检测到 Claude Code"
            install_claude_code
            show_install_info "$HOME/.claude/skills/$SKILL_NAME"
            ;;
        codefuse)
            print_success "检测到 CodeFuse"
            install_codefuse
            show_install_info "$HOME/.codefuse/skills/$SKILL_NAME"
            ;;
        *)
            manual_install
            ;;
    esac
    
    print_success "安装完成！"
}

# 运行主程序
main "$@"