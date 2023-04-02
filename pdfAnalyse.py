import io
import re
from PIL import Image
import spacy
import PyPDF2
import pytesseract
import streamlit as st
from spacy import displacy
import tabula
import tempfile

spacy_model = "de_core_news_md"
models = ["de_core_news_sm", "de_core_news_md"]

st.title("PDF-Dokument-Analyse")

default_text = '''Boiman Solutions ist ein zukunftsorientiertes Unternehmen, das sich auf Beratung, Qualitätssicherung, Künstliche Intelligenz (KI), Automatisierung, agile Prozesse und mobile App-Entwicklung spezialisiert.
Unsere Expertise ermöglicht es uns, sowohl manuelle als auch digitale Prozesse zu automatisieren, um Abläufe zu optimieren und KI-Technologien nahtlos in Ihre Geschäftsprozesse zu integrieren.
Wir bieten umfassende Unterstützung für Unternehmen jeder Größe, indem wir sie von der Konzeption über die Umsetzung bis hin zur erfolgreichen Markteinführung begleiten und dabei helfen, ihre Abläufe effizienter, intelligenter und zukunftssicher zu gestalten.'''


def extract_images_from_page(page):
    images = []
    if '/XObject' in page['/Resources']:
        x_objects = page['/Resources']['/XObject'].get_object()
        if x_objects is not None:
            for obj in x_objects:
                subtype = x_objects[obj]['/Subtype']
                if subtype == '/Image':
                    image_stream = x_objects[obj].get_data()
                    image = Image.open(io.BytesIO(image_stream))
                    images.append(image)
    return images


def extract_text_from_images(images):
    image_text = []
    for image in images:
        image_text.append(pytesseract.image_to_string(image))
    return image_text


def extract_text_from_images(images):
    image_text = []
    for image in images:
        image_text.append(pytesseract.image_to_string(image))
    return image_text


def extract_information_from_page(page_content, image_text, page_number):
    # Extrahieren von Briefkopf, Absender, Empfänger, Titel, Inhalt usw.
    briefkopf_muster = r"([A-Za-z0-9À-ÖØ-öø-ÿ\s]*)(Seite \d+ von \d+)?\n([A-Za-z0-9À-ÖØ-öø-ÿ\s]*)(\n[A-Za-z0-9À-ÖØ-öø-ÿ\s]*[^\n])(\n[A-Za-z0-9À-ÖØ-öø-ÿ\s]*[^\n])?(\n[A-Za-z0-9À-ÖØ-öø-ÿ\s]*[^\n])?(\n[A-Za-z0-9À-ÖØ-öø-ÿ\s]*[^\n])?"
    absender_muster = r"([A-Za-z0-9À-ÖØ-öø-ÿ\s]*)(\n[A-Za-z0-9À-ÖØ-öø-ÿ\s]*)(\n[A-Za-z0-9À-ÖØ-öø-ÿ\s]*[^\n])(\n[A-Za-z0-9À-ÖØ-öø-ÿ\s]*[^\n])?(\n[A-Za-z0-9À-ÖØ-öø-ÿ\s]*[^\n])?"

    empfaenger_name = ""
    empfaenger_strasse = ""
    empfaenger_plz = ""
    empfaenger_ort = ""

    absender_name = ""
    absender_strasse = ""
    absender_plz = ""
    absender_ort = ""

    briefkopf = re.search(briefkopf_muster, page_content)
    if briefkopf is not None:
        briefkopf_titel = briefkopf.group(1)
        briefkopf_anrede = briefkopf.group(3)
        briefkopf_strasse = briefkopf.group(4)
        briefkopf_plz = briefkopf.group(5)
        briefkopf_ort = briefkopf.group(6)
        briefkopf_land = briefkopf.group(7)

        # Empfänger extrahieren
    empfaenger = ""
    empfaenger_muster = r"An\n([A-Za-z0-9À-ÖØ-öø-ÿ\s]*)(\n[A-Za-z0-9À-ÖØ-öø-ÿ\s]*[^\n])?(\n[A-Za-z0-9À-ÖØ-öø-ÿ\s]*[^\n])?(\n[A-Za-z0-9À-ÖØ-öø-ÿ\s]*[^\n])?"
    empfaenger_match = re.search(empfaenger_muster, page_content)
    if empfaenger_match is not None:
        empfaenger_name = empfaenger_match.group(1)
        empfaenger_strasse = empfaenger_match.group(2)
        empfaenger_plz = empfaenger_match.group(3)
        empfaenger_ort = empfaenger_match.group(4)
        empfaenger = empfaenger_name

    # Absender extrahieren
    absender = ""
    absender_match = re.search(absender_muster, page_content)
    if absender_match is not None:
        absender_name = absender_match.group(1)
        absender_strasse = absender_match.group(2)
        absender_plz = absender_match.group(3)
        absender_ort = absender_match.group(4)

    # Text extrahieren
    text = page_content
    for img_text in image_text:
        text += "\n" + img_text

    return {
        'page_number': page_number,
        'briefkopf': {
            'titel': briefkopf_titel,
            'anrede': briefkopf_anrede,
            'strasse': briefkopf_strasse,
            'plz': briefkopf_plz,
            'ort': briefkopf_ort,
            'land': briefkopf_land
        },
        'empfaenger': {
            'name': empfaenger_name,
            'strasse': empfaenger_strasse,
            'plz': empfaenger_plz,
            'ort': empfaenger_ort
        },
        'absender': {
            'name': absender_name,
            'strasse': absender_strasse,
            'plz': absender_plz,
            'ort': absender_ort
        },
        'text': text
    }


def extract_text_from_page(page_content, image_text, page_number):
    # Text extrahieren
    text = page_content
    for img_text in image_text:
        text += "\n" + img_text

    return {
        'page_number': page_number,
        'text': text
    }


def process_pdf_pages(pdf_reader):
    all_pages_info = []
    for page_number, page in enumerate(pdf_reader.pages):
        page_content = page.extract_text()
        images = extract_images_from_page(page)
        image_text = extract_text_from_images(images)
        page_info = extract_information_from_page(
            page_content, image_text, page_number)
        # page_info = extract_information_from_page(page_content, image_text, page_number)
        page_info['images'] = images
        page_info['image_text'] = image_text
        all_pages_info.append(page_info)
    return all_pages_info


def display_entities(doc):
    st.subheader("Entity recognizer")
    ent_html = displacy.render(doc, style="ent", jupyter=False)
    st.write(ent_html, unsafe_allow_html=True)


def display_dependencies(doc):
    st.subheader("Dependency visualizer")
    sentences = [sentence.text for sentence in doc.sents]
    sentence_selected = st.selectbox("Wähle einen Satz", options=sentences)
    for sentence in doc.sents:
        if sentence.text == sentence_selected:
            dep_svg = displacy.render(sentence, style="dep", jupyter=False)
            st.image(dep_svg, use_column_width='always')


def extract_table_from_pdf(pdf_path):
    # Versucht, Tabellen mit der Lattice-Methode zu extrahieren
    tables = tabula.read_pdf(pdf_path, pages="all",
                             multiple_tables=True, lattice=True)

    # Wenn keine Tabellen gefunden wurden, versucht die Stream-Methode
    if not tables:
        tables = tabula.read_pdf(
            pdf_path, pages="all", multiple_tables=True, stream=True)

    if tables:
        return tables
    else:
        return None


pdf_file = st.file_uploader("Bitte PDF-Datei auswählen", type="pdf")

if pdf_file is not None:
    nlp = spacy.load(spacy_model)
    menu = ["Home", "Dependency visualizer", "Entity recognizer", "Page content",
            "Extracted text from images", "Extracted Tables", "Special Tables"]
    choice = st.sidebar.radio("Menu", menu)

    pdf_reader = PyPDF2.PdfReader(pdf_file)
    with tempfile.NamedTemporaryFile(delete=False) as temp_pdf:
        temp_pdf.write(pdf_file.getvalue())
        temp_pdf_path = temp_pdf.name

    all_pages_info = process_pdf_pages(pdf_reader)
    table = extract_table_from_pdf(temp_pdf_path)

    if choice == "Home":
        for page_info in all_pages_info:
            images = page_info['images']
            for img in images:
                st.image(img)
    elif choice == "Entity recognizer":
        for page_info in all_pages_info:
            page_content = page_info['text']
            doc = nlp(page_content)
            display_entities(doc)
    elif choice == "Page content":
        for page_info in all_pages_info:
            st.write(f"Page {page_info['page_number']} content:")
            st.write(page_info['text'])
    elif choice == "Extracted text from images":
        for page_info in all_pages_info:
            st.write(
                f"Page {page_info['page_number']} extracted text from images:")
            st.write(page_info['image_text'])
    elif choice == "Extracted Tables":
        if table:
            for i, extracted_table in enumerate(table):
                st.write(f"Table {i + 1}:")
                st.write(extracted_table)
                st.write("\n")
        else:
            st.warning("Keine Tabellen im PDF gefunden.")
    elif choice == "Special Tables":
        special_table = tabula.read_pdf_with_template(
            temp_pdf_path, template_path="metadata/AbschlagUE50_Allianz.tabula-template.json")
        for i, extracted_table in enumerate(special_table):
            st.write(f"Table {i + 1}:")
            st.write(extracted_table)
            st.write("\n")
    elif choice == "Dependency visualizer":
        for page_info in all_pages_info:
            page_content = page_info['text']
            doc = nlp(page_content)
            display_dependencies(doc)

    st.text(f"Analyzed using spaCy model {spacy_model}")

else:
    menu = ["Dependency visualizer", "Entity recognizer"]
    choice = st.sidebar.radio("Entity recognizer", menu)

    nlp = spacy.load(spacy_model)

    def count_lines(text):
        return len(text.split("\n"))

    default_text_lines = count_lines(default_text)
    text_area_height = min(default_text_lines * 20, 500)
    user_input = st.text_area("Text zur Analyse", default_text, height=text_area_height,
                              help="Geben Sie den Text ein, den Sie analysieren möchten.")
    doc = nlp(user_input)

    if choice == "Entity recognizer":
        display_entities(doc)
    elif choice == "Dependency visualizer":
        display_dependencies(doc)
