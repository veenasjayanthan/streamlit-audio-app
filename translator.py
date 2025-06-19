from googletrans import Translator, LANGUAGES
from gtts import gTTS
import tempfile
from googletrans import Translator

def get_supported_languages():
    return LANGUAGES  # this is a dictionary of language codes and names

def translate_text(text, target_lang):
    translator = Translator()
    return translator.translate(text, dest=target_lang).text

def speak_text(text, lang_code):
    tts = gTTS(text=text, lang=lang_code)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)
    return temp_file.name




def translate_text(text, target_lang):
    translator = Translator()
    translation = translator.translate(text, dest=target_lang)  # src auto-detected
    return translation.text


from googletrans import Translator

def translate_text(text, target_lang, source_lang='auto'):
    translator = Translator()
    translation = translator.translate(text, src=source_lang, dest=target_lang)
    return translation.text


