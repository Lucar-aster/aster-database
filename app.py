import streamlit as st
from st_supabase_connection import SupabaseConnection

# Configurazione Pagina
st.set_page_config(page_title="Gestore Commesse", layout="wide")

# Connessione a Supabase
conn = st.connection("supabase", type=SupabaseConnection)

st.title("🏗️ Gestione Commesse e Ordini")

# --- BARRA LATERALE PER INSERIMENTO ---
with st.sidebar:
    st.header("Nuovo Inserimento")
    tipo = st.radio("Cosa vuoi inserire?", ["Commessa", "Ordine", "Documento"])

    if tipo == "Commessa":
        nome_c = st.text_input("Nome Commessa")
        if st.button("Salva Commessa"):
            conn.table("commesse").insert({"nome": nome_c}).execute()
            st.success("Commessa salvata!")

    elif tipo == "Ordine":
        c_list = conn.table("commesse").select("*").execute()
        nomi_c = {c['nome']: c['id'] for c in c_list.data}
        scelta_c = st.selectbox("Per quale commessa?", list(nomi_c.keys()))
        nome_o = st.text_input("Nome Sottogruppo/Ordine")
        if st.button("Salva Ordine"):
            conn.table("ordini").insert({"commessa_id": nomi_c[scelta_c], "nome": nome_o}).execute()
            st.success("Ordine salvato!")

# --- AREA PRINCIPALE: REGISTRAZIONE DOCUMENTO ---
st.header("📂 Registra Documento su più Ordini")

# 1. Seleziona Ordini (anche di commesse diverse se vuoi)
tutti_ordini = conn.table("ordini").select("id, nome").execute()
dizionario_ordini = {o['nome']: o['id'] for o in tutti_ordini.data}

ordini_scelti = st.multiselect("Seleziona uno o più Ordini/Sottogruppi", list(dizionario_ordini.keys()))

nome_doc = st.text_input("Nome del File (es. Planimetria Variante)")
path_doc = st.text_input("Percorso locale (es. D:/Lavori/file.pdf)")

if st.button("Indicizza Documento"):
    if ordini_scelti and nome_doc and path_doc:
        # Inserisce il documento
        res = conn.table("documenti").insert({"nome": nome_doc, "percorso": path_doc}).execute()
        doc_id = res.data[0]['id']
        
        # Inserisce i collegamenti nella tabella ponte
        for o_nome in ordini_scelti:
            conn.table("ponte").insert({"documenti_id": doc_id, "ordine_id": dizionario_ordini[o_nome]}).execute()
        
        st.success("Documento indicizzato correttamente!")
    else:
        st.error("Compila tutti i campi e seleziona almeno un ordine.")

# --- VISUALIZZAZIONE ---
st.divider()
st.subheader("🔍 Consulta Documenti per Ordine")
ordine_filtro = st.selectbox("Scegli un ordine per vedere i file associati", list(dizionario_ordini.keys()))

if ordine_filtro:
    o_id = dizionario_ordini[ordine_filtro]
    # Query complessa: trova i documenti collegati a questo ordine
    docs = conn.table("ponte").select("documenti(nome, percorso)").eq("ordine_id", o_id).execute()
    
    for item in docs.data:
        d = item['documenti']
        st.write(f"📄 **{d['nome']}**")
        st.code(d['percorso'])
