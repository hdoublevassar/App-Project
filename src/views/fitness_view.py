"""
Fitness Tracker View
Track workouts, physical activity, and exercise trends.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw
from datetime import date, datetime, timedelta


class FitnessView(Adw.NavigationPage):
    """Fitness tracking view."""
    
    WORKOUT_TYPES = [
        "Running", "Walking", "Cycling", "Swimming", "Weightlifting",
        "Yoga", "HIIT", "Pilates", "Sports", "Dancing", "Other"
    ]
    
    def __init__(self, main_window):
        super().__init__(title="Fitness Tracker")
        self.main_window = main_window
        self.db = main_window.db
        
        # Main container
        toolbar_view = Adw.ToolbarView()
        self.set_child(toolbar_view)
        
        # Header with add button
        header = Adw.HeaderBar()
        
        add_btn = Gtk.Button(icon_name="list-add-symbolic")
        add_btn.set_tooltip_text("Log Workout")
        add_btn.connect("clicked", self._show_add_workout_dialog)
        header.pack_end(add_btn)
        
        toolbar_view.add_top_bar(header)
        
        # Scrollable content
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
        
        # Weekly summary card
        summary_group = Adw.PreferencesGroup()
        summary_group.set_title("This Week")
        content.append(summary_group)
        
        self.summary_row = Adw.ActionRow()
        self.summary_row.set_title("Workouts")
        self.summary_row.set_icon_name("emblem-favorite-symbolic")
        summary_group.add(self.summary_row)
        
        self.time_row = Adw.ActionRow()
        self.time_row.set_title("Total Time")
        self.time_row.set_icon_name("alarm-symbolic")
        summary_group.add(self.time_row)
        
        self.intensity_row = Adw.ActionRow()
        self.intensity_row.set_title("Avg Intensity")
        self.intensity_row.set_icon_name("battery-full-symbolic")
        summary_group.add(self.intensity_row)
        
        # Goals section
        goals_group = Adw.PreferencesGroup()
        goals_group.set_title("Weekly Goals")
        content.append(goals_group)
        
        self.goal_progress_row = Adw.ActionRow()
        self.goal_progress_row.set_title("Workout Goal")
        self.goal_progress_row.set_subtitle("Set a goal to track progress")
        goals_group.add(self.goal_progress_row)
        
        # Recent workouts
        workouts_label = Gtk.Label(label="Recent Workouts")
        workouts_label.add_css_class("title-4")
        workouts_label.set_halign(Gtk.Align.START)
        content.append(workouts_label)
        
        self.workouts_list = Gtk.ListBox()
        self.workouts_list.add_css_class("boxed-list")
        self.workouts_list.set_selection_mode(Gtk.SelectionMode.NONE)
        content.append(self.workouts_list)
        
        # Recommendations
        rec_group = Adw.PreferencesGroup()
        rec_group.set_title("Recommendations")
        content.append(rec_group)
        
        self.recommendation_label = Gtk.Label()
        self.recommendation_label.set_wrap(True)
        self.recommendation_label.add_css_class("dim-label")
        rec_group.add(self.recommendation_label)
        
        # Load data
        self._refresh_data()
    
    def _refresh_data(self):
        """Refresh all fitness data."""
        # Get weekly summary
        summary = self.db.get_fitness_summary(7) if self.db.conn else {}
        
        workouts = summary.get('total_workouts', 0) or 0
        minutes = summary.get('total_minutes', 0) or 0
        intensity = summary.get('avg_intensity', 0) or 0
        
        self.summary_row.set_subtitle(f"{workouts} workouts")
        self.time_row.set_subtitle(f"{minutes} minutes")
        self.intensity_row.set_subtitle(f"{intensity:.1f}/10" if intensity else "—")
        
        # Update recommendations
        if workouts == 0:
            self.recommendation_label.set_label(
                "Start your week strong! Any movement counts. "
                "Even a 10-minute walk makes a difference."
            )
        elif workouts < 3:
            self.recommendation_label.set_label(
                f"Great start with {workouts} workout(s)! "
                "Aim for 3-4 sessions per week for optimal health benefits."
            )
        else:
            self.recommendation_label.set_label(
                f"Excellent! You've logged {workouts} workouts this week. "
                "Keep up the great momentum! 💪"
            )
        
        # Load recent workouts
        self._load_workouts()
    
    def _load_workouts(self):
        """Load recent workout entries."""
        while child := self.workouts_list.get_first_child():
            self.workouts_list.remove(child)
        
        entries = self.db.get_fitness_entries(14) if self.db.conn else []
        
        if not entries:
            empty_row = Adw.ActionRow()
            empty_row.set_title("No workouts logged yet")
            empty_row.set_subtitle("Tap + to log your first workout")
            self.workouts_list.append(empty_row)
            return
        
        for entry in entries:
            row = Adw.ActionRow()
            
            entry_date = datetime.strptime(entry['entry_date'], "%Y-%m-%d")
            row.set_title(f"{entry['workout_type']} - {entry_date.strftime('%b %d')}")
            
            duration = entry.get('duration_minutes', 0) or 0
            intensity = entry.get('intensity', 0) or 0
            row.set_subtitle(f"{duration} min • Intensity: {intensity}/10")
            
            row.set_icon_name("emblem-favorite-symbolic")
            
            self.workouts_list.append(row)
    
    def _show_add_workout_dialog(self, button):
        """Show dialog to add a new workout."""
        dialog = Adw.Dialog()
        dialog.set_title("Log Workout")
        dialog.set_content_width(400)
        dialog.set_content_height(500)
        
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
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        toolbar_view.set_content(scroll)
        
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_margin_top(24)
        content.set_margin_bottom(24)
        content.set_margin_start(24)
        content.set_margin_end(24)
        scroll.set_child(content)
        
        # Workout type
        type_group = Adw.PreferencesGroup()
        type_group.set_title("Workout Type")
        content.append(type_group)
        
        type_combo = Adw.ComboRow()
        type_combo.set_title("Type")
        type_list = Gtk.StringList.new(self.WORKOUT_TYPES)
        type_combo.set_model(type_list)
        type_group.add(type_combo)
        
        # Duration
        duration_row = Adw.SpinRow.new_with_range(1, 300, 5)
        duration_row.set_title("Duration (minutes)")
        duration_row.set_value(30)
        type_group.add(duration_row)
        
        # Intensity
        details_group = Adw.PreferencesGroup()
        details_group.set_title("Details")
        content.append(details_group)
        
        intensity_row = Adw.ActionRow()
        intensity_row.set_title("Intensity")
        
        intensity_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, 10, 1)
        intensity_scale.set_value(5)
        intensity_scale.set_draw_value(True)
        intensity_scale.set_size_request(200, -1)
        intensity_scale.set_valign(Gtk.Align.CENTER)
        intensity_row.add_suffix(intensity_scale)
        details_group.add(intensity_row)
        
        # Calories (optional)
        calories_row = Adw.SpinRow.new_with_range(0, 2000, 10)
        calories_row.set_title("Calories (optional)")
        calories_row.set_value(0)
        details_group.add(calories_row)
        
        # Notes
        notes_row = Adw.EntryRow()
        notes_row.set_title("Notes")
        details_group.add(notes_row)
        
        def on_save(btn):
            workout_type = self.WORKOUT_TYPES[type_combo.get_selected()]
            
            data = {
                'entry_date': date.today().isoformat(),
                'workout_type': workout_type,
                'duration_minutes': int(duration_row.get_value()),
                'intensity': int(intensity_scale.get_value()),
                'calories_burned': int(calories_row.get_value()) if calories_row.get_value() > 0 else None,
                'notes': notes_row.get_text()
            }
            
            self.db.save_fitness_entry(data)
            dialog.close()
            self._refresh_data()
            
            toast = Adw.Toast.new("Workout logged! 💪")
            if hasattr(self.main_window, 'add_toast'):
                self.main_window.add_toast(toast)
        
        save_btn.connect("clicked", on_save)
        
        dialog.present(self.main_window)
