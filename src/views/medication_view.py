"""
Medication & Appointments View
Track medications and upcoming appointments.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw
from datetime import date, datetime, timedelta


class MedicationView(Adw.NavigationPage):
    """Medication and appointment tracking view."""
    
    FREQUENCIES = [
        "Once daily", "Twice daily", "Three times daily",
        "Every morning", "Every evening", "Every night",
        "As needed", "Weekly", "Other"
    ]
    
    def __init__(self, main_window):
        super().__init__(title="Medications & Appointments")
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
        
        # View switcher
        view_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        view_box.add_css_class("linked")
        view_box.set_halign(Gtk.Align.CENTER)
        content.append(view_box)
        
        self.meds_btn = Gtk.ToggleButton(label="Medications")
        self.meds_btn.set_active(True)
        self.meds_btn.connect("toggled", lambda b: self._switch_view("meds") if b.get_active() else None)
        view_box.append(self.meds_btn)
        
        self.appts_btn = Gtk.ToggleButton(label="Appointments")
        self.appts_btn.connect("toggled", lambda b: self._switch_view("appts") if b.get_active() else None)
        view_box.append(self.appts_btn)
        
        # Stack for views
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        content.append(self.stack)
        
        self.stack.add_named(self._create_medications_view(), "meds")
        self.stack.add_named(self._create_appointments_view(), "appts")
        
        self._refresh_data()
    
    def _switch_view(self, view_name: str):
        """Switch between medications and appointments view."""
        self.stack.set_visible_child_name(view_name)
        self.meds_btn.set_active(view_name == "meds")
        self.appts_btn.set_active(view_name == "appts")
    
    def _create_medications_view(self) -> Gtk.Widget:
        """Create medications management view."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        
        # Add medication button
        add_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        add_box.set_halign(Gtk.Align.END)
        
        add_btn = Gtk.Button(label="Add Medication")
        add_btn.set_icon_name("list-add-symbolic")
        add_btn.connect("clicked", self._show_add_medication_dialog)
        add_box.append(add_btn)
        box.append(add_box)
        
        # Today's medications
        self.today_meds_group = Adw.PreferencesGroup()
        self.today_meds_group.set_title("Today's Medications")
        self.today_meds_group.set_description("Tap to mark as taken")
        box.append(self.today_meds_group)
        
        # All medications
        self.all_meds_group = Adw.PreferencesGroup()
        self.all_meds_group.set_title("All Medications")
        box.append(self.all_meds_group)
        
        return box
    
    def _create_appointments_view(self) -> Gtk.Widget:
        """Create appointments management view."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        
        # Add appointment button
        add_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        add_box.set_halign(Gtk.Align.END)
        
        add_btn = Gtk.Button(label="Add Appointment")
        add_btn.set_icon_name("list-add-symbolic")
        add_btn.connect("clicked", self._show_add_appointment_dialog)
        add_box.append(add_btn)
        box.append(add_box)
        
        # Upcoming appointments
        self.upcoming_group = Adw.PreferencesGroup()
        self.upcoming_group.set_title("Upcoming Appointments")
        box.append(self.upcoming_group)
        
        return box
    
    def _refresh_data(self):
        """Refresh medication and appointment data."""
        self._load_medications()
        self._load_appointments()
    
    def _load_medications(self):
        """Load medications list."""
        # Clear existing
        for group in [self.today_meds_group, self.all_meds_group]:
            while child := group.get_first_child():
                if isinstance(child, (Adw.ActionRow, Adw.SwitchRow)):
                    group.remove(child)
        
        meds = self.db.get_medications() if self.db.conn else []
        
        if not meds:
            empty_row = Adw.ActionRow()
            empty_row.set_title("No medications added")
            empty_row.set_subtitle("Tap 'Add Medication' to get started")
            self.all_meds_group.add(empty_row)
            return
        
        for med in meds:
            # Today's view - checkbox style
            today_row = Adw.SwitchRow()
            today_row.set_title(med['name'])
            today_row.set_subtitle(f"{med.get('dosage', '')} • {med.get('time_of_day', '')}")
            today_row.connect("notify::active", lambda r, p, m=med: self._on_med_taken(m, r.get_active()))
            self.today_meds_group.add(today_row)
            
            # All medications view
            all_row = Adw.ActionRow()
            all_row.set_title(med['name'])
            all_row.set_subtitle(f"{med.get('dosage', '')} • {med.get('frequency', '')}")
            all_row.set_icon_name("accessories-calculator-symbolic")
            self.all_meds_group.add(all_row)
    
    def _load_appointments(self):
        """Load upcoming appointments."""
        while child := self.upcoming_group.get_first_child():
            if isinstance(child, Adw.ActionRow):
                self.upcoming_group.remove(child)
        
        appointments = self.db.get_upcoming_appointments() if self.db.conn else []
        
        if not appointments:
            empty_row = Adw.ActionRow()
            empty_row.set_title("No upcoming appointments")
            empty_row.set_subtitle("Tap 'Add Appointment' to schedule one")
            self.upcoming_group.add(empty_row)
            return
        
        for appt in appointments:
            row = Adw.ActionRow()
            row.set_title(appt['title'])
            
            appt_date = datetime.strptime(appt['appointment_date'], "%Y-%m-%d")
            time_str = appt.get('appointment_time', '')
            row.set_subtitle(f"{appt_date.strftime('%A, %B %d')} at {time_str}")
            
            row.set_icon_name("x-office-calendar-symbolic")
            
            if appt.get('location'):
                location_label = Gtk.Label(label=appt['location'])
                location_label.add_css_class("dim-label")
                location_label.set_valign(Gtk.Align.CENTER)
                row.add_suffix(location_label)
            
            self.upcoming_group.add(row)
    
    def _on_med_taken(self, medication: dict, taken: bool):
        """Log that a medication was taken."""
        if taken:
            self.db.log_medication({
                'medication_id': medication['id'],
                'taken_at': datetime.now().isoformat(),
                'taken': True
            })
            
            toast = Adw.Toast.new(f"✓ {medication['name']} logged")
            if hasattr(self.main_window, 'add_toast'):
                self.main_window.add_toast(toast)
    
    def _show_add_medication_dialog(self, button):
        """Show dialog to add a medication."""
        dialog = Adw.Dialog()
        dialog.set_title("Add Medication")
        dialog.set_content_width(400)
        dialog.set_content_height(450)
        
        toolbar_view = Adw.ToolbarView()
        dialog.set_child(toolbar_view)
        
        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(False)
        header.set_show_start_title_buttons(False)
        
        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", lambda b: dialog.close())
        header.pack_start(cancel_btn)
        
        save_btn = Gtk.Button(label="Add")
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
        
        name_row = Adw.EntryRow()
        name_row.set_title("Medication Name")
        group.add(name_row)
        
        dosage_row = Adw.EntryRow()
        dosage_row.set_title("Dosage")
        dosage_row.set_text("e.g., 10mg")
        group.add(dosage_row)
        
        freq_combo = Adw.ComboRow()
        freq_combo.set_title("Frequency")
        freq_list = Gtk.StringList.new(self.FREQUENCIES)
        freq_combo.set_model(freq_list)
        group.add(freq_combo)
        
        time_row = Adw.EntryRow()
        time_row.set_title("Time of Day")
        time_row.set_text("e.g., 8:00 AM")
        group.add(time_row)
        
        notes_row = Adw.EntryRow()
        notes_row.set_title("Notes")
        group.add(notes_row)
        
        def on_save(btn):
            if not name_row.get_text():
                return
            
            data = {
                'name': name_row.get_text(),
                'dosage': dosage_row.get_text(),
                'frequency': self.FREQUENCIES[freq_combo.get_selected()],
                'time_of_day': time_row.get_text(),
                'notes': notes_row.get_text()
            }
            
            self.db.add_medication(data)
            dialog.close()
            self._refresh_data()
        
        save_btn.connect("clicked", on_save)
        
        dialog.present(self.main_window)
    
    def _show_add_appointment_dialog(self, button):
        """Show dialog to add an appointment."""
        dialog = Adw.Dialog()
        dialog.set_title("Add Appointment")
        dialog.set_content_width(400)
        dialog.set_content_height(450)
        
        toolbar_view = Adw.ToolbarView()
        dialog.set_child(toolbar_view)
        
        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(False)
        header.set_show_start_title_buttons(False)
        
        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", lambda b: dialog.close())
        header.pack_start(cancel_btn)
        
        save_btn = Gtk.Button(label="Add")
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
        
        title_row = Adw.EntryRow()
        title_row.set_title("Appointment Title")
        group.add(title_row)
        
        date_row = Adw.EntryRow()
        date_row.set_title("Date")
        date_row.set_text(date.today().isoformat())
        group.add(date_row)
        
        time_row = Adw.EntryRow()
        time_row.set_title("Time")
        time_row.set_text("10:00 AM")
        group.add(time_row)
        
        location_row = Adw.EntryRow()
        location_row.set_title("Location")
        group.add(location_row)
        
        notes_row = Adw.EntryRow()
        notes_row.set_title("Notes")
        group.add(notes_row)
        
        def on_save(btn):
            if not title_row.get_text():
                return
            
            data = {
                'title': title_row.get_text(),
                'appointment_date': date_row.get_text(),
                'appointment_time': time_row.get_text(),
                'location': location_row.get_text(),
                'notes': notes_row.get_text()
            }
            
            self.db.add_appointment(data)
            dialog.close()
            self._refresh_data()
        
        save_btn.connect("clicked", on_save)
        
        dialog.present(self.main_window)
