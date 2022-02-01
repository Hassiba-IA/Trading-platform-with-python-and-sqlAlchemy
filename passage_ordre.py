 
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, select, insert
from sqlalchemy_utils import database_exists, create_database
from datetime import date 
from matplotlib import pyplot as plt
import pandas_datareader.data as web
import altair as alt
from PIL import Image
from datetime import datetime

boolean='False'
def page():
 global capital
 global boolean #un boolean pour que la page elle reste affichée
 global nom #récupérer le nom aprés la connexion
 global prénom #récupérer le prénom aprés la connexion
 #un arrière plan
 st.markdown(
    """
    <style>
    .reportview-container {
        background: url("https://s3.amazonaws.com/rm3.photos.prod.readmedia.com/students/5444764/cover-original/mustard_yellow.png?1578524709")
    }
   
    </style>
    """,
    unsafe_allow_html=True
)

 today = date.today() #récupérer la date d'aujourd'ui 
 ##créer un engine pour connecter à la base de données
 engine = create_engine("mysql+pymysql://root:@localhost/streamlit_finance")

# creation de la base de données si inéxistante

 if not database_exists(engine.url):
    create_database(engine.url)
 else:
    engine.connect() # connection à la base de données si elle existe
 
 connection = engine.raw_connection()#connexion aux lignes de la table
 cur = connection.cursor()#créer un curseur de connexion 

#créer un formulaire dans sidebar
 st.sidebar.info('Vous devez connecter pour accéder au contenu de la page')
 st.sidebar.title("Connexion")
 with st.sidebar.form(key='formulaire',clear_on_submit=True):
  nom1 = st.text_input("Nom",placeholder="Saisir le nom", max_chars= 25, key= str )
  prénom1 = st.text_input("Prénom", placeholder="Saisir le prénom",  max_chars= 25, key= str )
  mot_de_passe= st.text_input("Mot de passe",placeholder="Saisir le nom", max_chars= 30, key= str, type="password" )
  connecter=st.form_submit_button("Connexion")

  nom=nom1
  prénom=prénom1
#vérifier si on a cliquer sur le boutton connecter
 if(connecter):
   #chercher dans la base de données si la personne existe dans la base de donée en vérifiant le nom, prénom et mot de pase saisie
    
    res=pd.read_sql("""SELECT nom,prénom FROM utilisateur WHERE nom like '%{}%' and prénom like '%{}%' and mot_de_passe like '%{}%'""".format(nom1,prénom1,mot_de_passe),connection)
    
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
   image = Image.open('C:\\Users\\ymmel\\OneDrive\\Bureau\\exam_pythonClass\\trading_platform.png')
   st.image(image, width=None) 
   #radio bouton pour chercher un seul ticker ou plusier en meme temps
   cours = st.radio('Pick one', ['Cours unique', 'Multiples Cours'])
   
   col1, col2 = st.columns(2) 
   
   with col1:
         ticker_1 = st.text_input("Ticker 1",placeholder="Saisir le ticket")
   with col2:
         quantité_ticket_1=st.selectbox('Quantité ticker 1',['1','2','3','4','5'])
   
   
   if(cours=='Multiples Cours'):#si radio boutton =='Multiples cours ' on affiche 2 champs de saisie de ticker en plus
      with col1:
            ticker_2 = st.text_input("Ticker 2", placeholder="Saisir le ticket")
            ticker_3 = st.text_input("Ticker 3", placeholder="Saisir le ticket")
      with col2:
            quantité_ticket_2=st.selectbox('Quantité ticker 2',['1','2','3','4','5'])
            quantité_ticket_3=st.selectbox('Quantité ticker 3',['1','2','3','4','5'])

   with col1:
         date_debut_cotat = st.date_input ("Date de début de Cotation",  min_value = None , max_value = today)

         
   with col2:
         date_fin_cotat = st.date_input("Date de fin de Cotation",  min_value = today , max_value = today)
   acheter =st.button('Acheter') 


        
   
      # si on clique sur afficher on va tester sur les champs de saisie et sur radio boutton
   def df_ticker(ticker): #récupérer les inormations de ticker spécifique
         return (web.DataReader(ticker, data_source = "yahoo", start = date_debut_cotat, end = date_fin_cotat))

   def prix_jour(tik,date_jour): # retourner le prix de jours apartir d'un ticket et date de jours
      info_ticker=web.DataReader(tik, data_source = "yahoo", start = date_jour, end = date_jour)
      return( ((info_ticker['High'].values+info_ticker['Low'].values)/2)[0])

 
   def rendement(ticker): #calculer le rendement d'un ticker
         first_val=df_ticker(ticker)['Close'].head(1).values
         final_val=df_ticker(ticker)['Close'].tail(1).values
         rendement=((final_val-first_val)/first_val)*100
         return(round(rendement[0],2 ))

   def chart_rendement(ticker):
         close_aujourdhui=df_ticker(ticker)['Close'].tail(1)#la valeur de Close aujourd'hui
         list_rendement=[]
         signe=[]
         for c in (df_ticker(ticker)['Close']):
            list_rendement.append(round((((close_aujourdhui[0]-c)/c)*100),2))
         copie_df=df_ticker(ticker)# la copie de dataframe affichage on lui ajoute des colonnes rendement et signe_rendement
         copie_df['rendement']=list_rendement
         for ren in(list_rendement):
            if (ren<0):
               signe.append("négatif")
            else:
               signe.append("positif")
         copie_df['signe_rendement']=signe #ajouter la colonne signe_rendement à la copie_df
         copie_df['date']=copie_df.index #ajouter la colonne date à la copie_df contien les ndex
         copie_df.set_index('date') #définir la colonne date comme index pour copie_df
         chart2 = alt.Chart(copie_df[['rendement','date','signe_rendement']]).mark_bar().encode(
            x=alt.X('date'),
            y=alt.Y('rendement'),
            color=alt.Color("signe_rendement")
            )
         return(chart2)
            

   if(cours=='Cours unique'):
         if(ticker_1 !=''):
            
            df_ticker(ticker_1)
            
            st.markdown(f'<h1 style="color:#730800;font-size:15px;">{f"le prix Low et le prix High de ticker {ticker_1} "}</h1>', unsafe_allow_html=True)
            st.line_chart(df_ticker(ticker_1)[['Low','High']])
            st.bar_chart(df_ticker(ticker_1)[['Low','High']])
            
            if(rendement(ticker_1)>=0):
               st.markdown(f'<h1 style="color:#32CD32;font-size:25px; padding_top: 95px;padding_bottom:120px;padding_left:75px;padding_right:75px; background-color:#90EE90">{f"le rendement aujourdhui est de: ({rendement(ticker_1)} % )"}</h1>', unsafe_allow_html=True)
            else:
               st.markdown(f'<h1 style="color:#f00020;font-size:25px; padding_top: 95px;padding_bottom:120px;padding_left:75px;padding_right:75px; background-color:#FFB6C1">{f"le rendement aujourdhui est de: ({rendement(ticker_1)} % )"}</h1>', unsafe_allow_html=True)
            
            st.altair_chart(chart_rendement(ticker_1))
            
         else:
            st.write(' ')
      
   else:
         st.header(f'Les visualisations de ticker_1 ({ticker_1})')
         col1, col2 = st.columns(2)
         st.header(f'Les visualisations de ticker_2({ticker_2})')
         col12,col22= st.columns(2)
         st.header(f'Les visualisations de ticker_3 ({ticker_3})')
         col13,col23=st.columns(2)
         

         if(ticker_1 !=''):#tester si le champs de saisie de ticker_1 n'est pas vide

            if(ticker_2 !=''):#tester si le champs de saisie de ticker_2 n'est pas vide

               if(ticker_3!=''):#tester si le champs de saisie de ticker_3 n'est pas vide


                  with col1:
                     
                     
                     st.line_chart(df_ticker(ticker_1)[['Low','High']])
                     st.bar_chart(df_ticker(ticker_1)['High'])

                     
                  with col12:
                     
                     st.line_chart(df_ticker(ticker_2)[['Low','High']])
                     st.bar_chart(df_ticker(ticker_2)['High'])
                     
                    
                  with col13: 
                       
                     st.line_chart(df_ticker(ticker_3)[['Low','High']])
                     st.bar_chart(df_ticker(ticker_3)['High'])


                  with col2:
         
                     if(rendement(ticker_1)>=0):
                        st.markdown(f'<div style="color:#32CD32;font-size:25px; padding_top: 95px;padding_bottom:120px;padding_left:75px;padding_right:75px; background-color:#90EE90">{f"le rendement aujourdhui est de: ({rendement(ticker_1)} % )"}</div>', unsafe_allow_html=True)
                     else:
                        st.markdown(f'<div style="color:#f00020;font-size:20px; padding_top: 95px;padding_bottom:120px;padding_left:75px;padding_right:75px; background-color:#FFB6C1">{f"le rendement aujourdhui est de: ({rendement(ticker_1)} % )"}</div>', unsafe_allow_html=True)
                     
                     st.altair_chart(chart_rendement(ticker_1))

                  with col22:
               
                     if(rendement(ticker_2)>=0):
                        st.markdown(f'<div style="color:#32CD32;font-size:25px; padding_top: 95px;padding_bottom:120px;padding_left:75px;padding_right:75px; background-color:#90EE90">{f"le rendement aujourdhui est de: ({rendement(ticker_2)} % )"}</div>', unsafe_allow_html=True)
                     else:
                        st.markdown(f'<div style="color:#f00020;font-size:25px; padding_top: 95px;padding_bottom:120px;padding_left:75px;padding_right:75px; background-color:#FFB6C1">{f"le rendement aujourdhui est de: ({rendement(ticker_2)} % )"}</div>', unsafe_allow_html=True)
                  
                     st.altair_chart(chart_rendement(ticker_1))
                  with col23:
                     
                     if(rendement(ticker_3)>=0):
                        st.markdown(f'<div style="color:#32CD32;font-size:25px; padding_top: 95px;padding_bottom:120px;padding_left:75px;padding_right:75px; background-color:#90EE90">{f"le rendement aujourdhui est de: ({rendement(ticker_3)} % )"}</div>', unsafe_allow_html=True)
                     else:
                        st.markdown(f'<div style="color:#f00020;font-size:25px; padding_top: 95px;padding_bottom:120px;padding_left:75px;padding_right:75px; background-color:#FFB6C1">{f"le rendement aujourdhui est de: ({rendement(ticker_3)} % )"}</div>', unsafe_allow_html=True)
                     st.altair_chart(chart_rendement(ticker_1))


               else:
                  
                  with col1:
                    
                     st.line_chart(df_ticker(ticker_1)[['Low','High']])
                     st.bar_chart(df_ticker(ticker_1)['High'])

                  
                  with col12:
           
                     st.line_chart(df_ticker(ticker_2)[['Low','High']])
                     st.bar_chart(df_ticker(ticker_2)['High'])

                  with col2:
                     
                     if(rendement(ticker_1)>=0):
                        st.markdown(f'<div style="color:#32CD32;font-size:25px; padding_top: 95px;padding_bottom:120px;padding_left:75px;padding_right:75px; background-color:#90EE90">{f"le rendement aujourdhui est de: ({rendement(ticker_1)} % )"}</div>', unsafe_allow_html=True)
                     else:
                        st.markdown(f'<div style="color:#f00020;font-size:25px; padding_top: 95px;padding_bottom:120px;padding_left:75px;padding_right:75px; background-color:#FFB6C1">{f"le rendement aujourdhui est de: ({rendement(ticker_1)} % )"}</div>', unsafe_allow_html=True)
                     st.altair_chart(chart_rendement(ticker_1))

                  with col22:
                     
                     if(rendement(ticker_2)>=0):
                        st.markdown(f'<div style="color:#32CD32;font-size:25px; padding_top: 95px;padding_bottom:120px;padding_left:75px;padding_right:75px; background-color:#90EE90">{f"le rendement aujourdhui est de: ({rendement(ticker_2)} % )"}</div>', unsafe_allow_html=True)
                     else:
                        st.markdown(f'<div style="color:#f00020;font-size:25px; padding_top: 95px;padding_bottom:120px;padding_left:75px;padding_right:75px; background-color:#FFB6C1">{f"le rendement aujourdhui est de: ({rendement(ticker_2)} % )"}</div>', unsafe_allow_html=True)
                    
                     st.altair_chart(chart_rendement(ticker_1)) 
            else:
               if(ticker_3 !=''):
                   
                   with col1:
                     
                     st.line_chart(df_ticker(ticker_1)[['Low','High']])
                     st.bar_chart(df_ticker(ticker_1)['High'])

                   with col13:

                     st.line_chart(df_ticker(ticker_3)[['Low','High']])
                     st.bar_chart(df_ticker(ticker_3)['High'])

                   with col2:
                  
                     if(rendement(ticker_1)>=0):
                        st.markdown(f'<div style="color:#32CD32;font-size:25px; padding_top: 95px;padding_bottom:120px;padding_left:75px;padding_right:75px; background-color:#90EE90">{f"le rendement aujourdhui est de: ({rendement(ticker_1)} % )"}</div>', unsafe_allow_html=True)
                     else:
                        st.markdown(f'<div style="color:#f00020;font-size:25px; padding_top: 95px;padding_bottom:120px;padding_left:75px;padding_right:75px; background-color:#FFB6C1">{f"le rendement aujourdhui est de: ({rendement(ticker_1)} % )"}</div>', unsafe_allow_html=True)
                     st.altair_chart(chart_rendement(ticker_1))

                   with col23:  
                     if(rendement(ticker_3)>=0):
                        st.markdown(f'<div style="color:#32CD32;font-size:25px; padding_top: 95px;padding_bottom:120px;padding_left:75px;padding_right:75px; background-color:#90EE90">{f"le rendement aujourdhui est de: ({rendement(ticker_3)} % )"}</div>', unsafe_allow_html=True)
                     else:
                        st.markdown(f'<div style="color:#f00020;font-size:25px; padding_top: 95px;padding_bottom:120px;padding_left:75px;padding_right:75px; background-color:#FFB6C1">{f"le rendement aujourdhui est de: ({rendement(ticker_3)} % )"}</div>', unsafe_allow_html=True)
                     st.altair_chart(chart_rendement(ticker_1))

 
               else:
                   
                   with col1:
                     st.line_chart(df_ticker(ticker_1)[['Low','High']])
                     st.bar_chart(df_ticker(ticker_1)['High'])
                   
                   
                   with col2:
                     if(rendement(ticker_1)>=0):
                        st.markdown(f'<div style="color:#32CD32;font-size:25px; padding_top: 95px;padding_bottom:120px;padding_left:75px;padding_right:75px; background-color:#90EE90">{f"le rendement aujourdhui est de: ({rendement(ticker_1)} % )"}</div>', unsafe_allow_html=True)
                     else:
                        st.markdown(f'<div style="color:#f00020;font-size:25px; padding_top: 95px;padding_bottom:120px;padding_left:75px;padding_right:75px; background-color:#FFB6C1">{f"le rendement aujourdhui est de: ({rendement(ticker_1)} % )"}</div>', unsafe_allow_html=True)
                     st.altair_chart(chart_rendement(ticker_1))
         else:
            if(ticker_2 != ''):
               

               if(ticker_3 != ''):
                  with col12:
                     st.line_chart(df_ticker(ticker_2)[['Low','High']])
                     st.bar_chart(df_ticker(ticker_2)[['Low','High']])
                  with col13:
                     st.line_chart(df_ticker(ticker_3)[['Low','High']])
                     st.bar_chart(df_ticker(ticker_3)['High'])

                  with col22:
                                          
                     if(rendement(ticker_2)>=0):
                        st.markdown(f'<div style="color:#32CD32;font-size:25px; padding_top: 95px;padding_bottom:120px;padding_left:75px;padding_right:75px; background-color:#90EE90">{f"le rendement aujourdhui est de: ({rendement(ticker_2)} % )"}</div>', unsafe_allow_html=True)
                     else:
                        st.markdown(f'<div style="color:#f00020;font-size:25px; padding_top: 95px;padding_bottom:120px;padding_left:75px;padding_right:75px; background-color:#FFB6C1">{f"le rendement aujourdhui est de: ({rendement(ticker_2)} % )"}</div>', unsafe_allow_html=True)
                     st.altair_chart(chart_rendement(ticker_2))

                     

                  with col23:   
                     if(rendement(ticker_3)>=0):
                        st.markdown(f'<div style="color:#32CD32;font-size:25px; padding_top: 95px;padding_bottom:120px;padding_left:75px;padding_right:75px; background-color:#90EE90">{f"le rendement aujourdhui est de: ({rendement(ticker_3)} % )"}</div>', unsafe_allow_html=True)
                     else:
                        st.markdown(f'<div style="color:#f00020;font-size:25px; padding_top: 95px;padding_bottom:120px;padding_left:75px;padding_right:75px; background-color:#FFB6C1">{f"le rendement aujourdhui est de: ({rendement(ticker_3)} % )"}</div>', unsafe_allow_html=True)
                     st.altair_chart(chart_rendement(ticker_3))
                  
               else:
                  with col12:
                     
                     st.line_chart(df_ticker(ticker_2)[['Low','High']])
                     st.bar_chart(df_ticker(ticker_2)[['Low','High']])

                  
                  with col22:
                                       
                     if(rendement(ticker_2)>=0):
                        st.markdown(f'<h1 style="color:#32CD32;font-size:25px; padding_top: 95px;padding_bottom:120px;padding_left:75px;padding_right:75px; background-color:#90EE90">{f"le rendement aujourdhui est de: ({rendement(ticker_2)} % )"}</h1>', unsafe_allow_html=True)
                     else:
                        st.markdown(f'<h1 style="color:#f00020;font-size:25px; padding_top: 95px;padding_bottom:120px;padding_left:75px;padding_right:75px; background-color:#FFB6C1">{f"le rendement aujourdhui est de: ({rendement(ticker_2)} % )"}</h1>', unsafe_allow_html=True)
                     st.altair_chart(chart_rendement(ticker_2))
                  
            else:
               

               if(ticker_3 != ''):
                  with col13:
                     st.line_chart(df_ticker(ticker_3)[['Low','High']])
                     st.bar_chart(df_ticker(ticker_3)[['Low','High']])

                  
                  with col23:
                     if(rendement(ticker_3)>=0):
                        st.markdown(f'<h1 style="color:#32CD32;font-size:25px; padding_top: 95px;padding_bottom:120px;padding_left:75px;padding_right:75px; background-color:#90EE90">{f"le rendement aujourdhui est de: ({rendement(ticker_3)} % )"}</h1>', unsafe_allow_html=True)
                     else:
                        st.markdown(f'<h1 style="color:#f00020;font-size:25px; padding_top: 95px;padding_bottom:120px;padding_left:75px;padding_right:75px; background-color:#FFB6C1">{f"le rendement aujourdhui est de: ({rendement(ticker_3)} % )"}</h1>', unsafe_allow_html=True)
                     st.altair_chart(chart_rendement(ticker_1))
               else:
                  st.write('')
   #créer la table achat               
   table_achat=""" 
               CREATE TABLE IF NOT EXISTS achat (
                    id_achat INT NOT NULL AUTO_INCREMENT,
                    action VARCHAR(40)NOT NULL,
                    quantité INT NOT NULL,
                    capital_restant FLOAT NOT NULL,
                    valeur FLOAT NOT NULL,
                    date_achat DATETIME NOT NULL,
                    Multiples_buy VARCHAR(5) NOT NULL,
                    id_utilisateur INT NOT NULL,
                    PRIMARY KEY(id_achat),
                    FOREIGN KEY(id_utilisateur) REFERENCES utilisateurs (id_utilisateur)
                ); """


   try:
    engine.execute(table_achat)
   except Exception as e:
    st.write('Message d\'erreur : \n{}'.format(e))
   
 
   if (acheter):
      id_util=''
      id_utilisateur=pd.read_sql("""SELECT id_utilisateur FROM utilisateur WHERE nom like '%{}%' and prénom like '%{}%'""".format(nom,prénom),connection)
      for i in id_utilisateur['id_utilisateur']:
         id_util=i

      def get_capital(): 
         capital= pd.read_sql("""SELECT capital FROM utilisateur WHERE nom like '%{}%' and prénom like '%{}%'""".format(nom,prénom),connection)
         for i in capital['capital']:
            return i
      def get_cout(ticker,quantité_ticker):
         return(prix_jour(ticker,date_fin_cotat)*(int(quantité_ticker)))#changer 

      def get_rest_capital(ticker,quantité_ticker):
         return(get_capital()-get_cout(ticker,quantité_ticker))
      
      mutiple_buy=''
      
      if (cours== 'Multiples Cours'):
         mutiple_buy='Oui'
         #inserer dans la table achat pour chaque achat effectué
         if(ticker_1 == ''):
            if(ticker_2 ==''):
               if(ticker_3 ==''):
                  st.error(' vous êtes en multiples Cours, vous devez acheter au moins 2 tikers')
               else:
                  st.error(' vous êtes en multiples Cours, vous devez acheter au moins 2 tikers')
            else:
               if(ticker_3 == ''):
                  st.error('vous êtes en multiples Cours, vous devez acheter au moins 2 tikers')
               else:
                  cout= get_cout(ticker_2,quantité_ticket_2)+get_cout(ticker_3,quantité_ticket_3)

                  rest_capital= get_capital()-cout

                  if(get_capital()< cout):
                     st.write('votre capital est insuffisant')
                  else:
                     cur.execute("""UPDATE utilisateur SET capital = {} WHERE nom like '%{}%' and prénom like '%{}%' and mot_de_passe like '%{}%' """.format(rest_capital,nom,prénom,mot_de_passe))
                     cur.execute("INSERT INTO achat (action,quantité,capital_restant,valeur,date_achat,Multiples_buy,id_utilisateur) VALUES ('{}','{}','{}','{}','{}','{}','{}')".format(ticker_2,quantité_ticket_2,get_rest_capital(ticker_2,quantité_ticket_2),get_cout(ticker_2,quantité_ticket_2),datetime.now(),mutiple_buy,id_util))
                     cur.execute("INSERT INTO achat (action,quantité,capital_restant,valeur,date_achat,Multiples_buy,id_utilisateur) VALUES ('{}','{}','{}','{}','{}','{}','{}')".format(ticker_3,quantité_ticket_3,get_rest_capital(ticker_3,quantité_ticket_3),get_cout(ticker_3,quantité_ticket_3),datetime.now(),mutiple_buy,id_util))
                     st.success('Votre achat est enregistré avec succé')
         else:
            if ((ticker_2 !='')):
               if(ticker_3 !=''):
                  cout= get_cout(ticker_2,quantité_ticket_2)+get_cout(ticker_3,quantité_ticket_3)+get_cout(ticker_1,quantité_ticket_1)
                  rest_capital= get_capital()-cout
                  if(get_capital()< cout):
                     st.write('votre capital est insuffisant')
                  else:
                     cur.execute("""UPDATE utilisateur SET capital = {} WHERE nom like '%{}%' and prénom like '%{}%' and mot_de_passe like '%{}%' """.format(rest_capital,nom,prénom,mot_de_passe))
                     cur.execute("INSERT INTO achat (action,quantité,capital_restant,valeur,date_achat,Multiples_buy,id_utilisateur) VALUES ('{}','{}','{}','{}','{}','{}','{}')".format(ticker_1,quantité_ticket_1,get_rest_capital(ticker_1,quantité_ticket_1),get_cout(ticker_1,quantité_ticket_1),datetime.now(),mutiple_buy,id_util))
                     cur.execute("INSERT INTO achat (action,quantité,capital_restant,valeur,date_achat,Multiples_buy,id_utilisateur) VALUES ('{}','{}','{}','{}','{}','{}','{}')".format(ticker_2,quantité_ticket_2,get_rest_capital(ticker_2,quantité_ticket_2),get_cout(ticker_2,quantité_ticket_2),datetime.now(),mutiple_buy,id_util))
                     cur.execute("INSERT INTO achat (action,quantité,capital_restant,valeur,date_achat,Multiples_buy,id_utilisateur) VALUES ('{}','{}','{}','{}','{}','{}','{}')".format(ticker_3,quantité_ticket_3,get_rest_capital(ticker_3,quantité_ticket_3),get_cout(ticker_3,quantité_ticket_3),datetime.now(),mutiple_buy,id_util))
                     st.success('Votre achat est enregistré avec succé')
               else:
                  cout= get_cout(ticker_2,quantité_ticket_2)+get_cout(ticker_1,quantité_ticket_1)
                  rest_capital= get_capital()-cout
                  if(get_capital()< cout):
                     st.write('votre capital est insuffisant')
                  else:
                     cur.execute("""UPDATE utilisateur SET capital = {} WHERE nom like '%{}%' and prénom like '%{}%' and mot_de_passe like '%{}%' """.format(rest_capital,nom,prénom,mot_de_passe))
                     cur.execute("INSERT INTO achat (action,quantité,capital_restant,valeur,date_achat,Multiples_buy,id_utilisateur) VALUES ('{}','{}','{}','{}','{}','{}','{}')".format(ticker_1,quantité_ticket_1,get_rest_capital(ticker_1,quantité_ticket_1),get_cout(ticker_1,quantité_ticket_1),datetime.now(),mutiple_buy,id_util))
                     cur.execute("INSERT INTO achat (action,quantité,capital_restant,valeur,date_achat,Multiples_buy,id_utilisateur) VALUES ('{}','{}','{}','{}','{}','{}','{}')".format(ticker_2,quantité_ticket_2,get_rest_capital(ticker_2,quantité_ticket_2),get_cout(ticker_2,quantité_ticket_2),datetime.now(),mutiple_buy,id_util))
                     st.success('Votre achat est enregistré avec succé')
            else:
               if (ticker_3 !=''):
                  cout= get_cout(ticker_1,quantité_ticket_1)+get_cout(ticker_3,quantité_ticket_3)
                  rest_capital= get_capital()-cout
                  if(get_capital()< cout):
                     st.write('votre capital est insuffisant')
                  else:
                     
                     cur.execute("INSERT INTO achat (action,quantité,capital_restant,valeur,date_achat,Multiples_buy,id_utilisateur) VALUES ('{}','{}','{}','{}','{}','{}','{}')".format(ticker_3,quantité_ticket_3,get_rest_capital(ticker_3,quantité_ticket_3),get_cout(ticker_3,quantité_ticket_3),datetime.now(),mutiple_buy,id_util))
                     cur.execute("INSERT INTO achat (action,quantité,capital_restant,valeur,date_achat,Multiples_buy,id_utilisateur) VALUES ('{}','{}','{}','{}','{}','{}','{}')".format(ticker_1,quantité_ticket_1,get_rest_capital(ticker_1,quantité_ticket_1),get_cout(ticker_1,quantité_ticket_1),datetime.now(),mutiple_buy,id_util))
                     cur.execute("""UPDATE utilisateur SET capital = {} WHERE nom like '%{}%' and prénom like '%{}%' and mot_de_passe like '%{}%' """.format(rest_capital,nom,prénom,mot_de_passe))
                     st.success('Votre achat est enregistré avec succé')
               else:   
                  st.error(' vous êtes en multiples Cours, vous devez acheter au moins 2 tikers')
      else:
         mutiple_buy='Non'
         if(ticker_1 != ''):
            cout= get_cout(ticker_1,quantité_ticket_1)
            rest_capital= get_capital()-cout

            if(get_capital()< cout):
               st.write('votre capital est insuffisant')
            else:
               
               cur.execute("""UPDATE utilisateur SET capital = {} WHERE nom like '%{}%' and prénom like '%{}%' and mot_de_passe like '%{}%' """.format(rest_capital,nom,prénom,mot_de_passe))
               cur.execute("INSERT INTO achat (action,quantité,capital_restant,valeur,date_achat,Multiples_buy,id_utilisateur) VALUES ('{}','{}','{}','{}','{}','{}','{}')".format(ticker_1,quantité_ticket_1,get_rest_capital(ticker_1,quantité_ticket_1),get_cout(ticker_1,quantité_ticket_1),datetime.now(),mutiple_buy,id_util))

               st.success('Votre achat est enregistré avec succé')
         else:
            st.error('il faut saisir un ticket')

      
 connection.commit()
 cur.close()

     


  

   

 