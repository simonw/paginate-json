from setuptools import setup, find_packages
import io
import os

VERSION = "0.3.1"


def get_long_description():
    with io.open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="paginate-json",
    description="CLI tool for fetching paginated JSON from a URL",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    version=VERSION,
    license="Apache License, Version 2.0",
    packages=find_packages(),
    install_requires=["requests", "click"],
    extras_require={"test": ["pytest", "requests-mock", "cogapp"], "pyjq": ["pyjq"]},
    entry_points="""
        [console_scripts]
        paginate-json=paginate_json.cli:cli
    """,
    url="https://github.com/simonw/paginate-json",
    project_urls={
        "Changelog": "https://github.com/simonw/paginate-json/releases",
        "Source code": "https://github.com/simonw/paginate-json",
        "Issues": "https://github.com/simonw/paginate-json/issues",
        "CI": "https://github.com/simonw/paginate-json/actions",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
