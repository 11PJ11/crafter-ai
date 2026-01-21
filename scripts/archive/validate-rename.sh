#!/bin/bash
# Validation script to ensure rename completeness

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "========================================="
echo "  nWave Rename Validation"
echo "========================================="
echo

errors=0

# Check 1: Directory structure
echo "Check 1: Directory structure..."
if [ -d "nWave" ]; then
    echo "✓ nWave/ directory exists"
else
    echo "✗ nWave/ directory NOT found"
    ((errors++))
fi

if [ ! -d "5d-wave" ]; then
    echo "✓ 5d-wave/ directory removed"
else
    echo "✗ 5d-wave/ directory still exists"
    ((errors++))
fi

if [ -d "nWave/tasks/nw" ]; then
    echo "✓ nWave/tasks/nw/ exists"
else
    echo "✗ nWave/tasks/nw/ NOT found"
    ((errors++))
fi

if [ ! -d "nWave/tasks/dw" ]; then
    echo "✓ nWave/tasks/dw/ removed"
else
    echo "✗ nWave/tasks/dw/ still exists"
    ((errors++))
fi

# Check 2: No remaining old references
echo
echo "Check 2: Searching for old references..."

old_dir_refs=$(grep -r "5d-wave" --exclude-dir={.git,dist,output,node_modules,tools} \
               --exclude="*.log" --exclude="validate-rename.sh" \
               --include="*.py" --include="*.sh" --include="*.yaml" --include="*.yml" \
               --include="*.md" --include="*.json" 2>/dev/null | wc -l)

if [ "$old_dir_refs" -eq 0 ]; then
    echo "✓ No remaining '5d-wave' references"
else
    echo "✗ Found $old_dir_refs remaining '5d-wave' references"
    ((errors++))
fi

old_cmd_refs=$(grep -r "/dw:" --exclude-dir={.git,dist,output,node_modules} \
               --include="*.md" --include="*.yaml" --include="*.yml" 2>/dev/null | wc -l)

if [ "$old_cmd_refs" -eq 0 ]; then
    echo "✓ No remaining '/dw:' command references"
else
    echo "✗ Found $old_cmd_refs remaining '/dw:' references"
    ((errors++))
fi

old_category_refs=$(grep -r "agents/dw\|commands/dw" --exclude-dir={.git,dist,output,node_modules,tools} \
                    --exclude="*.log" --exclude="validate-rename.sh" \
                    --include="*.py" --include="*.sh" --include="*.yaml" --include="*.yml" \
                    2>/dev/null | wc -l)

if [ "$old_category_refs" -eq 0 ]; then
    echo "✓ No remaining 'dw' category path references"
else
    echo "✗ Found $old_category_refs remaining 'dw' category references"
    ((errors++))
fi

# Check 3: Build system validation
echo
echo "Check 3: Build system validation..."
if grep -q "nWave" tools/build_config.yaml; then
    echo "✓ build_config.yaml updated"
else
    echo "✗ build_config.yaml not updated"
    ((errors++))
fi

if grep -q "agents/nw" tools/build_config.yaml; then
    echo "✓ IDE category updated to 'nw'"
else
    echo "✗ IDE category not updated"
    ((errors++))
fi

# Check 4: Configuration authority
echo
echo "Check 4: Configuration validation..."
if [ -f "nWave/framework-catalog.yaml" ]; then
    if grep -q 'methodology: "nWave"' nWave/framework-catalog.yaml; then
        echo "✓ Methodology name updated in framework-catalog.yaml"
    else
        echo "✗ Methodology name not updated in framework-catalog.yaml"
        ((errors++))
    fi
else
    echo "✗ nWave/framework-catalog.yaml not found"
    ((errors++))
fi

# Check 5: CI/CD validation
echo
echo "Check 5: CI/CD configuration..."
if grep -q "nWave/agents" .github/workflows/ci-cd-pipeline.yml; then
    echo "✓ CI/CD pipeline updated"
else
    echo "✗ CI/CD pipeline not updated"
    ((errors++))
fi

# Summary
echo
echo "========================================="
if [ $errors -eq 0 ]; then
    echo "✓ All validation checks PASSED"
    echo "========================================="
    exit 0
else
    echo "✗ Validation FAILED with $errors errors"
    echo "========================================="
    exit 1
fi
