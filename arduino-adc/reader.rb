require 'rubygems'
require 'serialport'

sp = SerialPort.new "/dev/ttyUSB0", 9600
while message_from_arduino = sp.gets
   puts message_from_arduino
end
