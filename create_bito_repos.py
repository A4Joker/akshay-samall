import requests
import time
import base64
from typing import List, Dict
import os
import random

class GitHubRepoCreator:
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'

    def create_repo(self, name: str, description: str = "", private: bool = False) -> Dict:
        """Create a single repository on GitHub."""
        url = f'{self.base_url}/user/repos'
        data = {
            'name': name,
            'description': description,
            'private': private,
            'auto_init': True
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 201:
            print(f"✅ Created repository: {name}")
            return response.json()
        else:
            print(f"❌ Failed to create repository: {name}")
            print(f"Status Code: {response.status_code}")
            print(f"Error: {response.text}")
            return None

    def create_file(self, repo_full_name: str, path: str, content: str, message: str, branch: str = "main") -> bool:
        """Create a file in the repository."""
        url = f'{self.base_url}/repos/{repo_full_name}/contents/{path}'
        
        data = {
            'message': message,
            'content': base64.b64encode(content.encode()).decode(),
            'branch': branch
        }
        
        response = requests.put(url, headers=self.headers, json=data)
        return response.status_code in (201, 200)

    def create_branch(self, repo_full_name: str, branch_name: str, base_sha: str) -> bool:
        """Create a new branch in the repository."""
        url = f'{self.base_url}/repos/{repo_full_name}/git/refs'
        data = {
            'ref': f'refs/heads/{branch_name}',
            'sha': base_sha
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        return response.status_code == 201

    def get_main_branch_sha(self, repo_full_name: str) -> str:
        """Get the SHA of the main branch."""
        url = f'{self.base_url}/repos/{repo_full_name}/git/refs/heads/main'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()['object']['sha']
        return None

    def setup_repository_content(self, repo_full_name: str, repo_number: int):
        """Set up sample code and branches in the repository."""
        # Sample code templates
        sample_files = {
            'src': {
                'main.py': f'''
# Bito Repository #{repo_number}
# Main application file

def main():
    print(f"Welcome to Bito Repository #{repo_number}!")
    
    # Example functionality
    data = process_data()
    display_results(data)

def process_data():
    return {{
        "repo_number": {repo_number},
        "status": "active",
        "features": ["automation", "testing", "documentation"]
    }}

def display_results(data):
    print(f"Repository Data: {{data}}")

if __name__ == "__main__":
    main()
''',
                'utils.py': f'''
# Bito Repository #{repo_number}
# Utility functions

import datetime

def get_repo_info():
    return {{
        "repo_number": {repo_number},
        "created_at": datetime.datetime.now().isoformat(),
        "version": "1.0.0"
    }}

def validate_input(data):
    """Validate input data."""
    if not data:
        raise ValueError("Data cannot be empty")
    return True

def format_output(data):
    """Format data for output."""
    return {{
        "timestamp": datetime.datetime.now().isoformat(),
        "repo_number": {repo_number},
        "data": data
    }}
'''
            },
            'tests': {
                'test_main.py': f'''
# Test suite for Bito Repository #{repo_number}

import pytest
from src.main import process_data, display_results

def test_process_data():
    result = process_data()
    assert isinstance(result, dict)
    assert result["repo_number"] == {repo_number}
    assert "status" in result
    assert "features" in result

def test_display_results(capsys):
    test_data = {{"test": "data"}}
    display_results(test_data)
    captured = capsys.readouterr()
    assert "Repository Data" in captured.out
'''
            },
            'docs': {
                'README.md': f'''
# Bito Repository #{repo_number}

## Overview
This is Bito test repository #{repo_number}, created as part of an automated repository generation process.

## Structure
- `src/`: Source code directory
  - `main.py`: Main application file
  - `utils.py`: Utility functions
- `tests/`: Test directory
  - `test_main.py`: Test suite
- `docs/`: Documentation

## Features
- Automated repository creation
- Basic Python project structure
- Test suite setup
- Multiple branch workflow

## Branches
- main: Production-ready code
- develop: Development branch
- feature/custom-logic: Custom feature implementation
- bugfix/error-handling: Bug fixes

## Getting Started
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python src/main.py`
4. Run tests: `pytest tests/`
''',
                'CONTRIBUTING.md': f'''
# Contributing to Bito Repository #{repo_number}

## Development Workflow
1. Create a feature branch from 'develop'
2. Make your changes
3. Write/update tests
4. Submit a pull request

## Code Style
- Follow PEP 8
- Add docstrings for functions
- Keep functions focused and small
- Write meaningful commit messages
'''
            }
        }

        # Create files in main branch
        for category, files in sample_files.items():
            for filename, content in files.items():
                path = f"{category}/{filename}"
                self.create_file(
                    repo_full_name,
                    path,
                    content,
                    f"Add {path} for Bito Repository #{repo_number}"
                )
                print(f"📝 Created {path}")

        # Get main branch SHA
        main_sha = self.get_main_branch_sha(repo_full_name)
        if not main_sha:
            return

        # Create additional branches
        branches = [
            "develop",
            "feature/custom-logic",
            "bugfix/error-handling"
        ]

        for branch in branches:
            if self.create_branch(repo_full_name, branch, main_sha):
                print(f"🌿 Created branch: {branch}")
                
                # Add branch-specific content
                if branch == "feature/custom-logic":
                    self.create_file(
                        repo_full_name,
                        "src/custom_logic.py",
                        f'''
# Custom logic for Bito Repository #{repo_number}

class BitoFeature:
    def __init__(self, repo_number):
        self.repo_number = repo_number
        
    def process(self):
        return f"Processing data for Bito Repository #{repo_number}"
        
    def analyze(self):
        return {{
            "repo": self.repo_number,
            "status": "analyzing",
            "timestamp": "{{timestamp}}"
        }}
''',
                        f"Add custom logic for repository #{repo_number}",
                        branch
                    )

    def bulk_create_repos(self, start: int, end: int, description_template: str = "") -> List[Dict]:
        """Create multiple repositories with sequential naming."""
        created_repos = []
        
        for i in range(start, end + 1):
            repo_name = f"bito_{i}"
            description = description_template.format(i=i) if description_template else f"Bito test repository #{i}"
            
            result = self.create_repo(repo_name, description)
            if result:
                created_repos.append(result)
                print(f"🔧 Setting up content for {result['full_name']}...")
                self.setup_repository_content(result['full_name'], i)
                print(f"✨ Completed setup for {result['full_name']}\n")
            
            # Add a small delay to avoid hitting rate limits
            time.sleep(2)
        
        return created_repos

def main():
    # Get GitHub token from environment variable for security
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("⚠️ Please set your GITHUB_TOKEN environment variable!")
        return

    creator = GitHubRepoCreator(token)
    
    # Configuration
    start_number = 1
    end_number = 50
    description_template = "Bito Test Repository #{i}"
    
    print(f"🚀 Starting creation of repositories bito_{start_number} through bito_{end_number}...")
    
    # Create repositories
    created_repos = creator.bulk_create_repos(start_number, end_number, description_template)
    
    # Summary
    print("\n📊 Summary:")
    print(f"Total repositories attempted: {end_number - start_number + 1}")
    print(f"Successfully created: {len(created_repos)}")
    print(f"Failed: {(end_number - start_number + 1) - len(created_repos)}")

if __name__ == "__main__":
    main()