import streamlit as st
import datetime
import json
from supabase import create_client, Client

# =====================================================================
# CONFIGURATION DE LA PAGE & DESIGN INTERFACE
# =====================================================================
st.set_page_config(page_title="Système LOTO - Sécurité", page_icon="🔒", layout="centered")

# Personnalisation élégante des boutons et des encadrés
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; font-weight: bold; }
    div.stLabel { font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# CONFIGURATION SUPABASE
# =====================================================================
SUPABASE_URL = "https://noyzqijchgowgvdbqawq.supabase.co"
SUPABASE_KEY = "sb_publishable_1IodYTMF_8gD9aQN2blcCA_CjSK0mF2"

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase = init_supabase()
except Exception as e:
    st.error(f"Erreur Supabase : {e}")

# Initialisation des variables de session (mémoire de l'application web)
if "employe" not in st.session_state:
    st.session_state.employe = None
if "systeme" not in st.session_state:
    st.session_state.systeme = None

# =====================================================================
# ÉCRAN 1 : CONNEXION SÉCURISÉE (CHAMPS VIDES)
# =====================================================================
if st.session_state.employe is None:
    st.markdown("<h2 style='text-align: center; color: #2c3e50;'>🔒 Connexion Sécurisée LOTO</h2>", unsafe_allow_html=True)
    
    with st.container(border=True):
        matricule = st.text_input("Numéro Employé (Matricule)", placeholder="Ex: EMP-1234").strip()
        pin = st.text_input("Code Confidentiel (PIN)", type="password", placeholder="••••").strip()
        
        if st.button("ENTRER", type="primary"):
            if matricule and pin:
                try:
                    reponse = supabase.table("employes").select("*").eq("matricule", matricule).eq("code_confidentiel", pin).execute()
                    if reponse.data:
                        st.session_state.employe = reponse.data[0]
                        st.rerun()
                    else:
                        st.error("Matricule ou code PIN incorrect.")
                except Exception as e:
                    st.error(f"Erreur technique : {e}")
            else:
                st.warning("Veuillez remplir tous les champs.")

# =====================================================================
# ÉCRAN 2 : ACCUEIL & RECHERCHE DE LA MACHINE
# =====================================================================
elif st.session_state.systeme is None:
    st.markdown(f"<h3 style='color: #27ae60;'>👋 Bienvenue, {st.session_state.employe['nom_prenom']}</h3>", unsafe_allow_html=True)
    st.markdown("<h4>🏠 Accueil - Recherche Système</h4>", unsafe_allow_html=True)
    
    with st.container(border=True):
        code_recherche = st.text_input("Scanner ou chercher la machine :", placeholder="Ex: Ligne d'embouteillage A")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            btn_chercher = st.button("🔍 Rechercher", type="primary")
        with col2:
            btn_simul = st.button("📷 [QR Test]")
            
        if btn_simul:
            code_recherche = "SYS-LIGNE-A"
            
        if btn_chercher or btn_simul:
            if code_recherche:
                try:
                    res_systeme = supabase.table("systemes").select("*").or_(f"code_qr_recherche.eq.{code_recherche},nom.ilike.%{code_recherche}%").execute()
                    if res_systeme.data:
                        st.session_state.systeme = res_systeme.data[0]
                        st.rerun()
                    else:
                        st.error("Aucun système trouvé.")
                except Exception as e:
                    st.error(f"Erreur de recherche : {e}")
                    
    if st.button("🚪 Se déconnecter"):
        st.session_state.employe = None
        st.rerun()

# =====================================================================
# ÉCRAN 3 : CHECK-LIST DYNAMIQUE (CONSIGNATION / DÉCONSIGNATION)
# =====================================================================
else:
    sys_nom = st.session_state.systeme["nom"]
    sys_id = st.session_state.systeme["id"]
    
    # Lecture en temps réel du dernier état sur Supabase
    try:
        res_etat = supabase.table("historique_consignations").select("action").eq("nom_systeme", sys_nom).order("created_at", desc=True).limit(1).execute()
        is_consigne = res_etat.data and res_etat.data[0]["action"] == "CONSIGNATION"
    except:
        is_consigne = False

    # Barre de navigation haute adaptative
    col_btn, col_status = st.columns([1, 2])
    with col_btn:
        if st.button("⬅ Retour"):
            st.session_state.systeme = None
            st.rerun()
            
    with col_status:
        if is_consigne:
            st.markdown("<p style='text-align:right; font-weight:bold; color:#c0392b; font-size:18px;'>État actuel : 🔴 CONSIGNÉ</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='text-align:right; font-weight:bold; color:#27ae60; font-size:18px;'>État actuel : 🟢 LIBRE</p>", unsafe_allow_html=True)

    # Paramétrage visuel selon le statut (Rouge = Consignation, Vert = Déconsignation)
    action_type = "DECONSIGNATION" if is_consigne else "CONSIGNATION"
    couleur = "#27ae60" if is_consigne else "#c0392b"
    titre_action = "🔓 Déconsignation" if is_consigne else "🔴 Consignation"
    instruction = "Retirez vos cadenas et cochez pour libérer :" if is_consigne else "Cochez après pose de votre cadenas physique :"

    st.markdown(f"<h2 style='color: {couleur};'>{titre_action} : {sys_nom}</h2>", unsafe_allow_html=True)
    st.info(instruction)

    # Récupération dynamique des équipements de la machine
    try:
        res_eq = supabase.table("equipments").select("*").eq("systeme_id", sys_id).execute()
        equipements = [e["nom_equipement"] for e in res_eq.data]
    except:
        equipements = []

    # Génération de la check-list
    cases_cochees = []
    with st.container(border=True):
        for eq in equipements:
            coche = st.checkbox(eq, key=eq)
            cases_cochees.append(coche)

    toutes_cochees = all(cases_cochees) if cases_cochees else False
    
    # Bouton de validation (bloqué tant que tout n'est pas coché)
    if st.button(f"VALIDER LA {action_type}", type="primary", disabled=not toutes_cochees):
        donnees = {
            "matricule_employe": st.session_state.employe["matricule"],
            "nom_systeme": sys_nom,
            "action": action_type,
            "equipement": ", ".join(equipements)
        }
        try:
            # Envoi à Supabase
            supabase.table("historique_consignations").insert([donnees]).execute()
            
            # Double sauvegarde locale réglementaire
            with open("backup_securite_loto.json", "a", encoding="utf-8") as f:
                donnees["date_heure"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(json.dumps(donnees, ensure_ascii=False) + "\n")
                
            st.success("Opération réussie ! Redirection...")
            
            # Déconnexion et reset pour l'opérateur suivant (sécurité d'usine)
            st.session_state.employe = None
            st.session_state.systeme = None
            st.rerun()
        except Exception as e:
            st.error(f"Erreur d'enregistrement : {e}")