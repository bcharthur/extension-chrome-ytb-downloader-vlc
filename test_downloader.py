# test_downloader.py
from downloader import download_video

if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=MrTqzaOgTGg"  # Remplacez par votre URL
    output_path = "downloads/Blankulk_Frankul_1.0_-_Les_Kassos__116.mp4"  # Chemin complet avec extension .mp4

    try:
        final_output = download_video(url, output_path)
        print(f"Vidéo téléchargée avec succès : {final_output}")
    except Exception as e:
        print(f"Erreur lors du téléchargement : {e}")
