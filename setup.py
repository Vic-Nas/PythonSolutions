from setuptools import setup, find_packages

# Read the README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vicutils",
    version="0.6",
    packages=find_packages(),
    install_requires=[],
    
    # Metadata for PyPI
    author="Vic-Nas",
    author_email="nasci.victorio@gmail.com",  # Optional
    description="Utility functions for Python programming",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Vic-Nas/PythonSolutions",  # Your repo
    project_urls={
        "Documentation": "https://vic-nas.github.io/PythonSolutions/vicutils/printBin.html",
        "Source": "https://github.com/Vic-Nas/PythonSolutions",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)