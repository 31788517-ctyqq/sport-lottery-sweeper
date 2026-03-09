#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分支保护规则自动化配置脚本
注意：需要GitHub CLI (gh) 和适当的权限
"""
import subprocess
import sys
import json

def run_gh_command(cmd):
    """执行GitHub CLI命令"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 命令执行失败: {cmd}")
        print(f"错误输出: {e.stderr}")
        return None

def setup_branch_protection():
    """设置分支保护规则"""
    print("🔧 开始配置分支保护规则...")
    
    # 检查GitHub CLI是否安装
    if not run_gh_command("gh --version"):
        print("[ERROR] GitHub CLI (gh) 未安装或未配置")
        print("请先安装GitHub CLI并登录: https://cli.github.com/")
        return False
    
    # 检查是否已登录
    if not run_gh_command("gh auth status"):
        print("[ERROR] 请先登录GitHub CLI: gh auth login")
        return False
    
    # 获取当前仓库信息
    repo_info = run_gh_command("gh repo view --json name,owner")
    if repo_info:
        repo_data = json.loads(repo_info)
        owner = repo_data["owner"]["login"]
        repo = repo_data["name"]
        print(f"[INFO] 当前仓库: {owner}/{repo}")
    else:
        print("[ERROR] 无法获取仓库信息")
        return False
    
    # 分支保护规则配置
    protection_rules = {
        "main": {
            "required_approving_review_count": 2,
            "require_code_owner_reviews": True,
            "dismiss_stale_reviews": True,
            "require_last_push_approval": False,
            "required_status_checks": [
                "CI/CD Pipeline (Optimized) / python-quality",
                "CI/CD Pipeline (Optimized) / javascript-quality", 
                "CI/CD Pipeline (Optimized) / backend-tests",
                "CI/CD Pipeline (Optimized) / frontend-tests",
                "CI/CD Pipeline (Optimized) / security-scan",
                "CI/CD Pipeline (Optimized) / e2e-tests",
                "Code quality check"
            ],
            "require_branches_to_be_up_to_date": True,
            "restrict_pushes": True,
            "restrict_force_pushes": True,
            "allow_deletions": False,
            "enforce_admins": True
        },
        "develop": {
            "required_approving_review_count": 1,
            "require_code_owner_reviews": False,
            "dismiss_stale_reviews": True,
            "required_status_checks": [
                "CI/CD Pipeline (Optimized) / python-quality",
                "CI/CD Pipeline (Optimized) / backend-tests",
                "Code quality check"
            ],
            "require_branches_to_be_up_to_date": True,
            "restrict_force_pushes": False,
            "allow_deletions": False,
            "enforce_admins": False
        },
        "stable-base": {
            "required_approving_review_count": 2,
            "require_code_owner_reviews": True,
            "dismiss_stale_reviews": True,
            "required_status_checks": [
                "CI/CD Pipeline (Optimized) / python-quality",
                "CI/CD Pipeline (Optimized) / javascript-quality",
                "CI/CD Pipeline (Optimized) / backend-tests",
                "CI/CD Pipeline (Optimized) / frontend-tests",
                "CI/CD Pipeline (Optimized) / security-scan",
                "CI/CD Pipeline (Optimized) / e2e-tests",
                "Code quality check"
            ],
            "require_branches_to_be_up_to_date": True,
            "restrict_force_pushes": True,
            "allow_deletions": False,
            "enforce_admins": True
        }
    }
    
    # 应用分支保护规则
    for branch, rules in protection_rules.items():
        print(f"\n[SETUP] 配置 {branch} 分支保护规则...")
        
        # 构建gh命令
        cmd_parts = [
            f"gh api repos/{owner}/{repo}/branches/{branch}/protection",
            "--method PUT",
            "--field required_status_checks[strict]=true",
            f'--field required_status_checks[contexts]={json.dumps(rules["required_status_checks"])}',
            f'--field enforce_admins={str(rules["enforce_admins"]).lower()}',
            f'--field required_pull_request_reviews[required_approving_review_count]={rules["required_approving_review_count"]}',
            f'--field required_pull_request_reviews[dismiss_stale_reviews]={str(rules["dismiss_stale_reviews"]).lower()}',
            f'--field required_pull_request_reviews[require_code_owner_reviews]={str(rules["require_code_owner_reviews"]).lower()}',
            f'--field restrictions=null'
        ]
        
        # 对于main和stable-base，添加更多限制
        if branch in ["main", "stable-base"]:
            cmd_parts.extend([
                "--field restrictions[users]=[]",
                "--field restrictions[teams]=[]"
            ])
        
        cmd = " ".join(cmd_parts)
        
        result = run_gh_command(cmd)
        if result is not None:
            print(f"[SUCCESS] {branch} 分支保护规则配置成功")
        else:
            print(f"[WARNING] {branch} 分支保护规则配置可能需要手动完成")
    
    print("\n✅ 分支保护规则配置完成")
    print("\n📋 手动配置提醒:")
    print("1. 登录GitHub仓库设置页面")
    print("2. 进入 Settings > Branches")
    print("3. 验证上述规则是否正确应用")
    print("4. 根据需要调整具体参数")
    
    return True

def create_branch_policies_doc():
    """创建分支策略文档"""
    doc_content = """# 分支管理策略

## 分支命名规范

### 功能分支
- `feature/JIRA-XXX-description` - 新功能开发
- 示例: `feature/SPORT-123-add-user-authentication`

### Bug修复分支  
- `bugfix/JIRA-XXX-description` - 一般Bug修复
- 示例: `bugfix/SPORT-456-fix-login-validation`

### 紧急热修复分支
- `hotfix/JIRA-XXX-description` - 生产环境紧急修复
- 示例: `hotfix/SPORT-789-emergency-security-patch`

### 其他分支类型
- `refactor/JIRA-XXX-description` - 代码重构
- `docs/JIRA-XXX-description` - 文档更新  
- `test/JIRA-XXX-description` - 测试相关
- `chore/JIRA-XXX-description` - 构建/工具链更新

## 工作流程

### 1. 创建分支
```bash
# 从main分支创建功能分支
git checkout main
git pull origin maingit checkout -b feature/JIRA-XXX-feature-description
```

### 2. 开发和提交
```bash
# 开发功能
git add .
git commit -m "feat: add user authentication feature"

# 推送分支
git push -u origin feature/JIRA-XXX-feature-description
```

### 3. 创建Pull Request
- 目标分支: main (生产发布) 或 develop (开发集成)
- 至少需要的审批数: 见分支保护规则
- 必须通过所有CI/CD检查

### 4. Code Review检查清单
- [ ] 代码符合项目规范
- [ ] 测试覆盖充分
- [ ] 安全性考虑周全
- [ ] 性能影响可接受
- [ ] 文档已更新

### 5. 合并策略
- **Squash and Merge** - 推荐使用，保持提交历史清晰
- **Create a merge commit** - 保留完整提交历史时使用
- **Rebase and merge** - 个人偏好，需团队同意

## 分支生命周期

### 功能分支
1. 创建自: main
2. 合并到: main (发布) 或 develop (集成)
3. 删除时机: PR合并后自动删除

### 发布分支
1. 创建自: main
2. 分支名: `release/vX.Y.Z`
3. 合并到: main 和 develop
4. 删除时机: 发布完成后

### 热修复分支
1. 创建自: main
2. 合并到: main 和 develop
3. 删除时机: PR合并后

## 自动化规则

### Pre-commit检查
- 代码格式化和风格检查
- 类型检查 (Python/TypeScript)
- 安全漏洞扫描
- Import语句验证
- Main.py入口保护

### CI/CD流水线
- Python代码质量检查
- JavaScript/TypeScript代码质量检查  
- 后端单元测试和集成测试
- 前端单元测试和E2E测试
- 安全扫描
- 依赖漏洞检查

### PR要求
- 必须通过所有CI/CD检查
- 需要指定Reviewers
- 必须通过Code Owner审核 (如适用)
- 禁止合并冲突
- 分支必须是最新的
"""
    
    with open("BRANCH_POLICIES.md", "w", encoding="utf-8") as f:
        f.write(doc_content)
    
    print("📄 分支策略文档已生成: BRANCH_POLICIES.md")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="分支保护规则配置工具")
    parser.add_argument("--setup", action="store_true", help="设置分支保护规则")
    parser.add_argument("--doc", action="store_true", help="生成分支策略文档")
    parser.add_argument("--all", action="store_true", help="执行所有操作")
    
    args = parser.parse_args()
    
    if not any([args.setup, args.doc, args.all]):
        parser.print_help()
        return
    
    if args.setup or args.all:
        setup_branch_protection()
    
    if args.doc or args.all:
        create_branch_policies_doc()
    
    print("\\n🎉 操作完成!")

if __name__ == "__main__":
    main()