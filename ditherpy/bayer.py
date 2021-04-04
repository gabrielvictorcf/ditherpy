class Bayer():
	"""Class for generating a Bayer matrix used as threshold map

    Attributes
	----------
	map : list[list[float]]
		The bayer matrix with values normalized to the [0,1] range"""

	def __init__(self,depth):
		self.width = 2**(depth+1)
		self.height = self.width
		self.type = 'ordered'

		self.depth = depth
		self.map = self.genBayerMatrix(self.depth)
		self.normalizeBayerMatrix()

	def genBayerMatrix(self,depth):
		if depth == 0: # Base un-normalized bayer matrix
			return [[0,2],[3,1]]
		else:
			prevBMatrix = self.genBayerMatrix(depth-1)

			bquadrant = []	# Assemble the matrix by quadrants
			for line in prevBMatrix:
				lHalf, rHalf = [],[]
				for num in line:
					finalNum = num*4
					lHalf.append(finalNum)
					rHalf.append(finalNum+2)

				bquadrant.append(lHalf+rHalf)

			lineQty = len(bquadrant)
			numQty = len(bquadrant[0])//2
			for linePos in range(lineQty):
				curLine = []
				for num in bquadrant[linePos][:numQty]:
					curLine.append(num+3)
				for num in bquadrant[linePos][numQty:]:
					curLine.append(num-1)

				bquadrant.append(curLine)
				linePos += 1

			return bquadrant

	def normalizeBayerMatrix(self):
		"""Normalize the values to the [0,1] to match the image brightness range"""
		coeff = 4**(self.depth+1)

		for i in range(self.height):
			for j in range(self.width):
				self.map[i][j] /= coeff