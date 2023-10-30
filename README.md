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

- remettre tout à zéro, db, content, etc ✅

- fichier pour pouvoir tous les contrôler

- passer quelques heures à tous débogguer, tout tester


- revoir le systeme de logs ✅


- revoir le systeme de cut video de tiktok vers youtube

- fonction is_removable 


=> cut ou accelerer la video peut être une option pour les videos tiktok vers youtube
=> concaténer les videos instagram vers tiktok



=> on a un problème avec le fait d'avoir des doublons de videos => on utilise souvent le filepath pour les identifier
mais si on a deux videos avec le même filepath mais pas le même nom, on va avoir un problème

=> changer les load_metadata pour avoir les id autoincrementés qui sont uniques

=> rallonger les videos de instagram vers tiktok en ralentissant ou en concaténant
=> tout implémenter dans le create content

=> remove apres is_published
contact.histoireincroyable@gmail.com


Problème :
- j'ai codé le is_scrappable mais pas le mettre tout de suite ✅
- Problème avec le update_one_dist 
- probleme avec le video processing ✅


test : 
- uplaod braintv sur youtube (sans modif mais avec les cut) et sur tiktok (avec modif mais sans cut)
- upload un compte tiktok sur youtube
- get_pool de contenu satisfaisant sur instagram et même tiktok 
- upload un compte instagram sur tiktok => créer l'algo pour compiler des videos instagram


energiedechampion : compte instagram


=> pour l'instant la traj instagram to tiktokest un peu plus complexe car il faudrait concaténer les videos pou rpouvoir etre monétiser sur tiktok et cela pose des problemes sur ce que cela produit sur les bdd car quand on va upload une video il va s'agir en realité de plusieurs videos en meme temps

**DISCLAIMER - The sole purpose of this Youtube channel is to provide viewers with cool content and promote the work of the creator. The channel was created for personal enjoyment and I do not take credit. Please feel free to contact me if you are unhappy with any particular video upload and I will be happy to take it down, rather than reporting the whole group as this will take away people's enjoyment of other videos across the channel. Thank You**

site formats videos: https://www.blogdumoderateur.com/guide-format-videos-reseaux-sociaux/


=> étendre le business à pinterest twitter et facebook pour un maximum d'argent


