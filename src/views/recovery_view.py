"""
Addiction Recovery View
Track recovery progress, milestones, and get support.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw
from datetime import date, datetime, timedelta


class RecoveryView(Adw.NavigationPage):
    """Addiction recovery tracking view."""
    
    ADDICTION_TYPES = [
        "Alcohol", "Nicotine", "Cannabis", "Cocaine", "Opioids/Heroin",
        "Prescription Drugs", "Gambling", "Pornography", "Social Media",
        "Gaming", "Shopping", "Other"
    ]
    
    ENCOURAGEMENT_MESSAGES = [
        "Every day clean is a victory. You're stronger than you know. 💪",
        "Recovery isn't linear, but every step forward counts.",
        "You're doing incredible work. Be proud of yourself.",
        "One day at a time. You've got this.",
        "Your strength and courage inspire others, even when you don't see it.",
        "Recovery is proof that change is possible. Keep going.",
        "The hardest battles are fought by the strongest people.",
        "You're not alone in this journey. Support is always available.",
    ]
    
    RESOURCES = {
        "Alcohol": [
            ("Alcoholics Anonymous", "aa.org"),
            ("SAMHSA Helpline", "1-800-662-4357"),
        ],
        "Gambling": [
            ("Gamblers Anonymous", "gamblersanonymous.org"),
            ("National Council on Problem Gambling", "1-800-522-4700"),
        ],
        "default": [
            ("SAMHSA National Helpline", "1-800-662-4357"),
            ("Crisis Text Line", "Text HOME to 741741"),
        ]
    }
    
    def __init__(self, main_window):
        super().__init__(title="Recovery Tracker")
        self.main_window = main_window
        self.db = main_window.db
        
        # Main container
        toolbar_view = Adw.ToolbarView()
        self.set_child(toolbar_view)
        
        # Header
        header = Adw.HeaderBar()
        
        add_btn = Gtk.Button(icon_name="list-add-symbolic")
        add_btn.set_tooltip_text("Track New Recovery")
        add_btn.connect("clicked", self._show_add_addiction_dialog)
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
        
        # Encouragement banner
        self.encouragement_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.encouragement_box.add_css_class("card")
        self.encouragement_box.set_margin_bottom(8)
        content.append(self.encouragement_box)
        
        encouragement_icon = Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
        encouragement_icon.set_pixel_size(32)
        encouragement_icon.set_margin_top(16)
        self.encouragement_box.append(encouragement_icon)
        
        self.encouragement_label = Gtk.Label()
        self.encouragement_label.set_wrap(True)
        self.encouragement_label.set_justify(Gtk.Justification.CENTER)
        self.encouragement_label.add_css_class("title-4")
        self.encouragement_label.set_margin_start(16)
        self.encouragement_label.set_margin_end(16)
        self.encouragement_label.set_margin_bottom(16)
        self.encouragement_box.append(self.encouragement_label)
        
        # Active recoveries
        self.recoveries_group = Adw.PreferencesGroup()
        self.recoveries_group.set_title("Your Recovery Journey")
        content.append(self.recoveries_group)
        
        # Resources section
        resources_group = Adw.PreferencesGroup()
        resources_group.set_title("Support Resources")
        resources_group.set_description("You're never alone. Help is available 24/7.")
        content.append(resources_group)
        
        for name, contact in self.RESOURCES["default"]:
            row = Adw.ActionRow()
            row.set_title(name)
            row.set_subtitle(contact)
            row.set_icon_name("phone-symbolic")
            resources_group.add(row)
        
        # Load data
        self._refresh_data()
    
    def _refresh_data(self):
        """Refresh recovery data."""
        # Set random encouragement
        import random
        self.encouragement_label.set_label(
            random.choice(self.ENCOURAGEMENT_MESSAGES)
        )
        
        # Clear and reload addictions
        while child := self.recoveries_group.get_first_child():
            if isinstance(child, Adw.ActionRow) or isinstance(child, Adw.ExpanderRow):
                self.recoveries_group.remove(child)
        
        addictions = self.db.get_addictions() if self.db.conn else []
        
        if not addictions:
            empty_row = Adw.ActionRow()
            empty_row.set_title("No active recoveries")
            empty_row.set_subtitle("Tap + to start tracking your recovery journey")
            self.recoveries_group.add(empty_row)
            return
        
        for addiction in addictions:
            self._add_addiction_row(addiction)
    
    def _add_addiction_row(self, addiction: dict):
        """Add a row for an addiction."""
        clean_days = self.db.get_clean_days(addiction['id']) if self.db.conn else 0
        
        expander = Adw.ExpanderRow()
        expander.set_title(addiction.get('custom_name') or addiction['addiction_type'])
        expander.set_subtitle(f"🌟 {clean_days} days clean")
        expander.set_icon_name("emblem-ok-symbolic")
        
        # Check-in button row
        checkin_row = Adw.ActionRow()
        checkin_row.set_title("Daily Check-in")
        checkin_row.set_subtitle("Record how you're feeling today")
        
        checkin_btn = Gtk.Button(label="Check In")
        checkin_btn.set_valign(Gtk.Align.CENTER)
        checkin_btn.add_css_class("suggested-action")
        checkin_btn.connect("clicked", lambda b, a=addiction: self._show_checkin_dialog(a))
        checkin_row.add_suffix(checkin_btn)
        expander.add_row(checkin_row)
        
        # Milestones row
        milestones = self.db.get_upcoming_milestones(addiction['id']) if self.db.conn else []
        if milestones:
            next_milestone = milestones[0]
            days_until = next_milestone['milestone_days'] - clean_days
            
            milestone_row = Adw.ActionRow()
            milestone_row.set_title("Next Milestone")
            milestone_row.set_subtitle(f"{next_milestone['milestone_days']} days ({days_until} days away)")
            milestone_row.set_icon_name("starred-symbolic")
            expander.add_row(milestone_row)
        
        # Progress row
        progress_row = Adw.ActionRow()
        progress_row.set_title("Started")
        start_date = datetime.strptime(addiction['start_date'], "%Y-%m-%d")
        progress_row.set_subtitle(start_date.strftime("%B %d, %Y"))
        progress_row.set_icon_name("x-office-calendar-symbolic")
        expander.add_row(progress_row)
        
        self.recoveries_group.add(expander)
        
        # Celebrate milestones
        if clean_days in [1, 3, 7, 14, 30, 60, 90, 180, 365]:
            self._celebrate_milestone(addiction, clean_days)
    
    def _celebrate_milestone(self, addiction: dict, days: int):
        """Show celebration for reaching a milestone."""
        milestone_names = {
            1: "First Day",
            3: "Three Days",
            7: "One Week",
            14: "Two Weeks",
            30: "One Month",
            60: "Two Months",
            90: "Three Months",
            180: "Six Months",
            365: "One Year"
        }
        
        name = milestone_names.get(days, f"{days} Days")
        toast = Adw.Toast.new(f"🎉 Congratulations! {name} milestone reached!")
        toast.set_timeout(5)
        if hasattr(self.main_window, 'add_toast'):
            self.main_window.add_toast(toast)
    
    def _show_add_addiction_dialog(self, button):
        """Show dialog to add a new addiction to track."""
        dialog = Adw.Dialog()
        dialog.set_title("Start Recovery Tracking")
        dialog.set_content_width(400)
        dialog.set_content_height(400)
        
        toolbar_view = Adw.ToolbarView()
        dialog.set_child(toolbar_view)
        
        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(False)
        header.set_show_start_title_buttons(False)
        
        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", lambda b: dialog.close())
        header.pack_start(cancel_btn)
        
        save_btn = Gtk.Button(label="Start")
        save_btn.add_css_class("suggested-action")
        header.pack_end(save_btn)
        
        toolbar_view.add_top_bar(header)
        
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_margin_top(24)
        content.set_margin_bottom(24)
        content.set_margin_start(24)
        content.set_margin_end(24)
        toolbar_view.set_content(content)
        
        # Type selection
        type_group = Adw.PreferencesGroup()
        type_group.set_title("What are you recovering from?")
        content.append(type_group)
        
        type_combo = Adw.ComboRow()
        type_combo.set_title("Type")
        type_list = Gtk.StringList.new(self.ADDICTION_TYPES)
        type_combo.set_model(type_list)
        type_group.add(type_combo)
        
        custom_name_row = Adw.EntryRow()
        custom_name_row.set_title("Custom Name (optional)")
        type_group.add(custom_name_row)
        
        # Start date
        date_group = Adw.PreferencesGroup()
        date_group.set_title("When did you start?")
        content.append(date_group)
        
        date_row = Adw.EntryRow()
        date_row.set_title("Clean Since")
        date_row.set_text(date.today().isoformat())
        date_group.add(date_row)
        
        # Encouragement
        note = Gtk.Label(label="Starting recovery takes incredible courage. We're proud of you. 💚")
        note.set_wrap(True)
        note.add_css_class("dim-label")
        note.set_margin_top(16)
        content.append(note)
        
        def on_save(btn):
            addiction_type = self.ADDICTION_TYPES[type_combo.get_selected()]
            
            data = {
                'addiction_type': addiction_type,
                'custom_name': custom_name_row.get_text() or None,
                'start_date': date_row.get_text(),
            }
            
            self.db.add_addiction(data)
            dialog.close()
            self._refresh_data()
            
            toast = Adw.Toast.new("Recovery tracking started. You've got this! 💪")
            if hasattr(self.main_window, 'add_toast'):
                self.main_window.add_toast(toast)
        
        save_btn.connect("clicked", on_save)
        
        dialog.present(self.main_window)
    
    def _show_checkin_dialog(self, addiction: dict):
        """Show daily check-in dialog."""
        dialog = Adw.Dialog()
        dialog.set_title("Daily Check-in")
        dialog.set_content_width(400)
        dialog.set_content_height(550)
        
        toolbar_view = Adw.ToolbarView()
        dialog.set_child(toolbar_view)
        
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
        
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        toolbar_view.set_content(scroll)
        
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_margin_top(24)
        content.set_margin_bottom(24)
        content.set_margin_start(24)
        content.set_margin_end(24)
        scroll.set_child(content)
        
        # Clean status
        status_group = Adw.PreferencesGroup()
        content.append(status_group)
        
        clean_switch = Adw.SwitchRow()
        clean_switch.set_title("Stayed clean today")
        clean_switch.set_active(True)
        status_group.add(clean_switch)
        
        # Feelings
        feelings_group = Adw.PreferencesGroup()
        feelings_group.set_title("How are you feeling?")
        content.append(feelings_group)
        
        urge_row = Adw.ActionRow()
        urge_row.set_title("Urge Level")
        urge_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, 10, 1)
        urge_scale.set_value(3)
        urge_scale.set_draw_value(True)
        urge_scale.set_size_request(150, -1)
        urge_scale.set_valign(Gtk.Align.CENTER)
        urge_row.add_suffix(urge_scale)
        feelings_group.add(urge_row)
        
        mood_row = Adw.ActionRow()
        mood_row.set_title("Overall Mood")
        mood_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, 10, 1)
        mood_scale.set_value(5)
        mood_scale.set_draw_value(True)
        mood_scale.set_size_request(150, -1)
        mood_scale.set_valign(Gtk.Align.CENTER)
        mood_row.add_suffix(mood_scale)
        feelings_group.add(mood_row)
        
        # Triggers & Coping
        details_group = Adw.PreferencesGroup()
        details_group.set_title("Reflection")
        content.append(details_group)
        
        trigger_row = Adw.EntryRow()
        trigger_row.set_title("Triggers today")
        details_group.add(trigger_row)
        
        coping_row = Adw.EntryRow()
        coping_row.set_title("Coping strategies used")
        details_group.add(coping_row)
        
        notes_row = Adw.EntryRow()
        notes_row.set_title("Additional notes")
        details_group.add(notes_row)
        
        def on_save(btn):
            data = {
                'addiction_id': addiction['id'],
                'checkin_date': date.today().isoformat(),
                'stayed_clean': clean_switch.get_active(),
                'urge_level': int(urge_scale.get_value()),
                'mood': int(mood_scale.get_value()),
                'trigger': trigger_row.get_text(),
                'coping_strategy': coping_row.get_text(),
                'notes': notes_row.get_text()
            }
            
            self.db.save_recovery_checkin(data)
            dialog.close()
            self._refresh_data()
            
            if clean_switch.get_active():
                toast = Adw.Toast.new("Another day strong! Keep going! 💪")
            else:
                toast = Adw.Toast.new("Recovery isn't perfect. Tomorrow is a new day. 💚")
            
            if hasattr(self.main_window, 'add_toast'):
                self.main_window.add_toast(toast)
        
        save_btn.connect("clicked", on_save)
        
        dialog.present(self.main_window)
