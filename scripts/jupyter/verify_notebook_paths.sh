#!/bin/bash

# Jupyter Notebook Path Verification Script
# ADS599 Capstone Soccer Intelligence System

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "=========================================="
echo "📓 Jupyter Notebook Path Verification"
echo "=========================================="
echo ""

# Define the specific notebook path
NOTEBOOKS_PATH="/Users/home/Documents/GitHub/ADS599_Capstone/notebooks"
PROJECT_PATH="/Users/home/Documents/GitHub/ADS599_Capstone"

print_status "Verifying notebook storage paths..."

# Check if project directory exists
if [ -d "$PROJECT_PATH" ]; then
    print_success "Project directory exists: $PROJECT_PATH"
else
    print_error "Project directory not found: $PROJECT_PATH"
    echo "Please ensure you're running this from the correct location."
    exit 1
fi

# Check if notebooks directory exists
if [ -d "$NOTEBOOKS_PATH" ]; then
    print_success "Notebooks directory exists: $NOTEBOOKS_PATH"
else
    print_warning "Notebooks directory not found. Creating it now..."
    mkdir -p "$NOTEBOOKS_PATH"
    print_success "Created notebooks directory: $NOTEBOOKS_PATH"
fi

# Verify directory structure
print_status "Checking notebook directory structure..."

directories=(
    "shared"
    "shared/templates"
    "shared/data_exploration"
    "shared/team_analysis"
    "shared/reports"
    "shared/tutorials"
    "personal"
    "personal/analyst_workspace"
    "personal/developer_workspace"
    "personal/researcher_workspace"
    "research"
    "research/methodology"
    "research/literature_review"
    "research/statistical_analysis"
    "research/publications"
    "archive"
    "archive/completed_projects"
    "archive/deprecated_analyses"
    "archive/backup_notebooks"
)

missing_dirs=()
existing_dirs=()

for dir in "${directories[@]}"; do
    full_path="$NOTEBOOKS_PATH/$dir"
    if [ -d "$full_path" ]; then
        existing_dirs+=("$dir")
    else
        missing_dirs+=("$dir")
    fi
done

if [ ${#existing_dirs[@]} -gt 0 ]; then
    print_success "Found ${#existing_dirs[@]} existing directories:"
    for dir in "${existing_dirs[@]}"; do
        echo "  ✅ $dir"
    done
fi

if [ ${#missing_dirs[@]} -gt 0 ]; then
    print_warning "Missing ${#missing_dirs[@]} directories:"
    for dir in "${missing_dirs[@]}"; do
        echo "  ❌ $dir"
    done
    echo ""
    print_status "Creating missing directories..."
    for dir in "${missing_dirs[@]}"; do
        mkdir -p "$NOTEBOOKS_PATH/$dir"
        print_success "Created: $dir"
    done
fi

# Check for existing notebooks
print_status "Scanning for existing notebooks..."

notebook_count=0
if [ -d "$NOTEBOOKS_PATH" ]; then
    notebook_count=$(find "$NOTEBOOKS_PATH" -name "*.ipynb" 2>/dev/null | wc -l)
fi

if [ $notebook_count -gt 0 ]; then
    print_success "Found $notebook_count existing notebook(s)"
    echo ""
    echo "📓 Existing notebooks:"
    find "$NOTEBOOKS_PATH" -name "*.ipynb" 2>/dev/null | while read nb; do
        rel_path=${nb#$NOTEBOOKS_PATH/}
        echo "  📄 $rel_path"
    done
else
    print_status "No existing notebooks found"
fi

# Check templates
print_status "Checking for notebook templates..."

template_path="$NOTEBOOKS_PATH/shared/templates"
if [ -d "$template_path" ]; then
    template_count=$(find "$template_path" -name "*.ipynb" 2>/dev/null | wc -l)
    if [ $template_count -gt 0 ]; then
        print_success "Found $template_count template(s)"
        find "$template_path" -name "*.ipynb" 2>/dev/null | while read template; do
            template_name=$(basename "$template")
            echo "  📄 $template_name"
        done
    else
        print_warning "No templates found. Run setup to create templates:"
        echo "  ./scripts/jupyter/setup_jupyter_collaboration.sh"
    fi
else
    print_warning "Templates directory not found"
fi

# Check Docker volume mounts
print_status "Verifying Docker volume mount configuration..."

if [ -f "docker-compose.yml" ]; then
    if grep -q "/Users/home/Documents/GitHub/ADS599_Capstone/notebooks:/app/notebooks" docker-compose.yml; then
        print_success "Docker volume mounts configured correctly"
    else
        print_warning "Docker volume mounts may need updating"
        echo "Expected mount: /Users/home/Documents/GitHub/ADS599_Capstone/notebooks:/app/notebooks"
    fi
else
    print_warning "docker-compose.yml not found in current directory"
fi

# Check permissions
print_status "Checking directory permissions..."

if [ -w "$NOTEBOOKS_PATH" ]; then
    print_success "Notebooks directory is writable"
else
    print_error "Notebooks directory is not writable"
    echo "You may need to fix permissions:"
    echo "  sudo chown -R \$USER:staff $NOTEBOOKS_PATH"
    echo "  chmod -R 755 $NOTEBOOKS_PATH"
fi

# Test file creation
print_status "Testing file creation..."

test_file="$NOTEBOOKS_PATH/.test_write_access"
if touch "$test_file" 2>/dev/null; then
    rm "$test_file"
    print_success "File creation test passed"
else
    print_error "Cannot create files in notebooks directory"
    echo "Check permissions and try again"
fi

# Summary
echo ""
echo "=========================================="
echo "📊 Path Verification Summary"
echo "=========================================="
echo ""
echo "📁 Notebook Storage Path: $NOTEBOOKS_PATH"
echo "📊 Directory Structure: Complete"
echo "📓 Existing Notebooks: $notebook_count"
echo "📄 Templates Available: $template_count"
echo ""

if [ ${#missing_dirs[@]} -eq 0 ] && [ -w "$NOTEBOOKS_PATH" ]; then
    print_success "✅ All path verification checks passed!"
    echo ""
    echo "🚀 Ready for Jupyter collaboration:"
    echo "  1. Start Jupyter environments: ./scripts/jupyter/manage_notebooks.sh start-jupyter all"
    echo "  2. Access your role-specific environment"
    echo "  3. Create notebooks in the shared directories"
    echo "  4. All notebooks will be stored at: $NOTEBOOKS_PATH"
else
    print_warning "⚠️  Some issues found. Please address them before proceeding."
    echo ""
    echo "🔧 Next steps:"
    if [ ${#missing_dirs[@]} -gt 0 ]; then
        echo "  - Missing directories have been created"
    fi
    if [ ! -w "$NOTEBOOKS_PATH" ]; then
        echo "  - Fix directory permissions"
    fi
    echo "  - Run setup if templates are missing: ./scripts/jupyter/setup_jupyter_collaboration.sh"
fi

echo ""
echo "📚 For more information:"
echo "  - Setup Guide: JUPYTER_COLLABORATION_SETUP.md"
echo "  - Full Documentation: docs/jupyter-collaboration/JUPYTER_COLLABORATION_GUIDE.md"
echo "  - Management Commands: ./scripts/jupyter/manage_notebooks.sh help"
