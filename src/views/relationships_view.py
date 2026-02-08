"""
Relationships View
Track interpersonal relationships and recognize patterns.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw
from datetime import date, datetime


class RelationshipsView(Adw.NavigationPage):
    """Relationship tracking view."""
    
    RELATIONSHIP_TYPES = [
        "Family", "Partner", "Friend", "Coworker",
        "Acquaintance", "Mentor", "Other"
    ]
    
    INTERACTION_TYPES = [
        "In person", "Phone call", "Video chat", "Text/Message",
        "Email", "Social media", "Other"
    ]
    
    def __init__(self, main_window):
        super().__init__(title="Relationships")
        self.main_window = main_window
        self.db = main_window.db
        
        toolbar_view = Adw.ToolbarView()
        self.set_child(toolbar_view)
        
        header = Adw.HeaderBar()
        
        add_btn = Gtk.Button(icon_name="list-add-symbolic")
        add_btn.set_tooltip_text("Add Relationship")
        add_btn.connect("clicked", self._show_add_relationship_dialog)
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
        
        # Introduction
        intro_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        intro_box.add_css_class("card")
        intro_box.set_margin_bottom(8)
        content.append(intro_box)
        
        intro_icon = Gtk.Image.new_from_icon_name("system-users-symbolic")
        intro_icon.set_pixel_size(32)
        intro_icon.set_margin_top(16)
        intro_box.append(intro_icon)
        
        intro_text = Gtk.Label(label="Track interactions to understand patterns in your relationships and their impact on your wellbeing.")
        intro_text.set_wrap(True)
        intro_text.set_justify(Gtk.Justification.CENTER)
        intro_text.add_css_class("dim-label")
        intro_text.set_margin_start(16)
        intro_text.set_margin_end(16)
        intro_text.set_margin_bottom(16)
        intro_box.append(intro_text)
        
        # Relationships list
        self.relationships_group = Adw.PreferencesGroup()
        self.relationships_group.set_title("People You're Tracking")
        content.append(self.relationships_group)
        
        # Insights
        self.insights_group = Adw.PreferencesGroup()
        self.insights_group.set_title("Relationship Insights")
        content.append(self.insights_group)
        
        self._refresh_data()
    
    def _refresh_data(self):
        """Refresh relationship data."""
        # Clear existing
        for group in [self.relationships_group, self.insights_group]:
            while child := group.get_first_child():
                if isinstance(child, (Adw.ActionRow, Adw.ExpanderRow)):
                    group.remove(child)
        
        relationships = self.db.get_relationships() if self.db.conn else []
        
        if not relationships:
            empty_row = Adw.ActionRow()
            empty_row.set_title("No relationships tracked yet")
            empty_row.set_subtitle("Tap + to add someone")
            self.relationships_group.add(empty_row)
            
            insight_row = Adw.ActionRow()
            insight_row.set_title("Track interactions for insights")
            self.insights_group.add(insight_row)
            return
        
        for rel in relationships:
            self._add_relationship_row(rel)
        
        self._generate_insights(relationships)
    
    def _add_relationship_row(self, relationship: dict):
        """Add a relationship expander row."""
        patterns = self.db.get_relationship_patterns(relationship['id']) if self.db.conn else {}
        
        expander = Adw.ExpanderRow()
        expander.set_title(relationship['name'])
        expander.set_subtitle(relationship.get('relationship_type', ''))
        expander.set_icon_name("avatar-default-symbolic")
        
        # Stats row
        if patterns.get('total_interactions', 0) > 0:
            stats_row = Adw.ActionRow()
            avg_quality = patterns.get('avg_quality', 0) or 0
            mood_change = patterns.get('avg_mood_change', 0) or 0
            
            stats_row.set_title("Interaction Quality")
            stats_row.set_subtitle(f"Avg: {avg_quality:.1f}/10")
            
            if mood_change > 0.5:
                stats_row.set_icon_name("go-up-symbolic")
            elif mood_change < -0.5:
                stats_row.set_icon_name("go-down-symbolic")
            else:
                stats_row.set_icon_name("go-next-symbolic")
            
            expander.add_row(stats_row)
        
        # Log interaction button
        log_row = Adw.ActionRow()
        log_row.set_title("Log Interaction")
        
        log_btn = Gtk.Button(label="Log")
        log_btn.set_valign(Gtk.Align.CENTER)
        log_btn.add_css_class("suggested-action")
        log_btn.connect("clicked", lambda b, r=relationship: self._show_log_interaction_dialog(r))
        log_row.add_suffix(log_btn)
        expander.add_row(log_row)
        
        self.relationships_group.add(expander)
    
    def _generate_insights(self, relationships: list):
        """Generate insights from relationship data."""
        positive_relationships = []
        negative_relationships = []
        
        for rel in relationships:
            patterns = self.db.get_relationship_patterns(rel['id']) if self.db.conn else {}
            mood_change = patterns.get('avg_mood_change', 0) or 0
            
            if mood_change > 0.5:
                positive_relationships.append(rel['name'])
            elif mood_change < -0.5:
                negative_relationships.append(rel['name'])
        
        if positive_relationships:
            row = Adw.ActionRow()
            row.set_title("Mood Boosters")
            row.set_subtitle(f"Time with {', '.join(positive_relationships)} tends to lift your mood")
            row.set_icon_name("face-smile-symbolic")
            self.insights_group.add(row)
        
        if negative_relationships:
            row = Adw.ActionRow()
            row.set_title("Worth Reflecting On")
            row.set_subtitle(f"Interactions with {', '.join(negative_relationships)} may affect your mood")
            row.set_icon_name("dialog-information-symbolic")
            self.insights_group.add(row)
        
        if not positive_relationships and not negative_relationships:
            row = Adw.ActionRow()
            row.set_title("Keep logging interactions")
            row.set_subtitle("Insights will appear as you track more interactions")
            self.insights_group.add(row)
    
    def _show_add_relationship_dialog(self, button):
        """Show dialog to add a new relationship."""
        dialog = Adw.Dialog()
        dialog.set_title("Add Relationship")
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
        name_row.set_title("Name")
        group.add(name_row)
        
        type_combo = Adw.ComboRow()
        type_combo.set_title("Relationship Type")
        type_list = Gtk.StringList.new(self.RELATIONSHIP_TYPES)
        type_combo.set_model(type_list)
        group.add(type_combo)
        
        notes_row = Adw.EntryRow()
        notes_row.set_title("Notes")
        group.add(notes_row)
        
        def on_save(btn):
            if not name_row.get_text():
                return
            
            data = {
                'name': name_row.get_text(),
                'relationship_type': self.RELATIONSHIP_TYPES[type_combo.get_selected()],
                'notes': notes_row.get_text()
            }
            
            self.db.add_relationship(data)
            dialog.close()
            self._refresh_data()
        
        save_btn.connect("clicked", on_save)
        
        dialog.present(self.main_window)
    
    def _show_log_interaction_dialog(self, relationship: dict):
        """Show dialog to log an interaction."""
        dialog = Adw.Dialog()
        dialog.set_title(f"Log Interaction with {relationship['name']}")
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
        
        # Interaction type
        type_group = Adw.PreferencesGroup()
        content.append(type_group)
        
        type_combo = Adw.ComboRow()
        type_combo.set_title("Interaction Type")
        type_list = Gtk.StringList.new(self.INTERACTION_TYPES)
        type_combo.set_model(type_list)
        type_group.add(type_combo)
        
        # Quality and mood
        feelings_group = Adw.PreferencesGroup()
        feelings_group.set_title("How did it go?")
        content.append(feelings_group)
        
        quality_row = Adw.ActionRow()
        quality_row.set_title("Interaction Quality")
        quality_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, 10, 1)
        quality_scale.set_value(5)
        quality_scale.set_draw_value(True)
        quality_scale.set_size_request(150, -1)
        quality_scale.set_valign(Gtk.Align.CENTER)
        quality_row.add_suffix(quality_scale)
        feelings_group.add(quality_row)
        
        mood_before_row = Adw.ActionRow()
        mood_before_row.set_title("Your Mood Before")
        mood_before_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, 10, 1)
        mood_before_scale.set_value(5)
        mood_before_scale.set_draw_value(True)
        mood_before_scale.set_size_request(150, -1)
        mood_before_scale.set_valign(Gtk.Align.CENTER)
        mood_before_row.add_suffix(mood_before_scale)
        feelings_group.add(mood_before_row)
        
        mood_after_row = Adw.ActionRow()
        mood_after_row.set_title("Your Mood After")
        mood_after_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, 10, 1)
        mood_after_scale.set_value(5)
        mood_after_scale.set_draw_value(True)
        mood_after_scale.set_size_request(150, -1)
        mood_after_scale.set_valign(Gtk.Align.CENTER)
        mood_after_row.add_suffix(mood_after_scale)
        feelings_group.add(mood_after_row)
        
        # Patterns and notes
        notes_group = Adw.PreferencesGroup()
        notes_group.set_title("Reflection")
        content.append(notes_group)
        
        patterns_row = Adw.EntryRow()
        patterns_row.set_title("Patterns noticed")
        notes_group.add(patterns_row)
        
        notes_row = Adw.EntryRow()
        notes_row.set_title("Notes")
        notes_group.add(notes_row)
        
        def on_save(btn):
            data = {
                'relationship_id': relationship['id'],
                'interaction_date': date.today().isoformat(),
                'interaction_type': self.INTERACTION_TYPES[type_combo.get_selected()],
                'quality': int(quality_scale.get_value()),
                'your_mood_before': int(mood_before_scale.get_value()),
                'your_mood_after': int(mood_after_scale.get_value()),
                'patterns_noticed': patterns_row.get_text(),
                'notes': notes_row.get_text()
            }
            
            self.db.save_interaction(data)
            dialog.close()
            self._refresh_data()
        
        save_btn.connect("clicked", on_save)
        
        dialog.present(self.main_window)
