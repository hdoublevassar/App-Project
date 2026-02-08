"""
Lifestyle Insights View
Synthesize data across all modules for comprehensive insights.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw
from datetime import date, datetime, timedelta


class InsightsView(Adw.NavigationPage):
    """Lifestyle insights and analytics view."""
    
    def __init__(self, main_window):
        super().__init__(title="Lifestyle Insights")
        self.main_window = main_window
        self.db = main_window.db
        
        toolbar_view = Adw.ToolbarView()
        self.set_child(toolbar_view)
        
        header = Adw.HeaderBar()
        
        refresh_btn = Gtk.Button(icon_name="view-refresh-symbolic")
        refresh_btn.set_tooltip_text("Refresh Insights")
        refresh_btn.connect("clicked", lambda b: self._refresh_data())
        header.pack_end(refresh_btn)
        
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
        
        # Header card
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        header_box.add_css_class("card")
        content.append(header_box)
        
        header_icon = Gtk.Image.new_from_icon_name("org.gnome.Settings-symbolic")
        header_icon.set_pixel_size(48)
        header_icon.set_margin_top(24)
        header_box.append(header_icon)
        
        header_title = Gtk.Label(label="Your Lifestyle Analytics")
        header_title.add_css_class("title-2")
        header_box.append(header_title)
        
        header_subtitle = Gtk.Label(label="Data-driven insights from all your tracking")
        header_subtitle.add_css_class("dim-label")
        header_subtitle.set_margin_bottom(24)
        header_box.append(header_subtitle)
        
        # Weekly summary
        self.weekly_group = Adw.PreferencesGroup()
        self.weekly_group.set_title("This Week at a Glance")
        content.append(self.weekly_group)
        
        # Correlations
        self.correlations_group = Adw.PreferencesGroup()
        self.correlations_group.set_title("Patterns & Correlations")
        self.correlations_group.set_description("Connections discovered in your data")
        content.append(self.correlations_group)
        
        # Recommendations
        self.recommendations_group = Adw.PreferencesGroup()
        self.recommendations_group.set_title("Personalized Recommendations")
        content.append(self.recommendations_group)
        
        # Trends
        self.trends_group = Adw.PreferencesGroup()
        self.trends_group.set_title("Trends Over Time")
        content.append(self.trends_group)
        
        self._refresh_data()
    
    def _refresh_data(self):
        """Refresh all insights."""
        self._clear_groups()
        
        insights = self.db.get_lifestyle_insights() if self.db.conn else {}
        
        self._populate_weekly_summary(insights.get('weekly_summary', {}))
        self._populate_correlations(insights)
        self._populate_recommendations(insights.get('recommendations', []))
        self._populate_trends()
    
    def _clear_groups(self):
        """Clear all groups."""
        for group in [self.weekly_group, self.correlations_group, 
                      self.recommendations_group, self.trends_group]:
            while child := group.get_first_child():
                if isinstance(child, Adw.ActionRow):
                    group.remove(child)
    
    def _populate_weekly_summary(self, summary: dict):
        """Populate weekly summary section."""
        sleep_data = summary.get('sleep', {})
        fitness_data = summary.get('fitness', {})
        med_data = summary.get('medication_adherence', {})
        
        # Sleep
        sleep_row = Adw.ActionRow()
        sleep_row.set_title("Average Sleep Quality")
        avg_sleep = sleep_data.get('avg_sleep')
        if avg_sleep:
            sleep_row.set_subtitle(f"{avg_sleep:.1f}/10")
            if avg_sleep >= 7:
                sleep_row.set_icon_name("weather-clear-symbolic")
            else:
                sleep_row.set_icon_name("weather-few-clouds-symbolic")
        else:
            sleep_row.set_subtitle("No data this week")
            sleep_row.set_icon_name("weather-clear-night-symbolic")
        self.weekly_group.add(sleep_row)
        
        # Mood
        mood_row = Adw.ActionRow()
        mood_row.set_title("Average Mood")
        avg_mood = sleep_data.get('avg_mood')
        if avg_mood:
            mood_row.set_subtitle(f"{avg_mood:.1f}/10")
            if avg_mood >= 7:
                mood_row.set_icon_name("face-smile-symbolic")
            elif avg_mood >= 4:
                mood_row.set_icon_name("face-plain-symbolic")
            else:
                mood_row.set_icon_name("face-sad-symbolic")
        else:
            mood_row.set_subtitle("Log your mood to see trends")
            mood_row.set_icon_name("face-smile-symbolic")
        self.weekly_group.add(mood_row)
        
        # Fitness
        fitness_row = Adw.ActionRow()
        fitness_row.set_title("Workouts This Week")
        workouts = fitness_data.get('workouts', 0) or 0
        minutes = fitness_data.get('total_minutes', 0) or 0
        fitness_row.set_subtitle(f"{workouts} workouts • {minutes} minutes")
        fitness_row.set_icon_name("emblem-favorite-symbolic")
        self.weekly_group.add(fitness_row)
        
        # Medication
        med_row = Adw.ActionRow()
        med_row.set_title("Medication Adherence")
        taken = med_data.get('taken', 0) or 0
        total = med_data.get('total', 0) or 0
        if total > 0:
            pct = (taken / total) * 100
            med_row.set_subtitle(f"{pct:.0f}% ({taken}/{total} doses)")
        else:
            med_row.set_subtitle("No medications tracked")
        med_row.set_icon_name("accessories-calculator-symbolic")
        self.weekly_group.add(med_row)
    
    def _populate_correlations(self, insights: dict):
        """Populate correlations section."""
        sleep_mood = insights.get('sleep_mood_correlation', {})
        fitness_energy = insights.get('fitness_energy_correlation', {})
        
        # Sleep-Mood correlation
        good_sleep_mood = sleep_mood.get('good_sleep_mood')
        poor_sleep_mood = sleep_mood.get('poor_sleep_mood')
        
        if good_sleep_mood and poor_sleep_mood:
            diff = good_sleep_mood - poor_sleep_mood
            
            row = Adw.ActionRow()
            row.set_title("Sleep ↔ Mood Connection")
            
            if diff > 1:
                row.set_subtitle(f"Good sleep nights → {good_sleep_mood:.1f} mood vs {poor_sleep_mood:.1f}")
                row.set_icon_name("emblem-important-symbolic")
            else:
                row.set_subtitle("Your mood appears stable regardless of sleep quality")
                row.set_icon_name("emblem-ok-symbolic")
            
            self.correlations_group.add(row)
        
        # Fitness-Energy correlation
        workout_energy = fitness_energy.get('workout_days_energy', 0)
        rest_energy = fitness_energy.get('rest_days_energy', 0)
        
        if workout_energy and rest_energy:
            row = Adw.ActionRow()
            row.set_title("Exercise ↔ Energy Connection")
            
            diff = workout_energy - rest_energy
            if diff > 0.5:
                row.set_subtitle(f"Workout days: {workout_energy:.1f} energy vs Rest days: {rest_energy:.1f}")
                row.set_icon_name("go-up-symbolic")
            elif diff < -0.5:
                row.set_subtitle("You may need more recovery time between workouts")
                row.set_icon_name("dialog-information-symbolic")
            else:
                row.set_subtitle("Energy levels stable on workout and rest days")
                row.set_icon_name("go-next-symbolic")
            
            self.correlations_group.add(row)
        
        # If no correlations yet
        if not self.correlations_group.get_first_child():
            row = Adw.ActionRow()
            row.set_title("Keep tracking!")
            row.set_subtitle("Patterns will emerge as you log more data")
            row.set_icon_name("system-search-symbolic")
            self.correlations_group.add(row)
    
    def _populate_recommendations(self, recommendations: list):
        """Populate recommendations section."""
        if not recommendations:
            # Generate some default recommendations
            recommendations = [
                "Log your sleep consistently to unlock personalized recommendations",
                "Track your mood multiple times a day for better pattern detection",
                "Connect the dots by using multiple tracking modules"
            ]
        
        for rec in recommendations:
            row = Adw.ActionRow()
            row.set_title(rec)
            row.set_icon_name("starred-symbolic")
            self.recommendations_group.add(row)
    
    def _populate_trends(self):
        """Populate trends section."""
        # Get sleep data for trend analysis
        sleep_entries = self.db.get_sleep_entries(30) if self.db.conn else []
        
        if len(sleep_entries) < 7:
            row = Adw.ActionRow()
            row.set_title("Need more data")
            row.set_subtitle("Log at least 7 days for trend analysis")
            row.set_icon_name("x-office-calendar-symbolic")
            self.trends_group.add(row)
            return
        
        # Compare recent week to previous week
        recent = sleep_entries[:7]
        previous = sleep_entries[7:14] if len(sleep_entries) >= 14 else []
        
        if recent and previous:
            recent_quality = sum(e['sleep_quality'] or 0 for e in recent) / len(recent)
            previous_quality = sum(e['sleep_quality'] or 0 for e in previous) / len(previous)
            
            row = Adw.ActionRow()
            row.set_title("Sleep Quality Trend")
            
            diff = recent_quality - previous_quality
            if diff > 0.5:
                row.set_subtitle(f"↑ Improving! This week: {recent_quality:.1f} vs Last week: {previous_quality:.1f}")
                row.set_icon_name("go-up-symbolic")
            elif diff < -0.5:
                row.set_subtitle(f"↓ Declining. This week: {recent_quality:.1f} vs Last week: {previous_quality:.1f}")
                row.set_icon_name("go-down-symbolic")
            else:
                row.set_subtitle(f"→ Stable around {recent_quality:.1f}/10")
                row.set_icon_name("go-next-symbolic")
            
            self.trends_group.add(row)
        
        # Mood trend
        if recent and previous:
            recent_mood = sum(e['daily_mood'] or 0 for e in recent if e.get('daily_mood')) / max(1, len([e for e in recent if e.get('daily_mood')]))
            previous_mood = sum(e['daily_mood'] or 0 for e in previous if e.get('daily_mood')) / max(1, len([e for e in previous if e.get('daily_mood')]))
            
            if recent_mood and previous_mood:
                row = Adw.ActionRow()
                row.set_title("Mood Trend")
                
                diff = recent_mood - previous_mood
                if diff > 0.5:
                    row.set_subtitle(f"↑ Looking up! This week: {recent_mood:.1f}")
                    row.set_icon_name("face-smile-symbolic")
                elif diff < -0.5:
                    row.set_subtitle(f"↓ Be gentle with yourself. This week: {recent_mood:.1f}")
                    row.set_icon_name("face-worried-symbolic")
                else:
                    row.set_subtitle(f"→ Steady around {recent_mood:.1f}/10")
                    row.set_icon_name("face-plain-symbolic")
                
                self.trends_group.add(row)
