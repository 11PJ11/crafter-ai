# Layer 4 for CI/CD

**Version**: 1.4.0
**Date**: 2026-01-21
**Status**: Production Ready

Pipeline integration for automated peer review in CI/CD workflows.

**Prerequisites**: nwave CLI available in CI environment.

**Related Docs**:
- [API Reference](../reference/layer-4-api-reference.md) (contracts)
- [For Developers](layer-4-for-developers.md) (code)
- [For Users](layer-4-for-users.md) (CLI)

---

## Quick Start

Add to your pipeline:

```yaml
- name: Layer 4 Review
  run: |
    nwave review \
      --artifact docs/requirements/requirements.md \
      --reviewer business-analyst-reviewer \
      --fail-on-critical \
      --output-format json
```

---

## GitHub Actions Integration

### Complete Workflow

**.github/workflows/layer4-review.yml**:

```yaml
name: Layer 4 Adversarial Verification

on:
  pull_request:
    paths:
      - 'docs/requirements/**'
      - 'docs/architecture/**'
      - 'tests/acceptance/**'
      - 'src/**'

jobs:
  layer4-peer-review:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup nWave
        uses: nwave/setup-action@v1
        with:
          version: '1.0.0'

      - name: Detect changed artifacts
        id: detect
        run: |
          CHANGED_FILES=$(git diff --name-only ${{ github.event.pull_request.base.sha }} ${{ github.sha }})
          echo "changed_files=$CHANGED_FILES" >> $GITHUB_OUTPUT

      - name: Run Layer 4 Review (Requirements)
        if: contains(steps.detect.outputs.changed_files, 'docs/requirements/')
        run: |
          nwave review \
            --artifact docs/requirements/requirements.md \
            --reviewer business-analyst-reviewer \
            --fail-on-critical \
            --output-format json > review_requirements.json

      - name: Run Layer 4 Review (Architecture)
        if: contains(steps.detect.outputs.changed_files, 'docs/architecture/')
        run: |
          nwave review \
            --artifact docs/architecture/architecture.md \
            --reviewer solution-architect-reviewer \
            --fail-on-critical \
            --output-format json > review_architecture.json

      - name: Run Layer 4 Review (Tests)
        if: contains(steps.detect.outputs.changed_files, 'tests/acceptance/')
        run: |
          nwave review \
            --artifact tests/acceptance/*.feature \
            --reviewer acceptance-designer-reviewer \
            --fail-on-critical \
            --output-format json > review_tests.json

      - name: Upload review reports
        uses: actions/upload-artifact@v3
        with:
          name: layer4-reviews
          path: review_*.json

      - name: Comment on PR
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            let comment = '## Layer 4 Adversarial Verification Results\n\n';

            const files = ['review_requirements.json', 'review_architecture.json', 'review_tests.json'];
            for (const file of files) {
              if (fs.existsSync(file)) {
                const review = JSON.parse(fs.readFileSync(file, 'utf8'));
                comment += `### ${review.artifact}\n`;
                comment += `**Status**: ${review.approval_status}\n`;
                comment += `**Issues**: ${review.critical_issues_count} critical, ${review.high_issues_count} high\n\n`;
              }
            }

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });

      - name: Fail if critical issues
        run: |
          for file in review_*.json; do
            if [ -f "$file" ]; then
              CRITICAL=$(jq -r '.critical_issues_count' "$file")
              if [ "$CRITICAL" -gt 0 ]; then
                echo "Critical issues in $file: $CRITICAL"
                exit 1
              fi
            fi
          done
```

---

## GitLab CI Integration

### .gitlab-ci.yml

```yaml
stages:
  - build
  - test_layer1
  - test_layer4
  - deploy

layer4_peer_review:
  stage: test_layer4
  image: nwave/cli:latest
  script:
    - echo "Layer 4 Adversarial Verification"

    # Review changed artifacts
    - |
      if [ -f "docs/requirements/requirements.md" ]; then
        nwave review \
          --artifact docs/requirements/requirements.md \
          --reviewer business-analyst-reviewer \
          --fail-on-critical \
          --output-format json > review_requirements.json
      fi

    # Check approval status
    - |
      if [ -f "review_requirements.json" ]; then
        APPROVAL=$(jq -r '.approval_status' review_requirements.json)
        if [ "$APPROVAL" != "approved" ]; then
          echo "Peer review not approved: $APPROVAL"
          exit 1
        fi
      fi

  artifacts:
    paths:
      - review_*.json
    when: always

  only:
    changes:
      - docs/requirements/**
      - docs/architecture/**
      - tests/acceptance/**
```

---

## Jenkins Pipeline Integration

### Jenkinsfile

```groovy
pipeline {
  agent any

  stages {
    stage('Build') {
      steps {
        sh 'make build'
      }
    }

    stage('Layer 1: Unit Tests') {
      steps {
        sh 'make test-layer1'
      }
    }

    stage('Layer 4: Peer Review') {
      steps {
        script {
          def reviewResult = sh(
            script: '''
              nwave review \
                --artifact docs/requirements/requirements.md \
                --reviewer business-analyst-reviewer \
                --output-format json
            ''',
            returnStdout: true
          ).trim()

          def review = readJSON text: reviewResult

          if (review.approval_status != 'approved') {
            error("Layer 4 review not approved: ${review.critical_issues_count} critical issues")
          }

          publishHTML([
            reportDir: 'reviews',
            reportFiles: 'review_*.html',
            reportName: 'Layer 4 Review Report'
          ])
        }
      }
    }

    stage('Deploy') {
      when {
        expression { currentBuild.result != 'FAILURE' }
      }
      steps {
        sh 'make deploy'
      }
    }
  }

  post {
    failure {
      slackSend(
        channel: '#ci-alerts',
        color: 'danger',
        message: "Layer 4 review failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
      )
    }
  }
}
```

---

## Pass/Fail Configuration

### Blocking Criteria

Configure when to fail the pipeline:

```yaml
# In .nwave/layer4.yaml
layer4:
  approval:
    block_on_critical: true       # Fail on any critical issue
    block_on_high_count: 3        # Fail if > 3 high issues
```

### Warning Only

Pass pipeline with warnings:

```bash
nwave review \
  --artifact docs/requirements/requirements.md \
  --reviewer business-analyst-reviewer \
  --warn-on-critical   # Don't fail, just warn
```

---

## Metrics Collection

### Export to Prometheus

```yaml
# In .nwave/layer4.yaml
layer4:
  metrics:
    enabled: true
    export_to:
      - prometheus
    endpoint: "http://prometheus:9090/metrics"
```

### Export to Datadog

```yaml
layer4:
  metrics:
    enabled: true
    export_to:
      - datadog
    datadog_api_key: "${DATADOG_API_KEY}"
```

### Available Metrics

| Metric | Description |
|--------|-------------|
| `layer4_review_duration_seconds` | Review time |
| `layer4_issues_per_review` | Issues by severity |
| `layer4_approval_rate` | Approval rate |
| `layer4_iteration_count` | Iterations to approval |

---

## Artifact-Based Triggers

### Review by File Path

```yaml
# GitHub Actions
- name: Review Requirements
  if: contains(steps.detect.outputs.changed_files, 'docs/requirements/')
  run: nwave review --artifact docs/requirements/ --reviewer business-analyst-reviewer

- name: Review Architecture
  if: contains(steps.detect.outputs.changed_files, 'docs/architecture/')
  run: nwave review --artifact docs/architecture/ --reviewer solution-architect-reviewer

- name: Review Tests
  if: contains(steps.detect.outputs.changed_files, 'tests/acceptance/')
  run: nwave review --artifact tests/acceptance/ --reviewer acceptance-designer-reviewer

- name: Review Code
  if: contains(steps.detect.outputs.changed_files, 'src/')
  run: nwave review --artifact src/ --reviewer software-crafter-reviewer
```

---

## Parallel Reviews

Run multiple reviews in parallel:

```yaml
# GitHub Actions with matrix
jobs:
  layer4-review:
    strategy:
      matrix:
        include:
          - artifact: docs/requirements/
            reviewer: business-analyst-reviewer
          - artifact: docs/architecture/
            reviewer: solution-architect-reviewer
          - artifact: tests/acceptance/
            reviewer: acceptance-designer-reviewer
    steps:
      - run: |
          nwave review \
            --artifact ${{ matrix.artifact }} \
            --reviewer ${{ matrix.reviewer }} \
            --fail-on-critical
```

---

## Notification Integration

### Slack Notification

```yaml
- name: Notify on failure
  if: failure()
  run: |
    curl -X POST $SLACK_WEBHOOK_URL \
      -H 'Content-Type: application/json' \
      -d '{
        "text": "Layer 4 review failed",
        "attachments": [{
          "color": "danger",
          "fields": [{
            "title": "PR",
            "value": "${{ github.event.pull_request.html_url }}"
          }]
        }]
      }'
```

### Email Notification

```yaml
- name: Email on critical issues
  if: failure()
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    subject: "Layer 4 Review Failed - ${{ github.repository }}"
    body: "Critical issues detected in PR #${{ github.event.pull_request.number }}"
    to: team@example.com
```

---

## Troubleshooting

### Pipeline Timeout

**Error**: `Review timed out`

**Fix**: Increase timeout:
```yaml
- name: Run review
  timeout-minutes: 15
  run: nwave review --artifact ...
```

### Missing Reviewer in CI

**Error**: `Reviewer not found`

**Fix**: Install reviewers in CI:
```yaml
- name: Setup nWave
  run: |
    ./scripts/install-nwave.sh
    ls $NWAVE_REVIEWERS_DIR/  # Verify
```

### JSON Parse Error

**Error**: `Invalid JSON output`

**Fix**: Use explicit format:
```bash
nwave review \
  --artifact ... \
  --output-format json \
  2>/dev/null > review.json
```

---

**Last Updated**: 2026-01-21
**Type**: How-to Guide
**Purity**: 95%+
