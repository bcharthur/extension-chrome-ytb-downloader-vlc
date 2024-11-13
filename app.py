# app.py
from flask import Flask, request, jsonify, send_file, url_for
import os
import logging
from downloader import download_video, get_video_info

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

    # Récupérer les informations de la vidéo
    try:
        video_info = get_video_info(url)
        title = video_info.get('title', 'video')
        logging.info(f"Téléchargement de la vidéo : {title}")
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la récupération des informations de la vidéo : {e}"}), 500

    # Télécharger la nouvelle vidéo
    try:
        filename = title  # Utiliser le titre de la vidéo comme nom de fichier
        # Nettoyer le nom de fichier pour éviter les caractères illégaux
        filename = "".join([c for c in filename if c.isalpha() or c.isdigit() or c in (' ', '.', '_', '-')]).rstrip()
        output_path = os.path.join(DOWNLOAD_DIR, filename)
        final_output = download_video(url, output_path)

        # Renvoyer le chemin du fichier téléchargé
        download_url = url_for('serve_file', filename=os.path.basename(final_output), _external=True)
        return jsonify({
            "message": "Vidéo téléchargée avec succès.",
            "download_url": download_url,
            "filename": os.path.basename(final_output),
            "title": title
        }), 200

    except Exception as e:
        logging.error(f"Erreur lors du téléchargement de la vidéo : {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/files/<path:filename>', methods=['GET'])
def serve_file(filename):
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"error": "Fichier non trouvé."}), 404

@app.route('/open_in_vlc', methods=['GET'])
def open_in_vlc_route():
    filename = request.args.get('file')
    if not filename:
        return jsonify({"error": "Nom de fichier manquant."}), 400

    file_path = os.path.join(DOWNLOAD_DIR, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "Fichier non trouvé."}), 404

    # Retourner une URL de téléchargement
    download_url = url_for('serve_file', filename=filename, _external=True)
    return jsonify({"download_url": download_url}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
