from setuptools import setup
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")
exec((here / "pparse/__init__.py").read_text(encoding="utf-8"))

setup(
    name = "pparse",
    version = __version__,
    description = "Utility to parse and filter Google Cloud IAM policy documents.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zefdelgadillo/policy-parser",
    author="Zef Delgadillo",
    author_email="zef.delgadillo@gmail.com",
    keywords="google-cloud, gcp, iam", 
    python_requires=">=3.8, <4",
    classifiers=[
       "Development Status :: 3 - Alpha",
       "License :: OSI Approved :: MIT License",
    ]
)
