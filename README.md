# TSL2561

The class to control the TSL2561 to work with python 2.
It works with Raspberry pi 3. Sensor module using the TSL2561 seems there are a variety of implementation.　This class is moving by mounting of strawberry Linux company.

https://strawberry-linux.com/catalog/items?code=12561

python-smbus is needed.

$ sudo apt-get install python-smbus

There is one problem. 
At High gain and high illumination, Raw data isn't sometimes right.
(raw data will be 5047 fixing)

When it's useful to you, I'm happy.
