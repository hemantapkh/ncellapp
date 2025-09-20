import setuptools

with open("README.md", "r") as fh:
    readme = fh.read()

setuptools.setup(
    name="ncellapp", 
    version="2.0.2",
    author="Hemanta Pokharel",
    author_email="yo@hemantapkh.com",
    description="Unofficial Python API Wrapper of Ncell",
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=["requests", "emoji"],
    url="https://github.com/hemantapkh/ncellapp",
    project_urls={
        "Documentation": "https://ncellapp.readthedocs.io/en/latest/",
        "Issue tracker": "https://github.com/hemantapkh/ncellapp/issues",
      },
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    python_requires='>=3.0',
)
