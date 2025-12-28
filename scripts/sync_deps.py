import tomli
import tomli_w
from pathlib import Path

def sync_requirements_to_pyproject():
    """
    Reads requirements/base.txt and dev.txt and updates pyproject.toml
    to ensure both are in sync.
    """
    base_req_path = Path("requirements/base.txt")
    dev_req_path = Path("requirements/dev.txt")
    pyproject_path = Path("pyproject.toml")

    if not base_req_path.exists() or not pyproject_path.exists():
        print("Files not found.")
        return

    # Read requirements
    with open(base_req_path, "r") as f:
        base_deps = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    
    dev_deps = []
    if dev_req_path.exists():
        with open(dev_req_path, "r") as f:
            dev_deps = [line.strip() for line in f if line.strip() and not line.startswith("#") and not line.startswith("-r")]

    # Read pyproject.toml
    with open(pyproject_path, "rb") as f:
        pyproject_data = tomli.load(f)

    # Update dependencies
    pyproject_data["project"]["dependencies"] = base_deps
    
    if "optional-dependencies" not in pyproject_data["project"]:
        pyproject_data["project"]["optional-dependencies"] = {}
    
    pyproject_data["project"]["optional-dependencies"]["dev"] = dev_deps

    # Write back
    with open(pyproject_path, "wb") as f:
        tomli_w.dump(pyproject_data, f)
    
    print("Successfully synced pyproject.toml with requirements files.")

if __name__ == "__main__":
    try:
        import tomli
        import tomli_w
    except ImportError:
        print("Please install tomli and tomli-w first: pip install tomli tomli-w")
    else:
        sync_requirements_to_pyproject()
