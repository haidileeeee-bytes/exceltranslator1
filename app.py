import os
import uuid
from flask import Flask, request, render_template, send_file, jsonify
from translator import translate_excel

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 최대 10MB

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

LANGUAGES = {
    'ko': '한국어',
    'ja': '일본어',
    'en': '영어',
    'zh-CN': '중국어 (간체)',
    'zh-TW': '중국어 (번체)',
    'fr': '프랑스어',
    'de': '독일어',
    'es': '스페인어',
}

@app.route('/')
def index():
    return render_template('index.html', languages=LANGUAGES)

@app.route('/translate', methods=['POST'])
def translate():
    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다.'}), 400

    file = request.files['file']
    source_lang = request.form.get('source_lang', 'ja')
    target_lang = request.form.get('target_lang', 'ko')

    if not file.filename.endswith('.xlsx'):
        return jsonify({'error': '.xlsx 파일만 지원합니다.'}), 400

    if source_lang == target_lang:
        return jsonify({'error': '출발 언어와 도착 언어가 같습니다.'}), 400

    uid = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_FOLDER, f'{uid}_input.xlsx')
    output_path = os.path.join(UPLOAD_FOLDER, f'{uid}_output.xlsx')

    file.save(input_path)

    try:
        translate_excel(input_path, output_path, source_lang, target_lang)
    except Exception as e:
        return jsonify({'error': f'번역 중 오류가 발생했습니다: {str(e)}'}), 500
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

    original_name = os.path.splitext(file.filename)[0]
    download_name = f'{original_name}_번역.xlsx'

    return send_file(
        output_path,
        as_attachment=True,
        download_name=download_name,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

if __name__ == '__main__':
    app.run(debug=False)
if __name__ == '__main__':
    app.run(debug=False)
```

그리고 Render → **Settings** → **Start Command** 를 이걸로 바꿔:
```
gunicorn --workers 1 --timeout 180 app:app
# 이 줄을
download_name = f'{original_name}_번역.xlsx'

# 이걸로 바꾸기
download_name = f'{original_name}_translated.xlsx'
