import re
import openpyxl
import time
from deep_translator import GoogleTranslator

# 언어 감지용 패턴
LANG_PATTERNS = {
    'ja': re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]+'),
    'zh-CN': re.compile(r'[\u4E00-\u9FFF\u3400-\u4DBF]+'),
    'en': re.compile(r'[a-zA-Z]{3,}'),
}

def translate_text(text, source, target):
    if not text or not isinstance(text, str):
        return text
    pattern = LANG_PATTERNS.get(source)
    if pattern and not pattern.search(text):
        return text
    try:
        return GoogleTranslator(source=source, target=target).translate(text)
    except Exception:
        return text

def translate_excel(input_path, output_path, source_lang, target_lang):
    wb = openpyxl.load_workbook(input_path)

    for sheet in wb.worksheets:
        # 시트 이름 번역
        translated_title = translate_text(sheet.title, source_lang, target_lang)
        if translated_title:
            sheet.title = translated_title[:31]  # 엑셀 시트명 31자 제한

        # 셀 내용 번역
        for row in sheet.iter_rows():
            for cell in row:
                if cell.value and isinstance(cell.value, str):
                    cell.value = translate_text(cell.value, source_lang, target_lang)
                    time.sleep(0.05)  # API 과부하 방지

    wb.save(output_path)
