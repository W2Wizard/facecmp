#==============================================================================
# Copyright (c) W2Wizard @ 2023
# See README in the root of the project for more information.
#==============================================================================

import os
import sqlite3
import face_recognition as fr
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from flask import Flask, request, jsonify

# NOTE(W2): I hate python, but it makes sense to use it for this project.
#==============================================================================

load_dotenv()

app = Flask(__name__)
cipher = Fernet(os.getenv('ENCRYPTION_KEY'))
conn = sqlite3.connect('data.sqlite', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
		login TEXT,
        encryptedData BLOB
    )
''')
conn.commit()

# Functions
#==============================================================================

def encrypt(data):
	return cipher.encrypt(bytes(str(data), encoding='utf-8'))

def decrypt(data):
	return eval(cipher.decrypt(data).decode('utf-8'))

# Route for data deletion (GDPR)
@app.route('/api/delete', methods=['DELETE'])
def delete():
	try:
		# Get from the json body the login
		login = request.json.get('login')
		if login:
			# check if cursor was able to delete the data (if the login exists)
			result = cursor.execute('SELECT * FROM data WHERE login = ?', (login,))
			conn.commit()
			if result.fetchone() is None:
				return jsonify({'message': 'Login not found'}), 404
			cursor.execute('DELETE FROM data WHERE login = ?', (login,))
			conn.commit()
			return jsonify({'message': 'Data deleted successfully'}), 200
		else:
			return jsonify({'message': 'Login not provided'}), 400
	except Exception as e:
		return jsonify({'message': str(e)}), 500

# Route for data retrieval and addition
@app.route('/api/match', methods=['POST'])
def match():
	try:
		file = request.files['file']
		login = request.args.get('login')
		if not file or not login:
			return jsonify({'message': 'Login or image not provided'}), 400
		file_encoding = fr.face_encodings(fr.load_image_file(file))[0]
		result = cursor.execute('SELECT * FROM data WHERE login = ?', (login,))
		conn.commit()
		data = result.fetchone()

		print(file_encoding)

		if data is None:
			# Add encrypted encoding and login to the database
			cursor.execute('INSERT INTO data (login, encryptedData) VALUES (?, ?)', (login, encrypt([login, [file_encoding]])))
			conn.commit()
			return jsonify({'message': 'Login not found'}), 404

		# Compare the uploaded image encoding with known face encodings
		matches = fr.compare_faces(decrypt(data[2]), file_encoding)
		names = [decrypt(data[1])[i] for i, match in enumerate(matches) if match]

		# Generate the response
		response = {
			'matches': names
		}

		return jsonify(response)
	except Exception as e:
		return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
