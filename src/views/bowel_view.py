"""
Bowel Tracker View
Private digestive health tracking.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw
from datetime import date, datetime, timedelta


class BowelView(Adw.NavigationPage):
    """Bowel/digestive health tracking view (private)."""
    
    # Bristol Stool Scale
    CONSISTENCY_LABELS = {
        1: "Type 1 - Separate hard lumps",
        2: "Type 2 - Lumpy, sausage-shaped",
        3: "Type 3 - Sausage with cracks",
        4: "Type 4 - Smooth, soft sausage",
        5: "Type 5 - Soft blobs with clear edges",
        6: "Type 6 - Fluffy, mushy pieces",
        7: "Type 7 - Watery, no solid pieces"
    }
    
    def __init__(self, main_window):
        super().__init__(title="Digestive Health")
        self.main_window = main_window
        self.db = main_window.db
        
        toolbar_view = Adw.ToolbarView()
        self.set_child(toolbar_view)
        
        header = Adw.HeaderBar()
        
        add_btn = Gtk.Button(icon_name="list-add-symbolic")
        add_btn.set_tooltip_text("Log Entry")
        add_btn.connect("clicked", self._show_add_entry_dialog)
        header.pack_end(add_btn)
        
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
        
        # Privacy notice
        privacy_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        privacy_box.add_css_class("card")
        content.append(privacy_box)
        
        privacy_icon = Gtk.Image.new_from_icon_name("security-high-symbolic")
        privacy_icon.set_pixel_size(24)
        privacy_icon.set_margin_start(16)
        privacy_icon.set_margin_top(12)
        privacy_icon.set_margin_bottom(12)
        privacy_box.append(privacy_icon)
        
        privacy_label = Gtk.Label(label="This data is private and not shown on the home screen or in insights.")
        privacy_label.set_wrap(True)
        privacy_label.add_css_class("dim-label")
        privacy_label.set_margin_end(16)
        privacy_label.set_margin_top(12)
        privacy_label.set_margin_bottom(12)
        privacy_box.append(privacy_label)
        
        # Quick log for today
        today_group = Adw.PreferencesGroup()
        today_group.set_title("Today")
        content.append(today_group)
        
        self.today_row = Adw.SwitchRow()
        self.today_row.set_title("Had a bowel movement today")
        self.today_row.connect("notify::active", self._on_today_toggle)
        today_group.add(self.today_row)
        
        # Weekly summary
        self.summary_group = Adw.PreferencesGroup()
        self.summary_group.set_title("Past 7 Days")
        content.append(self.summary_group)
        
        # Recent entries
        self.entries_group = Adw.PreferencesGroup()
        self.entries_group.set_title("Recent Entries")
        content.append(self.entries_group)
        
        # Recommendations
        self.recommendations_group = Adw.PreferencesGroup()
        self.recommendations_group.set_title("Lifestyle Suggestions")
        content.append(self.recommendations_group)
        
        self._refresh_data()
    
    def _refresh_data(self):
        """Refresh all bowel data."""
        self._load_today_status()
        self._load_summary()
        self._load_entries()
        self._load_recommendations()
    
    def _load_today_status(self):
        """Check if there's an entry for today."""
        entries = self.db.get_bowel_entries(1) if self.db.conn else []
        today = date.today().isoformat()
        
        for entry in entries:
            if entry['entry_date'] == today:
                self.today_row.set_active(entry['had_movement'])
                return
        
        self.today_row.set_active(False)
    
    def _load_summary(self):
        """Load weekly summary."""
        while child := self.summary_group.get_first_child():
            if isinstance(child, Adw.ActionRow):
                self.summary_group.remove(child)
        
        entries = self.db.get_bowel_entries(7) if self.db.conn else []
        
        movements = sum(1 for e in entries if e['had_movement'])
        avg_consistency = 0
        consistencies = [e['consistency'] for e in entries if e.get('consistency')]
        if consistencies:
            avg_consistency = sum(consistencies) / len(consistencies)
        
        avg_pain = 0
        pains = [e['pain_level'] for e in entries if e.get('pain_level')]
        if pains:
            avg_pain = sum(pains) / len(pains)
        
        # Frequency row
        freq_row = Adw.ActionRow()
        freq_row.set_title("Bowel Movements")
        freq_row.set_subtitle(f"{movements} in the past 7 days")
        if movements >= 3:
            freq_row.set_icon_name("emblem-ok-symbolic")
        else:
            freq_row.set_icon_name("dialog-warning-symbolic")
        self.summary_group.add(freq_row)
        
        # Consistency row
        if avg_consistency > 0:
            cons_row = Adw.ActionRow()
            cons_row.set_title("Average Consistency")
            cons_row.set_subtitle(f"Type {avg_consistency:.0f} on Bristol Scale")
            if 3 <= avg_consistency <= 5:
                cons_row.set_icon_name("emblem-ok-symbolic")
            else:
                cons_row.set_icon_name("dialog-information-symbolic")
            self.summary_group.add(cons_row)
        
        # Pain row
        if avg_pain > 0:
            pain_row = Adw.ActionRow()
            pain_row.set_title("Average Pain Level")
            pain_row.set_subtitle(f"{avg_pain:.1f}/10")
            if avg_pain <= 2:
                pain_row.set_icon_name("emblem-ok-symbolic")
            else:
                pain_row.set_icon_name("dialog-warning-symbolic")
            self.summary_group.add(pain_row)
    
    def _load_entries(self):
        """Load recent entries."""
        while child := self.entries_group.get_first_child():
            if isinstance(child, Adw.ActionRow):
                self.entries_group.remove(child)
        
        entries = self.db.get_bowel_entries(14) if self.db.conn else []
        
        if not entries:
            empty_row = Adw.ActionRow()
            empty_row.set_title("No entries yet")
            empty_row.set_subtitle("Tap + to log an entry")
            self.entries_group.add(empty_row)
            return
        
        for entry in entries[:10]:  # Show last 10
            row = Adw.ActionRow()
            
            entry_date = datetime.strptime(entry['entry_date'], "%Y-%m-%d")
            row.set_title(entry_date.strftime("%A, %B %d"))
            
            if entry['had_movement']:
                consistency = entry.get('consistency')
                pain = entry.get('pain_level', 0) or 0
                subtitle = f"Type {consistency}" if consistency else "Logged"
                if pain > 0:
                    subtitle += f" • Pain: {pain}/10"
                row.set_subtitle(subtitle)
                row.set_icon_name("emblem-ok-symbolic")
            else:
                row.set_subtitle("No movement")
                row.set_icon_name("window-close-symbolic")
            
            self.entries_group.add(row)
    
    def _load_recommendations(self):
        """Load lifestyle recommendations."""
        while child := self.recommendations_group.get_first_child():
            if isinstance(child, Adw.ActionRow):
                self.recommendations_group.remove(child)
        
        recommendations = self.db.get_bowel_recommendations() if self.db.conn else []
        
        if not recommendations:
            row = Adw.ActionRow()
            row.set_title("Keep tracking for personalized suggestions")
            row.set_icon_name("dialog-information-symbolic")
            self.recommendations_group.add(row)
            return
        
        for rec in recommendations:
            row = Adw.ActionRow()
            row.set_title(rec)
            row.set_icon_name("starred-symbolic")
            self.recommendations_group.add(row)
    
    def _on_today_toggle(self, switch, param):
        """Handle today's toggle."""
        today = date.today().isoformat()
        
        if switch.get_active():
            # Show full entry dialog
            self._show_add_entry_dialog(None, prefill_date=today, prefill_had=True)
        else:
            # Save as no movement
            self.db.save_bowel_entry({
                'entry_date': today,
                'had_movement': False,
                'consistency': None,
                'pain_level': 0
            })
    
    def _show_add_entry_dialog(self, button, prefill_date=None, prefill_had=True):
        """Show dialog to add a bowel entry."""
        dialog = Adw.Dialog()
        dialog.set_title("Log Entry")
        dialog.set_content_width(400)
        dialog.set_content_height(500)
        
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
        
        # Date
        date_group = Adw.PreferencesGroup()
        content.append(date_group)
        
        date_row = Adw.EntryRow()
        date_row.set_title("Date")
        date_row.set_text(prefill_date or date.today().isoformat())
        date_group.add(date_row)
        
        # Had movement
        movement_switch = Adw.SwitchRow()
        movement_switch.set_title("Had bowel movement")
        movement_switch.set_active(prefill_had)
        date_group.add(movement_switch)
        
        # Details (shown when had movement)
        details_group = Adw.PreferencesGroup()
        details_group.set_title("Details")
        content.append(details_group)
        
        # Consistency (Bristol Scale)
        consistency_combo = Adw.ComboRow()
        consistency_combo.set_title("Consistency (Bristol Scale)")
        consistency_list = Gtk.StringList.new([
            "1 - Separate hard lumps",
            "2 - Lumpy, sausage-shaped", 
            "3 - Sausage with cracks",
            "4 - Smooth, soft sausage (ideal)",
            "5 - Soft blobs with clear edges",
            "6 - Fluffy, mushy pieces",
            "7 - Watery, no solid pieces"
        ])
        consistency_combo.set_model(consistency_list)
        consistency_combo.set_selected(3)  # Default to type 4 (ideal)
        details_group.add(consistency_combo)
        
        # Pain level
        pain_row = Adw.ActionRow()
        pain_row.set_title("Pain Level")
        
        pain_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 10, 1)
        pain_scale.set_value(0)
        pain_scale.set_draw_value(True)
        pain_scale.set_size_request(150, -1)
        pain_scale.set_valign(Gtk.Align.CENTER)
        pain_row.add_suffix(pain_scale)
        details_group.add(pain_row)
        
        # Blood present
        blood_switch = Adw.SwitchRow()
        blood_switch.set_title("Blood present")
        blood_switch.set_subtitle("If persistent, consult a doctor")
        details_group.add(blood_switch)
        
        # Notes
        notes_row = Adw.EntryRow()
        notes_row.set_title("Notes")
        details_group.add(notes_row)
        
        def on_save(btn):
            data = {
                'entry_date': date_row.get_text(),
                'had_movement': movement_switch.get_active(),
                'consistency': consistency_combo.get_selected() + 1 if movement_switch.get_active() else None,
                'pain_level': int(pain_scale.get_value()),
                'blood_present': blood_switch.get_active(),
                'notes': notes_row.get_text()
            }
            
            self.db.save_bowel_entry(data)
            dialog.close()
            self._refresh_data()
        
        save_btn.connect("clicked", on_save)
        
        dialog.present(self.main_window)
