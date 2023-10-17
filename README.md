date schedule de la forme 02/05/05 H:M

Règles à respecter pour l'architecture :
- les pools doivent être uniques
- les dist_accounts doivent être uniques par leur nom
- les comptes à scrapper doivent être dans un seul pool



comptes pour les pools de videos satisfaisantes : @videosaleatorios2.l
utiliser ffmepg pour devenir riche let's go

- pour tiktok pas de schedule date à priori mais peut être à LT => juste à gérer le maximum d'upload par jour

- Pour gérer les problemes avec les droits d'auteurs => toujours citer les auteurs et leur permettre de pouvoir supprimer les videos si ils le souhaitent en mettant dans la description du compte un email pour me contacter


Prochaines choses à dev :

- faire fonctionner le systeme de tiktok uploader
=> load_metadata

- faire fonctionner le get_pools (bientot fini) ✅

- rajouter des pools pour les pools contents ✅

- faire fonctionner le ytb_uploader (probleme avec des fonctions qui ont ete recodees) ✅
 => j'ai recode une partie des fonctions que j'utilisais pour schedule et aussi pour is_uploadable donc bien remettre à jour le ytb uplaoder avec ces fonctions ✅
 => bien schedule juste avant l'upload pour ne pas avoir de probleme ✅


- retravailler la creation des descriptions des videos pour etre en accord avec les droits d'auteurs

- travailler sur le systeme de creation de content avec moviepy, ffmpeg, etc ✅
 => creation de videos satisfaisantes compilees ✅
 => utiliser du blur et des effets pour modifier les contents
 => coller avec des videos content ✅
 => puis update is_processed ✅


- creer une fonction pour savoir quels content doivent être processed ou non ✅
 => il va falloir le prendre en compte dans l'ARC ✅ dans les fichiers arc/dist


- puisque content et pool se retrouvent dans la meme database il va falloir adpater les requetes sql en consequence
- regarder la coherence des bases de donnees (est ce que vraiment necessaire ?)


je pense qu'une fois tout cela dev et fonctionnel on sera capable de se lancer en masse sur tiktok et ytb



on a quand meme un peu avance sur le projet c'est cool
mais on va devoir taffe un peu plus pour que ca soit vraiment fonctionnel
et qu'on puisse se lancer en masse sur tiktok et ytb
donc ce week end on va travailler lorsque l'on a du e libre sur la creation de content puis sur le tiktok uploader pour le rendre operationnel