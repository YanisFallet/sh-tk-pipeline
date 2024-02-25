Règles à respecter pour l'architecture :

- les pools doivent être uniques

- les dist_accounts doivent être uniques par leur nom

- les comptes à scrapper doivent être dans un seul pool

- un unique dist account tiktok doit être associé à un compte google

- jusqu'à 100 dist accounts ytb peuvent être associés à un compte google

- INTERDIT D'AVOIR LE MEME NOM DE CHAINES YTB ET TIKTOK



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

energiedechampion : compte instagram
=> contacter xcomics pour informations sur animatediff et controlnet


=> cas ou il n'y a pas assez de videos pour creer une video de 1 min
=> probleme dans le cas où on va linker les videos et pour les supprimer ensuite


=> pour l'instant la traj instagram to tiktokest un peu plus complexe car il faudrait concaténer les videos pou rpouvoir etre monétiser sur tiktok et cela pose des problemes sur ce que cela produit sur les bdd car quand on va upload une video il va s'agir en realité de plusieurs videos en meme temps

**DISCLAIMER - The sole purpose of this Youtube channel is to provide viewers with cool content and promote the work of the creator. The channel was created for personal enjoyment and I do not take credit. Please feel free to contact me if you are unhappy with any particular video upload and I will be happy to take it down, rather than reporting the whole group as this will take away people's enjoyment of other videos across the channel. Thank You**

site formats videos: https://www.blogdumoderateur.com/guide-format-videos-reseaux-sociaux/

=> kaiber
=> replicate peut être




=> Modifier le contenu avec des IA comme animatediff et controlnet
=> Demander la permission pour scrapper soit en échnages de visibilités soit en échanges d'argent
- Comment calculer le montantn générer par les videos d'une chaine lorsque l'on upload le contenu de plusieurs chaines sur un dist account


=> revoir l'enchainement des uploads sur tiktok
   => j'ai besoin de recoder une grande partie du tiktok uploader car l'enchainement est compliqué
   => il faut faire un code specifique pour la premiere video
   => attendre le message de confirmation puis aller sur new videos ou manage post
   => si new_video reupload et ainsi de suite


on a trouvé la solution il suffit de cliquer sur new upload puis soit rediriger vers une nouvelle page titkok soit quit$