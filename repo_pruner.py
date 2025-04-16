#!/usr/bin/env python3
import os
from github import Github
from dotenv import load_dotenv
import sys
from datetime import datetime

def get_github_client():
    load_dotenv()
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN not found in environment variables")
        sys.exit(1)
    return Github(token)

def get_repositories(g, sort_by='alpha'):
    repos = list(g.get_user().get_repos())
    if sort_by == 'alpha':
        return sorted(repos, key=lambda x: x.name.lower())
    return sorted(repos, key=lambda x: x.created_at, reverse=True)

def process_repositories():
    g = get_github_client()
    sort_mode = input("Sort by (A)lphabetical or (R)ecency? [A]: ").lower()
    sort_by = 'recent' if sort_mode == 'r' else 'alpha'
    
    repos = get_repositories(g, sort_by)
    total_repos = len(repos)
    i = 0
    
    while i < len(repos):
        try:
            repo = repos[i]
            progress_percent = round((i / total_repos) * 100)
            print(f"\nProgress: Repository {i+1}/{total_repos} ({progress_percent}% Reviewed)")
            print(f"Repository: {repo.name}")
            print(f"Visibility: {'Private' if repo.private else 'Public'}")
            print(f"Created: {repo.created_at}")
            print(f"URL: {repo.html_url}")
            print(f"Description: {repo.description}")
            
            action = input("Action - (Enter/K)eep, (D)elete, (B)ack: ").lower()
            
            if action == 'b':
                i = max(0, i - 1)
                continue
            elif action == 'd':
                confirm = input(f"Are you sure you want to delete {repo.name}? (Y/n): ").lower()
                if confirm != 'n':
                    try:
                        repo.delete()
                        print(f"Deleted {repo.name}")
                        repos.pop(i)  # Remove from our local list
                        i -= 1  # Adjust index since we removed a repo
                    except Exception as e:
                        if "404" in str(e):
                            print(f"Repository {repo.name} was already deleted")
                            repos.pop(i)  # Remove from our local list
                            i -= 1
                        else:
                            raise
            i += 1
        except Exception as e:
            print(f"Error processing repository: {e}")
            action = input("(S)kip or (Q)uit? [S]: ").lower()
            if action == 'q':
                break
            i += 1

if __name__ == "__main__":
    try:
        process_repositories()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"An error occurred: {e}")
