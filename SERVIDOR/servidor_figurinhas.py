from flask import Flask, render_template_string, send_from_directory, send_file
import os
import zipfile
import io
import socket

app = Flask(__name__)

# Coloque aqui o mesmo nome da pasta de destino que você usou no outro script
PASTA_FIGURINHAS = "./figurinhas_prontas"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minhas Figurinhas</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; background: #ece5dd; padding: 20px; color: #333; }
        h1 { color: #075e54; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 15px; margin-top: 30px; }
        .sticker { width: 100%; max-width: 120px; border-radius: 10px; background: transparent; filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.1)); }
        .btn { display: inline-block; padding: 15px 25px; background: #25d366; color: white; text-decoration: none; border-radius: 50px; font-weight: bold; margin-top: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .btn:hover { background: #128c7e; }
        .aviso { font-size: 0.9em; color: #666; margin-top: 10px; }
    </style>
</head>
<body>
    <h1>📲 Suas Figurinhas</h1>
    <p>Acesse pelo celular e baixe o pacote pronto.</p>
    
    <a href="/baixar_zip" class="btn">📥 Baixar Todas (ZIP)</a>
    <p class="aviso">Após baixar, descompacte no celular para importar no Zap!</p>

    <div class="grid">
        {% for fig in figurinhas %}
            <img src="/figurinhas/{{ fig }}" class="sticker" alt="Figurinha">
        {% endfor %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    if not os.path.exists(PASTA_FIGURINHAS):
        os.makedirs(PASTA_FIGURINHAS)
    # Pega só os arquivos .webp
    figurinhas = [f for f in os.listdir(PASTA_FIGURINHAS) if f.endswith('.webp')]
    return render_template_string(HTML_TEMPLATE, figurinhas=figurinhas)

@app.route('/figurinhas/<nome_arquivo>')
def servir_figurinha(nome_arquivo):
    return send_from_directory(PASTA_FIGURINHAS, nome_arquivo)

@app.route('/baixar_zip')
def baixar_zip():
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for f in os.listdir(PASTA_FIGURINHAS):
            if f.endswith('.webp'):
                caminho_completo = os.path.join(PASTA_FIGURINHAS, f)
                zf.write(caminho_completo, f) # Adiciona ao ZIP
    memory_file.seek(0)
    return send_file(memory_file, download_name="minhas_figurinhas.zip", as_attachment=True)

def pegar_ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

if __name__ == '__main__':
    ip = pegar_ip_local()
    print("="*50)
    print(f"🚀 SERVIDOR DE FIGURINHAS ONLINE!")
    print(f"📱 Pegue seu celular e acesse o endereço abaixo no navegador:")
    print(f"👉 http://{ip}:5000")
    print("="*50)
    app.run(host='0.0.0.0', port=5000)