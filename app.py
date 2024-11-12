# app.py
from flask import Flask, request, jsonify, send_file, url_for, redirect
import os
import logging
import subprocess
import platform
from downloader import download_video

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

DOWNLOAD_DIR = 'downloads'

def clean_download_directory():
    """
    Supprime tous les fichiers du répertoire de téléchargement.
    """
    try:
        for filename in os.listdir(DOWNLOAD_DIR):
            file_path = os.path.join(DOWNLOAD_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        logging.info("Anciennes vidéos supprimées avec succès.")
    except Exception as e:
        logging.error(f"Erreur lors du nettoyage du répertoire de téléchargement : {e}")

@app.route('/download', methods=['POST'])
def download_video_route():
    data = request.get_json()
    url = data.get('url')
    format = data.get('format', 'mp4')  # par défaut en mp4

    if not url:
        return jsonify({"error": "URL manquante."}), 400

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # Supprimer les vidéos précédentes
    clean_download_directory()

    # Télécharger la nouvelle vidéo
    try:
        filename = "video"  # nom de fichier temporaire, peut être remplacé par un titre extrait
        output_path = os.path.join(DOWNLOAD_DIR, filename)
        final_output = download_video(url, output_path)

        # Renvoyer le chemin du fichier téléchargé
        download_url = url_for('serve_file', filename=os.path.basename(final_output), _external=True)
        return jsonify({
            "message": "Vidéo téléchargée avec succès.",
            "download_url": download_url,
            "filename": os.path.basename(final_output)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/open_in_vlc')
def open_in_vlc_route():
    # (Votre code pour ouvrir dans VLC)
    pass

@app.route('/files/<path:filename>', methods=['GET'])
def serve_file(filename):
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"error": "Fichier non trouvé."}), 404

if __name__ == '__main__':
    app.run(debug=True)
