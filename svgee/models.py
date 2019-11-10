# coding: utf-8
from django.template.loader import render_to_string

# Create your views here.
import math
import random


class Piechart:
	class Part:
		color = ""
		value = 0.0
		percentage = 0.0
		text = ""
	
	parts = []
	total = 0.0
	side = 200
	r = 0
	pulled_out = 0 # How much the sector is pulled out
	
	def __init__(self):
		self.parts = []
		self.total = 0.0
		self.side = 200
		self.r = 0
		self.pulled_out = 0
	
	def add_part(self, value, color, text="", pulled_out=0.0):
		self.total += float(value)
		part = self.Part()
		part.color = color
		part.value = float(value)
		part.text = text
		part.pulled_out = pulled_out;
		self.parts.append(part)
	
	# Prepare for rendering
	def prepare(self):
		if not self.r:
			self.r = self.side/2 - 5
		for part in self.parts:
			part.percentage = part.value / self.total
	
	def svg_and_js(self):
		self.prepare()
		
		parts = self.parts
		key = random.randint(0, 100000)

		ang = 0
		i = 0
		ret_parts = []
		svgjs = ""
		for part in parts:
			toang = ang+math.pi*2*part.percentage
			color = part.color
			x = self.side/2 + math.sin(toang)*self.r
			y = self.side/2 - math.cos(toang)*self.r
			sx = 0 + math.sin(ang)*self.r
			sy = 0 - math.cos(ang)*self.r
			hoverx = self.side/2 + math.sin((ang+toang)/2)*(self.r - 15)
			hovery = self.side/2 - math.cos((ang+toang)/2)*(self.r - 15)
			
			dx = math.sin((ang+toang)/2)*part.pulled_out
			dy = -math.cos((ang+toang)/2)*part.pulled_out
			
			ang = toang
			# Store some in JS, so we have information about the graph that we can show
			if part.percentage>0.5:
				large_arc_flag = "1"
			else:
				large_arc_flag = "0"


#			text = ""
#			if part.text:
#				text += part.text + "<br />"
			name = part.text
			text = "%.1f%%" % (part.percentage*100)

			ret_parts.append({
				'id': i,
				'color': color,
				'sx': sx,
				'sy': sy,
				'cx': self.side/2 + dx,
				'cy': self.side/2 + dy,
				'x': x+dx,
				'y': y+dy,
				'name': name,
				'text': text,
				'hoverx': hoverx + dx,
				'hovery': hovery + dy,
				'large_arc_flag': large_arc_flag,
			})
			i += 1

		data = {
			'side': self.side, 
			'halfside': self.side/2, 
			'r': self.r, 
			'rplus': self.r+2, 
			'key': key, 
			'parts': ret_parts,
			'backfill': "#444",
		}
		svgdata = render_to_string("svgee/piechart.html", data)
		svgjs = render_to_string("svgee/piechart.js", data)
		pielegend = render_to_string("svgee/pielegend.html", data)
		return (svgdata, svgjs, pielegend)
	