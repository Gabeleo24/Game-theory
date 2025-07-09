#!/usr/bin/env python3
"""
QUICK ACCESS - REAL MADRID MATCH REPORTS VIEWER
Easy access to all 52 generated match analysis reports
"""

import os
import sys
import glob

def show_available_reports():
    """Show all available match reports organized by competition."""
    
    base_dir = "logs/match_analysis/2023-2024"
    
    print("🏆 REAL MADRID 2023-2024 CHAMPIONS LEAGUE WINNING SEASON 🏆")
    print("📊 Comprehensive Match Analysis Reports")
    print("=" * 80)
    
    # Check if reports exist
    if not os.path.exists(base_dir):
        print("❌ No match reports found. Run the generator first:")
        print("   python scripts/analysis/comprehensive_match_generator.py")
        return
    
    competitions = {
        'uefa_champions_league': '🏆 UEFA Champions League',
        'la_liga': '🇪🇸 La Liga', 
        'copa_del_rey': '🏆 Copa del Rey'
    }
    
    total_reports = 0
    
    for comp_dir, comp_name in competitions.items():
        comp_path = os.path.join(base_dir, comp_dir)
        if os.path.exists(comp_path):
            reports = glob.glob(os.path.join(comp_path, "match_analysis_*.log"))
            reports.sort()
            
            if reports:
                print(f"\n{comp_name}")
                print("-" * 80)
                
                for i, report_path in enumerate(reports, 1):
                    filename = os.path.basename(report_path)
                    # Extract info from filename
                    parts = filename.replace('.log', '').split('_')
                    if len(parts) >= 4:
                        match_id = parts[2]
                        opponent = parts[3].replace('_', ' ').title()
                        date = parts[4] if len(parts) > 4 else 'Unknown'
                        
                        # Format date
                        if len(date) == 8:
                            formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
                        else:
                            formatted_date = date
                        
                        print(f"   {i:2d}. Match {match_id:<3} vs {opponent:<20} ({formatted_date})")
                        print(f"       File: {filename}")
                
                total_reports += len(reports)
    
    # Show summary files
    summary_dir = os.path.join(base_dir, "summary")
    if os.path.exists(summary_dir):
        print(f"\n📋 Summary Files")
        print("-" * 80)
        summary_files = glob.glob(os.path.join(summary_dir, "*.log"))
        for summary_file in summary_files:
            filename = os.path.basename(summary_file)
            print(f"   📊 {filename}")
    
    print(f"\n{'=' * 80}")
    print(f"✅ Total Match Reports: {total_reports}")
    print(f"📁 Location: {base_dir}")
    print(f"{'=' * 80}")
    
    # Usage instructions
    print(f"\n🚀 USAGE:")
    print(f"   View specific report: cat {base_dir}/[competition]/[filename]")
    print(f"   View master summary: cat {base_dir}/summary/master_summary.log")
    print(f"   View competition index: cat {base_dir}/[competition]/[competition]_index.log")
    
    print(f"\n📖 EXAMPLES:")
    print(f"   # Champions League Final")
    print(f"   cat {base_dir}/uefa_champions_league/match_analysis_4_borussia_dortmund_20240601.log")
    print(f"   ")
    print(f"   # El Clasico")
    print(f"   cat {base_dir}/la_liga/match_analysis_51_barcelona_20240421.log")
    print(f"   ")
    print(f"   # Master Summary")
    print(f"   cat {base_dir}/summary/master_summary.log")

def view_specific_report(report_path):
    """View a specific match report."""
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(content)
    else:
        print(f"❌ Report not found: {report_path}")

def main():
    """Main function."""
    if len(sys.argv) > 1:
        # View specific report
        report_path = sys.argv[1]
        view_specific_report(report_path)
    else:
        # Show all available reports
        show_available_reports()

if __name__ == "__main__":
    main()
