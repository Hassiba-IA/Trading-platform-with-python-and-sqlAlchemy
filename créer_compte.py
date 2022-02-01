
import streamlit as st
from datetime import date
import pandas as pd
from sqlalchemy import create_engine, insert
from sqlalchemy_utils import database_exists, create_database
from PIL import Image


today = date.today() #réupérer la date d'aujourd'hui
def page(): #une fonction qui s'exécute lors de choix de cette page

 #un arrière plan
 st.markdown( 
    """
    <style>
    .reportview-container {
        background: url("https://i.pinimg.com/originals/94/bd/cb/94bdcbbeb8b7569395a062593499ac6b.png")
    }
   
    </style>
    """,
    unsafe_allow_html=True
)

 image = Image.open('C:\\Users\\ymmel\\OneDrive\\Bureau\\exam_pythonClass\\compte.png')
 st.image(image) 
 
#créer un engine pour connecter à la base de données
 engine = create_engine("mysql+pymysql://root:@localhost/streamlit_finance")

# creation de la base de données si inéxistante

 if not database_exists(engine.url):
    create_database(engine.url)
 else:
    engine.connect() # connection à la base de données si elle existe

 connection = engine.raw_connection() #créer une connexion sous forme d'une ligne (enregitrement)


#creation la tables utilisateur

 table_utilisateur=""" 
               CREATE TABLE IF NOT EXISTS utilisateur (
                    id_utilisateur INT NOT NULL AUTO_INCREMENT,
                    mot_de_passe VARCHAR (30) NOT NULL,
                    nom VARCHAR(40)NOT NULL,
                    prénom VARCHAR (40) NOT NULL,
                    capital FLOAT NOT NULL, 
                    date_creation DATE NOT NULL,
                    PRIMARY KEY(id_utilisateur)
                ); """

 try:
    engine.execute(table_utilisateur)
 except Exception as e:
    st.write('Message d\'erreur : \n{}'.format(e))



 cur = connection.cursor() # sous element de la connecxion qui permet d'effectuer les opérations itératives 



#fonction pour vérifier le contenu des champs nom et prénonm 
 def verif_champ_string(chaine,chain_req=''):
    
    if (chaine==""): #si le champs est vide
        return ("erreur le champ est vide")
    else:
        for i in range(len(chaine)):

         if chaine[i].isdigit():#si la chaine contient un chiffre
           return ("vérifiez les champs: Impossibilité de saisir un chiffre")
           break
         elif chaine[i] in list('[~!@#$%^&*()_?-+{}:;,.\\ ]+$ "\''):#si la chaine contient un des caractère spiciaux
           return("vérifiez les champs: Impossible de saisir des caractères spéciaux ")
           break
       
         else:
           chain_req1=chain_req+chaine[i] #concatener les lettres lus dans chaine_req1
           chaine1=chaine[i+1:]
           if (chaine1==""):#si la chaine est terminée on la returne sinon on appelle encore la fonction récurssif verif_champ_string
            return (chain_req1)
           else :
            return (verif_champ_string(chaine1,chain_req1))


#fonction pour vérifier le contenu de champ capital
 def verif_champ_capital(chaine,chain_req=''):
    if (chaine==""): #si le champs est vide
        return ("erreur le champ est vide")
    elif(chaine=='.'):#si le champs commence par un point
        return("capital invalide")
    else:
        for i in range(len(chaine)):

         if chaine[i].isalpha():#si la champs contient une lettre
           return ("vérifiez les champs: Impossibilité de saisir une lettre")
           break
         elif chaine[i] in list('[~!@#$%^&*()_?-+{}:;,\\ ]+$ "\''):#si le champs contient un de ces caractère séciaux
           return("vérifiez les champs: Impossible de saisir un caractère spécial")
           break
       
         else:
           if((chaine[i]=='.')&(len(chaine[i+1:])>2)):#vérifier si le nombre de chiffre aprés la vérgule (.) est supérieur à 2
                 return("erreur:le capital dépasse deux chiffres aprés le point")
           else:
              chain_req1=chain_req+chaine[i] #concatener les lettres lus dans chaine_req1
              chaine1=chaine[i+1:]
              if (chaine1==""): #si la chaine est terminée on la returne sinon on appelle encore la fonction récurssif verif_champ_capital
                 return (chain_req1)
              else :
                 return (verif_champ_capital(chaine1,chain_req1))
  
 mot_de_passe = st.text_input("Mot De Passe",placeholder="Saisir le mot de passe", max_chars= 25, key= str ,type="password")
 nom = st.text_input("Nom",placeholder="Saisir le nom", max_chars= 25, key= str )
 prénom = st.text_input("Prénom", placeholder="Saisir le prénom",  max_chars= 25, key= str )
 capital = st.text_input("Capital", placeholder="Example 1750.00", key= int )
 date_creation = st.date_input("Date de fin de Cotation",  min_value = today , max_value = today)
 créer_compte=st.button("Créer")

 if(créer_compte): #si le button créer_compte est cliqué
		if(verif_champ_string(nom)!=nom):#vérifier si le champ nom est différent avec le resultat de la fonction verif_champ_string(nom)
			st.error(verif_champ_string(nom))
		else:
			if(verif_champ_string(prénom)!=prénom):#vérifier si le champ prénom est différent avec le resultat de la fonction verif_champ_string(prénom)
				st.error(verif_champ_string(prénom))
			else:
				if(verif_champ_capital(capital)!=capital):#vérifier si le champ capital est différent avec le resultat de la fonction verif_champ_capital(capital)
					st.error(verif_champ_capital(capital))
				else:
                    #vérifier si la personne n'existe pas déja dans la base de données 
					res=pd.read_sql("""SELECT nom,prénom FROM utilisateur WHERE nom like '%{}%' and prénom like '%{}%'""".format(nom,prénom),connection)
					if(len(res)==1):
						st.error("le compte existe déja !")
					else:
                        #si la personne n'existe pas on l'insere ans la base de données (dans la table utilisateur)
						cur.execute("INSERT INTO utilisateur (mot_de_passe,nom,prénom,capital,date_creation) VALUES ('{}','{}','{}','{}','{}')".format(mot_de_passe,nom,prénom,float(capital),date_creation))
						st.sidebar.success("Le compte est crée avec succée")
						st.sidebar.success("Vous pouvez connecter pour accéder aux autre pages")
						
    
 connection.commit()
 cur.close()