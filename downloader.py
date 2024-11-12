# downloader.py
import yt_dlp
import logging

logging.basicConfig(level=logging.INFO)


def get_video_info(url):
    """
    Récupère les informations de la vidéo YouTube, y compris les codecs vidéo et audio.

    :param url: URL de la vidéo YouTube
    :return: Dictionnaire contenant le titre, le codec vidéo et audio, et le format de la vidéo.
    """
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'bestvideo+bestaudio/best',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_codec = info_dict.get('vcodec', 'unknown')
            audio_codec = info_dict.get('acodec', 'unknown')
            format = info_dict.get('ext', 'unknown')
            title = info_dict.get('title', 'video')

        return {
            "title": title,
            "video_codec": video_codec,
            "audio_codec": audio_codec,
            "format": format,
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
            ydl.download([url])

        logging.info(f'Vidéo téléchargée avec succès : {output_path}')
        return output_path
    except Exception as e:
        logging.error(f"Erreur lors du téléchargement de la vidéo : {e}")
        raise