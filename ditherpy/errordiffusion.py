class Diffusor():
	""" Class with precomputed Error-diffusion matrices
	
	Attributes
    ----------
    diffMatrix : list[tuple(x,y,weight)]
		List with the x,y offsets and the error weight in relation to current pixel"""

	simple = [(1,0,0.5), (0,1,0.5)]

	floydSteinberg = [(0,1,0.4375),(1,-1,0.1875),(1,0,0.3125),(1,1,0.0625)]

	jjn = [(0,1,0.14583333333333334), (0,2,0.10416666666666667), (1,-2,0.0625), (1,-1,0.10416666666666667), 
			(1,0,0.14583333333333334), (1,1,0.10416666666666667), (1,2,0.0625), (2,-2,0.020833333333333332),
			(2,-1,0.0625), (2,0,0.10416666666666667), (2,1,0.0625), (2,2,0.020833333333333332)]

	atkinson = [(0,1,0.125),(0,2,0.125),(1,-1,0.125),(1,0,0.125),(1,1,0.125),(2,0,0.125)]

	def __init__(self,style):
		self.type = 'error-diffusion'

		if 'simple' in style:
			self.diffMatrix = self.simple
		elif 'floyd-steinberg' in style:
			self.diffMatrix = self.floydSteinberg
		elif 'jjn' in style:
			self.diffMatrix = self.jjn
		elif 'atkinson' in style:
			self.diffMatrix = self.atkinson
		else:
			self.diffMatrix = self.floydSteinberg