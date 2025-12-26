from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'chave_super_secreta_coletas'

# --- CONFIGURAÇÃO ---
PASTA_PLANILHAS = 'planilhas'

# Dicionário de Rotas
CONFIG_PLANILHAS = {
    # 'barra_shopping': {'titulo': 'Coleta Barra Shopping', 'arquivo': 'coleta barra shopping.xlsx'},
    'campo_grande':   {'titulo': 'Coleta Campo Grande',   'arquivo': 'coleta_campo_grande.xlsx'},
    'everton':        {'titulo': 'Coleta Everton',        'arquivo': 'coleta_everton.xlsx'},
    'jairo':          {'titulo': 'Coleta Jairo',          'arquivo': 'coleta_jairo.xlsx'},
    'moises':         {'titulo': 'Coleta Moises',         'arquivo': 'coleta_moises.xlsx'},
    'paulo':          {'titulo': 'Coleta Paulo',          'arquivo': 'coleta_paulo.xlsx'},
    'yago':           {'titulo': 'Coleta Yago',           'arquivo': 'coleta_yago.xlsx'},
    'BarraManha':      {'titulo': 'Coleta Barra Manhã',     'arquivo': 'coleta_barra_manha.xlsx'},
    'RioDesignManha':     {'titulo': 'Coleta RioDesign manhã',    'arquivo': 'coleta_RioDesign_manha.xlsx'},
    'Yago+Jairo':     {'titulo': 'Coleta Yago + Jairo',    'arquivo': 'coleta_jairoYago.xlsx'},
}


# --- FUNÇÃO DE CARREGAMENTO INTELIGENTE ---
def carregar_df(nome_rota):
    info = CONFIG_PLANILHAS.get(nome_rota)
    if not info: return None, None
    
    caminho = os.path.join(PASTA_PLANILHAS, info['arquivo'])
    os.makedirs(PASTA_PLANILHAS, exist_ok=True)
    
    # Se não existe, cria com as 3 colunas
    if not os.path.exists(caminho):
        df = pd.DataFrame(columns=['Empresa', 'Endereço', 'Complemento'])
        df.to_excel(caminho, index=False)
        return df, caminho

    try:
        df = pd.read_excel(caminho, dtype=str).fillna('')
        
        # Normaliza nomes de colunas
        df.columns = [c.strip() for c in df.columns]
        
        # Garante que as colunas existam (para arquivos antigos)
        if 'Empresa' not in df.columns: df['Empresa'] = ''
        if 'Endereço' not in df.columns: df['Endereço'] = ''
        if 'Complemento' not in df.columns: df['Complemento'] = '' # Nova Coluna

        return df, caminho

    except Exception as e:
        print(f"ERRO: {e}")
        return pd.DataFrame(columns=['Empresa', 'Endereço', 'Complemento']), caminho

# --- ROTAS ---

@app.route('/')
def index():
    return render_template('menu.html', opcoes=CONFIG_PLANILHAS)

@app.route('/coleta/<nome_rota>')
def ver_coleta(nome_rota):
    if nome_rota not in CONFIG_PLANILHAS:
        return redirect(url_for('index'))
    
    df, _ = carregar_df(nome_rota)
    
    registros = []
    for i, row in df.iterrows():
        registros.append({
            'id': i, 
            'Empresa': row['Empresa'], 
            'Endereço': row['Endereço'],
            'Complemento': row['Complemento'] # Passa o complemento para o HTML
        })
        
    titulo = CONFIG_PLANILHAS[nome_rota]['titulo']
    return render_template('tabela.html', nome_rota=nome_rota, titulo=titulo, registros=registros)

@app.route('/coleta/<nome_rota>/adicionar', methods=['POST'])
def adicionar(nome_rota):
    empresa = request.form.get('empresa')
    endereco = request.form.get('endereco')
    complemento = request.form.get('complemento') # Pega o novo campo
    posicao = request.form.get('posicao')
    
    df, caminho = carregar_df(nome_rota)
    
    nova_linha = pd.DataFrame([{
        'Empresa': empresa, 
        'Endereço': endereco,
        'Complemento': complemento
    }])
    
    if posicao == 'inicio':
        df = pd.concat([nova_linha, df], ignore_index=True)
    elif posicao == 'fim' or not posicao:
        df = pd.concat([df, nova_linha], ignore_index=True)
    else:
        try:
            idx = int(posicao)
            parte_superior = df.iloc[:idx+1]
            parte_inferior = df.iloc[idx+1:]
            df = pd.concat([parte_superior, nova_linha, parte_inferior], ignore_index=True)
        except:
            df = pd.concat([df, nova_linha], ignore_index=True)
    
    df.to_excel(caminho, index=False)
    flash('Adicionado com sucesso!', 'success')
    return redirect(url_for('ver_coleta', nome_rota=nome_rota))

@app.route('/coleta/<nome_rota>/editar', methods=['POST'])
def editar(nome_rota):
    try:
        id_linha = int(request.form.get('id_linha'))
        empresa = request.form.get('empresa')
        endereco = request.form.get('endereco')
        complemento = request.form.get('complemento') # Pega o novo campo
        
        df, caminho = carregar_df(nome_rota)
        
        if id_linha in df.index:
            df.at[id_linha, 'Empresa'] = empresa
            df.at[id_linha, 'Endereço'] = endereco
            df.at[id_linha, 'Complemento'] = complemento
            df.to_excel(caminho, index=False)
            flash('Atualizado!', 'info')
    except Exception as e:
        flash(f'Erro: {e}', 'danger')
        
    return redirect(url_for('ver_coleta', nome_rota=nome_rota))

@app.route('/coleta/<nome_rota>/excluir/<int:id_linha>')
def excluir(nome_rota, id_linha):
    df, caminho = carregar_df(nome_rota)
    if id_linha in df.index:
        df = df.drop(id_linha)
        df.to_excel(caminho, index=False)
        flash('Excluído.', 'secondary')
    return redirect(url_for('ver_coleta', nome_rota=nome_rota))

# if __name__ == '__main__':
#     app.run(debug=True)
