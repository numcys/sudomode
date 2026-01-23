"""Setup configuration for SudoMode SDK"""
from setuptools import setup, find_packages
from pathlib import Path

# Try to read README.md, fallback to description if not found
try:
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        long_description = readme_path.read_text(encoding="utf-8")
    else:
        # Fallback: try root README.md
        root_readme = Path(__file__).parent.parent / "README.md"
        if root_readme.exists():
            long_description = root_readme.read_text(encoding="utf-8")
        else:
            long_description = "Governance SDK for AI agents - The missing sudo command for AI"
except Exception:
    long_description = "Governance SDK for AI agents - The missing sudo command for AI"

setup(
    name="sudomode",
    version="0.1.0",
    author="SudoMode AI",
    description="Governance SDK for AI agents - The missing sudo command for AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sudomode-ai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security",
    ],
    python_requires=">=3.10",
    install_requires=[
        "httpx>=0.27.0",
        "pydantic>=2.9.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
    },
)

