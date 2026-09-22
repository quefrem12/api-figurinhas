import os
import streamlit as st
from PIL import Image
import tkinter as tk
from tkinter import filedialog

# Configuração da página do Streamlit
st.set_page_config(page_title="Gerador de Figurinhas WhatsApp", page_icon="🖼️", layout="centered")

st.title("🖼️ Gerador de Figurinhas para WhatsApp")
st.markdown("Converta imagens de uma pasta em figurinhas (`.webp`) de forma automática, processando apenas as novas imagens.")

# Função para abrir a janela nativa de seleção de pastas
def selecionar_pasta(titulo="Selecionar Pasta"):
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal do Tkinter
    root.attributes('-topmost', True)  # Mantém a janela de seleção na frente
    caminho = filedialog.askdirectory(title=titulo)
    root.destroy()
    return caminho

# Inicializar estados para os caminhos das pastas caso não existam
if 'pasta_origem' not in st.session_state:
    st.session_state.pasta_origem = "./imagens_origem"
if 'pasta_destino' not in st.session_state:
    st.session_state.pasta_destino = "./figurinhas_prontas"

# Seção de configuração de pastas com botões de seleção
st.subheader("📁 Caminhos das Pastas")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Pasta de Origem**")
    if st.button("📂 Escolher Pasta de Origem"):
        pasta_escolhida = selecionar_pasta("Selecione a Pasta de Origem das Imagens")
        if pasta_escolhida:
            st.session_state.pasta_origem = pasta_escolhida
            st.rerun()
    
    # Campo de texto para exibir/editar manualmente se preferir
    pasta_origem = st.text_input("Caminho Origem", value=st.session_state.pasta_origem, label_visibility="collapsed")
    st.session_state.pasta_origem = pasta_origem

with col2:
    st.markdown("**Pasta de Destino**")
    if st.button("📂 Escolher Pasta de Destino"):
        pasta_escolhida = selecionar_pasta("Selecione a Pasta onde salvar as Figurinhas")
        if pasta_escolhida:
            st.session_state.pasta_destino = pasta_escolhida
            st.rerun()
            
    # Campo de texto para exibir/editar manualmente se preferir
    pasta_destino = st.text_input("Caminho Destino", value=st.session_state.pasta_destino, label_visibility="collapsed")
    st.session_state.pasta_destino = pasta_destino

# Criar as pastas caso não existam
os.makedirs(st.session_state.pasta_origem, exist_ok=True)
os.makedirs(st.session_state.pasta_destino, exist_ok=True)

# Seção de importação direta de novas imagens
st.subheader("📥 Importar Novas Imagens")
imagens_upadas = st.file_uploader(
    "Arraste ou selecione imagens para salvar diretamente na pasta de origem:", 
    type=["png", "jpg", "jpeg", "webp"], 
    accept_multiple_files=True
)

if imagens_upadas:
    salvas = 0
    for img_file in imagens_upadas:
        caminho_salvar = os.path.join(st.session_state.pasta_origem, img_file.name)
        if not os.path.exists(caminho_salvar):
            with open(caminho_salvar, "wb") as f:
                f.write(img_file.getbuffer())
            salvas += 1
    if salvas > 0:
        st.success(f"{salvas} nova(s) imagem(ns) salva(s) com sucesso na pasta de origem!")

# Função para converter imagem para o formato de figurinha do WhatsApp (.webp)
def converter_para_figurinha(caminho_img, caminho_saida):
    try:
        img = Image.open(caminho_img)
        
        # Redimensionar mantendo a proporção para caber no limite do WhatsApp (máximo 512x512)
        img.thumbnail((512, 512))
        
        # Salvar como WebP com fundo transparente (se houver canal alfa)
        img.save(caminho_saida, "WEBP", quality=80)
        return True
    except Exception as e:
        st.error(f"Erro ao converter {os.path.basename(caminho_img)}: {e}")
        return False

# Botão principal para processar as conversões
st.subheader("⚡ Processar Conversão")
if st.button("Transformar Novas Imagens em Figurinhas", type="primary"):
    extensoes_validas = (".png", ".jpg", ".jpeg", ".webp")
    
    if not os.path.exists(st.session_state.pasta_origem):
        st.warning("A pasta de origem selecionada não existe.")
    else:
        arquivos = [f for f in os.listdir(st.session_state.pasta_origem) if f.lower().endswith(extensoes_validas)]
        
        if not arquivos:
            st.info("Nenhuma imagem encontrada na pasta de origem.")
        else:
            novas_convertidas = 0
            barra_progresso = st.progress(0)
            total = len(arquivos)
            
            for i, arquivo in enumerate(arquivos):
                nome_base, _ = os.path.splitext(arquivo)
                nome_saida = f"{nome_base}.webp"
                
                caminho_origem_completo = os.path.join(st.session_state.pasta_origem, arquivo)
                caminho_destino_completo = os.path.join(st.session_state.pasta_destino, nome_saida)
                
                # Verifica se a figurinha já foi gerada
                if not os.path.exists(caminho_destino_completo):
                    sucesso = converter_para_figurinha(caminho_origem_completo, caminho_destino_completo)
                    if sucesso:
                        novas_convertidas += 1
                
                barra_progresso.progress((i + 1) / total)
            
            st.success(f"Processo concluído! {novas_convertidas} nova(s) figurinha(s) gerada(s). As figurinhas salvas estão em: `{st.session_state.pasta_destino}`")

# Exibir status atual das pastas
st.markdown("---")
st.subheader("📊 Status Atual")
if os.path.exists(st.session_state.pasta_origem):
    total_origem = len([f for f in os.listdir(st.session_state.pasta_origem) if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))])
    total_destino = len([f for f in os.listdir(st.session_state.pasta_destino) if f.endswith(".webp")]) if os.path.exists(st.session_state.pasta_destino) else 0
    
    c1, c2 = st.columns(2)
    c1.metric("Imagens na Origem", total_origem)
    c2.metric("Figurinhas Prontas", total_destino)