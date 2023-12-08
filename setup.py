import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    install_requires = fh.readlines()

with open("__version__", "r") as fh:
    version = fh.read()
    version = version.strip()

extras = {'demo': ['loguru', 'python-dotenv']}

setuptools.setup(
    name="embeddable_assistant",
    version=version,
    author="Will Gathright",
    description="Staple an OpenAI assistant onto any streamlit app",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    extras_require=extras,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)