import streamlit as st
import requests
import re
import json
from bs4 import BeautifulSoup

st.set_page_config(page_title="Catalogue Magic Pixel", layout="wide")

st.title("📸 Catalogue de Prompts & Photos Avant/Après")
st.markdown("### Extraire automatiquement vos prompts et images depuis Gemini")

url = st.text_input(
    "🔗 Collez votre lien Gemini :",
    placeholder="https://gemini.google.com/share/..."
)

if st.button("🚀 Extraire le contenu", type="primary") and url:
    with st.spinner("Récupération du contenu..."):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
            }
            
            r = requests.get(url, headers=headers, timeout=20)
            r.raise_for_status()
            
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Extraire les images
            images = []
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if src and ('gstatic.com' in src or 'googleusercontent.com' in src):
                    images.append(src)
            
            # Extraire le texte (prompts)
            scripts = soup.find_all('script')
            text_content = []
            
            for script in scripts:
                if script.string:
                    # Chercher les patterns de texte dans les données JSON
                    matches = re.findall(r'"text"\s*:\s*"([^"]+)"', script.string)
                    text_content.extend(matches)
            
            # Affichage
            st.success("✅ Contenu extrait avec succès !")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📝 Prompts trouvés")
                if text_content:
                    for i, text in enumerate(text_content[:10], 1):
                        # Nettoyer le texte des caractères d'échappement
                        clean_text = text.replace('\\n', ' ').replace('\\', '')
                        if len(clean_text) > 50:
                            with st.expander(f"Prompt {i}"):
                                st.write(clean_text)
                else:
                    st.info("Aucun prompt textuel trouvé")
            
            with col2:
                st.subheader("🖼️ Images trouvées")
                if images:
                    st.write(f"**{len(images)} images détectées**")
                    for i, img_url in enumerate(images[:20], 1):
                        st.image(img_url, caption=f"Image {i}", use_container_width=True)
                else:
                    st.info("Aucune image trouvée")
            
            # Section données brutes
            with st.expander("🔍 Voir les données brutes (debug)"):
                st.json({
                    "source": url,
                    "images_count": len(images),
                    "prompts_count": len(text_content),
                    "images": images[:5],
                    "prompts": text_content[:5]
                })
                
        except Exception as e:
            st.error(f"❌ Erreur : {str(e)}")
else:
    st.info("👆 Entrez un lien Gemini ci-dessus pour commencer")
