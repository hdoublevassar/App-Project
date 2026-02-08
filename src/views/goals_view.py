"""
Goals Tracker View
Track long-term goals and milestones.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw
from datetime import date, datetime


class GoalsView(Adw.NavigationPage):
    """Goals tracking view."""
    
    CATEGORIES = [
        "Health & Fitness", "Career", "Education", "Financial",
        "Personal Development", "Relationships", "Creative", "Other"
    ]
    
    def __init__(self, main_window):
        super().__init__(title="Goals")
        self.main_window = main_window
        self.db = main_window.db
        
        toolbar_view = Adw.ToolbarView()
        self.set_child(toolbar_view)
        
        header = Adw.HeaderBar()
        
        add_btn = Gtk.Button(icon_name="list-add-symbolic")
        add_btn.set_tooltip_text("Add Goal")
        add_btn.connect("clicked", self._show_add_goal_dialog)
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
        
        # Motivational quote
        quote_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        quote_box.add_css_class("card")
        content.append(quote_box)
        
        quote_icon = Gtk.Image.new_from_icon_name("starred-symbolic")
        quote_icon.set_pixel_size(32)
        quote_icon.set_margin_top(16)
        quote_box.append(quote_icon)
        
        quote_label = Gtk.Label(label='"The journey of a thousand miles begins with a single step."')
        quote_label.set_wrap(True)
        quote_label.set_justify(Gtk.Justification.CENTER)
        quote_label.add_css_class("title-4")
        quote_label.set_margin_start(16)
        quote_label.set_margin_end(16)
        quote_box.append(quote_label)
        
        quote_attr = Gtk.Label(label="— Lao Tzu")
        quote_attr.add_css_class("dim-label")
        quote_attr.set_margin_bottom(16)
        quote_box.append(quote_attr)
        
        # Active goals
        self.active_group = Adw.PreferencesGroup()
        self.active_group.set_title("Active Goals")
        content.append(self.active_group)
        
        # Completed goals
        self.completed_group = Adw.PreferencesGroup()
        self.completed_group.set_title("Completed Goals")
        content.append(self.completed_group)
        
        self._refresh_data()
    
    def _refresh_data(self):
        """Refresh goals data."""
        for group in [self.active_group, self.completed_group]:
            while child := group.get_first_child():
                if isinstance(child, (Adw.ActionRow, Adw.ExpanderRow)):
                    group.remove(child)
        
        active_goals = self.db.get_goals('active') if self.db.conn else []
        completed_goals = self.db.get_goals('completed') if self.db.conn else []
        
        if not active_goals:
            empty_row = Adw.ActionRow()
            empty_row.set_title("No active goals")
            empty_row.set_subtitle("Tap + to set a goal and start your journey")
            self.active_group.add(empty_row)
        else:
            for goal in active_goals:
                self._add_goal_row(goal, self.active_group)
        
        if not completed_goals:
            empty_row = Adw.ActionRow()
            empty_row.set_title("Completed goals will appear here")
            empty_row.add_css_class("dim-label")
            self.completed_group.add(empty_row)
        else:
            for goal in completed_goals:
                self._add_goal_row(goal, self.completed_group, completed=True)
    
    def _add_goal_row(self, goal: dict, group: Adw.PreferencesGroup, completed: bool = False):
        """Add a goal row to the group."""
        expander = Adw.ExpanderRow()
        expander.set_title(goal['title'])
        
        progress = goal.get('progress', 0) or 0
        category = goal.get('category', '')
        expander.set_subtitle(f"{category} • {progress}% complete")
        
        if completed:
            expander.set_icon_name("emblem-ok-symbolic")
        else:
            expander.set_icon_name("starred-symbolic")
        
        # Progress bar
        progress_row = Adw.ActionRow()
        progress_row.set_title("Progress")
        
        progress_bar = Gtk.ProgressBar()
        progress_bar.set_fraction(progress / 100)
        progress_bar.set_valign(Gtk.Align.CENTER)
        progress_bar.set_size_request(150, -1)
        progress_row.add_suffix(progress_bar)
        expander.add_row(progress_row)
        
        if not completed:
            # Update progress button
            update_row = Adw.ActionRow()
            update_row.set_title("Update Progress")
            
            update_btn = Gtk.Button(label="Update")
            update_btn.set_valign(Gtk.Align.CENTER)
            update_btn.connect("clicked", lambda b, g=goal: self._show_update_progress_dialog(g))
            update_row.add_suffix(update_btn)
            expander.add_row(update_row)
            
            # Mark complete button
            complete_row = Adw.ActionRow()
            complete_row.set_title("Mark Complete")
            
            complete_btn = Gtk.Button(label="Complete")
            complete_btn.set_valign(Gtk.Align.CENTER)
            complete_btn.add_css_class("suggested-action")
            complete_btn.connect("clicked", lambda b, g=goal: self._mark_complete(g))
            complete_row.add_suffix(complete_btn)
            expander.add_row(complete_row)
        
        # Description
        if goal.get('description'):
            desc_row = Adw.ActionRow()
            desc_row.set_title("Description")
            desc_row.set_subtitle(goal['description'])
            expander.add_row(desc_row)
        
        # Target date
        if goal.get('target_date'):
            date_row = Adw.ActionRow()
            date_row.set_title("Target Date")
            target = datetime.strptime(goal['target_date'], "%Y-%m-%d")
            date_row.set_subtitle(target.strftime("%B %d, %Y"))
            date_row.set_icon_name("x-office-calendar-symbolic")
            expander.add_row(date_row)
        
        group.add(expander)
    
    def _show_add_goal_dialog(self, button):
        """Show dialog to add a new goal."""
        dialog = Adw.Dialog()
        dialog.set_title("Set a New Goal")
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
        
        save_btn = Gtk.Button(label="Create")
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
        
        group = Adw.PreferencesGroup()
        content.append(group)
        
        title_row = Adw.EntryRow()
        title_row.set_title("Goal Title")
        group.add(title_row)
        
        desc_row = Adw.EntryRow()
        desc_row.set_title("Description")
        group.add(desc_row)
        
        category_combo = Adw.ComboRow()
        category_combo.set_title("Category")
        category_list = Gtk.StringList.new(self.CATEGORIES)
        category_combo.set_model(category_list)
        group.add(category_combo)
        
        date_row = Adw.EntryRow()
        date_row.set_title("Target Date (optional)")
        date_row.set_text("")
        group.add(date_row)
        
        priority_row = Adw.ActionRow()
        priority_row.set_title("Priority")
        priority_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, 5, 1)
        priority_scale.set_value(3)
        priority_scale.set_draw_value(True)
        priority_scale.set_size_request(150, -1)
        priority_scale.set_valign(Gtk.Align.CENTER)
        priority_row.add_suffix(priority_scale)
        group.add(priority_row)
        
        # Tips
        tips_label = Gtk.Label(label="💡 Tip: Break big goals into smaller milestones for better tracking")
        tips_label.set_wrap(True)
        tips_label.add_css_class("dim-label")
        tips_label.set_margin_top(16)
        content.append(tips_label)
        
        def on_save(btn):
            if not title_row.get_text():
                return
            
            data = {
                'title': title_row.get_text(),
                'description': desc_row.get_text(),
                'category': self.CATEGORIES[category_combo.get_selected()],
                'target_date': date_row.get_text() if date_row.get_text() else None,
                'priority': int(priority_scale.get_value())
            }
            
            self.db.add_goal(data)
            dialog.close()
            self._refresh_data()
            
            toast = Adw.Toast.new("Goal created! You've got this! 🎯")
            if hasattr(self.main_window, 'add_toast'):
                self.main_window.add_toast(toast)
        
        save_btn.connect("clicked", on_save)
        
        dialog.present(self.main_window)
    
    def _show_update_progress_dialog(self, goal: dict):
        """Show dialog to update goal progress."""
        dialog = Adw.Dialog()
        dialog.set_title("Update Progress")
        dialog.set_content_width(350)
        dialog.set_content_height(250)
        
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
        
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_margin_top(24)
        content.set_margin_bottom(24)
        content.set_margin_start(24)
        content.set_margin_end(24)
        content.set_valign(Gtk.Align.CENTER)
        toolbar_view.set_content(content)
        
        title = Gtk.Label(label=goal['title'])
        title.add_css_class("title-3")
        content.append(title)
        
        progress_label = Gtk.Label(label="Progress (%)")
        progress_label.add_css_class("heading")
        content.append(progress_label)
        
        progress_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 5)
        progress_scale.set_value(goal.get('progress', 0) or 0)
        progress_scale.set_draw_value(True)
        content.append(progress_scale)
        
        def on_save(btn):
            self.db.update_goal_progress(goal['id'], int(progress_scale.get_value()))
            dialog.close()
            self._refresh_data()
        
        save_btn.connect("clicked", on_save)
        
        dialog.present(self.main_window)
    
    def _mark_complete(self, goal: dict):
        """Mark a goal as complete."""
        self.db.update_goal_progress(goal['id'], 100)
        
        cursor = self.db.conn.cursor()
        cursor.execute("UPDATE goals SET status = 'completed' WHERE id = ?", (goal['id'],))
        self.db.conn.commit()
        
        self._refresh_data()
        
        toast = Adw.Toast.new(f"🎉 Congratulations on completing '{goal['title']}'!")
        toast.set_timeout(5)
        if hasattr(self.main_window, 'add_toast'):
            self.main_window.add_toast(toast)
