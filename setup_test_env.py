import os
import subprocess
import shutil

TEST_ROOT = "test_env"

def run_cmd(cmd, cwd):
    subprocess.run(cmd, shell=True, cwd=cwd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def setup():
    if os.path.exists(TEST_ROOT):
        shutil.rmtree(TEST_ROOT)
    os.makedirs(TEST_ROOT)

    # 1. Clean Repo
    repo_clean = os.path.join(TEST_ROOT, "repo_clean")
    os.makedirs(repo_clean)
    run_cmd("git init -b main", repo_clean)
    run_cmd("git config user.email 'test@example.com'", repo_clean)
    run_cmd("git config user.name 'Test User'", repo_clean)
    with open(os.path.join(repo_clean, "README.md"), "w") as f:
        f.write("# Clean Repo")
    run_cmd("git add . && git commit -m 'Initial'", repo_clean)

    # 2. Dirty Repo
    repo_dirty = os.path.join(TEST_ROOT, "repo_dirty")
    os.makedirs(repo_dirty)
    run_cmd("git init -b main", repo_dirty)
    run_cmd("git config user.email 'test@example.com'", repo_dirty)
    run_cmd("git config user.name 'Test User'", repo_dirty)
    with open(os.path.join(repo_dirty, "main.py"), "w") as f:
        f.write("print('hello')")
    run_cmd("git add . && git commit -m 'Initial'", repo_dirty)
    with open(os.path.join(repo_dirty, "main.py"), "w") as f:
        f.write("print('hello world')")

    # 3. Code Folder (Uninitialized)
    code_no_git = os.path.join(TEST_ROOT, "code_no_git")
    os.makedirs(code_no_git)
    with open(os.path.join(code_no_git, "script.js"), "w") as f:
        f.write("console.log('hi')")

    # 4. Empty Folder
    empty_dir = os.path.join(TEST_ROOT, "empty_dir")
    os.makedirs(empty_dir)

    # 5. Nested Structure
    nested_dir = os.path.join(TEST_ROOT, "project_group", "nested_repo")
    os.makedirs(nested_dir)
    run_cmd("git init -b main", nested_dir)
    run_cmd("git config user.email 'test@example.com'", nested_dir)
    run_cmd("git config user.name 'Test User'", nested_dir)
    with open(os.path.join(nested_dir, "lib.cpp"), "w") as f:
        f.write("// clean cpp")
    run_cmd("git add . && git commit -m 'Initial'", nested_dir)

    print(f"Test environment created at {os.path.abspath(TEST_ROOT)}")

if __name__ == "__main__":
    setup()
