#!/usr/bin/env python3
import os
import argparse
import subprocess
import sys

# Common source code extensions to identify code directories
CODE_EXTENSIONS = {
    '.py', '.js', '.ts', '.c', '.cpp', '.h', '.hpp', '.java', 
    '.go', '.rs', '.rb', '.php', '.html', '.css', '.sh', '.bat', 
    '.json', '.xml', '.yml', '.yaml', '.md'
}

def get_git_status(repo_path):
    """
    Checks the git status of a repository.
    Returns a dictionary with 'is_dirty', 'unpushed_commits', etc.
    """
    status = {
        'is_dirty': False,
        'unpushed': False,
        'error': None
    }
    
    try:
        # Check for uncommitted changes
        result = subprocess.run(
            ['git', 'status', '--porcelain'], 
            cwd=repo_path, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            check=False
        )
        if result.returncode != 0:
            status['error'] = result.stderr.strip()
            return status
            
        if result.stdout.strip():
            status['is_dirty'] = True
            
        # Check for unpushed commits (against upstream)
        # First check if there is an upstream configured
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}'],
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            # Upstream exists, check for unpushed
            result = subprocess.run(
                ['git', 'log', '@{u}..'],
                cwd=repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            if result.stdout.strip():
                status['unpushed'] = True
                
    except Exception as e:
        status['error'] = str(e)
        
    return status

def scan_directory(root_dir, verbose=False):
    """
    Walks the directory tree.
    - Specifies if a directory is a Git Repo.
    - If not a repo, checks if it contains code files (Uninitialized).
    - Ignores directories inside existing Git Repos (no nested scanning unless submodule logic needed, but user said 'no submodules').
    """
    
    print(f"Scanning {os.path.abspath(root_dir)}...\n")
    
    found_repos = []
    uninitialized_dirs = []
    
    # os.walk allows modifying 'dirs' in-place to prune traversal
    for current_root, dirs, files in os.walk(root_dir):
        # specific check to skip .git directories themselves from being walked
        if '.git' in dirs:
            # This directory is a git repo
            dirs.remove('.git') # don't walk into .git
            
            # Determine status
            git_stat = get_git_status(current_root)
            
            repo_info = {
                'path': current_root,
                'status': git_stat
            }
            found_repos.append(repo_info)
            
            # Use logic: do we want to scan INSIDE this repo for other repos?
            # User said: "not submodules! just repos". 
            # Usually nested repos are submodules. 
            # If we STOP walking into this dir's subdirs, we strictly respect the "top level repos" logic 
            # unless there's a repo inside a repo that isn't a submodule. 
            # But the safer, low-overhead approach is usually to NOT recurse into a git repo.
            # However, sometimes users have 'projects/ProjectA' (git) and 'projects/ProjectB' (git).
            # The walk handles siblings fine. This decision is about children of a git repo using `dirs[:] = []`.
            # I will choose to PRUNE traversal here to avoid scanning node_modules, etc.
            dirs[:] = [] 
            continue
            
        # If not a git repo, check if it looks like code
        # We only care if it's a "project root" candidate.
        # Simple heuristic: has code files.
        # But we don't want to list EVERY subdirectory.
        # We want to find "roots".
        # If we are effectively a leaf or near-leaf with code, report it.
        # Actually, for "What directories have code in it, but has not yet been initialized",
        # users usually mean "I have a project folder here that I forgot to git init".
        # If I see ANY code file in this dir, I'll flag it, BUT...
        # If I recurse, I might flag current_root AND current_root/src.
        # To avoid noise, maybe only flag if verify strictly?
        # Let's just collect all and maybe filter path containment later?
        # Strategy: Check if any file in `files` has a code extension.
        
        has_code = any(f.endswith(tuple(CODE_EXTENSIONS)) for f in files)
        if has_code:
            uninitialized_dirs.append(current_root)
            # We CONTINUE walking into subdirs because maybe there's a git repo deep inside a non-git folder.
            # E.g. /home/user/projects (no git) -> /home/user/projects/repo1 (git)
            
    return found_repos, uninitialized_dirs

def print_report(repos, uninit, root_dir):
    print(f"{'='*60}")
    print(f"GIT REPOSITORIES FOUND: {len(repos)}")
    print(f"{'='*60}")
    
    # Sort by path
    repos.sort(key=lambda x: x['path'])
    
    for r in repos:
        path = r['path']
        rel_path = os.path.relpath(path, root_dir)
        status = r['status']
        
        # Formatting
        status_str = []
        if status['error']:
            status_str.append(f"[ERROR: {status['error']}]")
        else:
            if status['is_dirty']:
                status_str.append("DIRTY (Uncommitted)")
            else:
                status_str.append("CLEAN")
                
            if status['unpushed']:
                status_str.append("UNPUSHED COMMITS")
                
        # Color simulation (simple ANSI)
        # Red for Dirty/Error, Green for Clean
        
        icon = "[?]"
        if status['error']:
            icon = "[!]"
        elif status['is_dirty'] or status['unpushed']:
            icon = "[*]"
        else:
            icon = "[OK]"
            
        print(f"{icon} {rel_path}  =>  {', '.join(status_str)}")

    if uninit:
        print(f"\n{'='*60}")
        print(f"UNINITIALIZED CODE DIRECTORIES (Potential Projects): {len(uninit)}")
        print(f"(Showing top-level non-nested matches to reduce noise)")
        print(f"{'='*60}")
        
        # Filter: If /a/b is in list, and /a/b/c is in list, hide /a/b/c?
        # Yes, we want the 'root' of the uninitialized code.
        uninit.sort()
        filtered_uninit = []
        for d in uninit:
            # Check if this d is a subdirectory of any already in filtered_uninit
            # path/to/parent vs path/to/parent/child
            is_child = False
            for parent in filtered_uninit:
                # Add slash to ensure strict directory prefix matching
                if d.startswith(os.path.join(parent, '')):
                    is_child = True
                    break
            if not is_child:
                filtered_uninit.append(d)
                
        for d in filtered_uninit:
            rel_path = os.path.relpath(d, root_dir)
            print(f"[?] {rel_path}")

def main():
    parser = argparse.ArgumentParser(description="Scan directories for git repositories and uninitialized code.")
    parser.add_argument('path', nargs='?', default=os.getcwd(), help="Root directory to scan (default: current)")
    parser.add_argument('--verbose', action='store_true', help="Show more details")
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.path):
        print(f"Error: Directory '{args.path}' not found.")
        sys.exit(1)
        
    repos, uninit = scan_directory(args.path, args.verbose)
    print_report(repos, uninit, args.path)

if __name__ == "__main__":
    main()
