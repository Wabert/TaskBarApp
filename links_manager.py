# links_manager.py
"""
Data management for Quick Links
Handles loading, saving, and CRUD operations for links
"""

import json
from pathlib import Path
from config import Paths, DEFAULT_CATEGORIES

class LinksManager:
    """Manages saved links with categories"""
    
    def __init__(self):
        # Ensure config directory exists
        Paths.ensure_config_dir()
        self.config_file = Paths.LINKS_FILE
        self.links = self.load_links()
    
    def load_links(self):
        """Load links from config file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Ensure all required keys exist
                    if 'categories' not in data:
                        data['categories'] = DEFAULT_CATEGORIES.copy()
                    if 'links' not in data:
                        data['links'] = []
                    if 'ui_preferences' not in data:
                        data['ui_preferences'] = {"menu_height": 300}
                    return data
            except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
                print(f"Error loading links: {e}. Creating new config.")
                return self._create_default_config()
        
        return self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration"""
        return {
            "categories": DEFAULT_CATEGORIES.copy(),
            "links": [],
            "ui_preferences": {
                "menu_height": 300  # Default menu height
            }
        }
    
    def save_links(self):
        """Save links to config file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.links, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving links: {e}")
            return False
    
    def add_link(self, name, path, category, icon="📄"):
        """Add a new link"""
        if not name or not path:
            return False
        
        # Ensure category exists
        if category not in self.links["categories"]:
            self.links["categories"].append(category)
        
        new_link = {
            "name": name.strip(),
            "path": path.strip(),
            "category": category,
            "icon": icon
        }
        
        self.links["links"].append(new_link)
        return self.save_links()
    
    def update_link(self, index, name, path, category, icon="📄"):
        """Update an existing link"""
        if not (0 <= index < len(self.links["links"])):
            return False
        
        if not name or not path:
            return False
        
        # Ensure category exists
        if category not in self.links["categories"]:
            self.links["categories"].append(category)
        
        self.links["links"][index] = {
            "name": name.strip(),
            "path": path.strip(),
            "category": category,
            "icon": icon
        }
        
        return self.save_links()
    
    def remove_link(self, index):
        """Remove a link by index"""
        if 0 <= index < len(self.links["links"]):
            del self.links["links"][index]
            return self.save_links()
        return False
    
    def get_links_by_category(self, category):
        """Get all links in a category"""
        return [link for link in self.links["links"] if link["category"] == category]
    
    def get_all_links(self):
        """Get all links"""
        return self.links["links"].copy()
    
    def get_categories(self):
        """Get all categories"""
        return self.links["categories"].copy()
    
    def add_category(self, category_name):
        """Add a new category"""
        if category_name and category_name not in self.links["categories"]:
            self.links["categories"].append(category_name)
            return self.save_links()
        return False
    
    def remove_category(self, category_name):
        """Remove a category and all its links"""
        if category_name in self.links["categories"]:
            # Remove all links in this category
            self.links["links"] = [
                link for link in self.links["links"] 
                if link["category"] != category_name
            ]
            # Remove the category
            self.links["categories"].remove(category_name)
            return self.save_links()
        return False
    
    def move_link(self, from_index, to_index):
        """Move a link from one position to another"""
        if (0 <= from_index < len(self.links["links"]) and 
            0 <= to_index < len(self.links["links"])):
            
            link = self.links["links"].pop(from_index)
            self.links["links"].insert(to_index, link)
            return self.save_links()
        return False
    
    def search_links(self, query):
        """Search links by name or path"""
        query = query.lower().strip()
        if not query:
            return self.get_all_links()
        
        results = []
        for link in self.links["links"]:
            if (query in link["name"].lower() or 
                query in link["path"].lower() or
                query in link["category"].lower()):
                results.append(link)
        
        return results
    
    def get_stats(self):
        """Get statistics about links"""
        total_links = len(self.links["links"])
        categories_count = {}
        
        for link in self.links["links"]:
            category = link["category"]
            categories_count[category] = categories_count.get(category, 0) + 1
        
        return {
            "total_links": total_links,
            "total_categories": len(self.links["categories"]),
            "links_per_category": categories_count
        }
    
    def export_links(self, file_path):
        """Export links to a JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.links, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting links: {e}")
            return False
    
    def import_links(self, file_path, merge=True):
        """Import links from a JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
            
            if not merge:
                # Replace all data
                self.links = imported_data
            else:
                # Merge data
                for category in imported_data.get("categories", []):
                    if category not in self.links["categories"]:
                        self.links["categories"].append(category)
                
                for link in imported_data.get("links", []):
                    # Check for duplicates (same name and path)
                    duplicate = any(
                        existing["name"] == link["name"] and existing["path"] == link["path"]
                        for existing in self.links["links"]
                    )
                    if not duplicate:
                        self.links["links"].append(link)
            
            return self.save_links()
        except Exception as e:
            print(f"Error importing links: {e}")
            return False
    
    def get_menu_height(self):
        """Get stored menu height"""
        return self.links.get("ui_preferences", {}).get("menu_height", 300)
    
    def set_menu_height(self, height):
        """Set menu height and save"""
        if "ui_preferences" not in self.links:
            self.links["ui_preferences"] = {}
        self.links["ui_preferences"]["menu_height"] = height
        return self.save_links()
    
    def move_link_to_category(self, link_index, new_category):
        """Move a link to a different category"""
        if not (0 <= link_index < len(self.links["links"])):
            return False
        
        # Ensure new category exists
        if new_category not in self.links["categories"]:
            self.links["categories"].append(new_category)
        
        # Update the link's category
        self.links["links"][link_index]["category"] = new_category
        return self.save_links()
    
    def reorder_links_in_category(self, category, old_position, new_position):
        """Reorder links within a category"""
        category_links = [i for i, link in enumerate(self.links["links"]) 
                         if link["category"] == category]
        
        if not (0 <= old_position < len(category_links) and 
                0 <= new_position < len(category_links)):
            return False
        
        # Get the actual indices in the main links array
        old_index = category_links[old_position]
        new_index = category_links[new_position]
        
        # Move the link
        link_to_move = self.links["links"].pop(old_index)
        
        # Adjust new_index if it's affected by the removal
        if old_index < new_index:
            new_index -= 1
        
        # Calculate the correct insertion position
        if new_position == 0:
            # Insert at the beginning of the category
            insert_index = category_links[0] if old_index != category_links[0] else 0
        elif new_position == len(category_links) - 1:
            # Insert at the end of the category
            insert_index = len(self.links["links"])
        else:
            # Insert at the specified position
            insert_index = category_links[new_position]
            if old_index < insert_index:
                insert_index -= 1
        
        self.links["links"].insert(insert_index, link_to_move)
        return self.save_links()
    
    def get_link_position_in_category(self, link_index):
        """Get the position of a link within its category"""
        if not (0 <= link_index < len(self.links["links"])):
            return -1
        
        link = self.links["links"][link_index]
        category = link["category"]
        
        category_links = [i for i, l in enumerate(self.links["links"]) 
                         if l["category"] == category]
        
        try:
            return category_links.index(link_index)
        except ValueError:
            return -1