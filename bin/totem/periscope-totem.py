import periscope
import totem
import gtk

import urllib2

#XML config to add to the menu
_ui_str = """
<ui>
    <menubar name="tmw-menubar">
         <menu name="view" action="view-menu">
			<menu name="subtitles" action="subtitles-menu">
				<separator />
				<menuitem name="periscope" action="download-periscope" />
			</menu>
		</menu>
	</menubar>
</ui>
"""


class Periscope (totem.Plugin):
	def __init__ (self):
		totem.Plugin.__init__ (self)


	def download_sub(self, action):
		''' use periscope to download the sub and load it '''		
		current_mrl = self.totem.get_current_mrl()
		local_url = urllib2.unquote(current_mrl[7:])
		subdl = periscope.Periscope()
		#subtitle = subdl.downloadSubtitle(local_url, ["en"])
		subtitle = None
		if subtitle: #Only do something if subtitle found
			current_time = self.totem.get_current_time()
			self.totem.action_set_mrl_and_play(current_mrl, "file://"+urllib2.quote(subtitle["subtitlepath"]))
			seconds = current_time/1000
			self.totem.action_seek_time(seconds) #TODO, don't think it's Py3K compatible
		self.totem.action_seek_time(600)

	def make_sensitive(self, totem_object, filename, boolean):
		'''set the periscope menu entry sensitive or not'''
		self.group.set_sensitive(boolean)

	def activate (self, totem_object):
		''' Load the menu entry'''
		self.totem = totem_object
		# The UI Managers merges the Menus
		ui_manager = totem_object.get_ui_manager()

		# Create a group and the actions for periscope
		self.group = gtk.ActionGroup('Periscope')
		#Name, StockID, Label, Accelerator, tooltip, callback
		self.actions = [('download-periscope', None, 'Download from Internet',
	     None, None, self.download_sub)]
		self.group.add_actions(self.actions)
		if not self.totem.get_current_mrl():
			self.group.set_sensitive(False)
			#Add a callback when a file is loaded
			self.totem.connect("file-opened", self.make_sensitive, True)

		ui_manager.insert_action_group(self.group, 0)
		self.ui_id = ui_manager.add_ui_from_string(_ui_str)

	def deactivate (self, totem_object):
		''' remove the menu entry'''
		ui_manager = totem_object.get_ui_manager()

		#Clean up: remove the added ui, actions and groups
		ui_manager.remove_ui(self.ui_id)
		ui_manager.remove_action_group(self.group)
		ui_manager.ensure_update()

