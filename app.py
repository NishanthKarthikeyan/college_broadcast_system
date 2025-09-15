import os
import csv
import threading
from flask import Flask, render_template, request, redirect, url_for, session, flash

# --- App Initialization ---
app = Flask(__name__)
# It's recommended to use a more complex, randomly generated secret key
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'a_default_but_still_secret_key')

# --- Admin Credentials (More Securely Handled) ---
# It's best practice to store credentials as environment variables, not in the code.
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin1') # Default password if not set

# --- Data Reading Function ---
def get_phone_numbers(target_year, target_department):
    """
    Reads phone numbers from CSV files based on the specified year and department.
    """
    phone_numbers = set()

    def get_suffix(year_str):
        """Helper to get the correct suffix (st, nd, rd, th) for a given year."""
        try:
            year = int(year_str)
            if 11 <= year <= 13:
                return 'th'
            if year % 10 == 1: return 'st'
            if year % 10 == 2: return 'nd'
            if year % 10 == 3: return 'rd'
            return 'th'
        except (ValueError, TypeError):
            return ''

    # Determine which files to read based on the selected year
    files_to_read = []
    if target_year == 'all_years':
        for year_num in range(1, 5):
            files_to_read.append(f'data/{year_num}{get_suffix(str(year_num))}_year_parents.csv')
    else:
        files_to_read.append(f'data/{target_year}{get_suffix(target_year)}_year_parents.csv')

    # Read each relevant file
    for file_path in files_to_read:
        try:
            with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Added .strip() to department for more robust matching
                    if target_department == 'all_departments' or row.get('department', '').strip().lower() == target_department.lower():
                        phone = row.get('phone_number', '').strip()
                        if phone:
                            phone_numbers.add(phone)
        except FileNotFoundError:
            print(f"Warning: Data file not found at {file_path}. Skipping.")
        except Exception as e:
            print(f"An error occurred while reading {file_path}: {e}")

    return list(phone_numbers)

# --- Background WhatsApp Task (More Reliable Version) ---
def send_whatsapp_in_background(phone_numbers, message):
    """
    Sends WhatsApp messages in a background thread.
    Increased delays to ensure reliability and prevent automation failures.
    """
    try:
        import pywhatkit
        import time
    except ImportError:
        print("Error: 'pywhatkit' is not installed. Please install it using 'pip install pywhatkit'")
        return

    print("--- BACKGROUND WHATSAPP BROADCAST STARTED (RELIABLE MODE) ---")

    for i, number in enumerate(phone_numbers):
        try:
            print(f"Sending message {i+1}/{len(phone_numbers)} to +91{number}...")
            # Using slightly longer, more reliable wait times for browser automation
            pywhatkit.sendwhatmsg_instantly(
                phone_no="+91" + number,
                message=message,
                wait_time=15,       # INCREASED: More reliable wait time for the tab to open and load.
                tab_close=True,
                close_time=5        # INCREASED: Allows more time for the message to be sent before closing.
            )
            print(f"Successfully initiated message to +91{number}")
            # A longer delay between messages prevents WhatsApp from flagging the activity as spam.
            time.sleep(10)
        except Exception as e:
            print(f"Failed to send message to +91{number}: {e}")
            # Wait a bit before trying the next number
            time.sleep(5)

    print("--- BACKGROUND WHATSAPP BROADCAST FINISHED ---")


# --- Flask Routes ---

@app.route('/')
def home():
    """Redirects the root URL to the login page."""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles the admin login process."""
    if 'username' in session:
        return redirect(url_for('dashboard'))

    error = None
    if request.method == 'POST':
        # Using .get() is safer than [''] as it avoids errors if the key is missing
        username = request.form.get('username')
        password = request.form.get('password')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid credentials. Please try again.'

    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    """Displays the main dashboard page, requires login."""
    if 'username' not in session:
        flash('You must be logged in to view the dashboard.', 'error')
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/send', methods=['POST'])
def send():
    """Handles the form submission for sending broadcasts."""
    if 'username' not in session:
        return redirect(url_for('login'))

    year = request.form.get('year')
    department = request.form.get('department')
    message = request.form.get('message')

    if not all([year, department, message]):
        flash("All fields are required. Please fill out the entire form.", 'warning')
        return redirect(url_for('dashboard'))

    phone_numbers_to_send = get_phone_numbers(year, department)

    if not phone_numbers_to_send:
        flash("No recipients found for the selected criteria. Please check your data files.", 'warning')
        return redirect(url_for('dashboard'))

    # Start the WhatsApp automation in a non-blocking background thread
    thread = threading.Thread(
        target=send_whatsapp_in_background,
        args=(phone_numbers_to_send, message)
    )
    thread.daemon = True  # Allows the main app to exit even if threads are running
    thread.start()

    flash(f"✅ Broadcast to {len(phone_numbers_to_send)} recipients has started. A browser window will open shortly to send messages.", 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    """Logs the admin out by clearing the session."""
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# --- Run the Application ---
if __name__ == '__main__':
    # Check if the ADMIN_PASSWORD is still the default
    if ADMIN_PASSWORD == 'admin123':
        print("\n" + "="*60)
        print("WARNING: You are using the default admin password ('admin123').")
        print("It is highly recommended to set a secure environment variable.")
        print("For example (in terminal): export ADMIN_PASSWORD='your_secure_password'")
        print("="*60 + "\n")

    # The host='0.0.0.0' makes the app accessible on your local network
    app.run(debug=True, host='0.0.0.0')