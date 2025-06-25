#!/usr/bin/env python3
"""
Code Exporter for SuiteView Taskbar Application
Exports all source code files to a single formatted text file for sharing
"""

import os
import sys
from datetime import datetime
from pathlib import Path

class CodeExporter:
    """Exports all project code to a single formatted text file"""
    
    def __init__(self, project_dir=None):
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.output_file = self.project_dir / "SuiteView_Complete_Source_Code.txt"
        
        # Define which file types and specific files to include
        self.python_extensions = {'.py'}
        self.config_files = {'requirements.txt', 'README.md'}
        self.exclude_files = {'__pycache__', '.pyc', '.git', 'code_exporter.py'}
        
    def get_project_files(self):
        """Get all relevant project files to export"""
        files_to_export = []
        
        # Get all Python files
        for file_path in self.project_dir.glob('*.py'):
            if file_path.name not in self.exclude_files:
                files_to_export.append(file_path)
        
        # Get configuration and documentation files
        for config_file in self.config_files:
            file_path = self.project_dir / config_file
            if file_path.exists():
                files_to_export.append(file_path)
        
        # Sort files for consistent output
        files_to_export.sort(key=lambda x: (x.suffix, x.name))
        
        return files_to_export
    
    def get_file_stats(self, file_path):
        """Get statistics about a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                non_empty_lines = [line for line in lines if line.strip()]
                
            return {
                'size_bytes': file_path.stat().st_size,
                'total_lines': len(lines),
                'non_empty_lines': len(non_empty_lines),
                'characters': len(content)
            }
        except Exception as e:
            return {
                'size_bytes': 0,
                'total_lines': 0,
                'non_empty_lines': 0,
                'characters': 0,
                'error': str(e)
            }
    
    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def create_header(self):
        """Create the header section for the exported file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        header = f"""
{'='*80}
                    SUITEVIEW TASKBAR APPLICATION
                         COMPLETE SOURCE CODE
{'='*80}

Export Information:
    Generated on: {timestamp}
    Project Directory: {self.project_dir}
    Export Tool: SuiteView Code Exporter v1.0

Description:
    This file contains the complete source code for the SuiteView Taskbar 
    Application - a customizable Windows taskbar replacement with quick links
    functionality, drag-and-drop support, and modern UI components.

Project Structure:
    • Main Application Files: main.py, taskbar.py
    • UI Components: ui_components.py, quick_links.py
    • Data Management: links_manager.py, config.py
    • Utilities: utils.py, browse_choice_dialog.py, restore_deskop.py
    • Configuration: requirements.txt, README.md

{'='*80}

"""
        return header
    
    def create_file_section(self, file_path):
        """Create a formatted section for a single file"""
        try:
            # Get file statistics
            stats = self.get_file_stats(file_path)
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create section header
            section_header = f"""
{'─'*80}
FILE: {file_path.name}
{'─'*80}
Path: {file_path.relative_to(self.project_dir)}
Size: {self.format_file_size(stats['size_bytes'])}
Lines: {stats['total_lines']} total, {stats['non_empty_lines']} non-empty
Characters: {stats['characters']:,}
Type: {self.get_file_description(file_path)}
{'─'*80}

"""
            
            # Add content with line numbers if it's a code file
            if file_path.suffix == '.py':
                lines = content.split('\n')
                numbered_content = '\n'.join([f"{i+1:4d}: {line}" for i, line in enumerate(lines)])
                file_content = f"{section_header}{numbered_content}\n"
            else:
                file_content = f"{section_header}{content}\n"
            
            return file_content
            
        except Exception as e:
            error_section = f"""
{'─'*80}
FILE: {file_path.name} (ERROR)
{'─'*80}
Path: {file_path.relative_to(self.project_dir)}
ERROR: Could not read file - {str(e)}
{'─'*80}

"""
            return error_section
    
    def get_file_description(self, file_path):
        """Get a description of what the file contains"""
        descriptions = {
            'main.py': 'Main application entry point',
            'taskbar.py': 'Core taskbar functionality and UI',
            'ui_components.py': 'Reusable UI components and dialogs',
            'quick_links.py': 'Quick links menu and management',
            'links_manager.py': 'Data management for links and categories',
            'config.py': 'Application configuration and constants',
            'utils.py': 'Utility functions and helper classes',
            'browse_choice_dialog.py': 'File/folder selection dialog',
            'restore_deskop.py': 'Desktop restoration utilities',
            'requirements.txt': 'Python package dependencies',
            'README.md': 'Project documentation and setup instructions'
        }
        
        return descriptions.get(file_path.name, f'{file_path.suffix.upper()} file')
    
    def create_summary(self, files_processed):
        """Create a summary section"""
        total_files = len(files_processed)
        total_size = sum(f.stat().st_size for f in files_processed)
        total_lines = 0
        
        # Calculate total lines for Python files
        for file_path in files_processed:
            if file_path.suffix == '.py':
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        total_lines += len(f.readlines())
                except:
                    pass
        
        summary = f"""

{'='*80}
                           EXPORT SUMMARY
{'='*80}

Files Processed: {total_files}
Total Size: {self.format_file_size(total_size)}
Total Python Lines: {total_lines:,}

File Breakdown:
"""
        
        # Add individual file breakdown
        for file_path in files_processed:
            stats = self.get_file_stats(file_path)
            summary += f"    {file_path.name:<25} {self.format_file_size(stats['size_bytes']):>8} ({stats['total_lines']:>4} lines)\n"
        
        summary += f"""
{'='*80}
                    END OF SUITEVIEW SOURCE CODE
{'='*80}
"""
        
        return summary
    
    def export_code(self):
        """Main method to export all code to a text file"""
        print(f"🚀 Starting SuiteView Code Export...")
        print(f"📁 Project Directory: {self.project_dir}")
        print(f"📄 Output File: {self.output_file}")
        
        try:
            # Get all files to process
            files_to_export = self.get_project_files()
            print(f"📋 Found {len(files_to_export)} files to export")
            
            # Create the export file
            with open(self.output_file, 'w', encoding='utf-8') as output:
                # Write header
                print("✍️  Writing header...")
                output.write(self.create_header())
                
                # Process each file
                for i, file_path in enumerate(files_to_export, 1):
                    print(f"📝 Processing {file_path.name} ({i}/{len(files_to_export)})")
                    file_section = self.create_file_section(file_path)
                    output.write(file_section)
                
                # Write summary
                print("📊 Writing summary...")
                output.write(self.create_summary(files_to_export))
            
            print(f"✅ Export completed successfully!")
            print(f"📁 Output saved to: {self.output_file}")
            print(f"📏 File size: {self.format_file_size(self.output_file.stat().st_size)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Export failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def export_with_options(self, include_comments=True, include_blank_lines=True):
        """Export with additional formatting options"""
        # This could be extended for custom export options
        return self.export_code()

def main():
    """Main function for command line usage"""
    print("🔧 SuiteView Code Exporter")
    print("="*50)
    
    # Create exporter instance
    exporter = CodeExporter()
    
    # Perform export
    success = exporter.export_code()
    
    if success:
        print("\n✨ Export completed! You can now share the generated text file.")
        print(f"📎 File location: {exporter.output_file}")
    else:
        print("\n❌ Export failed. Please check the error messages above.")
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Export interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 