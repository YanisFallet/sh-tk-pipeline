Règles à respecter pour l'architecture :

- les pools doivent être uniques

- les dist_accounts doivent être uniques par leur nom

- les comptes à scrapper doivent être dans un seul pool

- un unique dist account tiktok doit être associé à un compte google

- jusqu'à 100 dist accounts ytb peuvent être associés à un compte google

- INTERDIT D'AVOIR LE MEME NOM DE CHAINES YTB ET TIKTOK


=> pour des raisons de droits d'auteurs on va commencer pas mettre du contenu depuis instagram sur tiktok 
et du contenu de tiktok sur ytb

Prochaines choses à dev :

- faire fonctionner le systeme de tiktok uploader ✅
=> load_metadata ✅

- retravailler la creation des descriptions des videos pour etre en accord avec les droits d'auteurs✅
=> voir quels dist doivent tagger les comptes ✅

- réorganiser le create content pour pouvoir passer des params de montage ✅ directement dans le fichier arc ✅
- terminer le create content ✅

- changer tous ce qui est impacté par les fichiers toml ✅

- résoudre le problème des logs qui ne vont pas dans le bon fichierfichier ✅

- résoudre le probleme des cuts videos ✅

- ecrire une fonction clear_input pour le tiktok uploader ✅

- remettre tout à zéro, db, content, etc

- fichier pour pouvoir tout controler

- passer quelques heures à tous débogguer, tout tester


- revoir le systeme de logs



Problème :
- j'ai codé le is_scrappable mais pas le mettre tout de suite
- Problème avec le update_one_dist 
- probleme avec le video processing