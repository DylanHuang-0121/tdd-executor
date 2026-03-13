#!/bin/bash
#
# TDD Executor 安装脚本
# 安装到当前项目的 .aone_copilot/skills/ 目录下
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

# 安装到项目的 .aone_copilot/skills/ 目录
install_to_project_skills() {
    local source_dir="$1"
    local project_dir="${2:-$(pwd)}"
    local target_dir="$project_dir/.aone_copilot/skills/$SKILL_NAME"
    
    print_info "安装到项目技能目录: $target_dir"
    
    # 创建目录
    mkdir -p "$target_dir"
    
    # 复制 SKILL.md
    if [ -f "$source_dir/SKILL.md" ]; then
        cp "$source_dir/SKILL.md" "$target_dir/"
        print_success "SKILL.md 已复制"
    else
        print_error "找不到 SKILL.md"
        exit 1
    fi
    
    # 复制所有 Python 文件
    for file in __main__.py utils.py tdd_pipeline.py issue_tracker.py tdd_runner.py requirements.txt; do
        if [ -f "$source_dir/$file" ]; then
            cp "$source_dir/$file" "$target_dir/"
            print_success "$file 已复制"
        fi
    done
    
    # 创建项目内的可执行脚本
    cat > "$target_dir/tdd-executor" << 'WRAPPER_EOF'
#!/bin/bash
# TDD Executor CLI Wrapper
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
python3 __main__.py "$@"
WRAPPER_EOF
    chmod +x "$target_dir/tdd-executor"
    
    print_success "CLI 命令已创建: $target_dir/tdd-executor"
    
    # 创建 pit-library 和 tdd-sessions 目录
    mkdir -p "$project_dir/pit-library"
    mkdir -p "$project_dir/tdd-sessions"
    
    print_success "已创建 pit-library/ 和 tdd-sessions/ 目录"
    
    # 显示安装结果
    echo ""
    print_info "验证安装结果:"
    ls -lh "$target_dir" | tail -n +2
}

# 主安装流程
main() {
    echo ""
    echo "╔════════════════════════════════════════╗"
    echo "║     TDD Executor 安装程序               ║"
    echo "╚════════════════════════════════════════╝"
    echo ""
    
    local source_dir=""
    local project_dir=""
    local need_cleanup=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--dir)
                project_dir="$2"
                shift 2
                ;;
            -h|--help)
                echo "用法: ./install.sh [-d|--dir <项目目录>]"
                echo ""
                echo "选项:"
                echo "  -d, --dir    指定安装到的项目目录（默认：当前目录）"
                echo "  -h, --help   显示帮助信息"
                echo ""
                echo "示例:"
                echo "  ./install.sh                      # 安装到当前项目的 .aone_copilot/skills/"
                echo "  ./install.sh -d /path/to/project  # 安装到指定项目的 .aone_copilot/skills/"
                echo ""
                echo "安装位置:"
                echo "  <项目目录>/.aone_copilot/skills/tdd-pipeline-executor/"
                exit 0
                ;;
            *)
                print_error "未知参数: $1"
                exit 1
                ;;
        esac
    done
    
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
    
    # 安装到项目技能目录
    install_to_project_skills "$source_dir" "$project_dir"
    
    # 清理临时文件
    if [ "$need_cleanup" = true ]; then
        echo ""
        print_info "清理临时文件..."
        rm -rf "$source_dir"
    fi
    
    # 显示使用说明
    local final_project_dir="${project_dir:-$(pwd)}"
    echo ""
    echo "======================================"
    echo "  安装完成！"
    echo "======================================"
    echo ""
    echo "安装位置:"
    echo "  技能目录: $final_project_dir/.aone_copilot/skills/$SKILL_NAME/"
    echo "  CLI 命令: $final_project_dir/.aone_copilot/skills/$SKILL_NAME/tdd-executor"
    echo "  数据目录: $final_project_dir/pit-library/ 和 $final_project_dir/tdd-sessions/"
    echo ""
    echo "使用方法:"
    echo "  1. 重启 Aone Copilot（如果正在运行）"
    echo "  2. 技能会自动加载: tdd-pipeline-executor"
    echo ""
    echo "  3. 或使用 CLI:"
    echo "     $final_project_dir/.aone_copilot/skills/$SKILL_NAME/tdd-executor init"
    echo ""
}

# 运行主程序
main "$@"