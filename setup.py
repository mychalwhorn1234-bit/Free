#!/usr/bin/env python3
"""
Setup script for FORScan Python automation tools.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() 
        for line in fh 
        if line.strip() and not line.startswith("#")
    ]

_ = setup(
    name="forscan-python",
    version="0.1.0",
    author="FORScan Automation Team",
    author_email="",
    description="Python automation tools for FORScan diagnostics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mychalwhorn1234-bit/Free",
    packages=find_packages(where="python"),
    package_dir={"": "python"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Hardware",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "isort>=5.12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "forscan-cli=forscan.cli:main",
            "forscan-server=forscan.server:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)