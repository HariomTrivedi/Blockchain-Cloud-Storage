from flask import Flask, request, jsonify, send_file, render_template
from blockchain import Blockchain
from file_utils import split_file
import os

app = Flask(__name__, template_folder='templates')


# Initialize Blockchain
blockchain = Blockchain()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    filename = file.filename

    # Split file into chunks
    chunks = split_file(file)

    for i, chunk in enumerate(chunks):
        transaction = {
            "file_name": filename,
            "chunk_index": i,
            "chunk": chunk.hex()  # Convert binary to hex for JSON storage
        }
        blockchain.add_transaction(transaction)

    return jsonify({"message": "File uploaded successfully!", "chunks": len(chunks)}), 200

@app.route("/files", methods=["GET"])
def list_files():
    """Return a list of stored files from blockchain"""
    file_map = {}

    for block in blockchain.chain:
        for tx in block.transactions:
            file_name = tx["file_name"]
            if file_name not in file_map:
                file_map[file_name] = []
            file_map[file_name].append(tx)

    return jsonify(file_map)

@app.route("/download/<file_name>", methods=["GET"])
def download_file(file_name):
    """Reconstruct and download a file from blockchain transactions"""
    file_chunks = []

    for block in blockchain.chain:
        for tx in block.transactions:
            if tx["file_name"] == file_name:
                file_chunks.append((tx["chunk_index"], bytes.fromhex(tx["chunk"])))  

    if not file_chunks:
        return jsonify({"error": "File not found"}), 404

    file_chunks.sort()  # Sort by chunk index
    file_data = b"".join(chunk[1] for chunk in file_chunks)

    # Save the reconstructed file
    file_path = os.path.join(UPLOAD_FOLDER, file_name)
    with open(file_path, "wb") as f:
        f.write(file_data)

    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
