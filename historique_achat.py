import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, select
from sqlalchemy_utils import database_exists
import pandas_datareader.data as web
from datetime import date 
from PIL import Image
boolean ='False' #un boolean pour que la page elle reste affichée
def page():
 global boolean
 today = date.today()  
 engine = create_engine("mysql+pymysql://root:@localhost/streamlit_finance")

# creation de la base de données si inéxistante

 if not database_exists(engine.url):
    create_database(engine.url)
 else:
    engine.connect() # connection à la base de données si elle existe
 
 connection = engine.raw_connection()#connexion aux lignes de la table
 cur = connection.cursor()#créer un curseur de connexion 

 st.markdown(
    """
    <style>
    .reportview-container {
        background: url("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRExxQfk9pciXsnPpNp3E9zKfVpYh9EKra25g&usqp=CAU")
    }
   
    </style>
    """,
    unsafe_allow_html=True
)
  

#créer un formulaire dans sidebar
 st.sidebar.info('Vous devez connecter pour accéder au contenu de la page')
 st.sidebar.title("Connexion")
 with st.sidebar.form(key='formulaire',clear_on_submit=True):
  nom1 = st.text_input("Nom",placeholder="Saisir le nom", max_chars= 25, key= str )
  prénom1 = st.text_input("Prénom", placeholder="Saisir le prénom",  max_chars= 25, key= str )
  mot_de_passe= st.text_input("Mot de passe",placeholder="Saisir le nom", max_chars= 30, key= str ,type="password")
  connecter=st.form_submit_button("Connexion")

#vérifier si on a cliquer sur le boutton connecter
 if(connecter):
   #chercher dans la base de données si la personne existe dans la base de donée en vérifiant le nom, prénom et mot de pase saisie
    
    res=pd.read_sql("""SELECT nom,prénom FROM utilisateur WHERE nom like '%{}%' and prénom like '%{}%' and mot_de_passe like '%{}%' """.format(nom1,prénom1,mot_de_passe),connection)
    
    if(len(res)==1): #si la taille de res contient une seul personne donc on afiche la connexion est réussie
        st.sidebar.success("La connexion est réussie")
        st.markdown(f'<h1 style="color:#008000;font-size:26px;">{f"Bien venu {prénom1} sur la Platforme Trading"}</h1>', unsafe_allow_html=True)
        #un boolean pour mettre à jour à chaque fois l'utilisateur modifie dans la page sinon sera pas intéractif
        boolean='True' 
        
  
    else: #si le res est déffirent de 1(la personne n'existe pas dans la base de données) donc il faut créer un compte
        boolean='False'
        st.error("la personne n'existe pas !")
        st.error("si vous avez pas un compte vous devez créer un pour se connecter")

 connection.commit() #envoyer la connexion
 if boolean == 'True':
        image = Image.open('C:\\Users\\ymmel\\OneDrive\\Bureau\\exam_pythonClass\\image_achat.png')
        st.image(image) 
        id_util=pd.read_sql("""SELECT id_utilisateur FROM utilisateur WHERE nom like '%{}%' and prénom like '%{}%'""".format(nom1,prénom1),connection)
        id_utilisateur=0
        for i in id_util['id_utilisateur']:
            id_utilisateur=int(i)
        
        date_min_achat=pd.read_sql("""SELECT min(date_achat) as date_achat FROM achat WHERE id_utilisateur like '%{}%'""".format(id_utilisateur),connection)
        date_creat_utilisateur=''
        for i in date_min_achat['date_achat']:
            date_creat_utilisateur=i
        st.info("sélectioner une durée d'achat")
        
        date_debut = st.date_input ("Date de début",  min_value = date_creat_utilisateur , max_value = today)
        
        date_fin = st.date_input ("Date de fin",  min_value = date_creat_utilisateur , max_value = today)

        st.subheader(f'Tableau historique de vos achats pour la période entre {date_debut} et {date_fin} ')
        id_u=pd.read_sql("""SELECT id_utilisateur FROM utilisateur WHERE nom like '%{}%' and prénom like '%{}%'""".format(nom1,prénom1),connection)
        id_util=''
        for i in id_u['id_utilisateur']:
            id_util=i
  
        #sélectionner les achats effectué par la personne connecté      
        df=pd.read_sql("""SELECT u.nom, u.prénom, a.* FROM achat a join utilisateur u on a.id_utilisateur = u.id_utilisateur WHERE  (u.id_utilisateur='{}') and (date_achat between  '{}' and '{}') """.format(id_util,date_debut,date_fin),connection)
        st.write(df) 

        
   
   


 