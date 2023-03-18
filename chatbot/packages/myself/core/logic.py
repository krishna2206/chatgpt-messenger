import json

from config import CHATGPT_CONFIG


def load_config() -> dict:
    with open(f"{CHATGPT_CONFIG}/EdgeGPT.json", "r") as file:
        return json.load(file)


def divide_text(text: str):
    segments = []
    paragraphs = text.split('\n\n')  # séparer le texte en paragraphes
    for p in paragraphs:
        if len(p) > 2000:
            # si le paragraphe est trop long, le diviser en segments de 2000 caractères
            words = p.split(' ')
            segment = ''
            for w in words:
                if len(segment + ' ' + w) > 2000:
                    segments.append(segment)
                    segment = ''
                segment += ' ' + w
            segments.append(segment)
        else:
            # sinon, ajouter le paragraphe entier comme un segment
            segments.append(p)
    return segments
