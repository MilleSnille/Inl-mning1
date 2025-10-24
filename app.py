from flask import Flask, render_template, request, session, url_for, redirect, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = '123456789' 

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  
    'password': '',  
    'database': 'Inlämning1'  
}

def get_db_connection():
    """Skapa och returnera en databasanslutning"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Fel vid anslutning till MySQL: {e}")
        return None 

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/')
def index():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    # hantera POST request från inloggningsformuläret
    if request.method == 'POST':
        username = request.form.get('username') 
        password = request.form.get('password') 
        
        # Anslut till databasen
        connection = get_db_connection()
        if connection is None:
            flash("Databasanslutning misslyckades.")
            return "Databasanslutning misslyckades", 500
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Fråga för att kontrollera om användare finns med matchande användarnamn
            query = "SELECT * FROM users WHERE username = %s"
            
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            
            # Kontrollera om användaren fanns i databasen och lösenordet är korrekt.
            # Om lösenordet är korrekt så sätt sessionsvariabler och skicka tillbaka en hälsning med användarens namn.
            # Om lösenordet inte är korrekt skicka tillbaka ett felmeddelande med http-status 401.
            if user and user['password'] == password:
                session[username] = user['username']
                flash(f'Välkommen, {user["username"]}!', 'success')
                return render_template('home.html', username=user['username'])
            else:
                # Inloggning misslyckades, skicka http status 401 (Unauthorized)
                flash('Ogiltigt användarnamn eller lösenord.', 'error')
                return ('Ogiltigt användarnamn eller lösenord', 401)

        except Error as e:
            print(f"Databasfel: {e}")
            flash("Databasfel inträffade.", 'error')
            return redirect(url_for('index'))
        
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()


if __name__ == '__main__':
    app.run(debug=True)