import io

from setuptools import setup


def read(path):
    with io.open(path, mode="r", encoding="utf-8") as fd:
        content = fd.read()
    # Convert Markdown links to reStructuredText links
    # return re.sub(r"\[([^]]+)\]\(([^)]+)\)", r"`\1 <\2>`_", content)
    return content


setup(
    name='linovelib2epub',
    version='0.0.4',
    author='wdpm',
    author_email='1137299673@qq.com',
    packages=['linovelib2epub'],
    url='https://github.com/wdpm/linovelib2epub',
    license='GNU Affero General Public License',
    description='Craw light novel from w.linovelib.com and convert to epub.',
    long_description=read('README.md'),
    keywords=['ebook', 'epub', 'light novel', '哔哩轻小说'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    # copy from requirement.txt
    install_requires=[
        'bs4>=0.0.1',
        'demjson>=2.2.4',
        'EbookLib>=0.17.1',
        'fake-useragent>=0.1.11',
        'requests>=2.28.1',
        'rich>=12.5.1',
        'uuid>=1.30'
    ],
    entry_points={
        # 'console_scripts': ['my-command=exampleproject.example:main']
        'console_scripts': ['linovel=linovelib2epub.linovel:main']
    },
    # setup_requires=['pytest-runner'],
    # tests_require=['pytest'],
    # package_data={'exampleproject': ['data/schema.json']}
)
