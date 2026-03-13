#!/bin/bash
#
# TDD Pipeline Executor 卸载脚本
# 支持 CodeFuse、Aone Copilot 和 Claude Code
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

# 检测已安装的平台
detect_installed_platforms() {
    local platforms=()
    
    if [ -d "$HOME/.aone_copilot/skills/$SKILL_NAME" ]; then
        platforms+=("aone_copilot")
    fi
    
    if [ -d "$HOME/.claude/skills/$SKILL_NAME" ]; then
        platforms+=("claude_code")
    fi
    
    if [ -d "$HOME/.codefuse/skills/$SKILL_NAME" ]; then
        platforms+=("codefuse")
    fi
    
    echo "${platforms[@]}"
}

# 从 Aone Copilot 卸载
uninstall_aone_copilot() {
    local target_dir="$HOME/.aone_copilot/skills/$SKILL_NAME"
    
    if [ -d "$target_dir" ]; then
        print_info "从 Aone Copilot 卸载..."
        rm -rf "$target_dir"
        print_success "已从 Aone Copilot 卸载"
    else
        print_warning "Aone Copilot 中未找到此技能"
    fi
}

# 从 Claude Code 卸载
uninstall_claude_code() {
    local target_dir="$HOME/.claude/skills/$SKILL_NAME"
    
    if [ -d "$target_dir" ]; then
        print_info "从 Claude Code 卸载..."
        rm -rf "$target_dir"
        print_success "已从 Claude Code 卸载"
    else
        print_warning "Claude Code 中未找到此技能"
    fi
}

# 从 CodeFuse 卸载
uninstall_codefuse() {
    local target_dir="$HOME/.codefuse/skills/$SKILL_NAME"
    
    if [ -d "$target_dir" ]; then
        print_info "从 CodeFuse 卸载..."
        rm -rf "$target_dir"
        print_success "已从 CodeFuse 卸载"
    else
        print_warning "CodeFuse 中未找到此技能"
    fi
}

# 从所有平台卸载
uninstall_all() {
    uninstall_aone_copilot
    uninstall_claude_code
    uninstall_codefuse
}

# 主卸载流程
main() {
    echo ""
    echo "╔════════════════════════════════════════╗"
    echo "║   TDD Pipeline Executor 卸载程序        ║"
    echo "╚════════════════════════════════════════╝"
    echo ""
    
    # 检测已安装的平台
    platforms=$(detect_installed_platforms)
    
    if [ -z "$platforms" ]; then
        print_warning "未检测到此技能的安装"
        exit 0
    fi
    
    # 显示已安装的平台
    print_info "检测到以下平台已安装此技能:"
    for platform in $platforms; do
        case $platform in
            aone_copilot)
                echo "  - Aone Copilot"
                ;;
            claude_code)
                echo "  - Claude Code"
                ;;
            codefuse)
                echo "  - CodeFuse"
                ;;
        esac
    done
    echo ""
    
    # 询问卸载选项
    read -p "是否卸载所有平台? [Y/n]: " choice
    choice=${choice:-Y}
    
    case $choice in
        y|Y|yes|YES)
            uninstall_all
            ;;
        n|N|no|NO)
            echo ""
            echo "请选择要卸载的平台:"
            echo "  1) Aone Copilot"
            echo "  2) Claude Code"
            echo "  3) CodeFuse"
            echo "  4) 取消"
            echo ""
            read -p "请输入选项 [1-4]: " platform_choice
            
            case $platform_choice in
                1)
                    uninstall_aone_copilot
                    ;;
                2)
                    uninstall_claude_code
                    ;;
                3)
                    uninstall_codefuse
                    ;;
                4)
                    print_info "已取消卸载"
                    exit 0
                    ;;
                *)
                    print_error "无效选项"
                    exit 1
                    ;;
            esac
            ;;
        *)
            print_error "无效选项"
            exit 1
            ;;
    esac
    
    echo ""
    print_success "卸载完成！"
}

# 运行主程序
main "$@"
