import face_recognition as fr
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load a sample picture and learn how to recognize it.
person_image = fr.load_image_file("<TODO>")
face_encoding = fr.face_encodings(person_image)[0]

# Create arrays of known face encodings and their names
# TODO: Change to database
known_face_encodings = [
    face_encoding,
]
known_face_names = [
    "Unknown",
]

@app.route('/compare_faces', methods=['POST'])
def compare_faces():
    file = request.files['image']

    uploaded_encoding = fr.face_encodings(fr.load_image_file(file))[0]

    # Compare the uploaded image encoding with known face encodings
    matches = fr.compare_faces(known_face_encodings, uploaded_encoding)
    names = [known_face_names[i] for i, match in enumerate(matches) if match]

    # Generate the response
    response = {
        'matches': names
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug = False, port = 5000, host = '0.0.0.0', threaded = True)
