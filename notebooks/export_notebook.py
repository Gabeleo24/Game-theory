#!/usr/bin/env python3
"""
Notebook Export Utility

This script provides multiple export options for the EDA notebook:
- HTML export (immediate, no dependencies)
- PDF export via HTML (using browser print)
- Standalone HTML with embedded plots
"""

import subprocess
import os
import sys
from pathlib import Path

def export_to_html(notebook_path, output_dir="exports"):
    """Export notebook to HTML format."""
    print("📄 Exporting notebook to HTML...")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Export to HTML
    output_file = f"{output_dir}/comprehensive_team_comparison_eda.html"
    
    try:
        cmd = [
            "jupyter", "nbconvert",
            "--to", "html",
            "--output", output_file,
            notebook_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ HTML export successful: {output_file}")
            return output_file
        else:
            print(f"❌ HTML export failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Export error: {str(e)}")
        return None

def export_to_slides(notebook_path, output_dir="exports"):
    """Export notebook to reveal.js slides."""
    print("🎯 Exporting notebook to slides...")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Export to slides
    output_file = f"{output_dir}/comprehensive_team_comparison_slides.html"
    
    try:
        cmd = [
            "jupyter", "nbconvert",
            "--to", "slides",
            "--output", output_file,
            notebook_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Slides export successful: {output_file}")
            return output_file
        else:
            print(f"❌ Slides export failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Export error: {str(e)}")
        return None

def check_latex_installation():
    """Check if LaTeX is installed for PDF export."""
    try:
        result = subprocess.run(["pdflatex", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ LaTeX is installed - PDF export available")
            return True
        else:
            print("❌ LaTeX not found - PDF export not available")
            return False
    except FileNotFoundError:
        print("❌ LaTeX not found - PDF export not available")
        return False

def export_to_pdf(notebook_path, output_dir="exports"):
    """Export notebook to PDF (requires LaTeX)."""
    print("📑 Exporting notebook to PDF...")
    
    if not check_latex_installation():
        print("⚠️ LaTeX not installed. Install with: brew install --cask mactex")
        return None
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Export to PDF
    output_file = f"{output_dir}/comprehensive_team_comparison_eda.pdf"
    
    try:
        cmd = [
            "jupyter", "nbconvert",
            "--to", "pdf",
            "--output", output_file,
            notebook_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ PDF export successful: {output_file}")
            return output_file
        else:
            print(f"❌ PDF export failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Export error: {str(e)}")
        return None

def create_export_summary(exported_files):
    """Create a summary of exported files."""
    summary_content = f"""# EDA Notebook Export Summary

## Exported Files

"""
    
    for file_type, file_path in exported_files.items():
        if file_path:
            summary_content += f"- **{file_type.upper()}**: `{file_path}`\n"
        else:
            summary_content += f"- **{file_type.upper()}**: ❌ Export failed\n"
    
    summary_content += f"""
## Usage Instructions

### HTML Version
- Open the HTML file in any web browser
- All visualizations are interactive
- Can be shared easily via email or web

### PDF Version (if available)
- Professional format for printing
- Static visualizations
- Suitable for reports and presentations

### Slides Version
- Reveal.js presentation format
- Navigate with arrow keys
- Perfect for presentations

## Browser Print to PDF
If PDF export failed, you can:
1. Open the HTML file in your browser
2. Use "Print" → "Save as PDF"
3. This creates a high-quality PDF version

Generated: {Path().absolute()}
"""
    
    with open("exports/export_summary.md", "w") as f:
        f.write(summary_content)
    
    print("📋 Export summary created: exports/export_summary.md")

def main():
    """Main export function."""
    print("🚀 EDA Notebook Export Utility")
    print("=" * 50)
    
    # Check if notebook exists
    notebook_path = "notebooks/comprehensive_team_comparison_eda.ipynb"
    if not os.path.exists(notebook_path):
        print(f"❌ Notebook not found: {notebook_path}")
        sys.exit(1)
    
    print(f"📊 Found notebook: {notebook_path}")
    
    # Export to different formats
    exported_files = {}
    
    # HTML export (always works)
    exported_files["html"] = export_to_html(notebook_path)
    
    # Slides export
    exported_files["slides"] = export_to_slides(notebook_path)
    
    # PDF export (if LaTeX available)
    exported_files["pdf"] = export_to_pdf(notebook_path)
    
    # Create summary
    create_export_summary(exported_files)
    
    print("\n" + "=" * 50)
    print("📊 EXPORT SUMMARY")
    print("=" * 50)
    
    success_count = sum(1 for path in exported_files.values() if path is not None)
    total_formats = len(exported_files)
    
    print(f"✅ Successfully exported: {success_count}/{total_formats} formats")
    
    for file_type, file_path in exported_files.items():
        status = "✅" if file_path else "❌"
        print(f"{status} {file_type.upper()}: {file_path or 'Failed'}")
    
    if exported_files["html"]:
        print(f"\n🌐 Open HTML version: open {exported_files['html']}")
    
    if not exported_files["pdf"]:
        print(f"\n💡 For PDF: Open HTML in browser → Print → Save as PDF")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
