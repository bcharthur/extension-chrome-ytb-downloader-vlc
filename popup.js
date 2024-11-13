// popup.js
let filename = '';

document.getElementById('closeButton').addEventListener('click', () => {
    window.close();
});

document.getElementById('downloadButton').addEventListener('click', () => {
    const status = document.getElementById('status');
    const openInVLC = document.getElementById('openInVLC');
    const vlcInfo = document.getElementById('vlcInfo');
    const videoTitleElement = document.getElementById('videoTitle');

    status.textContent = 'Récupération de l\'URL...';
    openInVLC.style.display = 'none';
    vlcInfo.style.display = 'none';
    videoTitleElement.textContent = '';

    // Utiliser chrome.tabs pour récupérer l'URL de l'onglet actif
    chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
        if (tabs.length === 0) {
            status.textContent = 'Impossible de récupérer l\'URL de l\'onglet actif.';
            console.error('Aucun onglet actif trouvé.');
            return;
        }

        const tab = tabs[0];
        const videoUrl = tab.url;
        console.log('URL de l\'onglet actif :', videoUrl);

        // Vérifiez que l'URL est une URL YouTube
        if (!videoUrl.includes('youtube.com/watch') && !videoUrl.includes('youtu.be')) {
            status.textContent = 'Veuillez ouvrir une vidéo YouTube.';
            console.log('URL non reconnue comme une vidéo YouTube.');
            return;
        }

        status.textContent = 'Tentative de connexion au serveur...';
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
                return;
            }

            console.log('Connecté au serveur.');
            status.textContent = 'Connecté au serveur. Téléchargement en cours...';

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

            openInVLC.style.display = 'block';
            vlcInfo.style.display = 'block';

        } catch (error) {
            console.error('Erreur lors de la requête:', error);
            status.textContent = 'Une erreur est survenue lors de la connexion au serveur.';
        }
    });
});

document.getElementById('openInVLC').addEventListener('click', async () => {
    const status = document.getElementById('status');

    try {
        const response = await fetch(`http://br0nson.ddns.net:5000/open_in_vlc?file=${encodeURIComponent(filename)}`);
        if (!response.ok) {
            const errorData = await response.json();
            status.textContent = `Erreur : ${errorData.error}`;
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
        });

    } catch (error) {
        console.error('Erreur lors de la requête:', error);
        status.textContent = 'Une erreur est survenue lors du téléchargement.';
    }
});
