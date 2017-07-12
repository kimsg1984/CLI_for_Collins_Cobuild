#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: SunGyo Kim
# Email: Kimsg1984@gmail.com
# irc.freenode #ubuntu-ko Sungyo

from webscraping import xpath
import re
import os
import sys
import subprocess
import cmd
import urllib2

import IO
dict_repogitory = os.path.expanduser('~/dict_repogitory.dat')

def parsing(xpath_content, parsing_code, return_all = False):
	result = xpath_content.search(parsing_code)
	if return_all == True : return result
	else:
		if len(result) == 0: return False
		elif len(result) == 1: return result[0]
		else: return result[0]

def clear():
	if os.name in ('nt','dos'):
		subprocess.call("cls")
	elif os.name in ('linux','osx','posix'):
		subprocess.call("clear")
	else:
		print "\n"*120

class CollinsCobuild:
	def __init__(self):
		self.url = 'https://www.collinsdictionary.com/search/?dictCode=english&q='
		self.finalurl = ''

	def readURL(self, url):
		req = urllib2.Request(url)
		self.res = urllib2.urlopen(req)
		content = self.res.read()
		self.finalurl = self.res.geturl()
		return content

	def searching_url(self, keyword):
		keyword = re.sub(r' ', '+', keyword)
		return self.url + keyword

	def search(self, keyword):  return self.readURL(self.searching_url(keyword))

class Dictionary():
	def __init__(self):
		self.element = {
			'all' : False,
			'meaning_limit' : 3,
			'origin_url' : False,
		}
		self.CC = CollinsCobuild()
		self.shelve = IO.Shelve(dict_repogitory)

	def dict_to_string(self, dic):
		def get_proun_type(xpath_content):
			result = xpath_content.search('//span[@class=pron type-]')

			if len(result) == 0: 
				result = xpath_content.search('//span[@class=pron type-ipa]')
				if len(result) == 0: return ''
			
			pronoun = result[0]
			pronoun = re.sub(r'<.+?>', '', pronoun)
			pronoun = re.sub(r'\n', '', pronoun)
			pronoun = pronoun.strip()
			return pronoun

		def dict_html_parser(content):
			content = re.sub('&nbsp;', '', content)
			content = re.sub('<div class=\"cit type-example\">', '', content)
			content = re.sub('<div class=\"cit type-example\">', '', content)
			#<span class="quote">Without more training or advanced technical skills, they'll lose their jobs.</span>
			content = re.sub(r'<span class=\"quote\">(.+?)</span>', r'"\1"', content)
			# <a href="/dictionary/english-thesaurus/advanced#advanced__1" title="Synonyms of advanced" class="ref type-thesaurus">More Synonyms of advanced</a>
			# content = rel.sub('')
			content = re.sub(r'<a href=\"/dictionary/english-thesaurus/(.+?) title="Synonyms of advanced"(.+?)</a>', '(more synyms)', content)
			content = re.sub(r'<(.+?)>', '', content)
			content = content.strip()
			content += '\n\n'
			return content

		word = parsing(dic, '//span[@class=orth]')
		pronoun = get_proun_type(dic)
		meaning = dic.search('//div[@class=hom]')
		
		result = ''
		if word: result = '%s / %s /\n' %(word, pronoun) 
		n = 1
		
		left = len(meaning) - self.element['meaning_limit']
		for m in meaning: 
			if not self.element['all']:
				if self.element['meaning_limit'] < n: 
					result += '(there are %s more meaning)...\n' %(left)
					break
			n += 1
			result += dict_html_parser(m)
		return result

	def search(self, keyword):
		if self.shelve.hasKey(keyword):
			xpath_content = self.shelve.load('content', keyword)
			finalurl = self.shelve.load('url', keyword)
		else:
			html_page = self.CC.search(keyword)
			xpath_doc = xpath.Doc(html_page)
			content = xpath_doc.search('//div[@class=dictionaries dictionary]')
			if not len(content): return False
			xpath_content = xpath.Doc(content[0])
			finalurl = self.CC.finalurl
			self.shelve.save('content', xpath_content, keyword)
			self.shelve.save('url', finalurl, keyword)

		result = ''
		for dic in xpath_content.search('/div'):
			# print(xpath_content); exit()
			if self.element['all']: 
				dict_type = (re.findall(r'data-type-block="(.+?)"', dic))
				if len(dict_type) >= 1: 
					result +=   '[%s]\n '%(dict_type[0])
				result += self.dict_to_string(xpath.Doc(dic))
			else: 
				result += self.dict_to_string(xpath.Doc(dic))
				break 
		if self.element['origin_url']: result += finalurl
		return result

class Console(cmd.Cmd):
	''' 딕셔너리 콘솔 클래스 '''
	intro='''
 ::: Welcome to Dictonary Concole Mode ::: 
	'help' : helping the command
	[Ctrl+D] exit \n\n\n
	'''
	prompt = '(dict) '

	def cmdloop(self, DIC):
		self.DIC = DIC
		return cmd.Cmd.cmdloop(self, self.intro)

	def preloop(self):
		clear()

	def do_all(self, line):
		''' Usage : all\n "To set printing all of meaning and dictionary" '''
		if self.DIC.element['all']:
			self.DIC.element['all'] = False
			print('only print one dictionary and %s meanings' %self.DIC.element['meaning_limit'])
		else:
			self.DIC.element['all'] = True
			print('Print all of meaning and dictionary')

	def do_url(self, line):
		''' Usage : url\n "To set printing URL of origin webpage" '''
		if self.DIC.element['origin_url']:
			self.DIC.element['origin_url'] = False
			print('remove URL')
		else:
			self.DIC.element['origin_url'] = True
			print('show URL')

	def do_limit(self, line):
		''' Usage : limit [int]\n "To set meaning limit" '''
		try :
			limit_number = int(line)
		except:
			print('please put \'int\' after comd \'limit\'  Ex) limit 3')
			limit_number = self.DIC.element['meaning_limit']

		self.DIC.element['meaning_limit'] = limit_number

	def do_clear(self, line):
		'''Usage: clear\n "clear the console" '''
		clear()

	def default(self, line):
		result = self.DIC.search(line)
		if result:
			clear()
			print(result)
		else: 
			print('\n \'%s\' 의 검색 결과가 존재하지 않습니다.\n' %line)

	def do_exit(self, line):
		"Exit the console gently;)"
		return True

	def do_EOF(self, line):
		"Exit the console gently with [Ctrl+D] ;)"
		return True

def main(argv):
	DIC = Dictionary()

	if len(argv) == 1: argv.append('-h')
	## Parser Setting ##
	usage = u"Usage: %prog [options]"
	parser = __import__('optparse').OptionParser(usage)

	## Parser Option ##	
	parser.add_option('-a', '--all', dest='all', action='store_true', help=u'사전과 예제를 전부 보여준다.')
	parser.add_option('-l', '--meaning_limit', dest='meaning_limit', type='int', help=u'의미 개수 제한을 늘린다. 기본 설정값은 %s 이다.' %(DIC.element['meaning_limit']))
	parser.add_option('-u', '--origin-url', dest='origin_url', action='store_true', help=u'출처 웹페이지 URL를 보여준다.')
	parser.add_option('-c', '--console', dest='console', action='store_true', help=u'콘솔 화면을 띄운다')
	
	## command logic  ##
	(opt, argv) = parser.parse_args(argv)
	if opt.all 			: DIC.element['all'] 			= True
	if opt.meaning_limit	: DIC.element['meaning_limit'] 	= opt.meaning_limit
	if opt.origin_url		: DIC.element['origin_url'] 		= True
	if opt.console		: Console().cmdloop(DIC); exit()

	keyword = argv[1]
	result = DIC.search(keyword)
	if result: 
		clear()
		print(result)
	else: print('\n \'%s\' 의 검색 결과가 존재하지 않습니다.\n' %keyword)

if __name__ == '__main__':
	main(__import__('sys').argv)