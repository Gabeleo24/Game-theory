#!/bin/bash

# Project Structure Verification Script
# ADS599 Capstone Soccer Intelligence System

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
echo "📁 ADS599 Capstone Project Structure Verification"
echo "=========================================="
echo ""

# Define the project root
PROJECT_ROOT="/Users/home/Documents/GitHub/ADS599_Capstone"

# Check if we're in the right directory
if [ ! -d "$PROJECT_ROOT" ]; then
    print_error "Project directory not found: $PROJECT_ROOT"
    exit 1
fi

cd "$PROJECT_ROOT"

print_status "Verifying project structure at: $PROJECT_ROOT"
echo ""

# Define required files in root directory
declare -a REQUIRED_ROOT_FILES=(
    ".dockerignore"
    ".env"
    ".env.backup"
    ".env.template"
    ".gitattributes"
    ".gitignore"
    "CAPSTONE_PROJECT_STARTUP_GUIDE.md"
    "clean_project.sh"
    "COMPLETE_PROJECT_STARTUP.md"
    "docker-compose.yml"
    "Dockerfile"
    "JUPYTER_COLLABORATION_SETUP.md"
    "Makefile"
    "NOTEBOOK_STORAGE_CONFIGURATION.md"
    "PROJECT_OVERVIEW.md"
    "README.md"
    "requirements_minimal.txt"
    "requirements.txt"
    "run_sql_with_logs.sh"
    "show_database_structure.sh"
    "TEAM_COLLABORATION_QUICK_START.md"
)

# Check root files
print_status "Checking root directory files..."
missing_files=()
found_files=()

for file in "${REQUIRED_ROOT_FILES[@]}"; do
    if [ -f "$file" ]; then
        found_files+=("$file")
        echo "  ✅ $file"
    else
        missing_files+=("$file")
        echo "  ❌ $file (MISSING)"
    fi
done

echo ""
print_status "Root files summary:"
echo "  ✅ Found: ${#found_files[@]} files"
if [ ${#missing_files[@]} -gt 0 ]; then
    echo "  ❌ Missing: ${#missing_files[@]} files"
    for file in "${missing_files[@]}"; do
        echo "    - $file"
    done
else
    print_success "All required root files are present!"
fi

echo ""

# Check directory structure
print_status "Checking directory structure..."

declare -a REQUIRED_DIRECTORIES=(
    "assignmentdocs"
    "backups"
    "backups/notebooks"
    "config"
    "config/jupyter"
    "data"
    "data/analysis"
    "data/cache"
    "docker"
    "docker/postgres"
    "docs"
    "docs/jupyter-collaboration"
    "docs/research-methodology"
    "docs/team-collaboration"
    "logs"
    "logs/sql_logs"
    "notebooks"
    "notebooks/shared"
    "notebooks/shared/templates"
    "notebooks/personal"
    "notebooks/research"
    "notebooks/archive"
    "scripts"
    "scripts/setup"
    "scripts/jupyter"
    "scripts/team"
    "scripts/data_loading"
    "src"
    "src/soccer_intelligence"
    "tests"
)

missing_dirs=()
found_dirs=()

for dir in "${REQUIRED_DIRECTORIES[@]}"; do
    if [ -d "$dir" ]; then
        found_dirs+=("$dir")
        echo "  ✅ $dir/"
    else
        missing_dirs+=("$dir")
        echo "  ❌ $dir/ (MISSING)"
    fi
done

echo ""
print_status "Directory structure summary:"
echo "  ✅ Found: ${#found_dirs[@]} directories"
if [ ${#missing_dirs[@]} -gt 0 ]; then
    echo "  ❌ Missing: ${#missing_dirs[@]} directories"
    for dir in "${missing_dirs[@]}"; do
        echo "    - $dir/"
    done
else
    print_success "All required directories are present!"
fi

echo ""

# Check key executable files
print_status "Checking executable permissions..."

declare -a EXECUTABLE_FILES=(
    "clean_project.sh"
    "run_sql_with_logs.sh"
    "show_database_structure.sh"
    "scripts/setup/team_member_setup.sh"
    "scripts/setup/verify_project_structure.sh"
    "scripts/jupyter/setup_jupyter_collaboration.sh"
    "scripts/jupyter/manage_notebooks.sh"
    "scripts/jupyter/verify_notebook_paths.sh"
    "scripts/team/manage_team_access.sh"
)

non_executable=()
executable=()

for file in "${EXECUTABLE_FILES[@]}"; do
    if [ -f "$file" ]; then
        if [ -x "$file" ]; then
            executable+=("$file")
            echo "  ✅ $file (executable)"
        else
            non_executable+=("$file")
            echo "  ⚠️  $file (not executable)"
        fi
    else
        echo "  ❌ $file (file not found)"
    fi
done

if [ ${#non_executable[@]} -gt 0 ]; then
    print_warning "Some files need executable permissions:"
    for file in "${non_executable[@]}"; do
        echo "    chmod +x $file"
    done
fi

echo ""

# Check notebook storage
print_status "Checking notebook storage configuration..."

NOTEBOOKS_PATH="/Users/home/Documents/GitHub/ADS599_Capstone/notebooks"
if [ -d "$NOTEBOOKS_PATH" ]; then
    print_success "Notebook storage configured at: $NOTEBOOKS_PATH"
    
    # Count notebooks
    notebook_count=$(find "$NOTEBOOKS_PATH" -name "*.ipynb" 2>/dev/null | wc -l)
    echo "  📓 Notebooks found: $notebook_count"
    
    # Check templates
    if [ -f "$NOTEBOOKS_PATH/shared/templates/data_analysis_template.ipynb" ]; then
        echo "  ✅ Analysis template available"
    else
        echo "  ⚠️  Analysis template missing"
    fi
else
    print_error "Notebook storage not found at: $NOTEBOOKS_PATH"
fi

echo ""

# Check Docker configuration
print_status "Checking Docker configuration..."

if [ -f "docker-compose.yml" ]; then
    if grep -q "/Users/home/Documents/GitHub/ADS599_Capstone/notebooks:/app/notebooks" docker-compose.yml; then
        print_success "Docker volume mounts configured correctly"
    else
        print_warning "Docker volume mounts may need updating"
    fi
else
    print_error "docker-compose.yml not found"
fi

echo ""

# Final summary
echo "=========================================="
echo "📊 Project Structure Verification Summary"
echo "=========================================="
echo ""

total_issues=0

if [ ${#missing_files[@]} -gt 0 ]; then
    print_error "Missing ${#missing_files[@]} required root files"
    total_issues=$((total_issues + ${#missing_files[@]}))
fi

if [ ${#missing_dirs[@]} -gt 0 ]; then
    print_error "Missing ${#missing_dirs[@]} required directories"
    total_issues=$((total_issues + ${#missing_dirs[@]}))
fi

if [ ${#non_executable[@]} -gt 0 ]; then
    print_warning "${#non_executable[@]} files need executable permissions"
fi

if [ $total_issues -eq 0 ]; then
    print_success "✅ Project structure verification PASSED!"
    echo ""
    echo "🎉 All required files and directories are in their correct locations:"
    echo "  📁 Root files: ${#found_files[@]}/${#REQUIRED_ROOT_FILES[@]} present"
    echo "  📂 Directories: ${#found_dirs[@]}/${#REQUIRED_DIRECTORIES[@]} present"
    echo "  📓 Notebook storage: Configured correctly"
    echo "  🐳 Docker configuration: Valid"
    echo ""
    echo "🚀 Project is ready for team collaboration!"
else
    print_error "❌ Project structure verification FAILED!"
    echo ""
    echo "🔧 Issues found: $total_issues"
    echo "Please address the missing files and directories before proceeding."
fi

echo ""
echo "📚 For setup help:"
echo "  🛠️  Run setup: ./scripts/setup/team_member_setup.sh"
echo "  📖 Documentation: COMPLETE_PROJECT_STARTUP.md"
echo "  🆘 Support: GitHub Issues"
