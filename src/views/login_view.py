"""
Login View - Password authentication
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw


class LoginView(Adw.NavigationPage):
    """Login view for password authentication."""
    
    def __init__(self, main_window):
        super().__init__(title="Login")
        self.main_window = main_window
        
        # Main container
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_child(self.box)
        
        # Header (minimal for login)
        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(True)
        self.box.append(header)
        
        # Content in a clamp
        clamp = Adw.Clamp()
        clamp.set_maximum_size(400)
        clamp.set_margin_top(48)
        clamp.set_margin_bottom(48)
        clamp.set_margin_start(24)
        clamp.set_margin_end(24)
        self.box.append(clamp)
        
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        content.set_valign(Gtk.Align.CENTER)
        content.set_vexpand(True)
        clamp.set_child(content)
        
        # App icon
        icon = Gtk.Image.new_from_icon_name("applications-science-symbolic")
        icon.set_pixel_size(80)
        icon.add_css_class("dim-label")
        content.append(icon)
        
        # Title
        title = Gtk.Label(label="LifeTracker")
        title.add_css_class("title-1")
        content.append(title)
        
        # Subtitle
        subtitle = Gtk.Label(label="Enter your password to continue")
        subtitle.add_css_class("dim-label")
        content.append(subtitle)
        
        # Password section
        password_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        password_box.set_margin_top(24)
        content.append(password_box)
        
        # Password entry
        self.password_entry = Adw.PasswordEntryRow()
        self.password_entry.set_title("Password")
        self.password_entry.connect("entry-activated", self.on_login_clicked)
        
        prefs_group = Adw.PreferencesGroup()
        prefs_group.add(self.password_entry)
        password_box.append(prefs_group)
        
        # Error label
        self.error_label = Gtk.Label()
        self.error_label.add_css_class("error")
        self.error_label.set_visible(False)
        password_box.append(self.error_label)
        
        # Login button
        self.login_button = Gtk.Button(label="Unlock")
        self.login_button.add_css_class("suggested-action")
        self.login_button.add_css_class("pill")
        self.login_button.set_margin_top(12)
        self.login_button.connect("clicked", self.on_login_clicked)
        password_box.append(self.login_button)
    
    def on_login_clicked(self, *args):
        """Handle login button click."""
        password = self.password_entry.get_text()
        
        if not password:
            self.show_error("Please enter your password")
            return
        
        if self.main_window.db.authenticate(password):
            self.main_window.show_home_view()
        else:
            self.show_error("Incorrect password")
            self.password_entry.set_text("")
    
    def show_error(self, message: str):
        """Display an error message."""
        self.error_label.set_label(message)
        self.error_label.set_visible(True)
