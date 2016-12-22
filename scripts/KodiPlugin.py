import xml.etree.ElementTree as ET
import os, sys, re, json, time
import importlib
import bridge
import kodi_utils
import Plugin
import traceback

if getattr(sys, 'frozen', False):
	# we are running in a bundle
	bundle_dir = sys._MEIPASS
else:
	bundle_dir = '.'

ADDONS_DIR = os.path.join(os.path.expanduser("~"), '.TVMLSERVER', 'addons')

def convert_kodi_tags_to_html_tags(s):
	s = s.replace('[B]', '<b>')
	s = s.replace('[/B]', '</b>')
	s = s.replace('[I]', '<i>')
	s = s.replace('[/I]', '</i>')
	return s


class KodiPlugin:
	def __init__(self, id):
		self.dir = os.path.join(ADDONS_DIR, id)
		tree = ET.parse(os.path.join(self.dir, 'addon.xml'))
		for e in tree.iter('addon'):
			self.name = e.attrib['name']
			self.id = e.attrib['id']
		for e2 in tree.iter('extension'):
			if e2.attrib['point'] == 'xbmc.python.pluginsource':
				self.script = e2.attrib['library']
				
		self.requires = []
		for e3 in tree.iter('import'):
			if e3.attrib['addon'].startswith('script'):
				self.requires.append(e3.attrib['addon'])
		self.icon = '/addons/{}/icon.png'.format(self.id)
		self.module = self.script[:-3]
		self.menuurl = '/menu/{}'.format(kodi_utils.b64encode(self.id))
		
	def __repr__(self):
		return json.dumps({'id':self.id, 'name':self.name, 'module':self.module})
		
	def settings(self, bridge, url):
		import xbmc
		xbmc.bridge = bridge
		import xbmcaddon
		xbmcaddon.Addon(self.id).openSettings()
			
	
	def run(self, bridge, url):
		if url.startswith('http') or url.startswith('https'):
			bridge.play(url, type_='video')
			return
		orig = sys.path
		sys.path.append(self.dir)
		sys.path.append(os.path.join(bundle_dir, 'scripts'))
		sys.path.append(os.path.join(bundle_dir, 'scripts', 'kodi'))
		
		for r in self.requires:
			if os.path.exists(os.path.join(ADDONS_DIR, r)):
				tree = ET.parse(os.path.join(ADDONS_DIR, r, 'addon.xml'))
				for e2 in tree.iter('extension'):
					if e2.attrib['point'] == 'xbmc.python.module':
						sys.path.append(os.path.join(ADDONS_DIR, r, e2.attrib['library']))
		import xbmc
		xbmc.bridge = bridge
		import Container
		xbmc.Container = Container.Container(self)
		if type(url) is not str:
			raise Exception('Kodi plugin only accepts one string argument')
				
		try:
			fp = open(os.path.join(bundle_dir, self.dir, self.script), 'rb')
			#old_sys_argv = sys.argv
			#plugin://plugin.video.youtube/play/?video_id=sa7kZXOHAtI
			#/playlist/PLpSnlSGciSWPewHLHBq5HFLJBGhHrsKnJ/
			#file://plugin.video.KIDSIL/default.py?url=plugin%3A%2F%2Fplugin.video.youtube%2Fplaylist%2FPLpSnlSGciSWPewHLHBq5HFLJBGhHrsKnJ%2F&mode=8&name=%D7%A6%D7%95%D7%9D+%D7%A6%D7%95%D7%9D&iconimage=http%3A%2F%2Fcfvod.kaltura.com%2Fp%2F1068292%2Fsp%2F106829200%2Fthumbnail%2Fentry_id%2F1_ojk9szi3%2Fversion%2F100011%2Facv%2F221%2Fwidth%2F1024%2Fheight%2F584&description=1
			#m = re.search('(.*://[^/]*([^?]*))*(\?*.*)', url)
			#if not m:
			#	return None
			#url = m.group(3)
			#script = m.group(2) if m.group(2) else os.path.join('file://{}'.format(self.id),self.script)
			if '?' in url:
				sys.argv = [url.split('?')[0], '1', '?{}'.format(url.split('?')[1])]
			else:
				sys.argv = [url, '1', '']
			#print 'before regex {}'.format(sys.argv[0])
			#m = re.search('.*://[^/]*(/.*)', sys.argv[0])
			#if m:
			#	sys.argv[0] = m.group(1)
			#print 'after regex {}'.format(sys.argv[0])
			
			if not sys.argv[0]:
				sys.argv[0] = 'file://{}/{}'.format(self.id,self.script)
				
			if not sys.argv[0].startswith('file://') and not sys.argv[0].startswith('plugin://'):
				sys.argv[0] = 'file://{}{}'.format(self.id, sys.argv[0])
			#sys.argv = [script, '1', url]
			print 'Calling plugin {} with {}'.format(self.name, sys.argv)
			import xbmcplugin, xbmcaddon
			import imp
			
			#some patches for internal python funcs
			import urllib			
			quote_plus_orig = urllib.quote_plus
			def quote_plus_patch(s, safe=''):
				if type(s) == unicode:
					s = s.encode('utf-8')
				return quote_plus_orig(s, safe)
			urllib.quote_plus = quote_plus_patch
			
			import sqlite3			
			sqlite3_connect_orig = sqlite3.connect
			def sqlite3_connect_patch(*args, **kwargs):
				print 'sqlite3 connect patch'
				database = args[0]
				dirname = os.path.dirname(database)
				if not os.path.exists(dirname):
					print 'creating non-existent directory {}'.format(dirname)
					os.makedirs(dirname)
				if not os.path.exists(database):
					open(database, 'a').close()
				for tries in range(5):
					try:
						return sqlite3_connect_orig(*args, **kwargs)
					except:
						time.sleep(1)
						traceback.print_exc(file=sys.stdout)
				raise Exception('Failed to open DB file {}'.format(database))
			sqlite3.connect = sqlite3_connect_patch
			
			dbapi2_connect_orig = sqlite3.dbapi2.connect
			def dbapi2_connect_patch(*args, **kwargs):
				print 'sqlite3.dbapi2 connect patch'
				database = args[0]
				dirname = os.path.dirname(database)
				if not os.path.exists(dirname):
					print 'creating non-existent directory {}'.format(dirname)
					os.makedirs(dirname)
				if not os.path.exists(database):
					open(database, 'a').close()
				for tries in range(5):
					try:
						return dbapi2_connect_orig(*args, **kwargs)
					except:
						time.sleep(1)
						traceback.print_exc(file=sys.stdout)
				raise Exception('Failed to open DB file {}'.format(database))
			sqlite3.dbapi2.connect = dbapi2_connect_patch
			
			xbmcplugin.items = []
			imp.load_module(self.module, fp, self.dir, ('.py', 'rb', imp.PY_SOURCE))
		except:
			print 'Failure in plugin run'
			traceback.print_exc(file=sys.stdout)
		fp.close()
		sys.path = orig
		#sys.argv = old_sys_argv
		items = xbmcplugin.items
		print 'Plugin {} ended with: {}'.format(self.name, items)
		
		#some cleanup
		if self.id in xbmcaddon.ADDON_CACHE:
			print 'Saving settings {}'.format(xbmcaddon.ADDON_CACHE[self.id])
			bridge._message({'type':'saveSettings','addon':self.id, 'settings':xbmcaddon.ADDON_CACHE[self.id]})
		if bridge.progress:
			print 'Closing left over progress'
			bridge.closeprogress()
		ans = []
		items = xbmcplugin.items
		from Plugin import Item
		if len(items) == 1 and hasattr(items[0], 'path'):
			return items
		for item in items:
			#url, title, subtitle=None, icon=None, details=None, menuurl='', info={})
			i = Item(url=item['url'], title=convert_kodi_tags_to_html_tags(item['listitem'].label), subtitle=item['listitem'].getProperty('subtitle'), icon=item['listitem'].thumbnailImage if item['listitem'].thumbnailImage != 'DefaultFolder.png' else '', details=item['listitem'].getProperty('details'),info=item['listitem'].infos, context=item['listitem'].context)
			if type(i.context) is list: #needs to be dict
				i.context = {x[0]:x[1] for x in i.context}
			infos = item['listitem'].infos
			if 'poster' in infos:
				i.icon = infos['poster']
			if 'plot' in infos:
				i.details = infos['plot']
			if 'year' in infos:
				i.year = infos['year']
			if 'trailer' in infos:
				i.context['Watch trailer'] = 'RunPlugin({})'.format(infos['trailer'])			
			ans.append(i)
		return ans