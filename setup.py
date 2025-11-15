from setuptools import setup, find_packages

setup(
    name="arduino-cnc-plotter",
    version="2.0.0",
    description="Professional Arduino CNC Suite Software",
    author="Tommaso Bocchietti",
    packages=find_packages(),
    install_requires=[
        "opencv-python>=4.8.0",
        "Pillow>=10.0.0",
        "numpy>=1.24.0",
        "pyserial>=3.5",
        "pyyaml>=6.0",
        "pydantic>=2.0.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "PySide6>=6.5.0",
    ],
    entry_points={
        "console_scripts": [
            "plotter=ui.cli.main:cli",
        ],
    },
    python_requires=">=3.12",
)
