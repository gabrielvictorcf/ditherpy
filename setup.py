from setuptools import setup

longDescription = open('README.md').read()
setup(
    name='ditherpy',
    version='1.0.0',
    description='Image dithering made easy with a diverse set of styles',
    author='Gabriel Victor',
    author_email='gabrielvcf@outlook.com',
    url='https://github.com/gabrielvictorcf/ditherpy',
    download_url='https://github.com/gabrielvictorcf/ditherpy',
    long_description=longDescription,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    keywords='ditherpy image-dithering dither',
    license='MIT',
    packages=['ditherpy'],
    entry_points={'console_scripts': ['ditherpy=ditherpy.__main__:main']},
    include_package_data=True,
    install_requires=[
         'pillow >= 8.1.2'
    ],
    python_requires='>=3.6',
)