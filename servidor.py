from flask import Flask, render_template_string, send_from_directory, send_file, request, redirect, url_for
import os
import zipfile
import io
import json
from PIL import Image
from werkzeug.utils import secure_filename

app = Flask(__name__)

PASTA_FIGURINHAS = "./figurinhas_prontas"
if not os.path.exists(PASTA_FIGURINHAS):
    os.makedirs(PASTA_FIGURINHAS)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fábrica de Figurinhas</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; background: #ece5dd; padding: 20px; color: #333; }
        h1 { color: #075e54; }
        .upload-box { background: white; padding: 20px; border-radius: 10px; margin: 20px auto; max-width: 500px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 15px; margin-top: 30px; }
        .sticker { width: 100%; max-width: 120px; border-radius: 10px; background: transparent; filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.1)); }
        .btn { display: inline-block; padding: 12px 20px; background: #25d366; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; border: none; cursor: pointer; }
        .btn:hover { background: #128c7e; }
        input[type="file"] { margin: 15px 0; }
    </style>
</head>
<body>
    <h1>🛠️ Fábrica de Figurinhas na Nuvem</h1>
    
    <div class="upload-box">
        <h3>1. Enviar Imagens do PC</h3>
        <p>Selecione suas fotos (JPG, PNG). Elas serão convertidas automaticamente!</p>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="imagens" multiple accept=".png, .jpg, .jpeg, .webp" required>
            <br>
            <button type="submit" class="btn">Converter para Figurinhas</button>
        </form>
    </div>

    <h3>2. Galeria Pronta para o Celular</h3>
    <div class="grid">
        {% for fig in figurinhas %}
            <img src="/figurinhas/{{ fig }}" class="sticker" alt="Figurinha">
        {% else %}
            <p style="grid-column: 1 / -1; color: #666;">Nenhuma figurinha gerada ainda. Faça o upload acima!</p>
        {% endfor %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    figurinhas = [f for f in os.listdir(PASTA_FIGURINHAS) if f.endswith('.webp')]
    return render_template_string(HTML_TEMPLATE, figurinhas=figurinhas)

@app.route('/upload', methods=['POST'])
def upload_imagens():
    arquivos = request.files.getlist('imagens')
    
    for arquivo in arquivos:
        if arquivo.filename == '':
            continue
            
        try:
            # Abre a imagem enviada
            img = Image.open(arquivo)
            
            # Converte para RGBA para garantir fundo transparente e redimensiona para 512x512
            img = img.convert("RGBA")
            img.thumbnail((512, 512))
            
            # Cria o nome do arquivo .webp
            nome_original = secure_filename(arquivo.filename)
            nome_base, _ = os.path.splitext(nome_original)
            nome_saida = f"{nome_base}.webp"
            caminho_saida = os.path.join(PASTA_FIGURINHAS, nome_saida)
            
            # Salva no formato exigido pelo WhatsApp
            img.save(caminho_saida, "WEBP", quality=80)
        except Exception as e:
            print(f"Erro ao processar {arquivo.filename}: {e}")
            
    return redirect(url_for('index'))

@app.route('/figurinhas/<nome_arquivo>')
def servir_figurinha(nome_arquivo):
    return send_from_directory(PASTA_FIGURINHAS, nome_arquivo)

@app.route('/baixar_zip')
def baixar_zip():
    memory_file = io.BytesIO()
    figurinhas = [f for f in os.listdir(PASTA_FIGURINHAS) if f.endswith('.webp')]
    
    if not figurinhas:
        return "Nenhuma figurinha encontrada.", 404

    with zipfile.ZipFile(memory_file, 'w') as zf:
        stickers_data = []
        
        for i, f in enumerate(figurinhas):
            caminho_completo = os.path.join(PASTA_FIGURINHAS, f)
            zf.write(caminho_completo, f)
            stickers_data.append({"image_file": f, "emojis": ["😎"]})
            
            if i == 0:
                try:
                    img = Image.open(caminho_completo)
                    img.thumbnail((96, 96))
                    tray_io = io.BytesIO()
                    img.save(tray_io, format="PNG")
                    zf.writestr("tray_icon.png", tray_io.getvalue())
                except Exception as e:
                    pass

        contents = {
            "android_play_store_link": "", "ios_app_store_link": "",
            "publisher_email": "", "publisher_website": "",
            "privacy_policy_website": "", "license_agreement_website": "",
            "image_data_version": "1", "avoid_cache": False,
            "sticker_packs": [
                {
                    "identifier": "figurinhas_nuvem",
                    "name": "Figurinhas do PC",
                    "publisher": "Importador Zap",
                    "tray_image_file": "tray_icon.png",
                    "image_data_version": "1",
                    "avoid_cache": False,
                    "publisher_email": "", "publisher_website": "",
                    "privacy_policy_website": "", "license_agreement_website": "",
                    "stickers": stickers_data
                }
            ]
        }
        zf.writestr("contents.json", json.dumps(contents, indent=2))

    memory_file.seek(0)
    return send_file(memory_file, download_name="figurinhas.zip", as_attachment=True)

if __name__ == '__main__':
    # O Railway usa a variável de ambiente PORT, se não achar usa 5000
    porta = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=porta)