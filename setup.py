import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="panelapp",
    version="0.7.0",
    author="Yujin Kim",
    author_email="yujin.kim@hotmail.fr",
    description="General purpose Panelapp package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NHS-NGS/panelapp",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
    py_modules=["requests"],
)