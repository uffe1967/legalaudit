import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# 1. KLISTRA IN DIN NYCKEL HÄR (mellan citattecknen):
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
def skrapa_webbsida(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style", "nav"]):
            script.extract()
        return soup.get_text(separator=' ', strip=True)
    except Exception as e:
        return f"Kunde inte läsa sidan: {e}"

def analysera_villkor(text_innehall):
    system_prompt = system_prompt = system_prompt = system_prompt = """
    Du är en expert på svensk e-handelsrätt och konsumentköplagen. 
    Din uppgift är att analysera webbsidans text och först avgöra verksamhetens natur.
    
    Steg 1: Bedöm om sidan säljer fysiska produkter, digitala produkter, eller en tjänst/konsultation. 
    Steg 2: Bedöm om köpet sker direkt på sidan eller om kunden omdirigeras till en tredjepart (t.ex. Fiverr).
    
    Utvärdera sedan villkoren baserat på din bedömning:
    - Fysiska varor kräver tydlig info om returfrakt, 3 års reklamationsrätt och 14 dagars ångerrätt.
    - Tjänster kräver info om ångerrätt (men inte returfrakt), och hur ångerrätten påverkas om tjänsten påbörjas med kundens samtycke.
    - Om köpet sker via en tredjepart (som Fiverr), kontrollera om sidan tydligt friskriver sig från transaktionsansvar och hänvisar till tredjepartens villkor. Kontrollera mycket noga i hela texten (särskilt mot slutet) om det redan finns en ansvarsfriskrivning gällande tredjepartstransaktioner innan du föreslår att en sådan saknas.

    Svara strikt med denna struktur:
    - **Verksamhetstyp:** (Din bedömning från Steg 1 och 2)
    - **Status:** (Godkänd / Varning / Underkänd)
    - **Brister som hittades:** (Lista specifika brott mot svensk lag eller otydligheter)
    - **Förslag på förbättring:** (Konkreta råd till företagaren)
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text_innehall[:10000]}
        ],
        temperature=0.1
    )
    return response.choices[0].message.content

# WEBBGRÄNSSNITTET
st.title("⚖️ LegalAudit AI")
st.subheader("Granska din e-handel mot svensk konsumentlagstiftning")

url_input = st.text_input("Webbadress (t.ex. https://minbutik.se/kopvillkor)")

if st.button("Starta granskning"):
    if url_input:
        with st.spinner("Analyserar webbsidan mot svensk lag..."):
            sida_text = skrapa_webbsida(url_input)
            if "Kunde inte läsa" in sida_text:
                st.error(sida_text)
            else:
                rapport = analysera_villkor(sida_text)
                st.success("Analys klar!")
                st.markdown(rapport)
    else:
        st.warning("Du måste skriva in en webbadress först!")
