from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pharmacy-management-system",
    version="1.0.0",
    author="Pharmacy Team",
    author_email="example@example.com",
    description="A Django-based web application for managing a pharmacy's inventory, sales, and customer transactions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pharmacy",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/pharmacy/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Framework :: Django :: 5.1",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Office/Business",
    ],
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "Django>=5.1,<5.2",
        "Pillow>=10.0.0",  # For image handling
    ],
    entry_points={
        "console_scripts": [
            "pharmacy=pharmacy.manage:main",
        ],
    },
)
