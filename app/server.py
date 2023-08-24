#==============================================================================
# Copyright (c) W2Wizard @ 2023
# See README in the root of the project for more information.
#==============================================================================

import os
import sqlite3
import face_recognition as fr
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from cryptography.fernet import Fernet

# Globals
#==============================================================================

app = Flask(__name__)
db = sqlite3.connect('./db/db.sqlite' , check_same_thread=False)
cursor = db.cursor()
load_dotenv()
cipher_suite = Fernet(os.getenv('ENCRYPTION_KEY'))

cursor.execute('''
	CREATE TABLE IF NOT EXISTS data (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		login TEXT NOT NULL,
		data TEXT NOT NULL
	)
''')
db.commit()

# Functions
#==============================================================================

def find_login(login: str) -> any or None:
	result = cursor.execute('SELECT * FROM data WHERE login = ?', (login, ))
	db.commit()

	return result.fetchone()

def find_matches(login: str, face_encodings: list[float]) -> list[str]:
	result = cursor.execute('SELECT * FROM data WHERE login != ?', (login,))
	db.commit()

	matches = []
	for row in result:
		row_encoding = cipher_suite.decrypt(row[2]).decode("utf-8")
		face_encoding = [float(value) for value in row_encoding.split(',')]
		if fr.compare_faces([face_encoding], face_encodings)[0]:
			matches.append(row[1])

	return matches

# Routes
#==============================================================================

# DELETE Route to comply with GDPR
@app.route('/api/delete', methods=['DELETE'])
def yeet():
	login = request.args['login']
	if not login:
		return jsonify({'message': 'Invalid request'}), 400
	if find_login(login) is None:
		return jsonify({'message': f'User {login} not found'}), 404

	cursor.execute('DELETE FROM data WHERE login = ?', (login, ))
	db.commit()

	return jsonify({'message': 'Data deleted successfully'}), 200

# POST Route to add either find a match or add a new user
@app.route('/api/recognize', methods=['POST'])
def recognize():
	try:
		image = request.files['file']
		login = request.args['login']
	except:
		return jsonify({'message': 'Oops! Invalid request'}), 400

	user = find_login(login)
	if user is not None:
		return jsonify({'message': f'User {login} already exists'}), 200

	encoding = fr.face_encodings(fr.load_image_file(image))[0]
	matches = find_matches(login, encoding)

	if len(matches) > 0:
		return jsonify({'message': 'Recognized user', 'matches': matches}), 200
	else:
		data = ','.join(str(value) for value in encoding)
		data = cipher_suite.encrypt(data.encode('utf-8'))
		cursor.execute('INSERT INTO data (login, data) VALUES (?, ?)', (login, data))
		db.commit()
		return jsonify({'message': 'Login not found, added.'}), 201

# Main
#==============================================================================

if __name__ == "__main__":
	debug = bool(os.getenv('DEBUG'))
	port = int(os.getenv('PORT'))
	host = str(os.getenv('HOST'))
	app.run(debug, port, host)