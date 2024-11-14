// popup.js
let filename = '';

const downloadButton = document.getElementById('downloadButton');
const openInVLC = document.getElementById('openInVLC');
const status = document.getElementById('status');
const vlcInfo = document.getElementById('vlcInfo');
const videoTitleElement = document.getElementById('videoTitle');
const spinner = document.getElementById('spinner');

document.getElementById('closeButton').addEventListener('click', () => {
    window.close();
});

downloadButton.addEventListener('click', () => {
    status.textContent = '';
    openInVLC.style.display = 'none';
    vlcInfo.style.display = 'none';
    videoTitleElement.textContent = '';

    spinner.style.display = 'inline-block'; // Afficher le spinner
    downloadButton.disabled = true; // Désactiver le bouton

    // Utiliser chrome.tabs pour récupérer l'URL de l'onglet actif
    chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
        if (tabs.length === 0) {
            status.textContent = 'Impossible de récupérer l\'URL de l\'onglet actif.';
            console.error('Aucun onglet actif trouvé.');
            spinner.style.display = 'none'; // Cacher le spinner
            downloadButton.disabled = false; // Réactiver le bouton
            return;
        }

        const tab = tabs[0];
        const videoUrl = tab.url;
        console.log('URL de l\'onglet actif :', videoUrl);

        // Vérifier que l'URL est une URL YouTube
        if (!videoUrl.includes('youtube.com/watch') && !videoUrl.includes('youtu.be')) {
            status.textContent = 'Veuillez ouvrir une vidéo YouTube.';
            console.log('URL non reconnue comme une vidéo YouTube.');
            spinner.style.display = 'none'; // Cacher le spinner
            downloadButton.disabled = false; // Réactiver le bouton
            return;
        }

        status.textContent = 'Connexion au serveur...';
        console.log('Tentative de connexion au serveur...');

        const data = {
            url: videoUrl,
            format: 'mp4'
        };

        try {
            const response = await fetch('http://br0nson.ddns.net:5000/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const errorData = await response.json();
                status.textContent = `Erreur : ${errorData.error}`;
                console.error(`Erreur du serveur : ${errorData.error}`);
                spinner.style.display = 'none'; // Cacher le spinner
                downloadButton.disabled = false; // Réactiver le bouton
                return;
            }

            console.log('Connecté au serveur.');

            const result = await response.json();
            filename = result.filename; // Stocker le nom du fichier

            // Afficher le nom de la vidéo en cours de téléchargement
            if (result.title) {
                videoTitleElement.textContent = `Titre de la vidéo : "${result.title}"`;
                status.textContent = `Téléchargement de "${result.title}" en cours...`;
                console.log(`Téléchargement de "${result.title}" en cours...`);
            } else {
                status.textContent = 'Téléchargement en cours...';
            }

            // Mise à jour du statut après le téléchargement
            status.textContent = `Vidéo "${result.title}" téléchargée avec succès.`;
            console.log(`Vidéo "${result.title}" téléchargée avec succès.`);

            // Cacher le bouton bleu et afficher le bouton vert
            downloadButton.style.display = 'none';
            openInVLC.style.display = 'inline-block';
            vlcInfo.style.display = 'block';

        } catch (error) {
            console.error('Erreur lors de la requête:', error);
            status.textContent = 'Une erreur est survenue lors de la connexion au serveur.';
            downloadButton.disabled = false; // Réactiver le bouton
        } finally {
            spinner.style.display = 'none'; // Cacher le spinner
        }
    });
});

openInVLC.addEventListener('click', async () => {
    status.textContent = 'Téléchargement de la vidéo...';
    spinner.style.display = 'inline-block'; // Afficher le spinner

    try {
        const response = await fetch(`http://br0nson.ddns.net:5000/open_in_vlc?file=${encodeURIComponent(filename)}`);
        if (!response.ok) {
            const errorData = await response.json();
            status.textContent = `Erreur : ${errorData.error}`;
            spinner.style.display = 'none'; // Cacher le spinner
            return;
        }

        const data = await response.json();
        const videoUrl = data.download_url;

        chrome.downloads.download({
            url: videoUrl,
            filename: filename,
            conflictAction: 'uniquify'
        }, (downloadId) => {
            if (chrome.runtime.lastError) {
                console.error(chrome.runtime.lastError.message);
                status.textContent = 'Erreur lors du téléchargement.';
            } else {
                status.textContent = 'Vidéo téléchargée avec succès.';
                console.log('Téléchargement démarré avec l\'ID :', downloadId);
            }
            spinner.style.display = 'none'; // Cacher le spinner
        });

    } catch (error) {
        console.error('Erreur lors de la requête:', error);
        status.textContent = 'Une erreur est survenue lors du téléchargement.';
        spinner.style.display = 'none'; // Cacher le spinner
    }
});
