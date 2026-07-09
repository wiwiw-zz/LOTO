import streamlit as st
import datetime
import json
from supabase import create_client, Client

# =====================================================================
# CONFIGURATION DE LA PAGE & DESIGN ULTRA-MOBILE (RESPONSIVE)
# =====================================================================
st.set_page_config(page_title="Système LOTO - Sécurité", page_icon="🔒", layout="centered")

# CSS hautement optimisé pour l'affichage sur smartphone et tablette
st.markdown("""
    <style>
    /* Masquer tous les menus et barres Streamlit/GitHub */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    .stAppHeader {display: none !important;}
    .stAppDeployButton {display: none !important;}
    footer {display: none !important; visibility: hidden !important;}
    div[data-testid="stFooter"] {display: none !important;}
    div[data-testid="stThemeProvider"] {display: none !important;}
    .viewerBadge_link__1S137 {display: none !important;}
    
    /* Optimisation des marges pour mobile (évite de devoir scroller) */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* Design responsive du logo Managem pour qu'il s'adapte à tous les écrans */
    .logo-container {
        text-align: center;
        margin-bottom: 15px;
    }
    .logo-container img {
        width: 100%;
        max-width: 220px; /* Taille idéale sur PC */
        height: auto;
    }
    @media (max-width: 480px) {
        .logo-container img {
            max-width: 160px; /* Taille ajustée pour les petits écrans de téléphone */
        }
    }

    /* Ajustement des boutons et formulaires pour le tactile */
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        height: 3.2em; 
        font-weight: bold; 
        font-size: 16px !important; /* Facile à cliquer avec le pouce */
    }
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

# Initialisation des variables de session
if "employe" not in st.session_state:
    st.session_state.employe = None
if "systeme" not in st.session_state:
    st.session_state.systeme = None
if "succes_action" not in st.session_state:
    st.session_state.succes_action = None

# Détection automatique de la machine via le QR Code (Lien URL)
query_params = st.query_params
if "machine" in query_params and st.session_state.systeme is None:
    code_url = query_params["machine"]
    try:
        res_url = supabase.table("systemes").select("*").eq("code_qr_recherche", code_url).execute()
        if res_url.data:
            st.session_state.systeme = res_url.data[0]
    except:
        pass

# =====================================================================
# ÉCRAN DE SUCCÈS (Bloquant, demande validation)
# =====================================================================
if st.session_state.succes_action:
    st.success(st.session_state.succes_action)
    if st.button("🔄 Continuer (Retour à l'accueil)"):
        st.session_state.succes_action = None
        st.session_state.systeme = None
        st.session_state.employe = None
        st.rerun()
    st.stop()

# =====================================================================
# ÉCRAN 1 : CONNEXION SÉCURISÉE (AVEC LOGO RESPONSIVE)
# =====================================================================
if st.session_state.employe is None:
    # Conteneur de logo optimisé pour la taille d'écran
    st.markdown("""
        <div class="logo-container">
            <img src="https://images.seeklogo.com/logo-png/31/1/groupe-managem-logo-png_seeklogo-318160.png" alt="Logo Managem">
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center; color: #2c3e50; margin-top:0; font-size: 20px;'>🔒 Connexion Sécurisée LOTO</h3>", unsafe_allow_html=True)
    
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
# ÉCRAN 2 : ACCUEIL & RECHERCHE
# =====================================================================
elif st.session_state.systeme is None:
    st.markdown(f"<h4 style='color: #27ae60;'>👋 Bienvenue, {st.session_state.employe['nom_prenom']}</h4>", unsafe_allow_html=True)
    st.markdown("<h5>🏠 Accueil - Recherche Système</h5>", unsafe_allow_html=True)
    
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
# ÉCRAN 3 : CHECK-LIST
# =====================================================================
else:
    sys_nom = st.session_state.systeme["nom"]
    sys_id = st.session_state.systeme["id"]
    
    try:
        res_etat = supabase.table("historique_consignations").select("action").eq("nom_systeme", sys_nom).order("created_at", desc=True).limit(1).execute()
        is_consigne = res_etat.data and res_etat.data[0]["action"] == "CONSIGNATION"
    except:
        is_consigne = False

    col_btn, col_status = st.columns([1, 1])
    with col_btn:
        if st.button("⬅ Retour"):
            st.session_state.systeme = None
            st.rerun()
            
    with col_status:
        if is_consigne:
            st.markdown("<p style='text-align:right; font-weight:bold; color:#c0392b; font-size:15px; margin-top:10px;'>🔴 CONSIGNÉ</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='text-align:right; font-weight:bold; color:#27ae60; font-size:15px; margin-top:10px;'> 🟢 LIBRE</p>", unsafe_allow_html=True)

    action_type = "DECONSIGNATION" if is_consigne else "CONSIGNATION"
    couleur = "#27ae60" if is_consigne else "#c0392b"
    titre_action = "🔓 Déconsignation" if is_consigne else "🔴 Consignation"
    instruction = "Retirez vos cadenas et cochez pour libérer :" if is_consigne else "Cochez après pose de votre cadenas :"

    st.markdown(f"<h3 style='color: {couleur}; font-size: 20px; margin-top: 10px;'>{titre_action} : {sys_nom}</h3>", unsafe_allow_html=True)
    st.info(instruction)

    try:
        res_eq = supabase.table("equipments").select("*").eq("systeme_id", sys_id).execute()
        equipements = [e["nom_equipement"] for e in res_eq.data]
    except:
        equipements = []

    cases_cochees = []
    with st.container(border=True):
        for eq in equipements:
            coche = st.checkbox(eq, key=eq)
            cases_cochees.append(coche)

    toutes_cochees = all(cases_cochees) if cases_cochees else False
    
    if st.button(f"VALIDER LA {action_type}", type="primary", disabled=not toutes_cochees):
        donnees = {
            "matricule_employe": st.session_state.employe["matricule"],
            "nom_systeme": sys_nom,
            "action": action_type,
            "equipement": ", ".join(equipements)
        }
        try:
            supabase.table("historique_consignations").insert([donnees]).execute()
            
            with open("backup_securite_loto.json", "a", encoding="utf-8") as f:
                donnees["date_heure"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(json.dumps(donnees, ensure_ascii=False) + "\n")
                
            if action_type == "CONSIGNATION":
                st.session_state.succes_action = f"🎉 CONSIGNATION RÉUSSIE ! Le système {sys_nom} est maintenant sécurisé."
            else:
                st.session_state.succes_action = f"🎉 DÉCONSIGNATION RÉUSSIE ! Le système {sys_nom} est libéré."
            
            st.rerun()
        except Exception as e:
            st.error(f"Erreur d'enregistrement : {e}")
