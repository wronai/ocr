#!/usr/bin/env python3
"""
Setup script for PDF OCR Processor
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Get version from file
def get_version():
    version_file = os.path.join("pdf_processor", "__version__.py")
    version = {}
    if os.path.exists(version_file):
        with open(version_file, "r") as f:
            exec(f.read(), version)
            return version.get("__version__", "2.0.0")
    return "2.0.0"

setup(
    name="pdf-ocr-processor",
    version=get_version(),
    author="PDF OCR Processor Team",
    author_email="team@pdf-ocr-processor.com",
    description="Advanced PDF OCR processing with AI-powered text extraction",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-repo/pdf-ocr-processor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Text Processing :: Markup",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "gpu": [
            "torch>=2.0.0",
            "torchvision>=0.15.0",
        ],
        "web": [
            "fastapi>=0.100.0",
            "uvicorn>=0.23.0",
            "streamlit>=1.25.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pdf-ocr=pdf_processor.cli:main",
            "pdf-ocr-web=pdf_processor.web:main",
        ],
    },
    include_package_data=True,
    package_data={
        "pdf_processor": [
            "config/*.yaml",
            "templates/*.html",
            "static/*.css",
            "static/*.js",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/your-repo/pdf-ocr-processor/issues",
        "Source": "https://github.com/your-repo/pdf-ocr-processor",
        "Documentation": "https://pdf-ocr-processor.readthedocs.io/",
    },
)
