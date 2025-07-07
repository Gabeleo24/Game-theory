#!/usr/bin/env python3
"""
Jupyter Notebook Security Manager
ADS599 Capstone Soccer Intelligence System

This script manages security aspects of Jupyter notebooks including:
- API key detection and masking
- Sensitive data identification
- Notebook sanitization
- Security audit reporting
"""

import os
import json
import re
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple
import nbformat
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NotebookSecurityManager:
    """Manages security aspects of Jupyter notebooks"""
    
    def __init__(self, notebooks_dir: str = "/Users/home/Documents/GitHub/ADS599_Capstone/notebooks"):
        self.notebooks_dir = Path(notebooks_dir)
        self.security_patterns = {
            'api_keys': [
                r'api[_-]?key\s*[=:]\s*["\']([a-zA-Z0-9]{20,})["\']',
                r'token\s*[=:]\s*["\']([a-zA-Z0-9]{20,})["\']',
                r'secret\s*[=:]\s*["\']([a-zA-Z0-9]{20,})["\']',
                r'password\s*[=:]\s*["\']([^"\']{8,})["\']',
            ],
            'database_credentials': [
                r'postgresql://([^:]+):([^@]+)@',
                r'mysql://([^:]+):([^@]+)@',
                r'mongodb://([^:]+):([^@]+)@',
            ],
            'sensitive_data': [
                r'\b\d{3}-\d{2}-\d{4}\b',  # SSN pattern
                r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',  # Credit card pattern
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email pattern
            ]
        }
        
    def scan_notebook(self, notebook_path: Path) -> Dict[str, Any]:
        """Scan a single notebook for security issues"""
        try:
            with open(notebook_path, 'r', encoding='utf-8') as f:
                notebook = nbformat.read(f, as_version=4)
            
            issues = {
                'api_keys': [],
                'database_credentials': [],
                'sensitive_data': [],
                'hardcoded_secrets': [],
                'file_path': str(notebook_path)
            }
            
            # Scan all cells
            for cell_idx, cell in enumerate(notebook.cells):
                if cell.cell_type == 'code':
                    cell_issues = self._scan_cell_content(cell.source, cell_idx)
                    for issue_type, found_issues in cell_issues.items():
                        issues[issue_type].extend(found_issues)
            
            return issues
            
        except Exception as e:
            logger.error(f"Error scanning notebook {notebook_path}: {e}")
            return {'error': str(e), 'file_path': str(notebook_path)}
    
    def _scan_cell_content(self, content: str, cell_idx: int) -> Dict[str, List]:
        """Scan cell content for security issues"""
        issues = {
            'api_keys': [],
            'database_credentials': [],
            'sensitive_data': [],
            'hardcoded_secrets': []
        }
        
        lines = content.split('\n')
        
        for line_idx, line in enumerate(lines):
            # Skip comments and empty lines
            if line.strip().startswith('#') or not line.strip():
                continue
            
            # Check for API keys and tokens
            for pattern in self.security_patterns['api_keys']:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    issues['api_keys'].append({
                        'cell': cell_idx,
                        'line': line_idx,
                        'content': line.strip(),
                        'matched_text': match.group(1) if match.groups() else match.group(0),
                        'severity': 'HIGH'
                    })
            
            # Check for database credentials
            for pattern in self.security_patterns['database_credentials']:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    issues['database_credentials'].append({
                        'cell': cell_idx,
                        'line': line_idx,
                        'content': line.strip(),
                        'username': match.group(1) if len(match.groups()) >= 1 else '',
                        'password': match.group(2) if len(match.groups()) >= 2 else '',
                        'severity': 'HIGH'
                    })
            
            # Check for sensitive data patterns
            for pattern in self.security_patterns['sensitive_data']:
                matches = re.finditer(pattern, line)
                for match in matches:
                    issues['sensitive_data'].append({
                        'cell': cell_idx,
                        'line': line_idx,
                        'content': line.strip(),
                        'matched_text': match.group(0),
                        'severity': 'MEDIUM'
                    })
        
        return issues
    
    def sanitize_notebook(self, notebook_path: Path, backup: bool = True) -> bool:
        """Sanitize a notebook by removing/masking sensitive content"""
        try:
            if backup:
                backup_path = notebook_path.with_suffix('.backup.ipynb')
                notebook_path.rename(backup_path)
                logger.info(f"Created backup: {backup_path}")
            
            with open(backup_path if backup else notebook_path, 'r', encoding='utf-8') as f:
                notebook = nbformat.read(f, as_version=4)
            
            # Sanitize each cell
            for cell in notebook.cells:
                if cell.cell_type == 'code':
                    cell.source = self._sanitize_cell_content(cell.source)
            
            # Clear all outputs
            for cell in notebook.cells:
                if hasattr(cell, 'outputs'):
                    cell.outputs = []
                if hasattr(cell, 'execution_count'):
                    cell.execution_count = None
            
            # Write sanitized notebook
            with open(notebook_path, 'w', encoding='utf-8') as f:
                nbformat.write(notebook, f)
            
            logger.info(f"Sanitized notebook: {notebook_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error sanitizing notebook {notebook_path}: {e}")
            return False
    
    def _sanitize_cell_content(self, content: str) -> str:
        """Sanitize cell content by masking sensitive information"""
        lines = content.split('\n')
        sanitized_lines = []
        
        for line in lines:
            sanitized_line = line
            
            # Mask API keys and tokens
            for pattern in self.security_patterns['api_keys']:
                sanitized_line = re.sub(
                    pattern,
                    lambda m: m.group(0).replace(m.group(1), '***MASKED***'),
                    sanitized_line,
                    flags=re.IGNORECASE
                )
            
            # Mask database credentials
            for pattern in self.security_patterns['database_credentials']:
                sanitized_line = re.sub(
                    pattern,
                    r'postgresql://***MASKED***:***MASKED***@',
                    sanitized_line,
                    flags=re.IGNORECASE
                )
            
            sanitized_lines.append(sanitized_line)
        
        return '\n'.join(sanitized_lines)
    
    def scan_all_notebooks(self) -> Dict[str, Any]:
        """Scan all notebooks in the notebooks directory"""
        results = {
            'scan_date': datetime.now().isoformat(),
            'total_notebooks': 0,
            'notebooks_with_issues': 0,
            'total_issues': 0,
            'notebooks': []
        }
        
        # Find all notebook files
        notebook_files = list(self.notebooks_dir.rglob('*.ipynb'))
        results['total_notebooks'] = len(notebook_files)
        
        for notebook_path in notebook_files:
            # Skip checkpoint files
            if '.ipynb_checkpoints' in str(notebook_path):
                continue
            
            logger.info(f"Scanning: {notebook_path}")
            issues = self.scan_notebook(notebook_path)
            
            if 'error' not in issues:
                total_notebook_issues = sum(len(v) for k, v in issues.items() if k != 'file_path')
                if total_notebook_issues > 0:
                    results['notebooks_with_issues'] += 1
                    results['total_issues'] += total_notebook_issues
                
                results['notebooks'].append(issues)
        
        return results
    
    def generate_security_report(self, scan_results: Dict[str, Any], output_file: str = None) -> str:
        """Generate a security report from scan results"""
        report_lines = [
            "# Jupyter Notebook Security Report",
            f"**Generated:** {scan_results['scan_date']}",
            "",
            "## Summary",
            f"- **Total Notebooks Scanned:** {scan_results['total_notebooks']}",
            f"- **Notebooks with Issues:** {scan_results['notebooks_with_issues']}",
            f"- **Total Security Issues:** {scan_results['total_issues']}",
            ""
        ]
        
        if scan_results['notebooks_with_issues'] > 0:
            report_lines.extend([
                "## Security Issues Found",
                ""
            ])
            
            for notebook in scan_results['notebooks']:
                if 'error' in notebook:
                    continue
                
                total_issues = sum(len(v) for k, v in notebook.items() if k != 'file_path')
                if total_issues == 0:
                    continue
                
                report_lines.extend([
                    f"### {notebook['file_path']}",
                    ""
                ])
                
                # API Keys
                if notebook['api_keys']:
                    report_lines.extend([
                        "#### 🔑 API Keys/Tokens Found",
                        ""
                    ])
                    for issue in notebook['api_keys']:
                        report_lines.append(f"- **Cell {issue['cell']}, Line {issue['line']}**: {issue['content'][:100]}...")
                    report_lines.append("")
                
                # Database Credentials
                if notebook['database_credentials']:
                    report_lines.extend([
                        "#### 🗄️ Database Credentials Found",
                        ""
                    ])
                    for issue in notebook['database_credentials']:
                        report_lines.append(f"- **Cell {issue['cell']}, Line {issue['line']}**: Connection string with credentials")
                    report_lines.append("")
                
                # Sensitive Data
                if notebook['sensitive_data']:
                    report_lines.extend([
                        "#### 🔒 Sensitive Data Patterns Found",
                        ""
                    ])
                    for issue in notebook['sensitive_data']:
                        report_lines.append(f"- **Cell {issue['cell']}, Line {issue['line']}**: {issue['matched_text']}")
                    report_lines.append("")
        
        # Recommendations
        report_lines.extend([
            "## Recommendations",
            "",
            "### High Priority",
            "1. **Remove hardcoded API keys** - Use environment variables or config files",
            "2. **Remove database credentials** - Use role-based connection methods",
            "3. **Sanitize notebooks** before committing to version control",
            "",
            "### Best Practices",
            "1. Use the provided security manager to scan notebooks regularly",
            "2. Follow the team's API key management guidelines",
            "3. Use role-appropriate database connections",
            "4. Clear notebook outputs before committing",
            "5. Review notebooks for sensitive information before sharing",
            "",
            "### Tools Available",
            "```bash",
            "# Scan all notebooks",
            "python scripts/jupyter/notebook_security_manager.py scan",
            "",
            "# Sanitize specific notebook",
            "python scripts/jupyter/notebook_security_manager.py sanitize notebook.ipynb",
            "",
            "# Generate security report",
            "python scripts/jupyter/notebook_security_manager.py report",
            "```"
        ])
        
        report_content = '\n'.join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"Security report saved to: {output_file}")
        
        return report_content

def main():
    parser = argparse.ArgumentParser(description='Jupyter Notebook Security Manager')
    parser.add_argument('action', choices=['scan', 'sanitize', 'report'], 
                       help='Action to perform')
    parser.add_argument('--notebook', help='Specific notebook file to process')
    parser.add_argument('--output', help='Output file for reports')
    parser.add_argument('--notebooks-dir',
                       default='/Users/home/Documents/GitHub/ADS599_Capstone/notebooks',
                       help='Directory containing notebooks')
    
    args = parser.parse_args()
    
    manager = NotebookSecurityManager(args.notebooks_dir)
    
    if args.action == 'scan':
        if args.notebook:
            # Scan specific notebook
            notebook_path = Path(args.notebook)
            if notebook_path.exists():
                issues = manager.scan_notebook(notebook_path)
                print(json.dumps(issues, indent=2))
            else:
                logger.error(f"Notebook not found: {args.notebook}")
        else:
            # Scan all notebooks
            results = manager.scan_all_notebooks()
            print(json.dumps(results, indent=2))
    
    elif args.action == 'sanitize':
        if not args.notebook:
            logger.error("--notebook argument required for sanitize action")
            return
        
        notebook_path = Path(args.notebook)
        if notebook_path.exists():
            success = manager.sanitize_notebook(notebook_path)
            if success:
                logger.info(f"Successfully sanitized: {args.notebook}")
            else:
                logger.error(f"Failed to sanitize: {args.notebook}")
        else:
            logger.error(f"Notebook not found: {args.notebook}")
    
    elif args.action == 'report':
        # Generate security report
        results = manager.scan_all_notebooks()
        output_file = args.output or f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report = manager.generate_security_report(results, output_file)
        
        if not args.output:
            print(report)

if __name__ == '__main__':
    main()
