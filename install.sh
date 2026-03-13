#!/bin/bash
#
# TDD Pipeline Executor 安装脚本
# 支持 CodeFuse、Aone Copilot 和 Claude Code
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 技能名称和仓库
SKILL_NAME="tdd-pipeline-executor"
SKILL_REPO="https://github.com/DylanHuang-0121/tdd-executor.git"

# 打印函数
print_info() { echo -e "${BLUE}ℹ ${NC}$1"; }
print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }

# 检测平台
detect_platform() {
    if [ -d "$HOME/.aone_copilot/skills" ]; then
        echo "aone_copilot"
    elif [ -d "$HOME/.claude/skills" ]; then
        echo "claude_code"
    elif [ -d "$HOME/.codefuse/skills" ]; then
        echo "codefuse"
    else
        echo "unknown"
    fi
}

# 下载仓库到临时目录
download_repo() {
    local temp_dir=$(mktemp -d)
    print_info "正在从 GitHub 下载..."
    
    git clone --depth 1 "$SKILL_REPO" "$temp_dir" || {
        print_error "克隆仓库失败"
        rm -rf "$temp_dir"
        exit 1
    }
    
    echo "$temp_dir"
}

# 安装 Python 模块到用户空间
install_python_module() {
    local source_dir="$1"
    
    print_info "安装 Python CLI 工具..."
    
    # 创建 Python 包目录
    local python_dir="$HOME/.tdd-toolkit"
    mkdir -p "$python_dir"
    
    # 复制必要的 Python 文件
    cp -r "$source_dir/tdd-toolkit" "$python_dir/" 2>/dev/null || true
    cp "$source_dir/__main__.py" "$python_dir/" 2>/dev/null || true
    cp "$source_dir/utils.py" "$python_dir/" 2>/dev/null || true
    cp "$source_dir/tdd-pipeline.py" "$python_dir/" 2>/dev/null || true
    cp "$source_dir/issue-tracker.py" "$python_dir/" 2>/dev/null || true
    cp "$source_dir/tdd-runner.py" "$python_dir/" 2>/dev/null || true
    cp "$source_dir/requirements.txt" "$python_dir/" 2>/dev/null || true
    
    # 创建可执行脚本
    local bin_dir="$HOME/.local/bin"
    mkdir -p "$bin_dir"
    
    cat > "$bin_dir/tdd-toolkit" << 'EOF'
#!/bin/bash
python3 -m tdd_toolkit "$@"
EOF
    chmod +x "$bin_dir/tdd-toolkit"
    
    print_success "Python CLI 已安装到: $bin_dir/tdd-toolkit"
    
    # 检查 PATH
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        print_warning "请将以下内容添加到 ~/.zshrc 或 ~/.bashrc:"
        echo '  export PATH="$HOME/.local/bin:$PATH"'
        echo "  然后运行: source ~/.zshrc"
    fi
}

# 安装到 Aone Copilot
install_aone_copilot() {
    local source_dir="$1"
    local target_dir="$HOME/.aone_copilot/skills/$SKILL_NAME"
    
    print_info "安装到 Aone Copilot..."
    
    # 创建目录
    mkdir -p "$target_dir"
    
    # 复制所有必要文件
    print_info "复制文件到: $target_dir"
    
    # 复制 SKILL.md
    if [ -f "$source_dir/SKILL.md" ]; then
        cp "$source_dir/SKILL.md" "$target_dir/"
        print_success "SKILL.md 已复制"
    else
        print_error "找不到 SKILL.md"
    fi
    
    # 复制 Python 模块目录
    if [ -d "$source_dir/tdd-toolkit" ]; then
        cp -r "$source_dir/tdd-toolkit" "$target_dir/"
        print_success "tdd-toolkit/ 目录已复制"
    else
        print_warning "找不到 tdd-toolkit 目录"
    fi
    
    # 复制其他必要文件
    for file in __main__.py utils.py tdd-pipeline.py issue-tracker.py tdd-runner.py requirements.txt; do
        if [ -f "$source_dir/$file" ]; then
            cp "$source_dir/$file" "$target_dir/"
            print_success "$file 已复制"
        fi
    done
    
    # 设置权限
    chmod +x "$target_dir"/*.py 2>/dev/null || true
    
    print_success "已安装到: $target_dir"
    
    # 验证并显示文件列表
    echo ""
    print_info "验证安装结果:"
    ls -lh "$target_dir" | tail -n +2
}

# 安装到 Claude Code
install_claude_code() {
    local source_dir="$1"
    local target_dir="$HOME/.claude/skills/$SKILL_NAME"
    
    print_info "安装到 Claude Code..."
    
    mkdir -p "$target_dir"
    cp "$source_dir/SKILL.md" "$target_dir/"
    
    print_success "已安装到: $target_dir"
}

# 安装到 CodeFuse
install_codefuse() {
    local source_dir="$1"
    local target_dir="$HOME/.codefuse/skills/$SKILL_NAME"
    
    print_info "安装到 CodeFuse..."
    
    mkdir -p "$target_dir"
    cp "$source_dir/SKILL.md" "$target_dir/"
    
    print_success "已安装到: $target_dir"
}

# 主安装流程
main() {
    echo ""
    echo "╔════════════════════════════════════════╗"
    echo "║   TDD Pipeline Executor 安装程序        ║"
    echo "╚════════════════════════════════════════╝"
    echo ""
    
    local source_dir=""
    local need_cleanup=false
    
    # 检测安装模式
    if [ -f "./SKILL.md" ]; then
        print_info "检测到本地安装模式"
        source_dir="$(pwd)"
    elif [ -n "${BASH_SOURCE[0]}" ] && [ -f "$(dirname "${BASH_SOURCE[0]}")/SKILL.md" ]; then
        print_info "检测到本地安装模式"
        source_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    else
        print_info "检测到远程安装模式"
        source_dir=$(download_repo)
        need_cleanup=true
    fi
    
    # 验证源文件
    if [ ! -f "$source_dir/SKILL.md" ]; then
        print_error "找不到 SKILL.md 文件"
        [ "$need_cleanup" = true ] && rm -rf "$source_dir"
        exit 1
    fi
    
    print_success "源文件准备完成: $source_dir"
    echo ""
    
    # 安装 Python 模块（全局可用）
    install_python_module "$source_dir"
    echo ""
    
    # 检测并安装到平台
    print_info "检测运行环境..."
    platform=$(detect_platform)
    
    case $platform in
        aone_copilot)
            print_success "检测到 Aone Copilot"
            install_aone_copilot "$source_dir"
            ;;
        claude_code)
            print_success "检测到 Claude Code"
            install_claude_code "$source_dir"
            ;;
        codefuse)
            print_success "检测到 CodeFuse"
            install_codefuse "$source_dir"
            ;;
        *)
            print_warning "未检测到已知平台，跳过平台安装"
            print_info "Python CLI 已安装，可使用: tdd-toolkit init"
            ;;
    esac
    
    # 清理临时文件
    if [ "$need_cleanup" = true ]; then
        echo ""
        print_info "清理临时文件..."
        rm -rf "$source_dir"
    fi
    
    # 显示使用说明
    echo ""
    echo "======================================"
    echo "  安装完成！"
    echo "======================================"
    echo ""
    echo "使用方法:"
    echo "  1. 重启你的 AI 助手（如需要）"
    echo "  2. 使用以下命令测试:"
    echo ""
    echo "     # 方式1: 使用 CLI"
    echo "     tdd-toolkit init"
    echo ""
    echo "     # 方式2: 使用 Python 模块"
    echo "     python3 -m tdd_toolkit init"
    echo ""
    echo "  3. 在项目中使用:"
    echo "     cd /path/to/your/project"
    echo "     tdd-toolkit init"
    echo "     tdd-toolkit pipeline --project my-feature"
    echo ""
}

# 运行主程序
main "$@"
