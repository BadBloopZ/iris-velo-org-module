from setuptools import setup

setup(
    name='iris_velo_org_module',
    python_requires='>=3.9',
    version='1.0.1',
    packages=['iris_velo_org_module', 'iris_velo_org_module.velo_handler'],
    url='https://github.com/BadBloopZ/iris-velo-org-module',
    license='Lesser GNU GPL v3.0',
    author='Stephan Mikiss',
    author_email='stephan.mikiss@gmail.com',
    description='`iris-velo-org-module` is an IRIS processor module. It hooks on created cases and adds the client of the case as new organization in Velociraptor. Furthermore, it can grant existing users in Velociraptor access to the case.',
    install_requires=[
        "pyvelociraptor",
        "setuptools==59.6.0"
    ]
)
