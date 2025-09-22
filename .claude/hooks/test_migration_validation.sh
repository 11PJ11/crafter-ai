#!/bin/bash
# Migration Validation Test
# Validates that migrated hooks produce identical results to originals

set -euo pipefail

echo "🧪 Testing Migration Validation"

# Test 1: state-initializer.sh migration
echo "Testing state-initializer.sh migration..."

# Clean state
rm -rf state/craft-ai test-results/

# Create test results directory
mkdir -p test-results/{original,migrated}

# Test original version
echo "  Testing original version..."
bash .claude/hooks/legacy/state-initializer-original.sh cai/atdd 2>/dev/null
cp -r state/craft-ai test-results/original/ 2>/dev/null || true

# Clean state
rm -rf state/craft-ai

# Test migrated version
echo "  Testing migrated version..."
bash .claude/hooks/workflow/state-initializer-v2.sh cai/atdd 2>/dev/null
cp -r state/craft-ai test-results/migrated/ 2>/dev/null || true

# Compare results
echo "  Comparing results..."
if diff -r test-results/original/craft-ai test-results/migrated/craft-ai >/dev/null 2>&1; then
    echo "✅ state-initializer.sh migration: IDENTICAL BEHAVIOR"
else
    echo "❌ state-initializer.sh migration: BEHAVIOR DIFFERS"
    diff -r test-results/original/craft-ai test-results/migrated/craft-ai || true
fi

# Test 2: Performance comparison
echo "Testing performance comparison..."

# Time original
time_original=$(bash -c 'time bash .claude/hooks/legacy/state-initializer-original.sh cai/atdd 2>&1' 2>&1 | grep real | awk '{print $2}')

# Time migrated (suppressing logs for fair comparison)
time_migrated=$(bash -c 'time bash .claude/hooks/workflow/state-initializer-v2.sh cai/atdd 2>/dev/null' 2>&1 | grep real | awk '{print $2}')

echo "  Original execution time: ${time_original:-N/A}"
echo "  Migrated execution time: ${time_migrated:-N/A}"

# Test 3: Error handling
echo "Testing error handling..."

# Test non-CAI workflow (should skip)
if bash .claude/hooks/workflow/state-initializer-v2.sh non-cai-command 2>/dev/null; then
    echo "✅ Non-CAI workflow correctly skipped"
else
    echo "❌ Non-CAI workflow handling failed"
fi

# Clean up
rm -rf state/craft-ai test-results/

echo "✅ Migration validation completed"