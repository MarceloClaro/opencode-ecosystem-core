"""Arquivo de setup para instalação tradicional via pip install -e .

Este setup.py complementa o pyproject.toml para compatibilidade com
instalação direta em modo editável durante desenvolvimento.
"""

from pathlib import Path

from setuptools import find_packages, setup

HERE = Path(__file__).parent.resolve()
README = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name="odontoia",
    version="0.1.0",
    description=(
        "Pacote central de códigos do livro 'Odontologia & Inteligência Artificial' — "
        "modelos, métricas, visualização e ferramentas para diagnóstico bucal assistido por IA."
    ),
    long_description=README,
    long_description_content_type="text/markdown",
    author="Edson Laranjeiras (via OpenCode Ecosystem)",
    author_email="edson.laranjeiras@openbook.odontologia",
    license="MIT",
    url="https://github.com/marceloclaro/opencode-ecosystem-core",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Healthcare Professionals",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="odontologia, inteligencia-artificial, deep-learning, radiografia, diagnostico-bucal",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.24",
        "pandas>=2.0",
        "matplotlib>=3.7",
        "scikit-learn>=1.3",
        "torch>=2.1",
        "torchvision>=0.16",
        "opencv-python>=4.8",
        "pillow>=10.0",
        "scipy>=1.11",
        "seaborn>=0.13",
        "pydantic>=2.4",
        "tqdm>=4.66",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4",
            "pytest-cov>=4.1",
            "jupyter>=1.0",
            "ipykernel>=6.28",
            "pylint>=3.0",
            "black>=23.12",
        ],
        "notebooks": [
            "jupyterlab>=4.0",
            "paperm>=2.5",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)