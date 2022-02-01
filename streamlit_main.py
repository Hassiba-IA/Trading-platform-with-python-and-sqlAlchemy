import streamlit as st
import passage_ordre
import créer_compte

import historique_achat

PAGES = {
    
    "Créer un compte": créer_compte,
    "Passage de l'ordre": passage_ordre,
    "Historique des transactions":historique_achat
}
selection = st.sidebar.selectbox("Choisissez une page", list(PAGES.keys()))
page=PAGES[selection]
page.page()
 