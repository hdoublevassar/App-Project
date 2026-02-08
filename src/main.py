#!/usr/bin/env python3
"""
LifeTracker - A Comprehensive Personal Wellness Application
============================================================
A privacy-focused, offline-first application for tracking personal health,
wellness, and lifestyle data. All data stays on your device.

Author: Hudson
License: MIT
"""

import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio, GLib, Gdk

from database import DatabaseManager
from views.login_view import LoginView
from views.home_view import HomeView
from views.sleep_view import SleepView
from views.fitness_view import FitnessView
from views.recovery_view import RecoveryView
from views.medication_view import MedicationView
from views.relationships_view import RelationshipsView
from views.goals_view import GoalsView
from views.insights_view import InsightsView
from views.bowel_view import BowelView
from views.settings_view import SettingsView


class LifeTrackerApp(Adw.Application):
    """Main application class for LifeTracker."""
    
    def __init__(self):
        super().__init__(
            application_id='io.github.lifetracker',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        
        self.db = None
        self.window = None
        self.is_authenticated = False
        
        # Connect signals
        self.connect('activate', self.on_activate)
        self.connect('shutdown', self.on_shutdown)
    
    def on_activate(self, app):
        """Called when the application is activated."""
        # Load CSS styling
        self._load_css()
        
        # Create the main window
        self.window = LifeTrackerWindow(application=self)
        self.window.present()
    
    def _load_css(self):
        """Load custom CSS stylesheet."""
        import os
        
        css_provider = Gtk.CssProvider()
        
        # Try multiple locations for the CSS file
        css_paths = [
            # Development path (when running from src/)
            os.path.join(os.path.dirname(__file__), '..', 'data', 'style.css'),
            # Installed path (Flatpak/system)
            '/app/share/lifetracker/style.css',
            os.path.join(GLib.get_user_data_dir(), 'lifetracker', 'style.css'),
        ]
        
        for css_path in css_paths:
            if os.path.exists(css_path):
                css_provider.load_from_path(css_path)
                Gtk.StyleContext.add_provider_for_display(
                    self.window.get_display() if hasattr(self, 'window') and self.window else 
                    Gdk.Display.get_default(),
                    css_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
                break
    
    def on_shutdown(self, app):
        """Called when the application shuts down."""
        if self.db:
            self.db.close()


class LifeTrackerWindow(Adw.ApplicationWindow):
    """Main application window."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Window properties
        self.set_title("LifeTracker")
        self.set_default_size(1200, 800)
        self.set_size_request(800, 600)
        
        # Initialize database
        self.db = DatabaseManager()
        self.app = kwargs.get('application')
        if self.app:
            self.app.db = self.db
        
        # Main layout
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(self.main_box)
        
        # Navigation view for page transitions
        self.navigation_view = Adw.NavigationView()
        self.main_box.append(self.navigation_view)
        
        # Check if first run or needs authentication
        if self.db.is_first_run():
            self.show_setup_view()
        else:
            self.show_login_view()
    
    def show_setup_view(self):
        """Show the initial setup/password creation view."""
        from views.setup_view import SetupView
        setup_view = SetupView(self)
        self.navigation_view.push(setup_view)
    
    def show_login_view(self):
        """Show the login view."""
        login_view = LoginView(self)
        self.navigation_view.push(login_view)
    
    def show_home_view(self):
        """Show the main home dashboard after authentication."""
        # Clear navigation and show home
        self.navigation_view.pop_to_tag("home")
        
        # If home doesn't exist, create it
        home_view = HomeView(self)
        home_view.set_tag("home")
        
        # Replace all with home
        while self.navigation_view.get_visible_page():
            self.navigation_view.pop()
        
        self.navigation_view.push(home_view)
    
    def navigate_to(self, view_name: str):
        """Navigate to a specific view."""
        view_map = {
            'home': HomeView,
            'sleep': SleepView,
            'fitness': FitnessView,
            'recovery': RecoveryView,
            'medication': MedicationView,
            'relationships': RelationshipsView,
            'goals': GoalsView,
            'insights': InsightsView,
            'bowel': BowelView,
            'settings': SettingsView,
        }
        
        if view_name in view_map:
            view = view_map[view_name](self)
            self.navigation_view.push(view)


def main():
    """Application entry point."""
    app = LifeTrackerApp()
    return app.run(sys.argv)


if __name__ == '__main__':
    sys.exit(main())
