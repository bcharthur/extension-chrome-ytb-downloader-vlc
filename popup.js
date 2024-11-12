document.getElementById('downloadButton').addEventListener('click', async () => {
    const status = document.getElementById('status');
    const downloadLink = document.getElementById('downloadLink');
    const openInVLC = document.getElementById('openInVLC');
    const vlcInfo = document.getElementById('vlcInfo');

    status.textContent = 'Récupération de l\'URL...';
    openInVLC.style.display = 'none';
    vlcInfo.style.display = 'none';

    try {
        // Récupérer l'URL de l'onglet actif
        let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        if (!tab || !tab.url) {
            status.textContent = 'Impossible de récupérer l\'URL de l\'onglet actif.';
            console.error('Aucun onglet actif trouvé ou URL manquante.');
            return;
        }

        const videoUrl = tab.url;
        status.textContent = 'Téléchargement en cours...';

        const data = {
            url: videoUrl,
            output_path: 'downloads',  // Vous pouvez personnaliser ce chemin
            format: 'mp4'  // Format par défaut
        };

        const response = await fetch('http://localhost:5000/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorData = await response.json();
            status.textContent = `Erreur : ${errorData.error}`;
            return;
        }

        const result = await response.json();
        status.textContent = result.message;

        // Afficher le bouton pour ouvrir dans VLC
        openInVLC.style.display = 'block';
        vlcInfo.style.display = 'block';

        openInVLC.onclick = async () => {
            try {
                // Tente d'ouvrir VLC via le serveur Flask
                const openResponse = await fetch(`http://localhost:5000/open_in_vlc?file=${encodeURIComponent(result.filename)}`);
                if (!openResponse.ok) {
                    throw new Error('Erreur lors de l\'ouverture avec VLC.');
                }
            } catch (error) {
                status.textContent = 'Erreur : VLC n\'est pas installé ou une erreur est survenue.';
            }
        };

    } catch (error) {
        console.error('Erreur lors de la requête:', error);
        status.textContent = 'Une erreur est survenue.';
    }
});
