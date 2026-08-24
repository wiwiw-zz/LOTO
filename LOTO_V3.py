import streamlit as st
import datetime
import json
import csv
import io
import pandas as pd
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
        max-width: 220px;
        height: auto;
    }
    @media (max-width: 480px) {
        .logo-container img {
            max-width: 160px;
        }
    }

    /* Ajustement des boutons et formulaires pour le tactile */
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        height: 3.2em; 
        font-weight: bold; 
        font-size: 16px !important;
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
if "page_admin" not in st.session_state:
    st.session_state.page_admin = None

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
    st.markdown("""
        <div class="logo-container">
            <img src="https://www.managemgroup.com/themes/managem/logo.png" alt="Logo Managem">
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
# ÉCRAN ADMIN : GESTION ADMIN UNIQUEMENT
# =====================================================================
elif st.session_state.employe["matricule"] == "EMP-5678":
    st.markdown("<h3 style='text-align: center; color: #8e44ad;'>👑 PANNEAU ADMINISTRATION</h3>", unsafe_allow_html=True)
    
    # Boutons de navigation admin
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Télécharger"):
            st.session_state.page_admin = "telechargement"
    
    with col2:
        if st.button("➕ Insertion"):
            st.session_state.page_admin = "insertion"
    
    with col3:
        if st.button("🗄️ Base de Données"):
            st.session_state.page_admin = "base_donnees"
    
    st.write("---")
    
    # PAGE 1 : TÉLÉCHARGEMENT
    if st.session_state.page_admin == "telechargement":
        st.markdown("<h4 style='color: #2980b9;'>📊 Télécharger l'Historique</h4>", unsafe_allow_html=True)
        
        # Sélecteur de mois
        st.markdown("**📅 Sélectionner le mois :**")
        col_mois, col_annee = st.columns(2)
        
        with col_mois:
            mois_selected = st.selectbox(
                "Mois",
                list(range(1, 13)),
                format_func=lambda x: datetime.date(2024, x, 1).strftime("%B - %m")
            )
        
        with col_annee:
            annee_selected = st.number_input("Année", value=datetime.datetime.now().year, min_value=2020)
        
        # Récupérer les données filtrées par mois
        try:
            # Récupérer l'historique complet
            res_historique = supabase.table("historique_consignations").select("*").order("created_at", desc=True).execute()
            
            if res_historique.data:
                # Convertir en DataFrame
                df = pd.DataFrame(res_historique.data)
                
                # Convertir la colonne created_at en datetime
                if 'created_at' in df.columns:
                    df['created_at'] = pd.to_datetime(df['created_at'])
                    
                    # Filtrer par mois et année
                    df_filtered = df[
                        (df['created_at'].dt.month == mois_selected) & 
                        (df['created_at'].dt.year == annee_selected)
                    ]
                else:
                    df_filtered = df
                
                if len(df_filtered) > 0:
                    st.success(f"✅ {len(df_filtered)} entrées trouvées pour {datetime.date(annee_selected, mois_selected, 1).strftime('%B %Y')}")
                    
                    # Boutons de téléchargement (3 colonnes)
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # Télécharger en EXCEL
                        try:
                            output = io.BytesIO()
                            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                df_filtered.to_excel(writer, index=False, sheet_name='Historique')
                                
                                # Formater le fichier Excel
                                workbook = writer.book
                                worksheet = writer.sheets['Historique']
                                
                                # Ajuster la largeur des colonnes
                                for i, column in enumerate(df_filtered.columns, 1):
                                    worksheet.column_dimensions[chr(64 + i)].width = 20
                            
                            output.seek(0)
                            st.download_button(
                                label="📊 Excel",
                                data=output.getvalue(),
                                file_name=f"historique_loto_{annee_selected}-{mois_selected:02d}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        except Exception as e:
                            st.error(f"Erreur Excel : {e}")
                    
                    with col2:
                        # Télécharger en JSON
                        try:
                            json_data = json.dumps(df_filtered.to_dict('records'), ensure_ascii=False, indent=2, default=str)
                            st.download_button(
                                label="📄 JSON",
                                data=json_data,
                                file_name=f"historique_loto_{annee_selected}-{mois_selected:02d}.json",
                                mime="application/json"
                            )
                        except Exception as e:
                            st.error(f"Erreur JSON : {e}")
                    
                    with col3:
                        # Télécharger en CSV
                        try:
                            csv_data = df_filtered.to_csv(index=False, encoding='utf-8')
                            st.download_button(
                                label="📋 CSV",
                                data=csv_data,
                                file_name=f"historique_loto_{annee_selected}-{mois_selected:02d}.csv",
                                mime="text/csv"
                            )
                        except Exception as e:
                            st.error(f"Erreur CSV : {e}")
                    
                    # Afficher un aperçu
                    st.markdown("**📋 Aperçu des données :**")
                    st.dataframe(df_filtered, use_container_width=True)
                else:
                    st.warning(f"⚠️ Aucune donnée trouvée pour {datetime.date(annee_selected, mois_selected, 1).strftime('%B %Y')}")
            else:
                st.info("📭 Aucun historique disponible.")
                
        except Exception as e:
            st.error(f"Erreur de récupération : {e}")
    
    # PAGE 2 : INSERTION DE DONNÉES
    elif st.session_state.page_admin == "insertion":
        st.markdown("<h4 style='color: #27ae60;'>➕ Insertion de Nouveaux Enregistrements</h4>", unsafe_allow_html=True)
        
        # Sélectionner le type de données à insérer
        type_insertion = st.radio(
            "Que voulez-vous ajouter ?",
            ["Nouvel Employé", "Nouveau Système", "Nouvel Équipement"],
            horizontal=True
        )
        
        st.write("---")
        
        # ================= INSERTION EMPLOYÉ =================
        if type_insertion == "Nouvel Employé":
            st.markdown("<h5 style='color: #e74c3c;'>👤 Ajouter un Nouvel Employé</h5>", unsafe_allow_html=True)
            
            with st.container(border=True):
                col_emp1, col_emp2 = st.columns(2)
                
                with col_emp1:
                    emp_matricule = st.text_input(
                        "🆔 Matricule (Obligatoire)",
                        placeholder="EMP-1234",
                        key="emp_matricule"
                    )
                    emp_nom = st.text_input(
                        "👤 Nom Prénom (Obligatoire)",
                        placeholder="Jean Dupont",
                        key="emp_nom"
                    )
                
                with col_emp2:
                    emp_pin = st.text_input(
                        "🔐 Code PIN (Obligatoire)",
                        placeholder="1234",
                        key="emp_pin",
                        type="password"
                    )
                    emp_poste = st.text_input(
                        "💼 Poste",
                        placeholder="Technicien",
                        key="emp_poste"
                    )
                
                if st.button("✅ Ajouter Employé", type="primary", use_container_width=True):
                    if emp_matricule and emp_nom and emp_pin:
                        try:
                            new_emp = {
                                "matricule": emp_matricule,
                                "nom_prenom": emp_nom,
                                "code_confidentiel": emp_pin,
                                "poste": emp_poste if emp_poste else "Non défini"
                            }
                            supabase.table("employes").insert([new_emp]).execute()
                            st.success(f"✅ Employé '{emp_nom}' ajouté avec succès !")
                            st.balloons()
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur : {str(e)}")
                    else:
                        st.warning("⚠️ Veuillez remplir tous les champs obligatoires (Matricule, Nom, PIN)")
        
        # ================= INSERTION SYSTÈME =================
        elif type_insertion == "Nouveau Système":
            st.markdown("<h5 style='color: #3498db;'>🏭 Ajouter un Nouveau Système</h5>", unsafe_allow_html=True)
            
            with st.container(border=True):
                col_sys1, col_sys2 = st.columns(2)
                
                with col_sys1:
                    sys_nom = st.text_input(
                        "📋 Nom du Système (Obligatoire)",
                        placeholder="Ligne d'embouteillage A",
                        key="sys_nom"
                    )
                    sys_code = st.text_input(
                        "📱 Code QR (Obligatoire)",
                        placeholder="SYS-LIGNE-A",
                        key="sys_code"
                    )
                
                with col_sys2:
                    sys_localisation = st.text_input(
                        "📍 Localisation",
                        placeholder="Atelier A - Zone 1",
                        key="sys_localisation"
                    )
                
                sys_description = st.text_area(
                    "📝 Description du Système",
                    placeholder="Décrivez les caractéristiques du système...",
                    key="sys_description",
                    height=100
                )
                
                if st.button("✅ Ajouter Système", type="primary", use_container_width=True):
                    if sys_nom and sys_code:
                        try:
                            new_sys = {
                                "nom": sys_nom,
                                "code_qr_recherche": sys_code,
                                "localisation": sys_localisation if sys_localisation else "Non définie",
                                "description": sys_description if sys_description else "Aucune description"
                            }
                            supabase.table("systemes").insert([new_sys]).execute()
                            st.success(f"✅ Système '{sys_nom}' ajouté avec succès !")
                            st.balloons()
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur : {str(e)}")
                    else:
                        st.warning("⚠️ Veuillez remplir les champs obligatoires (Nom, Code QR)")
        
        # ================= INSERTION ÉQUIPEMENT =================
        elif type_insertion == "Nouvel Équipement":
            st.markdown("<h5 style='color: #f39c12;'>⚙️ Ajouter un Nouvel Équipement</h5>", unsafe_allow_html=True)
            
            # Récupérer les systèmes disponibles
            try:
                res_systemes = supabase.table("systemes").select("id, nom").execute()
                systemes_list = {s["nom"]: s["id"] for s in res_systemes.data} if res_systemes.data else {}
            except:
                systemes_list = {}
            
            with st.container(border=True):
                col_eq1, col_eq2 = st.columns(2)
                
                with col_eq1:
                    eq_nom = st.text_input(
                        "⚙️ Nom Équipement (Obligatoire)",
                        placeholder="Moteur Principal",
                        key="eq_nom"
                    )
                    eq_type = st.text_input(
                        "🔧 Type",
                        placeholder="Moteur / Pompe / Valve",
                        key="eq_type"
                    )
                
                with col_eq2:
                    if systemes_list:
                        eq_systeme_nom = st.selectbox(
                            "🏭 Système Associé (Obligatoire)",
                            list(systemes_list.keys()),
                            key="eq_systeme_select"
                        )
                        eq_systeme_id = systemes_list[eq_systeme_nom]
                    else:
                        st.warning("❌ Aucun système disponible. Créez d'abord un système.")
                        eq_systeme_id = None
                
                eq_description = st.text_area(
                    "📝 Description",
                    placeholder="Caractéristiques de l'équipement...",
                    key="eq_description",
                    height=100
                )
                
                if st.button("✅ Ajouter Équipement", type="primary", use_container_width=True, disabled=(eq_systeme_id is None)):
                    if eq_nom and eq_systeme_id:
                        try:
                            new_eq = {
                                "nom_equipement": eq_nom,
                                "type": eq_type if eq_type else "Non défini",
                                "systeme_id": eq_systeme_id,
                                "description": eq_description if eq_description else "Aucune description"
                            }
                            supabase.table("equipments").insert([new_eq]).execute()
                            st.success(f"✅ Équipement '{eq_nom}' ajouté avec succès !")
                            st.balloons()
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur : {str(e)}")
                    else:
                        st.warning("⚠️ Veuillez remplir les champs obligatoires")
    
    # PAGE 3 : GESTION BASE DE DONNÉES
    elif st.session_state.page_admin == "base_donnees":
        st.markdown("<h4 style='color: #27ae60;'>🗄️ Gestion Base de Données</h4>", unsafe_allow_html=True)
        
        # Sélectionner une table à visualiser
        table_choice = st.selectbox(
            "Sélectionner une table :",
            ["employes", "systemes", "equipments", "historique_consignations"],
            key="table_select"
        )
        
        st.write("---")
        
        try:
            res_table = supabase.table(table_choice).select("*").limit(100).execute()
            if res_table.data:
                df_table = pd.DataFrame(res_table.data)
                st.markdown(f"**📊 {len(df_table)} entrées dans '{table_choice}'**")
                st.dataframe(df_table, use_container_width=True)
                
                # ================= SECTION SUPPRESSION =================
                st.markdown("<h5 style='color: #e74c3c;'>🗑️ Supprimer un enregistrement</h5>", unsafe_allow_html=True)
                
                if 'id' in df_table.columns:
                    col_del1, col_del2 = st.columns([3, 1])
                    with col_del1:
                        id_to_delete = st.selectbox(
                            "Sélectionner l'ID à supprimer :",
                            df_table['id'].tolist(),
                            key=f"delete_{table_choice}"
                        )
                    with col_del2:
                        if st.button("❌ Supprimer", type="secondary", key=f"btn_del_{table_choice}"):
                            try:
                                supabase.table(table_choice).delete().eq("id", id_to_delete).execute()
                                st.success(f"✅ Enregistrement {id_to_delete} supprimé de '{table_choice}'")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erreur lors de la suppression : {e}")
            else:
                st.write(f"Aucune donnée dans '{table_choice}'.")
        except Exception as e:
            st.error(f"Erreur : {e}")
    
    st.write("---")
    if st.button("🚪 Se déconnecter"):
        st.session_state.employe = None
        st.session_state.page_admin = None
        st.rerun()

# =====================================================================
# ÉCRAN 2 : ACCUEIL & RECHERCHE (Employés normaux)
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
                    
    # BOUTONS D'ACTION DU BAS
    st.write("---")

    if st.button("🚪 Se déconnecter"):
        st.session_state.employe = None
        st.rerun()

# =====================================================================
# ÉCRAN 3 : CHECK-LIST (Employés normaux - Consignation)
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
