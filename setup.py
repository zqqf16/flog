from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="flog",
    version="0.0.5",
    author="zqqf16",
    author_email="zqqf16@gmail.com",
    description="Yet another log parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zqqf16/flog",
    project_urls={
        "Bug Tracker": "https://github.com/zqqf16/flog/issues",
    },
    install_requires=[
        'PyYAML',
        'jinja2',
    ],
    tests_require=[
        'pytest',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["flog"],
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'flog=flog.flog:main',
        ]
    }
)
