#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import smbus
import time

# Strawberry Linux社の「TSL2561 照度センサ・モジュール」から
# I2Cでデータを取得するクラス(python 2)
#
# This class controls "made by Strawberry Linux company 
# TSL2561 Illumination sensor module" by I2C. (python 2)
#
# https://strawberry-linux.com/catalog/items?code=12561
#
# 2016-05-03 Boyaki Machine
class SL_TSL2561:
	def __init__(self, address, channel):
		self.address	= address
		self.channel	= channel
		self.bus		= smbus.SMBus(self.channel)
		self.gain 		= 0x00			# 0x00=normal, 0x10=×16
		self.integrationTime 	= 0x02	# 0x02=402ms, 0x01=101ms, 0x00=13.7ms
		self.scale 		= 1.0

		#  Sensor initialization
		self.setLowGain()
		self.setIntegrationTime('default')

	def powerOn(self):
		self.bus.write_i2c_block_data(self.address, 0x80, [0x03])
		time.sleep(0.5)

	def powerOff(self):
		self.bus.write_i2c_block_data(self.address, 0x80, [0x00])

	# Set high Gain(x16?)
	def setHighGain(self):
		# Problem : 
		# At High gain and high illumination, Raw data isn't sometimes right.
		# (raw data will be 5047 fixing)
		self.gain 	= 0x10
		data 		= self.integrationTime | self.gain
		self.bus.write_i2c_block_data(self.address, 0x81, [data])
		self.calcScale()

	# Set low Gain (default)
	def setLowGain(self):
		self.gain 	= 0x00
		data 		= self.integrationTime | self.gain
		self.bus.write_i2c_block_data(self.address, 0x81, [data])
		self.calcScale()

	# Set integration time
	# val : short, middle, logn(default)
	def setIntegrationTime(self, val):
		if val=='short':
			self.integrationTime 	= 0x00	# 13.7ms scale=0.034
		elif val=='middle':
			self.integrationTime 	= 0x01 	# 101ms	 scale=0.252
		else:
			self.integrationTime 	= 0x02  # defaultVal 402ms  scale=1.0
		data = self.integrationTime | self.gain
		self.bus.write_i2c_block_data(self.address, 0x81, [data])
		self.calcScale()

	def getVisibleLightRawData(self):
		data 	= self.bus.read_i2c_block_data(self.address, 0xAC ,2)
		raw 	= data[1] << 8 | data[0]	# 16bit , Low byte previous
		return raw

	def getInfraredRawData(self):
		data 	= self.bus.read_i2c_block_data(self.address, 0xAE ,2)
		raw 	= data[1] << 8 | data[0]	# 16bit , Low byte previous
		return raw

	def getRawData(self):
		data 	= self.bus.read_i2c_block_data(self.address, 0xAC ,4)
		VL 		= data[1] << 8 | data[0]	# Visible Light　16bit , Low byte previous
		IR 		= data[3] << 8 | data[2]	# IR　16bit , Low byte previous
		return (VL,IR)

	def calcScale(self):
		_scale = 1.0
		# scale of integration time
		if self.integrationTime == 0x01:	# middle
			_scale = _scale / 0.252
		elif self.integrationTime == 0x00:	# short
			_scale = _scale / 0.034
		
		# scale of gain
		if self.gain == 0x00 :				# gain 1
			_scale = _scale * 16.0

		self.scale = _scale

	def getLux(self):
		# get raw data
		raw  = self.getRawData()

		# If raw data is 65535, return error.
		if raw[0] == 65535 or raw[1] == 65535:
			return "Range Over"

		#  Raw data is scaled by sensor setting.
		VLRD = raw[0] * self.scale
		IRRD = raw[1] * self.scale

		# Avoid the division of zero               
		if (float(VLRD) == 0):
			ratio = 9999
		else:
			ratio = (IRRD / float(VLRD))

		# Calculation of Lux
		if ((ratio >= 0) & (ratio <= 0.52)):
			lux = (0.0315 * VLRD) - (0.0593 * VLRD * (ratio**1.4))
		elif (ratio <= 0.65):
			lux = (0.0229 * VLRD) - (0.0291 * IRRD)
		elif (ratio <= 0.80):
			lux = (0.0157 * VLRD) - (0.018 * IRRD)
		elif (ratio <= 1.3):
			lux = (0.00338 * VLRD) - (0.0026 * IRRD)
		elif (ratio > 1.3):
			lux = 0

		return lux 


if __name__ == "__main__":
	sensor 	= SL_TSL2561(0x39,1) 
	sensor.powerOn()
	# sensor.setHighGain()
	sensor.setIntegrationTime('default')
	while True:
		print "Lux : " + str(sensor.getLux())
		time.sleep(1.0)

