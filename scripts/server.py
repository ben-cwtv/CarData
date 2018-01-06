##!/usr/bin/env python
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import os
import serial
import sys
import string
import time

wss =[]

arduino = serial.Serial('/dev/ttyAMA0', 9600, timeout=2)

class WSHandler(tornado.websocket.WebSocketHandler):
  def check_origin(self, origin):
    return True
  def open(self):
    #print 'New user is connected.\n' 
    if self not in wss:
      wss.append(self)
  def on_close(self):
    #print 'connection closed\n'
    if self in wss:
      wss.remove(self)

application = tornado.web.Application([(r'/ws', WSHandler),])

if __name__ == "__main__":
  interval_msec = 2000

  def wsSend(message):
    for ws in wss:
      if not ws.ws_connection.stream.socket:
        print "Web socket does not exist anymore!!!"
        wss.remove(ws)
      else:
        ws.write_message(message)

  def read_temp():
    try:
      time.sleep(10)
      arduino.write('2')
      lines = arduino.readlines()
      temp = str(float(lines[0]))
      #print temp

      arduino.write('3')
      lines = arduino.readlines()
      temp += ';' + str(float(lines[0]))
      #print temp
      wsSend(temp)
    except:
      wsSend("-;-")

  http_server = tornado.httpserver.HTTPServer(application)
  http_server.listen(8080)
    
  main_loop = tornado.ioloop.IOLoop.instance()
  sched_temp = tornado.ioloop.PeriodicCallback(read_temp, interval_msec,   io_loop = main_loop)

  sched_temp.start()
  main_loop.start()
