# Ditherpy
<img src="https://i.imgur.com/pNedu6i.png" alt="img" align="right" width="400px">

Ditherpy is image dithering made easy with a wide selection of styles.
The tool comes with many parameters to tinker and experiment with and
find out what looks best on your image.

Currently there are 6 different styles, each corresponding to an algorithm, with
some styles having customizable parameters.

## Installing:

### Requirements
Ditherpy is built using python3 and the Pillow library, so you'll need:
* python3 >= 3.6
* Pillow >= 8.1.2

### Pip install
	pip install git+https://github.com/gabrielvictorcf/ditherpy#egg=ditherpy

### Manual/Git install
	git clone https://github.com/gabrielvictorcf/ditherpy
	cd ditherpy
	sudo pip3 install .

# Usage
The most basic use, which defaults to Bayer dithering with depth of 1, is just

	ditherpy image

Since `bayer` is an ordered algorithm, we can change the `depth` parameter
through the `-d` flag:

    ditherpy image -d 0
    ditherpy image -d 3
    ditherpy image -d 8

The impact of depth depends on input size, so for very large images bayer goes to
about 9 and blue noise only goes to 3

If an image is predominantly of a single color, you can also use the `--channel color`
flag to process only that channel

	ditherpy image --chanel red

## Styles
To use differents styles, i.e: bluenoise, the `-s` flag is used:

	ditherpy image -s bluenoise

As of now, the following styles are available:

Style | Type | Description
------|------|------------
bayer | ordered | videogame-y look with plus sign like pattern, nice edges
bluenoise | ordered | organic look with no clear structures
simple | error-diffusion | simplest of it's type, lots of artifacts because of sequentiality
floyd-steinberg | error-diffusion | very fine diffusion with much less artifacts
atkinson | error-diffusion | fine diffusion with strong contrast on very dark/light areas
jjn | error-diffusion | rigorous diffusion with minimal artifacts