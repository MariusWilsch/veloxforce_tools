from setuptools import setup, find_packages

# Read version from __init__.py
with open("veloxforce_tools/__init__.py", "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break

# Read long description from README.md
with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="veloxforce-tools",
    version=version,
    description="Veloxforce Tools - A toolkit for working with OpenRouter, Langfuse, and Email APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Marius Wilsch",
    author_email="marius.santiago.wilsch@gmail.com",
    url="https://github.com/MariusWilsch/veloxforce-tools",
    packages=find_packages(),
    package_data={"veloxforce_tools": ["py.typed"]},
    include_package_data=True,
    install_requires=[
        "httpx",
        "pydantic",
        "tenacity",
        "rich",
        "pydantic-settings",
        "openai>=1.76.0",
        "langfuse>=2.60.3",
        "imap-tools>=1.0.0",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
