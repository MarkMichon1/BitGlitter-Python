from setuptools import setup, find_namespace_packages

with open("README.md", "r") as openReadMe:
    long_description = openReadMe.read()

setup(
    name="BitGlitter",
    version="2.0.0",
    author="Mark Michon",
    author_email="markkmichon@gmail.com",
    description="⚡ Embed data payloads inside of ordinary images or video, through high performance 2-D matrix codes.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MarkMichon1/BitGlitter-Python",
    packages=find_namespace_packages(),
    install_requires=[
        "bitstring",
        "cryptography",
        "ffmpeg-python",
        "opencv-python",
        "Pillow",
        "SQLAlchemy"
    ],
    extra_require={"dev": "pytest"},
    classifiers=[
        "Programming Language :: Python :: 3.9.5",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
