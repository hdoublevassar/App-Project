"""
Settings View
App settings, password management, and data deletion.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw


class SettingsView(Adw.NavigationPage):
    """App settings view."""
    
    def __init__(self, main_window):
        super().__init__(title="Settings")
        self.main_window = main_window
        self.db = main_window.db
        
        toolbar_view = Adw.ToolbarView()
        self.set_child(toolbar_view)
        
        header = Adw.HeaderBar()
        toolbar_view.add_top_bar(header)
        
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        toolbar_view.set_content(scroll)
        
        clamp = Adw.Clamp()
        clamp.set_maximum_size(600)
        clamp.set_margin_top(24)
        clamp.set_margin_bottom(24)
        clamp.set_margin_start(24)
        clamp.set_margin_end(24)
        scroll.set_child(clamp)
        
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        clamp.set_child(content)
        
        # Appearance
        appearance_group = Adw.PreferencesGroup()
        appearance_group.set_title("Appearance")
        content.append(appearance_group)
        
        # Dark mode
        dark_mode_row = Adw.SwitchRow()
        dark_mode_row.set_title("Dark Mode")
        dark_mode_row.set_subtitle("Use dark color scheme")
        dark_mode_row.set_icon_name("weather-clear-night-symbolic")
        
        # Get current style and set switch state
        style_manager = Adw.StyleManager.get_default()
        dark_mode_row.set_active(style_manager.get_dark())
        dark_mode_row.connect("notify::active", self._on_dark_mode_changed)
        appearance_group.add(dark_mode_row)
        
        # Security
        security_group = Adw.PreferencesGroup()
        security_group.set_title("Security")
        content.append(security_group)
        
        # Change password
        password_row = Adw.ActionRow()
        password_row.set_title("Change Password")
        password_row.set_subtitle("Update your app password")
        password_row.set_icon_name("dialog-password-symbolic")
        password_row.set_activatable(True)
        password_row.connect("activated", self._show_change_password_dialog)
        
        password_arrow = Gtk.Image.new_from_icon_name("go-next-symbolic")
        password_row.add_suffix(password_arrow)
        security_group.add(password_row)
        
        # Privacy info
        privacy_row = Adw.ActionRow()
        privacy_row.set_title("Privacy")
        privacy_row.set_subtitle("All data is stored locally on your device only")
        privacy_row.set_icon_name("security-high-symbolic")
        security_group.add(privacy_row)
        
        # Data
        data_group = Adw.PreferencesGroup()
        data_group.set_title("Data Management")
        content.append(data_group)
        
        # Export (future feature)
        export_row = Adw.ActionRow()
        export_row.set_title("Export Data")
        export_row.set_subtitle("Coming soon")
        export_row.set_icon_name("document-save-symbolic")
        export_row.set_sensitive(False)
        data_group.add(export_row)
        
        # About
        about_group = Adw.PreferencesGroup()
        about_group.set_title("About")
        content.append(about_group)
        
        version_row = Adw.ActionRow()
        version_row.set_title("Version")
        version_row.set_subtitle("1.0.0")
        version_row.set_icon_name("dialog-information-symbolic")
        about_group.add(version_row)
        
        # Danger zone
        danger_group = Adw.PreferencesGroup()
        danger_group.set_title("Danger Zone")
        danger_group.set_description("These actions cannot be undone")
        content.append(danger_group)
        
        # Delete all data
        delete_row = Adw.ActionRow()
        delete_row.set_title("Delete All Data")
        delete_row.set_subtitle("Permanently erase all tracked data")
        delete_row.set_icon_name("user-trash-symbolic")
        delete_row.add_css_class("error")
        delete_row.set_activatable(True)
        delete_row.connect("activated", self._show_delete_confirmation)
        
        delete_arrow = Gtk.Image.new_from_icon_name("go-next-symbolic")
        delete_row.add_suffix(delete_arrow)
        danger_group.add(delete_row)
    
    def _on_dark_mode_changed(self, switch, param):
        """Toggle dark mode."""
        style_manager = Adw.StyleManager.get_default()
        if switch.get_active():
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
    
    def _show_change_password_dialog(self, row):
        """Show change password dialog."""
        dialog = Adw.Dialog()
        dialog.set_title("Change Password")
        dialog.set_content_width(400)
        dialog.set_content_height(350)
        
        toolbar_view = Adw.ToolbarView()
        dialog.set_child(toolbar_view)
        
        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(False)
        header.set_show_start_title_buttons(False)
        
        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", lambda b: dialog.close())
        header.pack_start(cancel_btn)
        
        save_btn = Gtk.Button(label="Change")
        save_btn.add_css_class("suggested-action")
        header.pack_end(save_btn)
        
        toolbar_view.add_top_bar(header)
        
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_margin_top(24)
        content.set_margin_bottom(24)
        content.set_margin_start(24)
        content.set_margin_end(24)
        toolbar_view.set_content(content)
        
        group = Adw.PreferencesGroup()
        content.append(group)
        
        current_row = Adw.PasswordEntryRow()
        current_row.set_title("Current Password")
        group.add(current_row)
        
        new_row = Adw.PasswordEntryRow()
        new_row.set_title("New Password")
        group.add(new_row)
        
        confirm_row = Adw.PasswordEntryRow()
        confirm_row.set_title("Confirm New Password")
        group.add(confirm_row)
        
        error_label = Gtk.Label()
        error_label.add_css_class("error")
        error_label.set_visible(False)
        content.append(error_label)
        
        def on_save(btn):
            current = current_row.get_text()
            new = new_row.get_text()
            confirm = confirm_row.get_text()
            
            if len(new) < 6:
                error_label.set_label("New password must be at least 6 characters")
                error_label.set_visible(True)
                return
            
            if new != confirm:
                error_label.set_label("New passwords do not match")
                error_label.set_visible(True)
                return
            
            if self.db.change_password(current, new):
                dialog.close()
                toast = Adw.Toast.new("Password changed successfully")
                if hasattr(self.main_window, 'add_toast'):
                    self.main_window.add_toast(toast)
            else:
                error_label.set_label("Current password is incorrect")
                error_label.set_visible(True)
        
        save_btn.connect("clicked", on_save)
        
        dialog.present(self.main_window)
    
    def _show_delete_confirmation(self, row):
        """Show multi-step delete confirmation dialog."""
        dialog = Adw.Dialog()
        dialog.set_title("Delete All Data")
        dialog.set_content_width(450)
        dialog.set_content_height(450)
        
        toolbar_view = Adw.ToolbarView()
        dialog.set_child(toolbar_view)
        
        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(False)
        header.set_show_start_title_buttons(False)
        
        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", lambda b: dialog.close())
        header.pack_start(cancel_btn)
        
        toolbar_view.add_top_bar(header)
        
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        content.set_margin_top(24)
        content.set_margin_bottom(24)
        content.set_margin_start(24)
        content.set_margin_end(24)
        content.set_valign(Gtk.Align.CENTER)
        toolbar_view.set_content(content)
        
        # Warning icon
        warning_icon = Gtk.Image.new_from_icon_name("dialog-warning-symbolic")
        warning_icon.set_pixel_size(64)
        warning_icon.add_css_class("error")
        content.append(warning_icon)
        
        # Warning title
        warning_title = Gtk.Label(label="This action cannot be undone")
        warning_title.add_css_class("title-2")
        content.append(warning_title)
        
        # Warning message
        warning_msg = Gtk.Label(label="All your sleep data, fitness records, recovery progress, medications, relationships, goals, and other tracked information will be permanently deleted.")
        warning_msg.set_wrap(True)
        warning_msg.set_justify(Gtk.Justification.CENTER)
        warning_msg.add_css_class("dim-label")
        content.append(warning_msg)
        
        # Confirmation inputs
        confirm_label = Gtk.Label(label='Type "Delete Data" in both boxes to confirm:')
        confirm_label.add_css_class("heading")
        confirm_label.set_margin_top(16)
        content.append(confirm_label)
        
        entry1 = Gtk.Entry()
        entry1.set_placeholder_text("Delete Data")
        content.append(entry1)
        
        entry2 = Gtk.Entry()
        entry2.set_placeholder_text("Delete Data")
        content.append(entry2)
        
        # Delete button
        delete_btn = Gtk.Button(label="Delete All Data")
        delete_btn.add_css_class("destructive-action")
        delete_btn.add_css_class("pill")
        delete_btn.set_margin_top(16)
        content.append(delete_btn)
        
        error_label = Gtk.Label()
        error_label.add_css_class("error")
        error_label.set_visible(False)
        content.append(error_label)
        
        def on_delete(btn):
            text1 = entry1.get_text()
            text2 = entry2.get_text()
            
            if text1 != "Delete Data" or text2 != "Delete Data":
                error_label.set_label("Please type 'Delete Data' exactly in both boxes")
                error_label.set_visible(True)
                return
            
            # Actually delete
            if self.db.delete_all_data():
                dialog.close()
                
                # Show final confirmation and exit
                final_dialog = Adw.AlertDialog()
                final_dialog.set_heading("Data Deleted")
                final_dialog.set_body("All data has been permanently erased. The application will now close.")
                final_dialog.add_response("ok", "OK")
                final_dialog.set_default_response("ok")
                final_dialog.connect("response", lambda d, r: self.main_window.get_application().quit())
                final_dialog.present(self.main_window)
            else:
                error_label.set_label("Failed to delete data. Please try again.")
                error_label.set_visible(True)
        
        delete_btn.connect("clicked", on_delete)
        
        dialog.present(self.main_window)
