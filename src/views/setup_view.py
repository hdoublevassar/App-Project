"""
Setup View - First-time password creation
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw


class SetupView(Adw.NavigationPage):
    """First-time setup view for creating a password."""
    
    def __init__(self, main_window):
        super().__init__(title="Welcome")
        self.main_window = main_window
        
        # Main container
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_child(self.box)
        
        # Header
        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(True)
        self.box.append(header)
        
        # Content in a clamp for proper sizing
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
        
        # App icon/logo placeholder
        icon = Gtk.Image.new_from_icon_name("applications-science-symbolic")
        icon.set_pixel_size(80)
        icon.add_css_class("dim-label")
        content.append(icon)
        
        # Welcome title
        title = Gtk.Label(label="Welcome to LifeTracker")
        title.add_css_class("title-1")
        content.append(title)
        
        # Subtitle
        subtitle = Gtk.Label(label="Your private wellness companion.\nAll data stays on your device.")
        subtitle.add_css_class("dim-label")
        subtitle.set_justify(Gtk.Justification.CENTER)
        content.append(subtitle)
        
        # Password section
        password_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        password_box.set_margin_top(24)
        content.append(password_box)
        
        password_label = Gtk.Label(label="Create a password to protect your data")
        password_label.add_css_class("heading")
        password_box.append(password_label)
        
        # Password entry
        self.password_entry = Adw.PasswordEntryRow()
        self.password_entry.set_title("Password")
        
        # Confirm password entry
        self.confirm_entry = Adw.PasswordEntryRow()
        self.confirm_entry.set_title("Confirm Password")
        
        # Put entries in a preferences group
        prefs_group = Adw.PreferencesGroup()
        prefs_group.add(self.password_entry)
        prefs_group.add(self.confirm_entry)
        password_box.append(prefs_group)
        
        # Error label
        self.error_label = Gtk.Label()
        self.error_label.add_css_class("error")
        self.error_label.set_visible(False)
        password_box.append(self.error_label)
        
        # Create button
        self.create_button = Gtk.Button(label="Create Account")
        self.create_button.add_css_class("suggested-action")
        self.create_button.add_css_class("pill")
        self.create_button.set_margin_top(12)
        self.create_button.connect("clicked", self.on_create_clicked)
        password_box.append(self.create_button)
        
        # Security note
        note = Gtk.Label(label="⚠️ This password cannot be recovered. Store it safely.")
        note.add_css_class("dim-label")
        note.add_css_class("caption")
        note.set_margin_top(12)
        password_box.append(note)
    
    def on_create_clicked(self, button):
        """Handle create account button click."""
        password = self.password_entry.get_text()
        confirm = self.confirm_entry.get_text()
        
        # Validation
        if len(password) < 6:
            self.show_error("Password must be at least 6 characters")
            return
        
        if password != confirm:
            self.show_error("Passwords do not match")
            return
        
        # Create account
        if self.main_window.db.setup_password(password):
            self.main_window.show_home_view()
        else:
            self.show_error("Failed to create account. Please try again.")
    
    def show_error(self, message: str):
        """Display an error message."""
        self.error_label.set_label(message)
        self.error_label.set_visible(True)
