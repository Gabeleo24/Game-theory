#!/usr/bin/env python3
"""
Export Verification Script

Verifies that the notebook exports are working correctly and provides
quick access commands for viewing the exported files.
"""

import os
import subprocess
import sys
from pathlib import Path

def check_file_exists(file_path, file_type):
    """Check if exported file exists and get its size."""
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        size_mb = size / (1024 * 1024)
        print(f"✅ {file_type}: {file_path} ({size_mb:.1f} MB)")
        return True
    else:
        print(f"❌ {file_type}: {file_path} (Not found)")
        return False

def open_file(file_path):
    """Open file with default application."""
    try:
        subprocess.run(["open", file_path], check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Could not open {file_path}")
        return False

def main():
    """Main verification function."""
    print("🔍 EDA Notebook Export Verification")
    print("=" * 50)
    
    # Define export files
    exports_dir = "notebooks/exports"
    html_file = f"{exports_dir}/comprehensive_team_comparison_eda.html"
    pdf_file = f"{exports_dir}/comprehensive_team_comparison_eda.pdf"
    readme_file = f"{exports_dir}/README.md"
    
    # Check if exports directory exists
    if not os.path.exists(exports_dir):
        print(f"❌ Exports directory not found: {exports_dir}")
        sys.exit(1)
    
    print(f"📁 Checking exports in: {exports_dir}")
    print("-" * 50)
    
    # Check each file
    files_status = {
        "HTML": check_file_exists(html_file, "HTML"),
        "PDF": check_file_exists(pdf_file, "PDF"), 
        "README": check_file_exists(readme_file, "README")
    }
    
    # Summary
    successful_exports = sum(files_status.values())
    total_files = len(files_status)
    
    print(f"\n📊 VERIFICATION SUMMARY")
    print("-" * 50)
    print(f"Files Found: {successful_exports}/{total_files}")
    print(f"Success Rate: {successful_exports/total_files*100:.1f}%")
    
    if successful_exports == total_files:
        print("🎉 All exports verified successfully!")
        
        # Provide quick access commands
        print(f"\n🚀 QUICK ACCESS COMMANDS")
        print("-" * 50)
        print(f"View HTML (interactive): open {html_file}")
        print(f"View PDF (static):      open {pdf_file}")
        print(f"View README:            open {readme_file}")
        
        # Ask user if they want to open files
        print(f"\n❓ Would you like to open the files now?")
        print("1. Open HTML version (interactive)")
        print("2. Open PDF version (static)")
        print("3. Open both")
        print("4. Skip")
        
        try:
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice == "1":
                print("🌐 Opening HTML version...")
                open_file(html_file)
            elif choice == "2":
                print("📑 Opening PDF version...")
                open_file(pdf_file)
            elif choice == "3":
                print("🌐 Opening HTML version...")
                open_file(html_file)
                print("📑 Opening PDF version...")
                open_file(pdf_file)
            else:
                print("⏭️ Skipping file opening")
                
        except KeyboardInterrupt:
            print("\n⏭️ Skipping file opening")
        
    else:
        print("❌ Some exports are missing or failed")
        print("\n🔧 To regenerate exports:")
        print("1. Run: jupyter nbconvert --to html notebooks/comprehensive_team_comparison_eda.ipynb --output-dir notebooks/exports")
        print("2. Run: jupyter nbconvert --to pdf notebooks/comprehensive_team_comparison_eda.ipynb --output-dir notebooks/exports")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
