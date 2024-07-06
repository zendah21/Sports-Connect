import hashlib
import re
from datetime import datetime
from decimal import Decimal

import mysql.connector
from flask import Flask, render_template, request, url_for, redirect, session, jsonify, flash

app = Flask(__name__)
app.secret_key = 'please let us pass'

try:
    # Configure MySQL database
    db = mysql.connector.connect(
        host='localhost',
        user='login',
        password='1234',
        database='sports_connect_DB'
    )
    print("Connected to MySQL!")
except mysql.connector.Error as err:
    print(f"Error: {err}")


# Function to hash the password using SHA-256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Function to validate email
def is_valid_email(email):
    return re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email)


# Function to validate player/manager IDs
def is_valid_id(id):
    return re.match(r'^[0-9]+$', id)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/Register')
def Register():
    return render_template('Register.html')


@app.route('/Login')
def Login():
    return render_template('Login.html')


@app.route('/submit_login', methods=['POST'])
def submit_login():
    global db
    email = request.form['email']
    password = request.form['password']
    login_type = request.form['login_type']

    if not is_valid_email(email):
        return render_template('login.html', error='Invalid email format')

    hashed_password = hash_password(password)

    try:
        db = mysql.connector.connect(
            host='localhost',
            user='login',
            password='1234',
            database='sports_connect_DB'
        )
        cursor = db.cursor()

        if login_type == 'player':
            cursor.execute('SELECT player_id FROM Player WHERE email = %s AND password = %s', (email, hashed_password))
            player = cursor.fetchone()
            if player:
                session['player_id'] = player[0]
                db.close()
                db = mysql.connector.connect(
                    host='localhost',
                    user='player',
                    password='player1',
                    database='sports_connect_DB')
                return redirect(url_for('main_player_page'))

        elif login_type == 'manager':
            cursor.execute('SELECT manager_id FROM CenterManager WHERE email = %s AND password = %s',
                           (email, hashed_password))
            manager = cursor.fetchone()
            if manager:
                print("manager part")
                session['manager_id'] = manager[0]
                db.close()
                db = mysql.connector.connect(
                    host='localhost',
                    user='manager',
                    password='manager1',
                    database='sports_connect_DB')
                return redirect(url_for('manager_main_page'))

        return render_template('Login.html', error='Invalid email or password')

    except mysql.connector.Error as err:
        return render_template('Login.html', error=f"Database error: {err}")


@app.route('/submit_signup', methods=['POST'])
def submit_signup():
    role = request.form['role']
    name = request.form['name']
    surname = request.form['surname']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    player_id = request.form['player_id']
    manager_phone_number = request.form.get('manager_phone_number', None)

    if password != confirm_password:
        error = 'Passwords do not match!'
        return render_template('Register.html', error=error)

    if not is_valid_email(email):
        return 'Invalid email format'

    if not is_valid_id(player_id):
        return 'Invalid player ID format'

    password = hash_password(password)

    try:
        cursor = db.cursor()
        if role == 'player':
            cursor.execute('INSERT INTO Player (player_id, name, surname, email, password) VALUES (%s, %s, %s, %s, %s)',
                           (player_id, name, surname, email, password))
        elif role == 'manager':
            cursor.execute('INSERT INTO CenterManager (phone_number, email, name, password) VALUES (%s, %s, %s, %s)',
                           (manager_phone_number, email, name, password))
        db.commit()
        cursor.close()
        return render_template('Login.html')
    except mysql.connector.IntegrityError as e:
        error = 'ID or Email already exists. Please try again.'
        return render_template('Register.html', error=error)
    except mysql.connector.Error as error:
        return render_template('Register.html', error=f"Database Error: {error}")


@app.route('/main_player_page')
def main_player_page():
    return render_template('Main Player Page.html')


@app.route('/view_my_posts')
def view_my_posts():
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Posts WHERE player_id = %s', (session['player_id'],))
    my_posts = cursor.fetchall()
    cursor.close()
    return render_template('view_my_posts.html', my_posts=my_posts)


@app.route('/create_new_post')
def create_new_post_page():
    return render_template('create_new_post.html')


@app.route('/submit_post', methods=['POST'])
def submit_post():
    player_id = session.get('player_id')
    sport = request.form['sport']
    date = request.form['date']
    time = request.form['time']
    location = request.form['location']
    description = request.form['description']

    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO Posts (player_id, sport, date, time, location, description) VALUES (%s, %s, %s, %s, %s, %s)',
        (player_id, sport, date, time, location, description))
    db.commit()
    cursor.close()

    return redirect(url_for('main_player_page'))


@app.route('/view_all_posts')
def view_all_posts():
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Posts')
    all_posts = cursor.fetchall()
    cursor.close()
    return render_template('view_all_posts.html', all_posts=all_posts)


@app.route('/view_all_bookings')
def view_all_bookings():
    cursor = db.cursor(dictionary=True)
    cursor.execute('''
        SELECT Books.start_time, Books.finish_time, Court.location, Books.player_id
        FROM Books
        JOIN Court ON Books.court_id = Court.court_id
    ''')
    all_bookings = cursor.fetchall()
    cursor.close()

    # Transforming the data to separate date and time
    for booking in all_bookings:
        booking['date'] = booking['start_time'].date()
        booking['time'] = booking['start_time'].time()

    return render_template('view_all_bookings.html', all_bookings=all_bookings)


@app.route('/view_my_bookings')
def view_my_bookings():
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Books WHERE player_id = %s', (session['player_id'],))
    my_bookings = cursor.fetchall()
    cursor.close()
    return render_template('view_my_bookings.html', my_bookings=my_bookings)


@app.route('/make_booking', methods=['GET', 'POST'])
def make_booking():
    if request.method == 'POST':
        player_id = session.get('player_id')
        court_id = request.form['court_id']
        start_date = request.form['start_date']
        start_time = request.form['start_time']
        finish_date = request.form['finish_date']
        finish_time = request.form['finish_time']

        # Combine date and time into datetime objects
        start_datetime = datetime.strptime(f"{start_date} {start_time}", '%Y-%m-%d %H:%M')
        finish_datetime = datetime.strptime(f"{finish_date} {finish_time}", '%Y-%m-%d %H:%M')

        if start_datetime >= finish_datetime:
            return 'Invalid time range'

        # Check for overlapping bookings
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT start_time, finish_time FROM Books WHERE court_id = %s', (court_id,))
        existing_bookings = cursor.fetchall()
        cursor.close()

        for booking in existing_bookings:
            existing_start = booking['start_time']
            existing_finish = booking['finish_time']
            if start_datetime < existing_finish and finish_datetime > existing_start:
                return 'Court is already booked during this time period'

        # Calculate duration in hours
        duration_in_hours = Decimal((finish_datetime - start_datetime).total_seconds() / 3600)

        # Fetch hourly rate for the selected court
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT hourly_rate FROM Court WHERE court_id = %s', (court_id,))
        court = cursor.fetchone()
        cursor.close()

        if not court:
            return 'Court not found'

        hourly_rate = court['hourly_rate']
        total_price = hourly_rate * duration_in_hours

        # Insert the booking
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO Books (player_id, court_id, price, start_time, finish_time) VALUES (%s, %s, %s, %s, %s)',
            (player_id, court_id, total_price, start_datetime, finish_datetime))
        db.commit()
        cursor.close()

        return redirect(url_for('main_player_page'))
    else:
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT court_id, location, hourly_rate FROM Court WHERE booking_status = "free"')
        courts = cursor.fetchall()
        cursor.close()
        return render_template('make_booking.html', courts=courts)


@app.route('/get_hourly_rate')
def get_hourly_rate():
    court_id = request.args.get('court_id')
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT hourly_rate FROM Court WHERE court_id = %s', (court_id,))
    hourly_rate = cursor.fetchone()['hourly_rate']
    cursor.close()
    return jsonify({'hourly_rate': hourly_rate})


@app.route('/manager_main_page')
def manager_main_page():
    return render_template('manager_main_page.html')


@app.route('/manage_courts')
def manage_courts():
    # Fetch all courts
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Court')
    courts = cursor.fetchall()
    cursor.close()
    return render_template('manage_courts.html', courts=courts)


@app.route('/update_court/<int:court_id>', methods=['GET', 'POST'])
def update_court(court_id):
    if request.method == 'POST':
        new_hourly_rate = request.form['hourly_rate']

        # Update hourly rate for the court
        cursor = db.cursor()
        cursor.execute('UPDATE Court SET hourly_rate = %s WHERE court_id = %s', (new_hourly_rate, court_id))
        db.commit()
        cursor.close()

        return redirect(url_for('manage_courts'))
    else:
        # Fetch the court details
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM Court WHERE court_id = %s', (court_id,))
        court = cursor.fetchone()
        cursor.close()
        return render_template('update_court.html', court=court)


@app.route('/add_court', methods=['GET', 'POST'])
def add_court():
    if request.method == 'POST':
        location = request.form['location']
        hourly_rate = request.form['hourly_rate']
        court_surface = request.form['court_surface']
        size = request.form['size']
        football_flag = 'football' in request.form
        basketball_flag = 'basketball' in request.form
        volleyball_flag = 'volleyball' in request.form

        # Ensure a valid court_id is provided
        court_id = request.form.get('court_id')
        if not court_id:
            return 'Error: Court ID is required'

        try:
            cursor = db.cursor()
            cursor.execute(
                'INSERT INTO Court (court_id, location, hourly_rate, court_surface, size, football_flag, basketball_flag, volleyball_flag) '
                'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                (court_id, location, hourly_rate, court_surface, size, football_flag, basketball_flag, volleyball_flag))
            db.commit()
            cursor.close()
            return render_template('manager_main_page.html')
        except mysql.connector.Error as error:
            return f"Error: {error}"

    else:
        return render_template('add_court.html')


@app.route('/delete_court', methods=['POST'])
def delete_court():
    if request.method == 'POST':
        court_id = request.form['court_id']

        cursor = db.cursor()
        cursor.execute('DELETE FROM Court WHERE court_id = %s', (court_id,))
        db.commit()
        cursor.close()

        return redirect(url_for('manage_courts'))


# Route to handle successful booking
@app.route('/success')
def success():
    return 'Booking successful!'


@app.route('/delete_booking', methods=['GET', 'POST'])
def delete_booking():
    if request.method == 'POST':
        # Get the list of booking IDs to delete from the form
        bookings_to_delete = request.form.getlist('booking_to_delete')

        if not bookings_to_delete:
            flash('Please select at least one booking to delete.', 'error')
            return redirect(url_for('view_my_bookings'))

        # Open cursor
        cursor = db.cursor()

        # Delete each selected booking
        for booking in bookings_to_delete:
            player_id, court_id, start_time, finish_time = booking.split('_')
            cursor.execute(
                'DELETE FROM Books WHERE player_id = %s AND court_id = %s AND start_time = %s AND finish_time = %s',
                (player_id, court_id, start_time, finish_time))
            cursor.execute('UPDATE Court SET booking_status = "free" WHERE court_id = %s', (court_id,))
            db.commit()

        # Close cursor
        cursor.close()

        flash('Selected bookings deleted successfully.', 'success')
        return redirect(url_for('view_my_bookings'))
    else:
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT player_id, court_id, start_time, finish_time FROM Books WHERE player_id = %s',
                       (session['player_id'],))
        bookings = cursor.fetchall()
        cursor.close()

        return render_template('delete_booking.html', bookings=bookings)


@app.route('/logout')
def logout():
    # Clear the session data
    session.clear()
    global db
    db.close()
    db = mysql.connector.connect(
        host='localhost',
        user='login',
        password='1234',
        database='sports_connect_DB'
    )
    # Redirect to the login page or home page
    return redirect(url_for('Login'))  # Replace 'login' with the route name for your login page


@app.route('/view_account_information', methods=['GET', 'POST'])
def view_account_information():
    player_id = session.get('player_id')  # Assuming the player_id is stored in session
    error = None

    if request.method == 'POST':
        friend_id = request.form['friend_id']

        cursor = db.cursor()
        try:
            # Check if friend_id exists and is a valid player
            cursor.execute('SELECT player_id FROM Player WHERE player_id = %s', (friend_id,))
            if not cursor.fetchone():
                error = 'Invalid friend ID'
            else:
                # Insert the friend relationship
                cursor.execute('INSERT INTO Friend (player_id, Friend_id) VALUES (%s, %s)', (player_id, friend_id))

                # Update friend count for both players
                cursor.execute('UPDATE Player SET Friend_count = Friend_count + 1 WHERE player_id = %s', (player_id,))
                cursor.execute('UPDATE Player SET Friend_count = Friend_count + 1 WHERE player_id = %s', (friend_id,))

                db.commit()
        except mysql.connector.Error as e:
            db.rollback()
            error = str(e)
        finally:
            cursor.close()

    # Fetch player information
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT name, surname, email FROM Player WHERE player_id = %s', (player_id,))
    player_info = cursor.fetchone()

    # Fetch all friends of the current player
    cursor.execute('''
        SELECT P.name, P.surname
        FROM Friend F
        JOIN Player P ON F.Friend_id = P.player_id
        WHERE F.player_id = %s
    ''', (player_id,))
    friends = cursor.fetchall()
    cursor.close()

    return render_template('player_profile.html', player_info=player_info, friends=friends, error=error)


@app.route('/view_profile')
def view_profile():
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT name, surname, email FROM Player WHERE player_id = %s', (session['player_id'],))
    player_info = cursor.fetchone()
    cursor.close()
    return render_template('player_profile.html', player_info=player_info)


@app.route('/update_profile')
def update_profile():
    return render_template('update_profile.html')


@app.route('/update_profile', methods=['POST'])
def update_profile_submit():
    updated_name = request.form['name']
    updated_surname = request.form['surname']

    cursor = db.cursor()
    cursor.execute('UPDATE Player SET name = %s, surname = %s WHERE player_id = %s',
                   (updated_name, updated_surname, session['player_id']))
    db.commit()
    cursor.close()

    return redirect(url_for('view_profile'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
