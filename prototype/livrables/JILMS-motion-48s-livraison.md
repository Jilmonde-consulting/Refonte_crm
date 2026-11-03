# JIL-MS — « Du cahier au clic » · livraison V5

**État :** animatic de travail, 48 s continues, 16:9, 1920 × 1080, 24 fps.
**Point clé :** aucun blanc entre les visuels et la voix off. La piste voix est continue de 0:00 à 0:47,5 ; le film se termine à 0:48,00.
**Débit :** la prise Kevin brute de 47,804 s est utilisée **telle quelle**, sans étirement ni ralentissement. La V5 est un cut court de validation, pas le master 60–90 s.

## Fichiers à ouvrir

| Fichier | Rôle |
|---|---|
| `JILMS-motion-48s-animatic-v5.html` | Animatic courant avec audio intégré. Ouvrir dans Chrome/Firefox/Safari, puis cliquer sur lecture. |
| `JILMS-motion-48s-animatic-v5.mp4` | Export vidéo de l’animatic, 48 s, 1920 × 1080, 24 fps, H.264/AAC. Contrôles et habillage de lecture masqués. |
| `JILMS-motion-48s-vo-mix-v5.wav` | Mix scratch : voix + habillage sonore léger. |
| `JILMS-motion-48s-vo-v5.wav` | Voix seule, pour contrôle ou sous-titrage. |
| `JILMS-motion-72s-animatic-v4.html` | Archive V4 72 s, voix ralentie. Conservée pour comparaison uniquement. |
| `JILMS-motion-75s-animatic-v3.html` | Version 75 s précédente, conservée pour comparaison. |
| `JILMS-motion-75s-animatic-v2.html` | Version plus animée, conservée. |
| `JILMS-motion-75s-animatic.html` | Animatic silencieux original, conservé tel quel. |

## Intégration à l’accueil

L’accueil du site charge la V5 dans une iframe 16:9 avec le mode intégré :

```html
<iframe
  src="livrables/JILMS-motion-48s-animatic-v5.html?embed=1&pause=1"
  title="Film de présentation Jil-MS — Du cahier au clic, 48 secondes"
  allow="autoplay; fullscreen"
  loading="lazy"></iframe>
```

- `embed=1` masque l’en-tête de l’animatic, les chapitres et les notes, et superpose les contrôles de lecture au cadre.
- `pause=1` démarre le film en pause ; la lecture reste déclenchée par l’utilisateur.
- Sans paramètre, `JILMS-motion-48s-animatic-v5.html` conserve sa présentation complète pour la validation.

## Export MP4

Le MP4 est un rendu image par image de la V5, à **24 fps**, sans les contrôles de lecture :

- **Vidéo :** H.264 High, 1920 × 1080, 24 fps, ~3,2 Mb/s.
- **Audio :** AAC mono 48 kHz, 192 kb/s, issu de `JILMS-motion-48s-vo-mix-v5.wav`.
- **Durée :** 48,00 s ; 1 152 images.
- **Fichier :** `JILMS-motion-48s-animatic-v5.mp4` (19 Mo).

Les fondus de scène sont recalculés à 24 fps pour rester identiques à la lecture HTML. Le grain est aussi recalé sur le temps du film. Les mentions **« MAQUETTE — REMPLACER PAR CAPTURE RÉELLE »** et **« JIL-MS · ANIMATIC »** sont conservées : elles rappellent que ce MP4 est un animatic de validation, pas le master final.

## Repères V5

| Temps | Événement |
|---:|---|
| 0:00,00 | Début du film et de la voix |
| 0:05,42 | Le désordre |
| 0:11,13 | Le constat |
| 0:17,37 | « Et le soir, il faut tout retrouver. » |
| 0:20,08 | « Un clic. » + clic visuel |
| 0:20,69 | Le rangement |
| 0:28,15 | La donnée |
| 0:30,68 | L'ancrage |
| 0:35,91 | Interface produit |
| 0:36,50 | Clic de validation |
| 0:36,62 | « Vous validez une facture. » |
| 0:44,02 | Signature JIL-MS |
| 0:47,20 | Dernier mot, « bilan » |
| 0:48,00 | Fin du film |

## Niveaux

- Mix : **−16,09 LUFS** intégré, pic **−1,30 dBFS**, 44,1 kHz / 16 bits mono.
- Voix seule : **−17,41 LUFS**.
- Durée exacte : **48,000 s**.

## Contrôles effectués

- Durée audio et vidéo : **48,000 s**.
- MP4 : **1 152 images** à 24 fps, flux vidéo H.264 et flux audio AAC présents, durée **48,00 s**.
- Aucun silence de plus de 0,8 s dans le mix ; aucun silence de voix de plus de 0,55 s.
- 8 chapitres / 9 séquences ; la signature reste une surcouche dans la séquence produit.
- Audio V5 chargé, lecture et arrêt en fin de film vérifiés dans le navigateur.
- Aucune erreur console dans le navigateur de contrôle.
- Signature affichée à partir de **44,02 s** ; film arrêté à **48,00 s**.
- Images clés vérifiées : 0:03,6, 0:05,7, 0:06,8, 0:08,0, 0:09,0, 0:12,2, 0:18,6, 0:20,2, 0:21,7, 0:29,7, 0:31,0, 0:33,6, 0:36,8, 0:39,3, 0:41,9, 0:44,8 et 0:48,0.

## Ce qui est volontairement provisoire

- **La voix** est la prise Kevin de travail à débit normal (47,804 s). Elle sert à valider la continuité et les cues ; la voix finale reste à choisir et à générer.
- **L'interface produit** est une maquette HTML explicitement marquée « Maquette ». Les captures réelles de JIL-MS restent à enregistrer avant l'export final.
- **La musique et le mix final** restent à produire. L'habillage actuel est une nappe de travail.
- **Les logos clients** ne sont pas intégrés : leur utilisation demande une autorisation écrite.
- La forme juridique (SAS/SARL) doit être harmonisée dans les documents de contact.

## Durée et version longue

La V5 dure **48 s** parce que la prise disponible dure 47,804 s. La cible initiale de 60–90 s n'est pas atteignable sans nouvelle narration : il faut environ **12–42 s** de texte supplémentaire et une nouvelle génération de voix au débit normal. Ne pas étirer la V5 pour atteindre 60 s : c'est le défaut de la V4 qui a été rejeté.

La V4 72 s est conservée uniquement comme archive de comparaison. La V3 75 s reste également une archive ; elle contient des blancs volontaires.
