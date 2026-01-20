
import streamlit as st
import pandas as pd
import altair as alt
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col, count

# 1. Connexion au contexte Snowflake
session = get_active_session()

st.title("🛡️ Dashboard Analyse Tickets")

# 2. Chargement optimisé des données
# On ne charge QUE les colonnes nécessaires pour éviter de charger les textes lourds (BODY/ANSWER)
@st.cache_data
def load_data():
    try:
        df = session.table("PROJECT_DB.PUBLIC.SUPPORT_TICKETS").select(
            col("QUEUE"), 
            col("PRIORITY"), 
            col("TYPE"),
            col("LANGUAGE")
        ).to_pandas()
        
        # Nettoyage simple : on remplace les valeurs nulles par 'Inconnu' pour l'affichage
        df = df.fillna('Inconnu')
        return df
    except Exception as e:
        st.error(f"Erreur de chargement : {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    
    # --- LAYOUT : 2 Colonnes ---
    col1, col2 = st.columns(2)
    
    # KPI Rapides
    with col1:
        st.metric("Total Tickets", len(df))
    with col2:
        # Compte le nombre de files d'attente (Queues) actives
        st.metric("Files (Queues) Actives", df['QUEUE'].nunique())

    st.divider()

    # --- VISUALISATION 1 : Charge par Queue et Priorité ---
    st.subheader("1. Où sont les urgences ? (Queue vs Priorité)")
    st.caption("Permet d'identifier si une file spécifique accumule trop de tickets 'High'.")

    chart_queue = alt.Chart(df).mark_bar().encode(
        x=alt.X('QUEUE', title='File d\'attente', sort='-y'),
        y=alt.Y('count()', title='Volume de tickets'),
        # On utilise la couleur pour montrer la priorité
        color=alt.Color('PRIORITY', title='Priorité', 
                        scale=alt.Scale(scheme='redyellowblue', domain=['High', 'Medium', 'Low'])), 
        tooltip=['QUEUE', 'PRIORITY', 'count()']
    ).properties(height=400)

    st.altair_chart(chart_queue, use_container_width=True)

    # --- VISUALISATION 2 : Typologie des demandes ---
    st.subheader("2. De quoi parlent les tickets ?")
    
    # On compte les types et on trie
    type_counts = df['TYPE'].value_counts().reset_index()
    type_counts.columns = ['TYPE', 'COUNT']
    
    chart_type = alt.Chart(type_counts).mark_bar().encode(
        x=alt.X('COUNT', title='Nombre de tickets'),
        y=alt.Y('TYPE', title='Type de demande', sort='-x'), # Tri décroissant
        color=alt.value('#29b5e8'), # Couleur bleu Snowflake fixe
        tooltip=['TYPE', 'COUNT']
    ).properties(height=400)

    st.altair_chart(chart_type, use_container_width=True)

else:
    st.warning("La table PROJECT_DB.PUBLIC.SUPPORT_TICKETS semble vide ou inaccessible.")