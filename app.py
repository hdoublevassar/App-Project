"""
Sleep Tracker Application
==========================
A locally-hosted web application for tracking sleep patterns, mood, and energy.

To run this application:
    1. Install requirements: pip install -r requirements.txt
    2. Run the app: python app.py
    3. Open your browser to: http://localhost:5000

Flask Basics Explained:
-----------------------
- @app.route('/path') - This "decorator" tells Flask: 
  "When someone visits this URL, run the function below it"
  
- render_template('file.html') - Loads an HTML file from the 'templates' folder
  and sends it to the browser

- request.form - Contains data submitted from HTML forms

- redirect() - Sends the user to a different page

- jsonify() - Converts Python data to JSON (for JavaScript to use)
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime, date, timedelta
import database

# Create the Flask application
app = Flask(__name__)

# Initialize the database when the app starts
database.init_database()


# ----- Page Routes -----

@app.route('/')
def home():
    """
    Home page / Dashboard
    Shows a summary of recent sleep data and quick actions.
    """
    # Get recent entries for the dashboard
    recent_entries = database.get_all_sleep_entries(limit=7)
    today = date.today().isoformat()
    today_entry = database.get_sleep_entry(today)
    
    return render_template(
        'index.html',
        recent_entries=recent_entries,
        today_entry=today_entry,
        today=today
    )


@app.route('/log', methods=['GET', 'POST'])
def log_entry():
    """
    Log or edit a sleep entry.
    GET: Display the form (empty or with existing data)
    POST: Save the submitted form data
    """
    # Default to today's date, but allow editing other dates
    entry_date = request.args.get('date', date.today().isoformat())
    
    if request.method == 'POST':
        # Collect form data
        data = {
            'entry_date': request.form.get('entry_date'),
            'bed_time': request.form.get('bed_time'),
            'wake_time': request.form.get('wake_time'),
            'med_melatonin': 1 if request.form.get('med_melatonin') else 0,
            'med_weed': 1 if request.form.get('med_weed') else 0,
            'med_cold_medicine': 1 if request.form.get('med_cold_medicine') else 0,
            'med_benadryl': 1 if request.form.get('med_benadryl') else 0,
            'wake_feeling': request.form.get('wake_feeling'),
            'overall_mood': request.form.get('overall_mood'),
            'wake_feeling_notes': request.form.get('wake_feeling_notes'),
            'mood_notes': request.form.get('mood_notes'),
            'general_notes': request.form.get('general_notes'),
        }
        
        database.save_sleep_entry(data)
        return redirect(url_for('home'))
    
    # GET request - show form with any existing data
    existing_entry = database.get_sleep_entry(entry_date)
    
    return render_template(
        'log_entry.html',
        entry=existing_entry,
        entry_date=entry_date
    )


@app.route('/history')
def history():
    """
    View all past sleep entries in a table format.
    """
    entries = database.get_all_sleep_entries()
    return render_template('history.html', entries=entries)


@app.route('/calendar')
def calendar_view():
    """
    Calendar view showing mood/sleep data for each day.
    """
    # Get month/year from URL or default to current
    year = request.args.get('year', date.today().year, type=int)
    month = request.args.get('month', date.today().month, type=int)
    
    # Handle month navigation
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1
    
    entries = database.get_entries_for_month(year, month)
    
    # Create a dict for easy lookup by date
    entries_by_date = {e['entry_date']: e for e in entries}
    
    return render_template(
        'calendar.html',
        year=year,
        month=month,
        entries_by_date=entries_by_date
    )


@app.route('/checkin', methods=['GET', 'POST'])
def mood_checkin():
    """
    Quick mood/energy check-in throughout the day.
    """
    if request.method == 'POST':
        data = {
            'entry_date': request.form.get('entry_date', date.today().isoformat()),
            'check_time': request.form.get('check_time', datetime.now().strftime('%H:%M')),
            'mood_level': request.form.get('mood_level'),
            'energy_level': request.form.get('energy_level'),
            'notes': request.form.get('notes'),
        }
        
        database.save_mood_checkin(data)
        return redirect(url_for('home'))
    
    today = date.today().isoformat()
    current_time = datetime.now().strftime('%H:%M')
    todays_checkins = database.get_mood_checkins(today)
    
    return render_template(
        'checkin.html',
        today=today,
        current_time=current_time,
        todays_checkins=todays_checkins
    )


@app.route('/charts')
def charts():
    """
    View charts and analytics of sleep data.
    """
    entries = database.get_all_sleep_entries(limit=30)
    checkins = database.get_recent_mood_checkins(days=30)
    
    return render_template(
        'charts.html',
        entries=entries,
        checkins=checkins
    )


# ----- API Routes (for JavaScript to fetch data) -----

@app.route('/api/entries')
def api_entries():
    """Return all entries as JSON for charts."""
    entries = database.get_all_sleep_entries(limit=30)
    return jsonify(entries)


@app.route('/api/checkins/<entry_date>')
def api_checkins(entry_date):
    """Return mood check-ins for a specific date."""
    checkins = database.get_mood_checkins(entry_date)
    return jsonify(checkins)


@app.route('/api/delete-checkin/<int:checkin_id>', methods=['POST'])
def api_delete_checkin(checkin_id):
    """Delete a mood check-in."""
    database.delete_mood_checkin(checkin_id)
    return jsonify({'success': True})


# ----- Run the Application -----

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  Sleep Tracker is running!")
    print("  Open your browser to: http://localhost:5000")
    print("=" * 50 + "\n")
    
    # debug=True enables auto-reload when you change code
    # Use debug=False in production
    app.run(debug=True, port=5000)
