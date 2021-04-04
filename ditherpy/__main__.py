import argparse
import os
import sys
from math import log2

from . import ditherer

def getArgs():
	desc = 'ditherpy - dithering with a diverse set of styles'
	arg = argparse.ArgumentParser(description=desc)

	arg.add_argument('image',metavar='image',
					help='input image')

	arg.add_argument('-s',metavar='style',choices=['bayer', 'bluenoise', 'simple',
					'atkinson', 'floyd-steinberg', 'jjn'],default='bayer',
					help=f'Choose dithering style: bayer, bluenoise, simple, \
					atkinson, floyd-steinberg, jjn - default bayer')

	arg.add_argument('-d',metavar='depth',type=int,default=1,
					help='Set dithering depth, the higher the more detailed \
					 - only works on Ordered dithering')

	arg.add_argument('-i',action='store_true',
					help='Invert output colors - interesting for very dark images')

	arg.add_argument('-g',action='store_false',
					help='Turn off gamma correction')

	arg.add_argument('--generate',action='store_true',
					help='Generate new bluenoise map')

	arg.add_argument('--p',metavar='sigma',type=float,default=1.9,
					help='Specify bluenoise sigma')

	arg.add_argument('--list',action='store_true',
					help='List available bluenoise threshold maps')

	arg.add_argument('--quantize',action='store_true',
					help='Override dithering and just quantize')

	arg.add_argument('--randomize',action='store_true',
					help='Simplest dithering with random thresholds')

	arg.add_argument('--channel',choices=['red','green',
					'blue'], default='all',
					help='Dither only a single channel: red, green or blue')

	return arg

def main():
	parser = getArgs()
	if len(sys.argv) <= 1:
		parser.print_help()
		exit(0)

	args = parser.parse_args()

	if args.list:
		print('Current bluenoise textures:')
		mapDir = os.path.join(os.path.dirname(__file__),'bnoisemaps')
		for texture in os.listdir(mapDir):
			depth, sigma = texture.split('-')
			depth = log2(int(depth.removeprefix('bnoise')))-5
			sigma = sigma.removesuffix('.png')
			print(f'\tDepth: {depth}  Sigma: {sigma}')
		exit(0)

	dt = ditherer.Ditherer(args.image,args.s,args.d,[args.generate,args.p])
	ditheredName = args.image[:args.image.find('.')]+'dt.png'

	if args.quantize: 
		dt.quantize(args.channel).save(ditheredName)
	elif args.randomize:
		dt.randomize(args.channel).save(ditheredName)
	else: # Common use case
		dt.dither(args.i,args.g,args.channel).save(ditheredName)

if __name__ == '__main__':
	main()