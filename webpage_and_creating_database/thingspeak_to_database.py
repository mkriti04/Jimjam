from flask import Flask, render_template, request, jsonify
import requests
import sqlite3

# ThingSpeak parameters
CHANNEL_ID = '2151471'  # Replace with your ThingSpeak Channel ID
READ_API_KEY = 'G0MB1GEUELFTQO29'  # Replace with your ThingSpeak Read API Key
FIELD_ID = 1  # Field 1 where you store the radius

# SQLite database setup
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    radius INTEGER,
                    time TEXT
                  )''')
conn.commit()

# Specify the number of entries you want to retrieve
num_entries = 100

# Make a GET request to retrieve data from ThingSpeak
url = f'https://api.thingspeak.com/channels/{CHANNEL_ID}/fields/{FIELD_ID}.json'
params = {'api_key': READ_API_KEY, 'results': num_entries}
response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    entries = data['feeds']

    # Process and insert the retrieved data into the database
    for entry in entries:
        radius = entry[f'field{FIELD_ID}']
        time = entry['created_at']

        # Check if the data already exists in the database
        cursor.execute("SELECT * FROM data WHERE radius = ? AND time = ?", (radius, time))
        existing_data = cursor.fetchone()

        if not existing_data:
            # Insert data into the SQLite database
            cursor.execute("INSERT INTO data (radius, time) VALUES (?, ?)", (radius, time))
            conn.commit()
            print(f'Data inserted into the database. Radius: {radius}, Time: {time}')
        else:
            print(f'Data already exists in the database. Radius: {radius}, Time: {time}')

    conn.close()
else:
    print(f'Failed to retrieve data. Status code: {response.status_code}')
