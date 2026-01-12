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
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
            }
            
            r = requests.get(url, headers=headers, timeout=20)
            r.raise_for_status()
            
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Méthode 1: Extraire toutes les images
            images = []
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if src and src.startswith('http') and 'gstatic' not in src:
                    if src not in images:
                        images.append(src)
            
            # Méthode 2: Chercher dans les balises <script> pour les images
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    # Chercher les URLs d'images dans le JSON
                    img_matches = re.findall(r'"(https://[^"]*\.(?:jpg|jpeg|png|webp)[^"]*?)"', script.string, re.IGNORECASE)
                    for img_url in img_matches:
                        if img_url not in images and 'gstatic' not in img_url:
                            images.append(img_url)
            
            # Extraire les prompts (texte)
            prompts = []
            
            # Méthode 1: Chercher dans le texte visible
            paragraphs = soup.find_all(['p', 'div'])
            for p in paragraphs:
                text = p.get_text(strip=True)
                # Filtrer les prompts (texte long et en anglais généralement)
                if len(text) > 100 and not text.startswith('Gemini') and 'Copier' not in text:
                    if text not in prompts:
                        prompts.append(text)
            
            # Méthode 2: Extraire depuis le JavaScript/JSON
            for script in scripts:
                if script.string:
                    # Patterns pour trouver du texte de prompt
                    text_matches = re.findall(r'"([^"]{100,})"', script.string)
                    for match in text_matches:
                        # Nettoyer le texte
                        clean = match.replace('\\n', ' ').replace('\\', '').strip()
                        # Vérifier si c'est un prompt (contient des mots-clés d'IA)
                        keywords = ['illustration', 'style', 'painting', 'realistic', 'portrait', 'art', 'image', 'watercolor']
                        if any(kw in clean.lower() for kw in keywords) and len(clean) > 50:
                            if clean not in prompts:
                                prompts.append(clean[:500])  # Limiter à 500 caractères
            
            # Affichage
            st.success("✅ Contenu extrait avec succès !")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📝 Prompts trouvés")
                if prompts:
                    st.write(f"**{len(prompts)} prompts détectés**")
                    for i, text in enumerate(prompts[:10], 1):
                        with st.expander(f"Prompt {i}"):
                            st.write(text)
                else:
                    st.info("Aucun prompt trouvé")
            
            with col2:
                st.subheader("🖼️ Images trouvées")
                if images:
                    st.write(f"**{len(images)} images détectées**")
                    for i, img_url in enumerate(images[:20], 1):
                        try:
                            st.image(img_url, caption=f"Image {i}", use_container_width=True)
                        except:
                            st.write(f"Image {i}: {img_url}")
                else:
                    st.info("Aucune image trouvée")
            
            # Section données brutes
            with st.expander("🔍 Voir les données brutes (debug)"):
                st.json({
                    "source": url,
                    "images_count": len(images),
                    "prompts_count": len(prompts),
                    "images": images[:5],
                    "prompts": [p[:100] + "..." for p in prompts[:5]]
                })
                
        except Exception as e:
            st.error(f"❌ Erreur : {str(e)}")
            import traceback
            st.code(traceback.format_exc())
else:
    st.info("👆 Entrez un lien Gemini ci-dessus pour commencer")
