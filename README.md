Règles à respecter pour l'architecture :

- les pools doivent être uniques

- les dist_accounts doivent être uniques par leur nom

- les comptes à scrapper doivent être dans un seul pool

- un unique dist account tiktok doit être associé à un compte google

- jusqu'à 100 dist accounts ytb peuvent être associés à un compte google

- INTERDIT D'AVOIR LE MEME NOM DE CHAINES YTB ET TIKTOK




Prochaines choses à dev :

- fichier pour pouvoir tous les contrôler

- passer quelques heures à tous débogguer, tout tester

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


test : 
- uplaod braintv sur youtube (sans modif mais avec les cut) et sur tiktok (avec modif mais sans cut)
- upload un compte tiktok sur youtube
- get_pool de contenu satisfaisant sur instagram et même tiktok 
- upload un compte instagram sur tiktok => créer l'algo pour compiler des videos instagram


le create_content bug un peu, il faut le debugguer
=> il va falloir traîté les cas où les vidéos téléchargées sont pas bonnes => peut être les supprimer et les mettre en published True   
=> fonction is_corrupted dans le traitement des videos

ajouter un moyen de pouvoir définir quelles descriptions mettre pour un dist account donné
=> faire ça dans les parametres des dist accounts
rajouter à la db is_corrupted pour les videos qui ne fonctionnent pas
rajouter à la db is_linked  pour le chainage de videos entre elles

=>sinon le tiktok scrapping fonctionne parfaitement
=> remis à zéro

energiedechampion : compte instagram
=> contacter xcomics pour informations sur animatediff et controlnet


=> cas ou il n'y a pas assez de videos pour creer une video de 1 min
=> probleme dans le cas où on va linker les videos et pour les supprimer ensuite


=> pour l'instant la traj instagram to tiktokest un peu plus complexe car il faudrait concaténer les videos pou rpouvoir etre monétiser sur tiktok et cela pose des problemes sur ce que cela produit sur les bdd car quand on va upload une video il va s'agir en realité de plusieurs videos en meme temps

=> probleme fonction is uploadable

mettre les videos linked en published et en linked avec l'id de la video principale

**DISCLAIMER - The sole purpose of this Youtube channel is to provide viewers with cool content and promote the work of the creator. The channel was created for personal enjoyment and I do not take credit. Please feel free to contact me if you are unhappy with any particular video upload and I will be happy to take it down, rather than reporting the whole group as this will take away people's enjoyment of other videos across the channel. Thank You**

site formats videos: https://www.blogdumoderateur.com/guide-format-videos-reseaux-sociaux/


=> étendre le business à pinterest twitter et facebook pour un maximum d'argent

=> kaiber
=> replicate peut être


=>Sometimes you don't need to be the smartest. You just need to be the guy who never gives up. That is the guy you need to be.

=> qu'immporte la manière on va générer 10k mois avec ce business.

=> Modifier le contenu avec des IA comme animatediff et controlnet
=> Demander la permission pour scrapper soit en échnages de visibilités soit en échanges d'argent
- Comment calculer le montantn générer par les videos d'une chaine lorsque l'on upload le contenu de plusieurs chaines sur un dist account




=> ameliorer la vitesse d'ecriture des videos

from moviepy.editor import VideoFileClip

input_video = VideoFileClip("input.mp4")
output_video = input_video.write_videofile("output.mp4", codec="libx264", preset="ultrafast", threads=4, bitrate="1000k")