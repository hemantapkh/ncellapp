import setuptools

with open("README.md", "r") as fh:
    readme = fh.read()

setuptools.setup(
    name="ncellapp", 
    version="0.1.1",
    author="Hemanta Pokharel",
    author_email="hemantapkh@yahoo.com",
    description="Unofficial Python API Wrapper for Ncell",
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=["crypto"],
    url="https://github.com/hemantapkh/ncellapp",
    project_urls={
        "Issue tracker": "https://github.com/hemantapkh/ncellapp/issues",
      },
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
)
