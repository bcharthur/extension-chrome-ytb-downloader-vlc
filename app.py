# app.py
import re

import unicodedata
from flask import Flask, request, jsonify, send_file, url_for, redirect
import os
import logging
import subprocess
import platform

from flask_cors import CORS

from downloader import download_video, get_video_info

app = Flask(__name__)
CORS(app)  # Permet les requêtes CORS depuis l'extension

logging.basicConfig(level=logging.INFO)


def sanitize_filename(filename):
    """
    Nettoie le nom du fichier en supprimant les caractères non-ASCII
    et en remplaçant les caractères indésirables par des underscores.
    """
    nfkd = unicodedata.normalize('NFKD', filename)
    only_ascii = nfkd.encode('ASCII', 'ignore').decode('ASCII')
    return re.sub(r'[^\w\-_\. ]', '_', only_ascii)

def open_in_vlc(filepath):
    """
    Ouvre un fichier dans VLC Media Player.
    """
    try:
        # Vérifie le système d'exploitation et adapte la commande pour lancer VLC
        if platform.system() == 'Windows':
            vlc_command = f'start vlc "{filepath}"'
        elif platform.system() == 'Darwin':  # macOS
            vlc_command = f'open -a VLC "{filepath}"'
        else:  # Linux
            vlc_command = f'vlc "{filepath}"'

        subprocess.run(vlc_command, shell=True)
        return True
    except Exception as e:
        logging.error(f"Erreur lors de l'ouverture dans VLC : {e}")
        return False

@app.route('/open_in_vlc')
def open_in_vlc_route():
    """
    Route pour ouvrir le fichier dans VLC. Redirige vers la page de téléchargement de VLC si VLC n'est pas disponible.
    """
    filename = request.args.get('file')
    if not filename:
        return jsonify({"error": "Nom de fichier non fourni"}), 400

    filepath = os.path.join('downloads', filename)
    if os.path.exists(filepath):
        if open_in_vlc(filepath):
            return jsonify({"message": "Ouverture dans VLC réussie"}), 200
        else:
            # Redirige vers la page de téléchargement de VLC si VLC n'est pas disponible
            return redirect("https://www.videolan.org/vlc/", code=302)
    else:
        return jsonify({"error": "Fichier non trouvé"}), 404

@app.route('/download', methods=['POST'])
def download_video_route():
    data = request.get_json()
    url = data.get('url')
    output_dir = data.get('output_path', 'downloads')

    if not url:
        logging.error("URL manquante dans la requête.")
        return jsonify({"error": "URL manquante."}), 400

    # Obtenir les informations de la vidéo
    video_info = get_video_info(url)
    title = sanitize_filename(video_info["title"])
    video_codec = video_info["video_codec"]
    audio_codec = video_info["audio_codec"]
    format = video_info["format"]

    filename = f"{title}.{format}"
    output_path = os.path.join(output_dir, title)

    os.makedirs(output_dir, exist_ok=True)

    try:
        # Télécharger la vidéo avec le format et les codecs d'origine
        download_video(url, output_path)
        download_url = url_for('serve_file', filename=filename, _external=True)

        return jsonify({
            "message": "Vidéo téléchargée avec succès.",
            "download_url": download_url,
            "filename": filename,
            "title": video_info["title"],
            "video_codec": video_codec,
            "audio_codec": audio_codec,
            "format": format
        }), 200

    except Exception as e:
        logging.error(f"Erreur lors du téléchargement : {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/files/<path:filename>', methods=['GET'])
def serve_file(filename):
    file_path = os.path.join('downloads', filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        logging.error(f"Fichier non trouvé : {file_path}")
        return jsonify({"error": "Fichier non trouvé."}), 404


@app.route('/')
def index():
    return "Serveur de téléchargement YouTube actif."


if __name__ == '__main__':
    app.run(debug=True)
