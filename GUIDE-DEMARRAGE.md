# 🚀 Guide de démarrage pas à pas

**De zéro jusqu'à un bot qui répond dans Telegram.** Compte 20 à 30 minutes.
Aucune connaissance en programmation n'est nécessaire : tu copies-colles les commandes.

> 💡 Tu as une erreur ? Va directement au tableau **[Dépannage](#-dépannage)** en bas.
> Cette page contient tout ce qui concerne **le code**. Tu peux aussi suivre le
> [tableau de bord de diagnostic](#étape-9--vérifier-que-tout-est-prêt-optionnel).

---

## Sommaire

| Étape | Ce que tu fais | Où |
|---|---|---|
| 1 | Créer le bot et récupérer le **token** | Telegram (BotFather) |
| 2 | Récupérer **API_ID** et **API_HASH** | my.telegram.org |
| 3 | Installer **Python** | ton PC |
| 4 | Installer **ffmpeg** et **deno** | ton PC |
| 5 | Récupérer **le code** | GitHub |
| 6 | Ouvrir le projet dans **VS Code** | VS Code |
| 7 | Créer l'environnement et installer les **dépendances** | VS Code |
| 8 | Créer le fichier **.env** (tes 3 secrets) | VS Code |
| 9 | **Lancer le bot** et le tester | VS Code + Telegram |

---

## Étape 1 — Créer ton bot Telegram avec @BotFather

C'est BotFather (un bot officiel de Telegram) qui crée les bots et donne le **token**.

1. Ouvre Telegram (téléphone ou ordinateur) et cherche **`@BotFather`**
   (celui avec le badge ✔️ bleu, des millions d'abonnés — attention aux faux).
2. Envoie la commande : **`/newbot`**
3. BotFather demande un **nom** → écris ce que tu veux, par exemple : `Mon YouTube Bot`
   *(c'est le nom affiché, tu pourras le changer plus tard)*
4. BotFather demande un **username** → il doit **finir par `bot`** et être unique, par exemple : `mon_youtube_dl_2026_bot`
   *(s'il est déjà pris, BotFather te demande d'en choisir un autre)*
5. 🎉 BotFather répond avec le **token**, une ligne du genre :

   ```
   Use this token to access the HTTP API:
   8123456789:AAF3xk9LmQ7dP2vR8sT1uW4yZ6aB0cD1eFg
   ```

6. **Copie ce token** et garde-le de côté.

> ⚠️ **Le token = le mot de passe de ton bot.** Ne le mets jamais sur GitHub, dans un chat,
> ou dans une capture d'écran. Si tu le perds ou le divulgues : dans BotFather, `/mybots` →
> ton bot → *API Token* → *Revoke current token*.

📌 Note aussi le lien de ton bot, affiché par BotFather : `t.me/mon_youtube_dl_2026_bot`.
Tu en auras besoin à l'étape 9.

---

## Étape 2 — Récupérer API_ID et API_HASH sur my.telegram.org

Le code a besoin de ces deux valeurs (elles identifient ton application auprès de Telegram,
ce n'est **pas** le token). C'est gratuit et ça prend 3 minutes.

1. Sur un **ordinateur**, va sur 👉 **<https://my.telegram.org>**
2. Dans « Your Phone Number », saisis ton numéro au **format international**, par exemple :
   `+33 6 12 34 56 78` (indicatif pays inclus, sans le 0)
3. Clique **Next**. Telegram t'envoie un **code** dans ton application Telegram
   (message provenant de « Telegram ») → recopie-le dans la page.
4. Tu arrives sur un menu → clique sur **« API development tools »**
5. Remplis le formulaire (peu importe le contenu, rien n'est vérifié) :
   - **App title** : `mon bot telegram`
   - **Short name** : `monbot`
   - **URL** : *(laisse vide)*
   - **Platform** : `Desktop`
   - **Description** : `mon bot perso`
6. Clique **Create application**. La page affiche :

   ```
   App api_id:    1234567
   App api_hash:  0123456789abcdef0123456789abcdef
   ```

7. **Copie ces deux valeurs.**

> ⚠️ `api_id` et `api_hash` sont liés à **ton compte Telegram**. Ne les partage jamais
> (quelqu'un qui les a peut se faire passer pour ton application).

### Tu as maintenant tes 3 secrets

| Nom | À quoi ça sert | Où tu l'as eu |
|---|---|---|
| `BOT_TOKEN` | identifie **ton bot** | BotFather (étape 1) |
| `API_ID` | identifie **ton application** | my.telegram.org (étape 2) |
| `API_HASH` | identifie **ton application** | my.telegram.org (étape 2) |

On les utilisera à l'**étape 8**. Ne les mets nulle part ailleurs pour l'instant.

---

## Étape 3 — Installer Python

Le code a besoin de **Python 3.10 ou plus récent** (3.11 ou 3.12 recommandé).

### 🪟 Windows

1. Va sur 👉 <https://www.python.org/downloads/> et clique sur le gros bouton **Download Python 3.x.x**
2. Lance l'installateur et **coche impérativement la case en bas** :
   ☑️ **« Add python.exe to PATH »**
   *(si tu oublies, la commande `python` ne fonctionnera pas)*
3. Clique **Install Now**, puis ferme l'installateur.
4. **Vérifie** : ouvre VS Code, menu **Terminal → Nouveau terminal**, et tape :

   ```powershell
   python --version
   ```

   Tu dois voir quelque chose comme `Python 3.12.4`. Si Windows ouvre le Microsoft Store,
   c'est que l'installation n'a pas marché → recommence en cochant bien « Add to PATH ».
   Tu peux aussi essayer `py --version` et utiliser `py` à la place de `python` ensuite.

### 🍎 macOS

```bash
# avec Homebrew (https://brew.sh) :
brew install python
python3 --version
```

### 🐧 Linux (Debian/Ubuntu)

```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip
python3 --version
```

> Sur macOS et Linux, la commande est `python3` (avec le 3). Sur Windows, `python`.
> Dans la suite du guide, adapte selon ton système.

---

## Étape 4 — Installer ffmpeg et deno

Les deux sont **nécessaires pour YouTube** :
- **ffmpeg** : convertit en MP3 et assemble la vidéo + le son.
- **deno** : permet à yt-dlp de déchiffrer les vidéos YouTube modernes
  *(sans lui, beaucoup de vidéos renverront une erreur)*.

### 🪟 Windows — la méthode simple

Dans le **terminal VS Code** (PowerShell), colle :

```powershell
winget install Gyan.FFmpeg
winget install DenoLand.Deno
```

Puis **ferme complètement VS Code et rouvre-le** (pour que les nouvelles commandes soient reconnues),
et vérifie dans un nouveau terminal :

```powershell
ffmpeg -version
deno --version
```

*Pas de `winget` ? Télécharge ffmpeg sur <https://www.gyan.dev/ffmpeg/builds/> (version « release essentials »),
dézippe-le dans `C:\ffmpeg`, puis ajoute `C:\ffmpeg\bin` au PATH. Ou installe
[Node.js](https://nodejs.org) à la place de deno, le bot le détecte aussi.*

### 🍎 macOS

```bash
brew install ffmpeg deno
```

### 🐧 Linux

```bash
sudo apt install -y ffmpeg
curl -fsSL https://deno.land/install.sh | sh
```

### ✅ Vérification

```bash
ffmpeg -version     # doit afficher "ffmpeg version ..."
deno --version      # doit afficher "deno 2.x.x"  (ou: node --version)
```

Si l'une des deux commandes n'est pas reconnue, ce n'est pas bloquant pour **démarrer**
le bot : il te le dira au lancement avec un avertissement. Mais YouTube ne marchera pas
complètement — reviens à cette étape.

---

## Étape 5 — Récupérer le code

Choisis **une** des deux méthodes.

### Méthode A — avec git (recommandée)

```bash
git clone https://github.com/TIMSOW/telegrambot.git
cd telegrambot
```

Pas de git installé ? Sur Windows : `winget install Git.Git` (puis rouvre VS Code).

> ⚠️ **Important** : les corrections se trouvent sur la branche `arena/01a0f8b3-telegrambot`.
> - Si la [pull request #1](https://github.com/TIMSOW/telegrambot/pull/1) est **fusionnée**,
>   la branche `main` est à jour : la commande ci-dessus suffit. ✅
> - Sinon, récupère la branche corrigée :
>   ```bash
>   git checkout arena/01a0f8b3-telegrambot
>   ```

### Méthode B — sans git (téléchargement ZIP)

1. Sur la page GitHub du dépôt, clique sur le bouton vert **`< > Code`** → **Download ZIP**
2. Dézippe le dossier dans un endroit simple, par exemple :
   - Windows : `C:\Users\TonNom\Documents\telegrambot`
   - macOS : `/Users/TonNom/Documents/telegrambot`
3. ⚠️ **Évite les chemins avec des accents ou des espaces** (ex. `Bureau\Mon bot\`) :
   ça peut casser Python.

---

## Étape 6 — Ouvrir le projet dans VS Code

1. Ouvre **VS Code**
2. Menu **Fichier → Ouvrir le dossier…** (ou *Open Folder*), et sélectionne le dossier `telegrambot`
3. Installe l'extension Python : clique sur l'icône **Extensions** dans la barre de gauche
   (les 4 carrés), cherche **`Python`** (éditeur : *Microsoft*), clique **Install**.
4. Ouvre le terminal intégré : menu **Terminal → Nouveau terminal**
   *(sur clavier AZERTY : **Ctrl + ù**)*

✅ Tu dois voir en bas de VS Code un terminal dont le chemin se termine par `telegrambot`.
**Toutes les commandes suivantes se tapent dans ce terminal.**

---

## Étape 7 — Créer l'environnement et installer les dépendances

Un « environnement virtuel » est un dossier (`.venv`) qui contient les bibliothèques du projet,
sans polluer ton système.

### 1) Créer l'environnement

```bash
# Windows :
python -m venv .venv

# macOS / Linux :
python3 -m venv .venv
```

### 2) L'activer

```bash
# Windows (PowerShell ou cmd) :
.venv\Scripts\activate

# macOS / Linux :
source .venv/bin/activate
```

✅ Quand c'est activé, tu vois **`(.venv)`** au début de la ligne du terminal.

> 🪟 **Windows : erreur `l'exécution de scripts est désactivée` ?**
> Tape d'abord : `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` puis relance l'activation.

### 3) Installer les dépendances (1 à 3 minutes)

```bash
pip install -r requirements.txt
```

✅ Ça se termine par `Successfully installed ...`. Erreurs fréquentes :

| Message | Solution |
|---|---|
| `pip: command not found` | l'environnement n'est pas activé (refais 2), ou utilise `python -m pip install -r requirements.txt` |
| erreurs de compilation sur `tgcrypto` | pas grave, le bot fonctionne sans (plus lent). Passe à la suite. |

### 4) Dire à VS Code d'utiliser cet environnement

`Ctrl+Shift+P` → tape **`Python: Select Interpreter`** → choisis celui qui contient **`.venv`**.

---

## Étape 8 — Créer le fichier `.env` avec tes secrets

C'est ici qu'on met les 3 valeurs des étapes 1 et 2.

1. Dans VS Code, à gauche : clic droit sur le dossier `telegrambot` → **Nouveau fichier**
   (ou icône « + » à côté du nom du dossier)
2. Nomme-le exactement : **`.env`** ⚠️ *(le point devant est obligatoire)*
3. Colle ce contenu **en remplaçant par tes vraies valeurs** :

   ```ini
   BOT_TOKEN=8123456789:AAF3xk9LmQ7dP2vR8sT1uW4yZ6aB0cD1eFg
   API_ID=1234567
   API_HASH=0123456789abcdef0123456789abcdef
   ```

4. **Enregistre** : `Ctrl+S`
5. Vérifie qu'il est bien à la racine, à côté de `bot.py` et `requirements.txt`.

### Règles à respecter dans ce fichier

| ✅ À faire | ❌ À éviter |
|---|---|
| `API_ID=1234567` | `API_ID = 1234567` *(pas d'espace)* |
| `API_HASH=0123abc...` | `API_HASH="0123abc..."` *(pas de guillemets)* |
| une ligne par valeur | tout sur une seule ligne |

> ℹ️ **Ne touche pas à `CHANNEL`** : cette ligne est optionnelle et concerne le
> « force-subscribe » (obliger les gens à rejoindre ta chaîne). Sans chaîne, laisse-la
> commentée (`# CHANNEL=`), comme dans le fichier `.env.example`.
>
> 🔒 Le fichier `.env` est déjà listé dans `.gitignore` : **il ne partira jamais sur GitHub.**
> C'est fait exprès. Ne le renomme pas et ne le copie pas dans un fichier suivi par git.

📄 Un modèle est fourni : tu peux aussi faire `cp .env.example .env`
(macOS/Linux) ou `copy .env.example .env` (Windows) puis remplir les valeurs dans VS Code.

---

## Étape 9 — Lancer le bot 🎊

Dans le terminal VS Code (environnement `(.venv)` activé) :

```bash
python bot.py        # (macOS/Linux : python3 bot.py)
```

Tu dois voir quelque chose comme :

```
ℹ️  .env chargé
18:26:17 | INFO | youtube-bot | ffmpeg trouvé : /usr/bin/ffmpeg
18:26:17 | INFO | youtube-bot | Runtime JavaScript détecté : deno
18:26:17 | INFO | youtube-bot | Cookies : aucun (mode anonyme)

============================================================
🚨  SECURITY WARNING for Forked Users  🚨
...
🎊 I AM ALIVE 🎊
```

🎉 **`🎊 I AM ALIVE 🎊` = ton bot est en ligne.**

> ⚠️ **Laisse le terminal ouvert !** Le bot tourne tant que cette commande tourne.
> Si tu fermes VS Code ou fais `Ctrl+C`, le bot s'arrête et ne répond plus.
> Pour le faire tourner 24h/24 → voir la section [Bonus](#-bonus--le-faire-tourner-24h24).

### Si ça affiche `❌ Configuration incomplète : ...`

Le message te dit quelles valeurs manquent : reviens à l'**étape 8**, corrige le `.env`
(enregistre bien le fichier), et relance.

### Astuce : un lanceur tout-en-un

Le dépôt contient un script qui vérifie tout avant de démarrer (macOS/Linux/Git Bash) :

```bash
./start.sh
```

### Étape 9 bis — Vérifier que tout est prêt (optionnel)

Dans un **second** terminal (`Terminal → Nouveau terminal`), lance le tableau de bord :

```bash
python app.py
```

Puis ouvre 👉 <http://localhost:8080> dans ton navigateur. Tu y verras l'état de
ffmpeg, deno, des cookies et de tes variables. **Arrête-le avec `Ctrl+C`** quand tu as fini,
et garde l'autre terminal (celui de `bot.py`) ouvert.

---

## Étape 10 — Tester ton bot dans Telegram

1. Ouvre Telegram et cherche ton bot (le lien `t.me/...` donné par BotFather à l'étape 1)
2. Envoie **`/start`** → il doit répondre avec un message d'accueil et des boutons.
   *(S'il ne répond pas : le bot n'est pas lancé, ou le token est faux → revois les étapes 8-9.)*
3. Envoie un **lien YouTube**, par exemple : `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
4. Le bot affiche la liste des formats disponibles → **clique sur un bouton**
5. ⏳ Il télécharge, affiche la progression, puis **t'envoie la vidéo** 🎬
6. Essaie aussi :
   - `/thumbnail https://www.youtube.com/watch?v=dQw4w9WgXcQ` → l'image de la vidéo
   - `/date France` → la date et l'heure à Paris
   - `/help` et `/about`

> 💡 Les vidéos longues ou en haute qualité peuvent dépasser la limite de **2 Go** de
> Telegram : le bot te prévient dans ce cas. Choisis une qualité inférieure.

---

## 🛠 Dépannage

| Symptôme | Cause probable | Solution |
|---|---|---|
| `'python' n'est pas reconnu` | Python pas installé ou pas dans le PATH | refais l'étape 3 en cochant « Add python.exe to PATH », puis **rouvre VS Code** |
| `❌ Configuration incomplète : BOT_TOKEN, API_ID, API_HASH` | `.env` absent, mal nommé ou vide | étape 8 : le fichier doit s'appeler exactement `.env`, à la racine |
| `⚠️ ffmpeg est introuvable` | ffmpeg pas installé / PATH non rafraîchi | étape 4, puis **ferme et rouvre VS Code** |
| `⚠️ Aucun runtime JavaScript (deno/node) trouvé` | deno/node absents | étape 4 (`winget install DenoLand.Deno` / `brew install deno`) |
| Le bot ne répond pas à `/start` | il n'est pas lancé, ou token invalide | vérifie que `🎊 I AM ALIVE 🎊` est affiché ; sinon relance `python bot.py` et lis l'erreur |
| `Unauthorized` / `Access token invalid` | `BOT_TOKEN` erroné | recopie-le depuis BotFather (`/mybots` → API Token) |
| `API_ID_INVALID` | `API_ID` / `API_HASH` erronés | revérifie sur <https://my.telegram.org> (étape 2) |
| `ERROR: Unable to extract ...` / `Sign in to confirm you're not a bot` | yt-dlp trop ancien ou YouTube demande une connexion | `pip install -U yt_dlp` puis relance ; en dernier recours ajoute tes cookies dans `cookies.txt` |
| La vidéo se télécharge mais pas de MP3 | ffmpeg manquant | étape 4 |
| `File too large` | vidéo > 2 Go | choisis un format plus léger |
| Le téléchargement échoue sur une seule vidéo | vidéo privée / régionale / supprimée | teste avec une autre vidéo |
| Ça marche puis ça s'arrête tout seul | tu as fermé le terminal, ou PC en veille | laisse le terminal ouvert (§Bonus) |

### Comment tester une correction

Après n'importe quelle modification du `.env` ou installation d'un outil :
**arrête le bot** (`Ctrl+C` dans le terminal), puis relance `python bot.py`.

---

## 🌍 Bonus — Le faire tourner 24h/24

Tant que le terminal est ouvert, le bot fonctionne. Pour qu'il tourne en permanence :

| Solution | Prix | Pour qui |
|---|---|---|
| **Un vieux PC / Raspberry Pi** allumé en continu | gratuit | simple, chez toi |
| **VPS** (Hetzner, Contabo, OVH…) | ~4 €/mois | la solution la plus fiable ; lance `screen`/`tmux` puis `python3 bot.py` |
| **Render / Railway / Koyeb** (plan gratuit ou quelques $) | 0-5 $/mois | pas de serveur à gérer : type *Worker*, commande `python3 bot.py` |

Sur un hébergeur, renseigne `BOT_TOKEN`, `API_ID`, `API_HASH` dans les
**variables d'environnement** du service (pas besoin de `.env`).
Le fichier `Dockerfile` fourni installe déjà ffmpeg et deno.
⚠️ Les plans gratuits mettent souvent le service en veille ou limitent le disque :
pour un bot qui télécharge des vidéos, un petit VPS est plus confortable.

---

## ✅ Récapitulatif — la check-list complète

```
[ ] 1. Token récupéré via @BotFather            → BOT_TOKEN
[ ] 2. API_ID + API_HASH sur my.telegram.org    → à copier
[ ] 3. Python installé et dans le PATH          → python --version
[ ] 4. ffmpeg + deno installés                  → ffmpeg -version / deno --version
[ ] 5. Code récupéré (git clone ou ZIP)
[ ] 6. Dossier ouvert dans VS Code + extension Python
[ ] 7. python -m venv .venv  →  activation  →  pip install -r requirements.txt
[ ] 8. Fichier .env créé à la racine avec les 3 valeurs
[ ] 9. python bot.py  →  🎊 I AM ALIVE 🎊
[ ] 10. /start dans Telegram  →  puis un lien YouTube 🎬
```

---

## 🔐 Sécurité — les 3 règles

1. **Ne publie jamais** ton `BOT_TOKEN`, ton `API_HASH`, ni le fichier `.env` / `cookies.txt`.
   *(S'ils ont fuité : `/revoke` auprès de BotFather pour le token, et régénère depuis my.telegram.org.)*
2. Le fichier `.gitignore` du dépôt protège déjà `.env`, `cookies.txt` et les fichiers
   `*.session`. **Ne les force pas** avec `git add -f`.
3. Si tu publies une capture d'écran, masque le contenu du terminal et du `.env`.

Bonne mise en route ! 🚀
