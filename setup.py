from setuptools import setup, find_packages

setup(
    name="supplier_portal_app",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["frappe", "requests"],
    author="OneKeyCo",
    description="ERPNext custom app for supplier invoice portal, bank integrations and transaction fee management.",
    license="MIT",
    classifiers=[
        "Framework :: Frappe",
        "Programming Language :: Python :: 3",
    ],
)
