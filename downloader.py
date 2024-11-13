# downloader.py
import yt_dlp
import logging

logging.basicConfig(level=logging.INFO)

def get_video_info(url):
    """
    Récupère les informations de la vidéo YouTube, y compris le titre.
    """
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'bestvideo+bestaudio/best',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            title = info_dict.get('title', 'video')

        return {
            "title": title,
        }
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des informations de la vidéo : {e}")
        raise

def download_video(url, output_path):
    """
    Télécharge la vidéo avec audio intégré sans conversion, dans le conteneur original si possible.

    :param url: URL de la vidéo YouTube
    :param output_path: Chemin complet où sauvegarder le fichier téléchargé (sans extension).
    """
    try:
        ydl_opts = {
            'outtmpl': f"{output_path}.%(ext)s",  # Le format d'extension sera celui d'origine
            'format': 'bestvideo+bestaudio/best',  # Télécharger la meilleure qualité sans conversion
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,  # Désactiver le téléchargement des playlists
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.download([url])

        # Obtenir l'extension du fichier téléchargé
        info_dict = ydl.extract_info(url, download=False)
        extension = info_dict.get('ext', 'mp4')

        final_output = f"{output_path}.{extension}"
        logging.info(f'Vidéo téléchargée avec succès : {final_output}')
        return final_output
    except Exception as e:
        logging.error(f"Erreur lors du téléchargement de la vidéo : {e}")
        raise
