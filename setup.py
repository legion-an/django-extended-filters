from setuptools import setup

files = ["templates/extended_filters/*", 'locale/ru/LC_MESSAGES/*']

setup(
    name='django-extended-filters',
    version='0.3',
    packages=['extended_filters'],
    url='https://bitbucket.org/legion_an/django-extended-filters',
    package_data = {'extended_filters' : files },
    license='',
    author='legion',
    author_email='legion_an@mail.ru',
    description='Add checkbox and daterange filters in django admin',
    keywords=[
        'django admin',
        'django date range',
        'django checkbox filter',
        'django admin filter'
        'django admin autocomplete filter'
    ],
    install_requires=[
        "django",
    ],
)
