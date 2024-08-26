from setuptools import setup, find_packages

def read_requirements():
    with open('requirements.txt') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name = "labelvim",
    version = "v1.1.0-beta",
    description="A simple tool to label images for object detection and segmentation tasks.",
    author="Dr. Amish Kumar",
    author_email="amishkumar562@gmail.com",
    url="https://github.com/VisioSphereAI/labelvim.git",
    packages=find_packages(),
    # print(f"Packages: , {packages}"),
    package_data={'labelvim': ['icon/*', 'docs/*', 'labelvim/*.yaml']},
    install_requires=read_requirements(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'labelvim=labelvim.main:main'
        ],
    },

    keywords="Image Annotation, Machine Learning, Object Detection, Segmentation, Image Labeling, Image Annotation Tool, Image Annotation Software, Computer Vision, Image Labeling Tool, Image Labeling Software",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
    ],
)