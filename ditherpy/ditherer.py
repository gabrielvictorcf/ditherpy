from PIL import Image
from functools import lru_cache
from random import randint
from ditherpy.bluenoise import Bluenoise
from ditherpy.bayer import Bayer
from ditherpy.errordiffusion import Diffusor

# Calculate brightness in the sRGB space
@lru_cache(maxsize=256)
def brightnessCRT(pixel:int)-> float:
	return pixel/255

# Calculate brightness in the linear RGB space
@lru_cache(maxsize=256)
def brightnessLinear(pixel:int)-> float:
	color = pixel / 255
	if color <= 0.04045:
		return color/12.92
	else:
		return ((color+0.055)/1.055)**2.4

class Ditherer():
	def __init__(self,imgName=None,style='bayer',depth=0,options=None) -> None:
		self.setStyle(style,depth,options)
		self.loadImage(imgName)

	def setStyle(self,style='bayer',depth=0,options=None):
		"""Sets the Ditherer styler, which is equivalent to a dithering algorithm"""
		if 'bayer' in style:
			self.styler = Bayer(depth)
		elif 'bluenoise' in style: # opt[0] = generate ; opt[1] = sigma
			self.styler = Bluenoise(depth,options[0],options[1])
		elif 'simple' in style:
			self.styler = Diffusor('simple')
		elif 'atkinson' in style:
			self.styler = Diffusor('atkinson')
		elif 'floyd-steinberg' in style:
			self.styler = Diffusor('floyd-steinberg')
		elif 'jjn' in style:
			self.styler = Diffusor('jjn')
		else: # Defaults to bayer
			self.styler = Bayer(depth)

	def loadImage(self,imgPath):
		"""Open image from imgPath and bind it to Ditherer"""
		if imgPath:
			try:
				self.img = Image.open(imgPath)
			except:
				print('Ditherer init error: Input image does not exist')
				exit(1)
		else:
			self.img = None

	def setImage(self,img):
		"""Bind img to Ditherer """
		if img != None and isinstance(img,Image):
			self.img = img
		else:
			print('Ditherer.setImage error: cannot assign to invalid Image object')
			exit(1)

	# Do necessary conversions or extractions before image acess on dither()
	def __prepareImage(self,img,channel):
		if 'red' in channel:
			img = self.img.getchannel(0)
		elif 'green' in channel:
			img = self.img.getchannel(1)
		elif 'blue' in channel:
			img = self.img.getchannel(2)
		else:
			img = self.img

		# Convert to greyscale using ITU-R 601-2 luma transform on each pixel
		if img.mode in ['RGB','RGBA','LA']:
			img = img.convert('L')  # L = R * 0.299 + G * 0.587 + B * 0.114

		return img
	
	def dither(self,invert=False,gamma=True,channel='all')-> Image:
		"""Dither the current image"""
		if self.img == None:
			print('Ditherer.dither error: no image to process')
			exit(1)

		if invert:
			threshold = lambda b,t: 1 if b > 1-t else 0
		else:
			threshold = lambda b,t: 1 if b > t else 0
		threshold = lru_cache(maxsize=None)(threshold)

		if gamma:
			bgt = brightnessLinear
		else:
			bgt = brightnessCRT

		img = self.__prepareImage(self.img,channel)
		imgData = img.load()
		dtImg = [[bgt(imgData[i,j]) for i in range(img.width)] for j in range(img.height)]

		if self.styler.type == 'ordered':
			dmap = self.styler.map
			mHei, mWid = self.styler.height, self.styler.width

			for i in range(img.height):
				for j in range(img.width):
					dtImg[i][j] = threshold(dtImg[i][j],dmap[i%mHei][j%mWid])

		elif self.styler.type == 'error-diffusion':
			dmatrix = self.styler.diffMatrix
			iHei, iWid = img.height, img.width

			for i in range(img.height):
				for j in range(img.width):
					brightness = dtImg[i][j]
					dtImg[i][j] = threshold(dtImg[i][j],0.5)

					quantError = brightness - dtImg[i][j]
					for diff in dmatrix:
						x = i+diff[0]
						if x >= iHei: continue
						y = j+diff[1]
						if y >= iWid or y < 0: continue
						dtImg[x][y] += quantError*diff[2]


		ditherImg = Image.new('1',(img.width,img.height))
		data = []
		for line in dtImg: data.extend(line)
		ditherImg.putdata(data)
		return ditherImg

	def quantize(self,channel='all')-> Image :
		"""Quantize the current image with threshold as 127"""
		qImg = self.__prepareImage(self.img,channel)
		quantized = [1 if pixel > 127 else 0 for pixel in qImg.getdata()]

		qImg = Image.new('1',(qImg.width,qImg.height))
		qImg.putdata(quantized)
		return qImg

	def randomize(self,channel='all')-> Image :
		"""Quantize the current image with random thresholds, which is equivalent to bluenoise"""
		rImg = self.__prepareImage(self.img,channel)
		randomized = [1 if pixel > randint(0,255) else 0 for pixel in rImg.getdata()]

		rImg = Image.new('1',(rImg.width,rImg.height))
		rImg.putdata(randomized)
		return rImg