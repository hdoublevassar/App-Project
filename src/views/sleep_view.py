"""
Sleep & Mental Health View
Track sleep patterns, mood, and energy levels.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw
from datetime import date, datetime, timedelta


class SleepView(Adw.NavigationPage):
    """Sleep and mental health tracking view."""
    
    def __init__(self, main_window):
        super().__init__(title="Sleep & Mind")
        self.main_window = main_window
        self.db = main_window.db
        self.selected_date = date.today().isoformat()
        
        # Main container
        toolbar_view = Adw.ToolbarView()
        self.set_child(toolbar_view)
        
        # Header
        header = Adw.HeaderBar()
        toolbar_view.add_top_bar(header)
        
        # Scrollable content
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        toolbar_view.set_content(scroll)
        
        # Clamp for content width
        clamp = Adw.Clamp()
        clamp.set_maximum_size(600)
        clamp.set_margin_top(24)
        clamp.set_margin_bottom(24)
        clamp.set_margin_start(24)
        clamp.set_margin_end(24)
        scroll.set_child(clamp)
        
        # Main content
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        clamp.set_child(content)
        
        # View switcher (Log / History / Insights)
        view_switcher = self._create_view_switcher()
        content.append(view_switcher)
        
        # Stack for different views
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        content.append(self.stack)
        
        # Add views to stack
        self.stack.add_titled(self._create_log_view(), "log", "Log Entry")
        self.stack.add_titled(self._create_history_view(), "history", "History")
        self.stack.add_titled(self._create_insights_view(), "insights", "Insights")
        
        # Load existing data for today
        self._load_entry_data()
    
    def _create_view_switcher(self) -> Gtk.Widget:
        """Create view switcher buttons."""
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        box.add_css_class("linked")
        box.set_halign(Gtk.Align.CENTER)
        
        self.log_btn = Gtk.ToggleButton(label="Log Entry")
        self.log_btn.set_active(True)
        self.log_btn.connect("toggled", lambda b: self._switch_view("log") if b.get_active() else None)
        box.append(self.log_btn)
        
        self.history_btn = Gtk.ToggleButton(label="History")
        self.history_btn.connect("toggled", lambda b: self._switch_view("history") if b.get_active() else None)
        box.append(self.history_btn)
        
        self.insights_btn = Gtk.ToggleButton(label="Insights")
        self.insights_btn.connect("toggled", lambda b: self._switch_view("insights") if b.get_active() else None)
        box.append(self.insights_btn)
        
        return box
    
    def _switch_view(self, view_name: str):
        """Switch to the specified view."""
        self.stack.set_visible_child_name(view_name)
        
        # Update toggle states
        self.log_btn.set_active(view_name == "log")
        self.history_btn.set_active(view_name == "history")
        self.insights_btn.set_active(view_name == "insights")
        
        # Refresh data when switching
        if view_name == "history":
            self._refresh_history()
        elif view_name == "insights":
            self._refresh_insights()
    
    def _create_log_view(self) -> Gtk.Widget:
        """Create the sleep entry logging view."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        
        # Date selector
        date_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        date_box.set_halign(Gtk.Align.CENTER)
        
        prev_btn = Gtk.Button(icon_name="go-previous-symbolic")
        prev_btn.connect("clicked", self._prev_date)
        date_box.append(prev_btn)
        
        self.date_label = Gtk.Label(label=date.today().strftime("%A, %B %d"))
        self.date_label.add_css_class("title-3")
        date_box.append(self.date_label)
        
        next_btn = Gtk.Button(icon_name="go-next-symbolic")
        next_btn.connect("clicked", self._next_date)
        date_box.append(next_btn)
        
        box.append(date_box)
        
        # Sleep times section
        times_group = Adw.PreferencesGroup()
        times_group.set_title("Sleep Times")
        box.append(times_group)
        
        # Bed time
        self.bed_time_row = Adw.EntryRow()
        self.bed_time_row.set_title("Bedtime")
        self.bed_time_row.set_text("")
        self.bed_time_row.set_input_hints(Gtk.InputHints.NO_SPELLCHECK)
        times_group.add(self.bed_time_row)
        
        # Wake time
        self.wake_time_row = Adw.EntryRow()
        self.wake_time_row.set_title("Wake Time")
        self.wake_time_row.set_text("")
        times_group.add(self.wake_time_row)
        
        # Quality & Mood section
        ratings_group = Adw.PreferencesGroup()
        ratings_group.set_title("How Did You Feel?")
        box.append(ratings_group)
        
        # Sleep quality slider
        self.sleep_quality_row = self._create_slider_row("Sleep Quality", 1, 10)
        ratings_group.add(self.sleep_quality_row)
        
        # Wake mood slider
        self.wake_mood_row = self._create_slider_row("Mood When Waking", 1, 10)
        ratings_group.add(self.wake_mood_row)
        
        # Wake energy slider
        self.wake_energy_row = self._create_slider_row("Energy When Waking", 1, 10)
        ratings_group.add(self.wake_energy_row)
        
        # Daily mood slider
        self.daily_mood_row = self._create_slider_row("Overall Daily Mood", 1, 10)
        ratings_group.add(self.daily_mood_row)
        
        # Daily energy slider
        self.daily_energy_row = self._create_slider_row("Overall Daily Energy", 1, 10)
        ratings_group.add(self.daily_energy_row)
        
        # Sleep aids section
        aids_group = Adw.PreferencesGroup()
        aids_group.set_title("Sleep Aids Used")
        box.append(aids_group)
        
        self.aid_melatonin = Adw.SwitchRow()
        self.aid_melatonin.set_title("Melatonin")
        aids_group.add(self.aid_melatonin)
        
        self.aid_weed = Adw.SwitchRow()
        self.aid_weed.set_title("Cannabis")
        aids_group.add(self.aid_weed)
        
        self.aid_benadryl = Adw.SwitchRow()
        self.aid_benadryl.set_title("Benadryl")
        aids_group.add(self.aid_benadryl)
        
        self.aid_cough_meds = Adw.SwitchRow()
        self.aid_cough_meds.set_title("Cough Medicine")
        aids_group.add(self.aid_cough_meds)
        
        self.aid_other_row = Adw.EntryRow()
        self.aid_other_row.set_title("Other")
        aids_group.add(self.aid_other_row)
        
        # Notes section
        notes_group = Adw.PreferencesGroup()
        notes_group.set_title("Notes")
        box.append(notes_group)
        
        self.notes_row = Adw.EntryRow()
        self.notes_row.set_title("Additional notes")
        notes_group.add(self.notes_row)
        
        # Save button
        save_btn = Gtk.Button(label="Save Entry")
        save_btn.add_css_class("suggested-action")
        save_btn.add_css_class("pill")
        save_btn.set_halign(Gtk.Align.CENTER)
        save_btn.set_margin_top(16)
        save_btn.connect("clicked", self._save_entry)
        box.append(save_btn)
        
        return box
    
    def _create_slider_row(self, title: str, min_val: int, max_val: int) -> Adw.ActionRow:
        """Create a row with a slider."""
        row = Adw.ActionRow()
        row.set_title(title)
        
        scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, min_val, max_val, 1)
        scale.set_value((min_val + max_val) / 2)
        scale.set_draw_value(True)
        scale.set_size_request(200, -1)
        scale.set_valign(Gtk.Align.CENTER)
        row.add_suffix(scale)
        
        # Store reference to scale on the row
        row.scale = scale
        
        return row
    
    def _create_history_view(self) -> Gtk.Widget:
        """Create the history view."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        
        title = Gtk.Label(label="Recent Sleep Entries")
        title.add_css_class("title-4")
        title.set_halign(Gtk.Align.START)
        box.append(title)
        
        # History list
        self.history_list = Gtk.ListBox()
        self.history_list.add_css_class("boxed-list")
        self.history_list.set_selection_mode(Gtk.SelectionMode.NONE)
        box.append(self.history_list)
        
        return box
    
    def _create_insights_view(self) -> Gtk.Widget:
        """Create the insights view."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        
        # Optimal sleep recommendation
        rec_group = Adw.PreferencesGroup()
        rec_group.set_title("Sleep Recommendations")
        box.append(rec_group)
        
        self.recommendation_row = Adw.ActionRow()
        self.recommendation_row.set_title("Optimal Bedtime")
        self.recommendation_row.set_subtitle("Gathering data...")
        self.recommendation_row.set_icon_name("weather-clear-night-symbolic")
        rec_group.add(self.recommendation_row)
        
        # Statistics
        stats_group = Adw.PreferencesGroup()
        stats_group.set_title("7-Day Averages")
        box.append(stats_group)
        
        self.avg_quality_row = Adw.ActionRow()
        self.avg_quality_row.set_title("Sleep Quality")
        self.avg_quality_row.set_icon_name("starred-symbolic")
        stats_group.add(self.avg_quality_row)
        
        self.avg_mood_row = Adw.ActionRow()
        self.avg_mood_row.set_title("Daily Mood")
        self.avg_mood_row.set_icon_name("face-smile-symbolic")
        stats_group.add(self.avg_mood_row)
        
        self.avg_energy_row = Adw.ActionRow()
        self.avg_energy_row.set_title("Daily Energy")
        self.avg_energy_row.set_icon_name("battery-full-symbolic")
        stats_group.add(self.avg_energy_row)
        
        # Sleep aid analysis
        aids_group = Adw.PreferencesGroup()
        aids_group.set_title("Sleep Aid Impact")
        aids_group.set_description("How different aids affect your sleep quality")
        box.append(aids_group)
        
        self.aids_analysis_label = Gtk.Label()
        self.aids_analysis_label.set_wrap(True)
        self.aids_analysis_label.add_css_class("dim-label")
        aids_group.add(self.aids_analysis_label)
        
        return box
    
    def _prev_date(self, button):
        """Go to previous date."""
        current = datetime.strptime(self.selected_date, "%Y-%m-%d").date()
        new_date = current - timedelta(days=1)
        self.selected_date = new_date.isoformat()
        self.date_label.set_label(new_date.strftime("%A, %B %d"))
        self._load_entry_data()
    
    def _next_date(self, button):
        """Go to next date."""
        current = datetime.strptime(self.selected_date, "%Y-%m-%d").date()
        if current >= date.today():
            return  # Don't go past today
        new_date = current + timedelta(days=1)
        self.selected_date = new_date.isoformat()
        self.date_label.set_label(new_date.strftime("%A, %B %d"))
        self._load_entry_data()
    
    def _load_entry_data(self):
        """Load entry data for selected date."""
        entry = self.db.get_sleep_entry(self.selected_date) if self.db.conn else None
        
        if entry:
            self.bed_time_row.set_text(entry.get('bed_time', '') or '')
            self.wake_time_row.set_text(entry.get('wake_time', '') or '')
            self.sleep_quality_row.scale.set_value(entry.get('sleep_quality', 5) or 5)
            self.wake_mood_row.scale.set_value(entry.get('wake_mood', 5) or 5)
            self.wake_energy_row.scale.set_value(entry.get('wake_energy', 5) or 5)
            self.daily_mood_row.scale.set_value(entry.get('daily_mood', 5) or 5)
            self.daily_energy_row.scale.set_value(entry.get('daily_energy', 5) or 5)
            self.aid_melatonin.set_active(bool(entry.get('aid_melatonin', 0)))
            self.aid_weed.set_active(bool(entry.get('aid_weed', 0)))
            self.aid_benadryl.set_active(bool(entry.get('aid_benadryl', 0)))
            self.aid_cough_meds.set_active(bool(entry.get('aid_cough_meds', 0)))
            self.aid_other_row.set_text(entry.get('aid_other', '') or '')
            self.notes_row.set_text(entry.get('notes', '') or '')
        else:
            # Reset to defaults
            self.bed_time_row.set_text('')
            self.wake_time_row.set_text('')
            self.sleep_quality_row.scale.set_value(5)
            self.wake_mood_row.scale.set_value(5)
            self.wake_energy_row.scale.set_value(5)
            self.daily_mood_row.scale.set_value(5)
            self.daily_energy_row.scale.set_value(5)
            self.aid_melatonin.set_active(False)
            self.aid_weed.set_active(False)
            self.aid_benadryl.set_active(False)
            self.aid_cough_meds.set_active(False)
            self.aid_other_row.set_text('')
            self.notes_row.set_text('')
    
    def _save_entry(self, button):
        """Save the current entry."""
        data = {
            'entry_date': self.selected_date,
            'bed_time': self.bed_time_row.get_text(),
            'wake_time': self.wake_time_row.get_text(),
            'sleep_quality': int(self.sleep_quality_row.scale.get_value()),
            'wake_mood': int(self.wake_mood_row.scale.get_value()),
            'wake_energy': int(self.wake_energy_row.scale.get_value()),
            'daily_mood': int(self.daily_mood_row.scale.get_value()),
            'daily_energy': int(self.daily_energy_row.scale.get_value()),
            'aid_melatonin': self.aid_melatonin.get_active(),
            'aid_weed': self.aid_weed.get_active(),
            'aid_benadryl': self.aid_benadryl.get_active(),
            'aid_cough_meds': self.aid_cough_meds.get_active(),
            'aid_other': self.aid_other_row.get_text(),
            'notes': self.notes_row.get_text(),
        }
        
        self.db.save_sleep_entry(data)
        
        # Show confirmation
        toast = Adw.Toast.new("Sleep entry saved!")
        if hasattr(self.main_window, 'add_toast'):
            self.main_window.add_toast(toast)
    
    def _refresh_history(self):
        """Refresh the history list."""
        # Clear existing items
        while child := self.history_list.get_first_child():
            self.history_list.remove(child)
        
        entries = self.db.get_sleep_entries(30) if self.db.conn else []
        
        for entry in entries:
            row = Adw.ActionRow()
            entry_date = datetime.strptime(entry['entry_date'], "%Y-%m-%d")
            row.set_title(entry_date.strftime("%A, %B %d"))
            
            quality = entry.get('sleep_quality', '-')
            mood = entry.get('daily_mood', '-')
            row.set_subtitle(f"Quality: {quality}/10 • Mood: {mood}/10")
            
            # Edit button
            edit_btn = Gtk.Button(icon_name="document-edit-symbolic")
            edit_btn.set_valign(Gtk.Align.CENTER)
            edit_btn.add_css_class("flat")
            edit_btn.connect("clicked", lambda b, d=entry['entry_date']: self._edit_entry(d))
            row.add_suffix(edit_btn)
            
            self.history_list.append(row)
    
    def _edit_entry(self, entry_date: str):
        """Switch to log view and load entry for editing."""
        self.selected_date = entry_date
        entry_dt = datetime.strptime(entry_date, "%Y-%m-%d")
        self.date_label.set_label(entry_dt.strftime("%A, %B %d"))
        self._load_entry_data()
        self._switch_view("log")
    
    def _refresh_insights(self):
        """Refresh the insights view."""
        entries = self.db.get_sleep_entries(7) if self.db.conn else []
        
        if not entries:
            self.recommendation_row.set_subtitle("Log at least 5 days of sleep for recommendations")
            return
        
        # Calculate averages
        qualities = [e['sleep_quality'] for e in entries if e.get('sleep_quality')]
        moods = [e['daily_mood'] for e in entries if e.get('daily_mood')]
        energies = [e['daily_energy'] for e in entries if e.get('daily_energy')]
        
        if qualities:
            avg_quality = sum(qualities) / len(qualities)
            self.avg_quality_row.set_subtitle(f"{avg_quality:.1f}/10")
        
        if moods:
            avg_mood = sum(moods) / len(moods)
            self.avg_mood_row.set_subtitle(f"{avg_mood:.1f}/10")
        
        if energies:
            avg_energy = sum(energies) / len(energies)
            self.avg_energy_row.set_subtitle(f"{avg_energy:.1f}/10")
        
        # Get optimal sleep recommendation
        rec = self.db.get_optimal_sleep_recommendation() if self.db.conn else {}
        if rec.get('has_recommendation'):
            self.recommendation_row.set_subtitle(
                f"Bed: {rec['recommended_bedtime']} • Wake: {rec['recommended_waketime']}"
            )
        
        # Analyze sleep aid impact
        self._analyze_aids(entries)
    
    def _analyze_aids(self, entries):
        """Analyze the impact of sleep aids."""
        aid_analysis = []
        
        # Group by aid type
        melatonin_nights = [e for e in entries if e.get('aid_melatonin')]
        no_aid_nights = [e for e in entries if not any([
            e.get('aid_melatonin'), e.get('aid_weed'), 
            e.get('aid_benadryl'), e.get('aid_cough_meds')
        ])]
        
        if melatonin_nights and no_aid_nights:
            mel_avg = sum(e['sleep_quality'] for e in melatonin_nights if e.get('sleep_quality')) / len(melatonin_nights)
            no_avg = sum(e['sleep_quality'] for e in no_aid_nights if e.get('sleep_quality')) / len(no_aid_nights)
            
            if mel_avg > no_avg:
                aid_analysis.append(f"Melatonin nights: {mel_avg:.1f}/10 avg quality (+{mel_avg-no_avg:.1f} vs no aids)")
            else:
                aid_analysis.append(f"Melatonin nights: {mel_avg:.1f}/10 avg quality")
        
        if aid_analysis:
            self.aids_analysis_label.set_label("\n".join(aid_analysis))
        else:
            self.aids_analysis_label.set_label("Not enough data to analyze sleep aid impact yet.")
