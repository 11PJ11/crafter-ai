# /git - Git Workflow Assistant Command

```yaml
---
command: "/git"
category: "Version Control & Deployment"
purpose: "Git workflow assistant with intelligent automation"
wave-enabled: false
performance-profile: "standard"
---
```

## Overview

Intelligent Git workflow assistant that streamlines version control operations with automated commit message generation, branch management, and deployment coordination.

## Auto-Persona Activation
- **DevOps**: Primary persona for deployment and infrastructure workflows
- **Scribe**: Professional commit messages and PR descriptions
- **QA**: Quality validation before commits
- **Security**: Security review for sensitive changes

## MCP Server Integration
- **Primary**: Sequential (workflow coordination and process management)
- **Secondary**: Context7 (Git best practices and workflow patterns)

## Tool Orchestration
- **Bash**: Git command execution
- **Read**: Code change analysis
- **Grep**: Change pattern analysis
- **Edit**: Git configuration updates
- **TodoWrite**: Workflow progress tracking

## Arguments

### Basic Usage
```bash
/git [operation]
```

### Advanced Usage
```bash
/git [operation] @<path> !<command> --<flags>
```

### Operations
- **commit**: Intelligent commit with auto-generated messages
- **branch**: Branch management and strategy
- **merge**: Merge operations and conflict resolution
- **rebase**: Rebase operations and history cleanup
- **release**: Release preparation and tagging
- **deploy**: Deployment coordination

### Path Arguments
- `@<path>`: Specific path for git operations
- `@.`: Current directory
- `@src/`: Source code changes
- `@docs/`: Documentation changes

### Command Arguments
- `!test`: Run tests before commit
- `!lint`: Run linting before commit
- `!build`: Build verification

### Flags
- `--message <msg>`: Custom commit message
- `--branch <name>`: Target branch
- `--force`: Force operation (use carefully)
- `--dry-run`: Preview operation without execution
- `--interactive`: Interactive mode for complex operations

## Git Operations

### Intelligent Commit
- **Change Analysis**: Automatic change categorization
- **Message Generation**: Professional commit message creation
- **Quality Gates**: Pre-commit validation
- **File Staging**: Smart file staging based on changes

### Branch Management
- **Branch Strategy**: GitFlow, GitHub Flow, or custom strategy
- **Naming Conventions**: Consistent branch naming
- **Branch Cleanup**: Remove merged and stale branches
- **Protection Rules**: Branch protection configuration

### Merge Operations
- **Merge Strategy**: Fast-forward, merge commit, or squash
- **Conflict Resolution**: Intelligent conflict resolution assistance
- **Pre-merge Validation**: Quality checks before merge
- **Post-merge Cleanup**: Branch cleanup after merge

### Release Management
- **Version Tagging**: Semantic versioning support
- **Release Notes**: Automatic release note generation
- **Change Log**: Comprehensive change documentation
- **Deployment Preparation**: Release artifact preparation

## Commit Message Templates

### Conventional Commits
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Formatting changes
- **refactor**: Code refactoring
- **test**: Test additions or modifications
- **chore**: Maintenance tasks

### Scopes
- **api**: API changes
- **ui**: User interface changes
- **auth**: Authentication changes
- **db**: Database changes
- **config**: Configuration changes

## Workflow Patterns

### Feature Development
1. **Feature Branch**: Create feature branch
2. **Development**: Implement feature with regular commits
3. **Testing**: Comprehensive testing
4. **Review**: Code review and approval
5. **Merge**: Merge to main branch
6. **Cleanup**: Remove feature branch

### Hotfix Process
1. **Hotfix Branch**: Create from main/production
2. **Quick Fix**: Implement minimal fix
3. **Testing**: Critical path testing
4. **Emergency Review**: Fast-track review
5. **Deploy**: Direct deployment
6. **Backport**: Apply to development branch

### Release Process
1. **Release Branch**: Create release candidate
2. **Stabilization**: Bug fixes and polish
3. **Testing**: Full regression testing
4. **Documentation**: Release documentation
5. **Tagging**: Version tag creation
6. **Deployment**: Production deployment

## Quality Gates

### Pre-Commit Hooks
- **Linting**: Code quality validation
- **Formatting**: Code formatting consistency
- **Testing**: Unit test execution
- **Security**: Security vulnerability scanning

### Pre-Push Hooks
- **Integration Tests**: Full test suite execution
- **Build Validation**: Successful build verification
- **Documentation**: Documentation completeness
- **Performance**: Performance regression testing

### Branch Protection
- **Required Reviews**: Minimum review requirements
- **Status Checks**: CI/CD pipeline validation
- **Up-to-date Branches**: Force branch updates
- **Admin Enforcement**: Apply rules to administrators

## Deployment Integration

### CI/CD Integration
- **Pipeline Triggers**: Automatic pipeline execution
- **Environment Promotion**: Stage-based deployment
- **Rollback Support**: Automatic rollback capability
- **Monitoring Integration**: Deployment monitoring

### Deployment Strategies
- **Blue-Green**: Zero-downtime deployment
- **Rolling**: Gradual deployment rollout
- **Canary**: Risk-mitigated deployment
- **Feature Flags**: Feature toggle deployment

## Security and Compliance

### Security Scanning
- **Secret Detection**: Prevent secret commits
- **Vulnerability Scanning**: Dependency vulnerability check
- **License Compliance**: License compatibility validation
- **Code Signing**: Commit and tag signing

### Audit Trail
- **Change Tracking**: Comprehensive change history
- **Author Attribution**: Clear change attribution
- **Review Records**: Code review documentation
- **Compliance Reporting**: Regulatory compliance reports

## Examples

### Smart Commit
```bash
/git commit @src/ !test --message "feat(auth): implement OAuth2 integration"
```

### Branch Management
```bash
/git branch --branch feature/user-dashboard !lint
```

### Release Preparation
```bash
/git release --version 1.2.0 !build
```

### Deployment
```bash
/git deploy --branch main --environment production
```

### Interactive Merge
```bash
/git merge --interactive --branch develop
```