from PIL import Image
import random
import os

class Bluenoise():
	""" Class for acessing/generating blue noise threshold maps generated using
	the void-and-cluster algorithm 
	
	Attributes
	----------
	map : list[list[float]]
		The Blue Noise with values normalized to the [0,1] range"""

	mapDir = os.path.join(os.path.dirname(__file__),'bnoisemaps')

	def __init__(self,depth,generate=False,sigma=1.9) -> None:
		if depth > 3:
			print('Bluenoise init error: depth is too high! Max depth = 3')
			exit(1)
		side = 2**(depth+5) # d0 = 32, d1 = 64, d2 = 128, d3 = 256
		self.width = side
		self.height = side
		self.type = 'ordered'

		self.sigma = sigma
		self.divisor = 2**(sigma*sigma) # What we effectively use the sigma for
		self.lookup = None

		mapName = os.path.join(self.mapDir,f'bnoise{side}-{sigma:.3}.png')

		if not os.path.isdir(self.mapDir):
			os.mkdir(self.mapDir)

		if generate:
			currentOnes = self.initialPattern()
			self.distributeSamples()
			self.finalPattern(currentOnes-1)
			self.saveMap(mapName)
		else:
			try:
				self.map = self.loadMap(mapName)
			except:
				print('Ditherer: Bluenoise init error: specified map does not exist')
				print("Use --generate to create it and --p <x.x> for it's sigma; default = 1.9")
				exit(1)
		
		self.normalize()
	
	def normalize(self):
		for i in range(self.height):
			for j in range(self.width):
				self.map[i][j] /= 255

	# Load an existing map image as a matrix
	def loadMap(self,mapName):
		initialData = list(Image.open(mapName).getdata())
		bnoise = []
		for i in range(self.height):
			bnoise.append(initialData[i*self.width:(i+1)*self.width])
		
		return bnoise
	
	def saveMap(self,mapName):
		data = []
		for line in self.map: data.extend(line)
		bluenoise = Image.new('L',(self.width,self.height))
		bluenoise.putdata(data)
		bluenoise.save(mapName)

	# Iterate through all pixels and update their value based
	# on the pixel at self.map[x][y]
	# value += e^(-(wrapDistance^2)/sigma^2)
	def updatelookup(self,x,y,sign):
		halfHeight = self.height/2
		halfWidth = self.width/2

		for i in range(self.height):
			xDist = abs(x - i) # Calculating wrap-around distance of vertical axis
			if xDist > halfHeight:
				xDist = self.height - xDist

			xDistSq = xDist*xDist
			for j in range(self.width):
				yDist = abs(y - j) # Calculating wrap-around distance of horizontal axis
				if yDist > halfWidth:
					yDist = self.width - yDist

				distanceSquared = (yDist*yDist)+xDistSq
				self.lookup[i][j] += sign * (2.7182**(-distanceSquared/self.divisor))

	# Search for either highest or lowest value of
	# entries that match with the passed value
	# When op = 0 do a min search, when op = 1 do max search
	def findlookup(self,value,operation):
		if operation == 0: # Min search
			cmpVal = 100000.0
			cmp = lambda e, val: e < val
		elif operation == 1: # Max search
			cmpVal = -100000.0
			cmp = lambda e, val: e > val
		srchPos = -1
		for i in range(self.height):
			for j in range(self.width):
				if self.map[i][j] == value and cmp(self.lookup[i][j],cmpVal):
					cmpVal = self.lookup[i][j]
					srchPos = (i,j)

		return srchPos

	# Create initial random pattern and the lookup table with each
	# pixel's value
	def initialPattern(self):
		self.map = [[0 for _ in range(self.width)] for _ in range(self.height)]

		totalPixels = self.width*self.height
		self.lookup = [[0.0 for _ in range(self.width)] for _ in range (self.height)]

		generated = set() # Making sure all initial points are unique
		initialSample = totalPixels//10
		for _ in range(initialSample):
			pos = random.randrange(0,totalPixels)
			while pos in generated:
				pos = random.randrange(0,totalPixels)
			generated.add(pos)

			row = pos//self.height
			col = pos%self.height
			self.map[row][col] = 255
			self.updatelookup(row,col,1)
		
		return initialSample

	# Switch voids and clusters until tighestCluster == largestVoid
	# results in initial prototype binary pattern
	def distributeSamples(self):
		tighestCl = -2 
		largestVd = -1 
		while tighestCl != largestVd:
			tighestCl = self.findlookup(255,1) # Finding '1' with highest energy
			clRow, clCol = tighestCl
			self.map[clRow][clCol] = 0
			self.updatelookup(clRow,clCol,-1)

			largestVd = self.findlookup(0,0) # Find '0' with lowest energy
			if tighestCl == largestVd: # Algorithm stops when removing a pixel generates the
				return                 # tighest cluster AND the largest void at the same spot
			vdRow, vdCol = largestVd
			self.map[vdRow][vdCol] = 255
			self.updatelookup(vdRow,vdCol,1)

	# Apply progressive logic to the initial, noisy, prototype pattern
	# until it has an uniform distribution: Blue noise!
	def finalPattern(self,currentOnes):
		ranks = [[0 for _ in range(self.width)] for _ in range(self.height)]

		#Phase 1: Remove the current sample points(10%) to start progressive logic
		while currentOnes > 0:
			tighestCl = self.findlookup(255,1)
			clRow, clCol = tighestCl
			self.map[clRow][clCol] = 0
			self.updatelookup(clRow,clCol,-1)

			ranks[clRow][clCol] = currentOnes
			currentOnes-=1

		#Phase 2: Paint half of total with progressive logic
		halfTotalPixels = (self.height*self.width)//2
		while currentOnes < halfTotalPixels:
			largestVd = self.findlookup(0,0)
			vdRow, vdCol = largestVd
			self.map[vdRow][vdCol] = 255
			self.updatelookup(vdRow,vdCol,1)

			ranks[vdRow][vdCol] = currentOnes
			currentOnes+=1

		#Phase 3: Paint rest of figure with progressive logic
		totalPixels = self.height*self.width
		while currentOnes < totalPixels:
			largestVd = self.findlookup(0,1)
			vdRow, vdCol = largestVd
			self.map[vdRow][vdCol] = 255
			self.updatelookup(vdRow,vdCol,-1)

			ranks[vdRow][vdCol] = currentOnes
			currentOnes+=1

		# Normalizing the bluenoise values to grayscale
		coeff = 256/totalPixels
		for i in range(self.height):
			for j in range(self.width):
				self.map[i][j] = int(coeff*(ranks[i][j]+0.5))