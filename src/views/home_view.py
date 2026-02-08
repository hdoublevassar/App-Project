"""
Home View - Main Dashboard
The central hub for accessing all LifeTracker modules.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
from datetime import date


class HomeView(Adw.NavigationPage):
    """Main dashboard view with module cards."""
    
    def __init__(self, main_window):
        super().__init__(title="LifeTracker")
        self.main_window = main_window
        self.db = main_window.db
        
        # Main container with toolbar view
        toolbar_view = Adw.ToolbarView()
        self.set_child(toolbar_view)
        
        # Header bar
        header = Adw.HeaderBar()
        
        # Settings button
        settings_btn = Gtk.Button(icon_name="emblem-system-symbolic")
        settings_btn.set_tooltip_text("Settings")
        settings_btn.connect("clicked", lambda b: main_window.navigate_to('settings'))
        header.pack_end(settings_btn)
        
        toolbar_view.add_top_bar(header)
        
        # Scrollable content
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        toolbar_view.set_content(scroll)
        
        # Main content clamp
        clamp = Adw.Clamp()
        clamp.set_maximum_size(900)
        clamp.set_margin_top(24)
        clamp.set_margin_bottom(24)
        clamp.set_margin_start(24)
        clamp.set_margin_end(24)
        scroll.set_child(clamp)
        
        # Content box
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        clamp.set_child(content)
        
        # Welcome header
        welcome_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        content.append(welcome_box)
        
        greeting = self._get_greeting()
        greeting_label = Gtk.Label(label=greeting)
        greeting_label.add_css_class("title-1")
        greeting_label.set_halign(Gtk.Align.START)
        welcome_box.append(greeting_label)
        
        date_label = Gtk.Label(label=date.today().strftime("%A, %B %d, %Y"))
        date_label.add_css_class("dim-label")
        date_label.set_halign(Gtk.Align.START)
        welcome_box.append(date_label)
        
        # Quick actions row
        quick_actions = self._create_quick_actions()
        content.append(quick_actions)
        
        # Module cards in a grid
        modules_label = Gtk.Label(label="Modules")
        modules_label.add_css_class("title-3")
        modules_label.set_halign(Gtk.Align.START)
        modules_label.set_margin_top(12)
        content.append(modules_label)
        
        # FlowBox for responsive grid
        self.modules_grid = Gtk.FlowBox()
        self.modules_grid.set_selection_mode(Gtk.SelectionMode.NONE)
        self.modules_grid.set_homogeneous(True)
        self.modules_grid.set_min_children_per_line(2)
        self.modules_grid.set_max_children_per_line(4)
        self.modules_grid.set_row_spacing(16)
        self.modules_grid.set_column_spacing(16)
        content.append(self.modules_grid)
        
        # Add module cards
        self._add_module_cards()
        
        # Today's summary section
        summary_label = Gtk.Label(label="Today's Overview")
        summary_label.add_css_class("title-3")
        summary_label.set_halign(Gtk.Align.START)
        summary_label.set_margin_top(24)
        content.append(summary_label)
        
        summary_box = self._create_today_summary()
        content.append(summary_box)
    
    def _get_greeting(self) -> str:
        """Get time-appropriate greeting."""
        from datetime import datetime
        hour = datetime.now().hour
        
        if hour < 12:
            return "Good Morning"
        elif hour < 17:
            return "Good Afternoon"
        else:
            return "Good Evening"
    
    def _create_quick_actions(self) -> Gtk.Widget:
        """Create quick action buttons."""
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.set_homogeneous(True)
        
        # Quick log sleep
        sleep_btn = Gtk.Button()
        sleep_btn.add_css_class("pill")
        sleep_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        sleep_box.set_halign(Gtk.Align.CENTER)
        sleep_box.append(Gtk.Image.new_from_icon_name("weather-clear-night-symbolic"))
        sleep_box.append(Gtk.Label(label="Log Sleep"))
        sleep_btn.set_child(sleep_box)
        sleep_btn.connect("clicked", lambda b: self.main_window.navigate_to('sleep'))
        box.append(sleep_btn)
        
        # Quick mood check
        mood_btn = Gtk.Button()
        mood_btn.add_css_class("pill")
        mood_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        mood_box.set_halign(Gtk.Align.CENTER)
        mood_box.append(Gtk.Image.new_from_icon_name("face-smile-symbolic"))
        mood_box.append(Gtk.Label(label="Mood Check"))
        mood_btn.set_child(mood_box)
        mood_btn.connect("clicked", self._show_quick_mood_dialog)
        box.append(mood_btn)
        
        # Quick workout
        workout_btn = Gtk.Button()
        workout_btn.add_css_class("pill")
        workout_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        workout_box.set_halign(Gtk.Align.CENTER)
        workout_box.append(Gtk.Image.new_from_icon_name("emblem-favorite-symbolic"))
        workout_box.append(Gtk.Label(label="Log Workout"))
        workout_btn.set_child(workout_box)
        workout_btn.connect("clicked", lambda b: self.main_window.navigate_to('fitness'))
        box.append(workout_btn)
        
        return box
    
    def _add_module_cards(self):
        """Add all module cards to the grid."""
        modules = [
            {
                'name': 'Sleep & Mind',
                'icon': 'weather-clear-night-symbolic',
                'description': 'Track sleep patterns and mental wellness',
                'view': 'sleep',
                'color': 'blue'
            },
            {
                'name': 'Fitness',
                'icon': 'emblem-favorite-symbolic',
                'description': 'Log workouts and physical activity',
                'view': 'fitness',
                'color': 'green'
            },
            {
                'name': 'Recovery',
                'icon': 'emblem-ok-symbolic',
                'description': 'Addiction recovery support',
                'view': 'recovery',
                'color': 'purple'
            },
            {
                'name': 'Medications',
                'icon': 'accessories-calculator-symbolic',
                'description': 'Track meds and appointments',
                'view': 'medication',
                'color': 'orange'
            },
            {
                'name': 'Relationships',
                'icon': 'system-users-symbolic',
                'description': 'Understand interpersonal patterns',
                'view': 'relationships',
                'color': 'pink'
            },
            {
                'name': 'Goals',
                'icon': 'starred-symbolic',
                'description': 'Long-term goal tracking',
                'view': 'goals',
                'color': 'yellow'
            },
            {
                'name': 'Insights',
                'icon': 'org.gnome.Settings-symbolic',
                'description': 'Lifestyle analytics',
                'view': 'insights',
                'color': 'teal'
            },
            {
                'name': 'Digestive',
                'icon': 'view-list-symbolic',
                'description': 'Private digestive health',
                'view': 'bowel',
                'color': 'brown'
            },
        ]
        
        for module in modules:
            card = self._create_module_card(module)
            self.modules_grid.append(card)
    
    def _create_module_card(self, module: dict) -> Gtk.Widget:
        """Create a single module card."""
        # Card button
        button = Gtk.Button()
        button.add_css_class("card")
        button.add_css_class("module-card")
        button.set_size_request(180, 140)
        button.connect("clicked", lambda b: self.main_window.navigate_to(module['view']))
        
        # Card content
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_valign(Gtk.Align.CENTER)
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        box.set_margin_start(16)
        box.set_margin_end(16)
        button.set_child(box)
        
        # Icon
        icon = Gtk.Image.new_from_icon_name(module['icon'])
        icon.set_pixel_size(32)
        icon.add_css_class("accent")
        box.append(icon)
        
        # Name
        name = Gtk.Label(label=module['name'])
        name.add_css_class("heading")
        box.append(name)
        
        # Description
        desc = Gtk.Label(label=module['description'])
        desc.add_css_class("dim-label")
        desc.add_css_class("caption")
        desc.set_wrap(True)
        desc.set_justify(Gtk.Justification.CENTER)
        box.append(desc)
        
        return button
    
    def _create_today_summary(self) -> Gtk.Widget:
        """Create today's summary section."""
        list_box = Gtk.ListBox()
        list_box.add_css_class("boxed-list")
        list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        
        # Check if there's sleep data for today
        today = date.today().isoformat()
        sleep_entry = self.db.get_sleep_entry(today) if self.db.conn else None
        
        # Sleep row
        sleep_row = Adw.ActionRow()
        sleep_row.set_title("Sleep")
        sleep_row.set_icon_name("weather-clear-night-symbolic")
        if sleep_entry:
            sleep_row.set_subtitle(f"Quality: {sleep_entry.get('sleep_quality', '-')}/10")
        else:
            sleep_row.set_subtitle("Not logged today")
            sleep_row.add_css_class("warning")
        list_box.append(sleep_row)
        
        # Mood row
        mood_row = Adw.ActionRow()
        mood_row.set_title("Mood")
        mood_row.set_icon_name("face-smile-symbolic")
        if sleep_entry and sleep_entry.get('daily_mood'):
            mood_row.set_subtitle(f"{sleep_entry.get('daily_mood')}/10")
        else:
            mood_row.set_subtitle("Check in anytime")
        list_box.append(mood_row)
        
        # Fitness row
        fitness_summary = self.db.get_fitness_summary(1) if self.db.conn else {}
        fitness_row = Adw.ActionRow()
        fitness_row.set_title("Fitness")
        fitness_row.set_icon_name("emblem-favorite-symbolic")
        if fitness_summary.get('total_workouts', 0) > 0:
            fitness_row.set_subtitle(f"{fitness_summary['total_minutes']} min today")
        else:
            fitness_row.set_subtitle("No workout logged today")
        list_box.append(fitness_row)
        
        # Medications row
        meds = self.db.get_medications() if self.db.conn else []
        meds_row = Adw.ActionRow()
        meds_row.set_title("Medications")
        meds_row.set_icon_name("accessories-calculator-symbolic")
        meds_row.set_subtitle(f"{len(meds)} active medications")
        list_box.append(meds_row)
        
        return list_box
    
    def _show_quick_mood_dialog(self, button):
        """Show quick mood check-in dialog."""
        dialog = Adw.Dialog()
        dialog.set_title("Mood Check-in")
        dialog.set_content_width(350)
        dialog.set_content_height(400)
        
        # Toolbar view for the dialog
        toolbar_view = Adw.ToolbarView()
        dialog.set_child(toolbar_view)
        
        # Header
        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(False)
        header.set_show_start_title_buttons(False)
        
        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", lambda b: dialog.close())
        header.pack_start(cancel_btn)
        
        save_btn = Gtk.Button(label="Save")
        save_btn.add_css_class("suggested-action")
        header.pack_end(save_btn)
        
        toolbar_view.add_top_bar(header)
        
        # Content
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_margin_top(24)
        content.set_margin_bottom(24)
        content.set_margin_start(24)
        content.set_margin_end(24)
        toolbar_view.set_content(content)
        
        # Mood slider
        mood_label = Gtk.Label(label="How are you feeling?")
        mood_label.add_css_class("heading")
        content.append(mood_label)
        
        mood_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, 10, 1)
        mood_scale.set_value(5)
        mood_scale.set_draw_value(True)
        content.append(mood_scale)
        
        # Energy slider
        energy_label = Gtk.Label(label="Energy level?")
        energy_label.add_css_class("heading")
        energy_label.set_margin_top(16)
        content.append(energy_label)
        
        energy_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, 10, 1)
        energy_scale.set_value(5)
        energy_scale.set_draw_value(True)
        content.append(energy_scale)
        
        # Notes
        notes_label = Gtk.Label(label="Notes (optional)")
        notes_label.add_css_class("heading")
        notes_label.set_margin_top(16)
        content.append(notes_label)
        
        notes_entry = Gtk.Entry()
        notes_entry.set_placeholder_text("How are things going?")
        content.append(notes_entry)
        
        def on_save(btn):
            self.db.save_mood_checkin({
                'mood_level': int(mood_scale.get_value()),
                'energy_level': int(energy_scale.get_value()),
                'notes': notes_entry.get_text()
            })
            dialog.close()
            # Show a toast
            toast = Adw.Toast.new("Mood check-in saved!")
            self.main_window.add_toast(toast)
        
        save_btn.connect("clicked", on_save)
        
        dialog.present(self.main_window)
