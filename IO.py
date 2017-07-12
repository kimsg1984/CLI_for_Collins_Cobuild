#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: SunGyo Kim
# Email: Kimsg1984@gmail.com
# irc.freenode #ubuntu-ko Sungyo

import shelve

class Shelve():
	""" 
	https://docs.python.org/2/library/shelve.html (기본적인 설명) 
	http://gwlee.blogspot.kr/2012/03/shelve.html (대용량으로 다룰 경우)
	""" 
	def __init__(self, filename='IO_db.dat'):
		self.db_file = filename

	def save(self, obj, sub, id=None):
		self.db = shelve.open(self.db_file)

		if id : 
			if self.db.has_key(id): 
				list = self.db[id]
				list[obj] = sub
				self.db[id] = list
				self.db.close()
				return True
			else: 
				list = {}
				list[obj] = sub
				self.db[id] = list
				self.db.close()
				return True
		else: 
			self.db[obj] =sub 
			self.db.close()
			return True

	def load(self, obj, id=False):
		self.db = shelve.open(self.db_file)
		if id:
			if self.db.has_key(id):
				if self.db[id].has_key(obj): 
					result = self.db[id][obj]
					self.db.close()
					return result
		else:
			if self.db.has_key(obj): 
				result = self.db[obj]
				self.db.close()
				return result
		self.db.close()
		return 'Null'

	def hasKey(self, obj, id=None):
		self.db = shelve.open(self.db_file)
		if id:
			if self.db.has_key(id): 
				if self.db.has_key(obj): 
					self.db.close()
					return True 
		else: 
			if self.db.has_key(obj): 
				self.db.close()
				return True
		self.db.close()
		return False 

	def list(self):
		db_result = {}
		self.db = shelve.open(self.db_file)
		for d in self.db: db_result[d] = self.db[d]
		self.db.close()
		return db_result

	def removeAll(self):
		self.db = shelve.open(self.db_file)
		for f in self.db: 
			del self.db[f]
		self.db.close()
		return True

	def remove(self, obj): 
		self.db = shelve.open(self.db_file)
		if self.db.has_key(obj): 
			del self.db[obj] 
			if self.db.has_key(obj) == False: # has removed
				self.db.close()
				return True
			else:
				self.db.close()
				return False
		else:	
			self.db.close()
			return True