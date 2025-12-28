from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pandas as pd
import os
import json
import re
from thefuzz import fuzz

app = Flask(__name__)
app.secret_key = 'chave_super_secreta_coletas'

# --- CONFIGURAÇÕES ---
PASTA_PLANILHAS = 'planilhas'
ARQUIVO_CONFIG = 'rotas.json'

CONFIG_INICIAL = {
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

# --- FUNÇÕES AUXILIARES ---
def carregar_config():
    if not os.path.exists(ARQUIVO_CONFIG):
        with open(ARQUIVO_CONFIG, 'w', encoding='utf-8') as f:
            json.dump(CONFIG_INICIAL, f, ensure_ascii=False, indent=4)
        return CONFIG_INICIAL
    with open(ARQUIVO_CONFIG, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_config(nova_config):
    with open(ARQUIVO_CONFIG, 'w', encoding='utf-8') as f:
        json.dump(nova_config, f, ensure_ascii=False, indent=4)

def normalizar_nome_arquivo(texto):
    s = texto.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_-]+', '_', s)
    return f"coleta_{s}.xlsx"

def carregar_df(nome_rota):
    config = carregar_config()
    info = config.get(nome_rota)
    if not info: return None, None
    
    caminho = os.path.join(PASTA_PLANILHAS, info['arquivo'])
    os.makedirs(PASTA_PLANILHAS, exist_ok=True)
    
    colunas_padrao = ['Empresa', 'Endereço', 'Complemento', 'Telefone']

    if not os.path.exists(caminho):
        df = pd.DataFrame(columns=colunas_padrao)
        df.to_excel(caminho, index=False)
        return df, caminho

    try:
        df = pd.read_excel(caminho, dtype=str).fillna('')
        df.columns = [c.strip() for c in df.columns]
        
        # Garante que todas as colunas existam
        for col in colunas_padrao:
            if col not in df.columns: df[col] = ''
            
        return df, caminho
    except Exception as e:
        return pd.DataFrame(columns=colunas_padrao), caminho

# --- PÁGINA INICIAL E BUSCA ---
@app.route('/')
def index():
    config = carregar_config()
    termo_busca = request.args.get('q', '').lower().strip()
    
    chk_empresa = request.args.get('chk_empresa')
    chk_endereco = request.args.get('chk_endereco')
    
    if not chk_empresa and not chk_endereco:
        chk_empresa = 'on'
        chk_endereco = 'on'

    resultados = []
    
    if termo_busca:
        for rota_id, dados in config.items():
            df, _ = carregar_df(rota_id)
            if df is not None and not df.empty:
                for i, row in df.iterrows():
                    empresa = str(row['Empresa']).lower()
                    endereco = str(row['Endereço']).lower()
                    match = False
                    
                    if chk_empresa and fuzz.partial_ratio(termo_busca, empresa) >= 70: match = True
                    if chk_endereco and fuzz.partial_ratio(termo_busca, endereco) >= 70: match = True
                    
                    if match:
                        resultados.append({
                            'rota_titulo': dados['titulo'],
                            'rota_id': rota_id,
                            'Empresa': row['Empresa'],
                            'Endereço': row['Endereço'],
                            'Complemento': row['Complemento'],
                            'Telefone': row.get('Telefone', '')
                        })

    return render_template('menu.html', opcoes=config, resultados=resultados, termo_busca=termo_busca, chk_empresa=chk_empresa, chk_endereco=chk_endereco)

# --- GERENCIAMENTO DE ROTAS ---
@app.route('/nova_rota', methods=['POST'])
def nova_rota():
    titulo = request.form.get('titulo_rota')
    if titulo:
        config = carregar_config()
        rota_id = normalizar_nome_arquivo(titulo).replace('.xlsx', '').replace('coleta_', '')
        arquivo_nome = normalizar_nome_arquivo(titulo)
        if rota_id not in config:
            config[rota_id] = {'titulo': titulo, 'arquivo': arquivo_nome}
            salvar_config(config)
            caminho = os.path.join(PASTA_PLANILHAS, arquivo_nome)
            if not os.path.exists(caminho):
                pd.DataFrame(columns=['Empresa', 'Endereço', 'Complemento', 'Telefone']).to_excel(caminho, index=False)
            flash(f'Rota "{titulo}" criada!', 'success')
    return redirect(url_for('index'))

@app.route('/renomear_rota', methods=['POST'])
def renomear_rota():
    rota_id = request.form.get('rota_id')
    novo_titulo = request.form.get('novo_titulo')
    if rota_id and novo_titulo:
        config = carregar_config()
        if rota_id in config:
            config[rota_id]['titulo'] = novo_titulo
            salvar_config(config)
            flash('Renomeado com sucesso!', 'info')
    return redirect(url_for('index'))

@app.route('/remover_rota/<rota_id>')
def remover_rota(rota_id):
    config = carregar_config()
    if rota_id in config:
        del config[rota_id]
        salvar_config(config)
        flash('Rota removida.', 'secondary')
    return redirect(url_for('index'))

# --- CRUD E OPERAÇÕES NA TABELA ---
@app.route('/coleta/<nome_rota>')
def ver_coleta(nome_rota):
    config = carregar_config()
    if nome_rota not in config: return redirect(url_for('index'))
    df, _ = carregar_df(nome_rota)
    
    # Adicionamos 'Telefone' na leitura
    registros = [{'id': i, **row} for i, row in df.iterrows()]
    return render_template('tabela.html', nome_rota=nome_rota, titulo=config[nome_rota]['titulo'], registros=registros, opcoes=config)

@app.route('/coleta/<nome_rota>/adicionar', methods=['POST'])
def adicionar(nome_rota):
    empresa = request.form.get('empresa')
    endereco = request.form.get('endereco')
    complemento = request.form.get('complemento')
    telefone = request.form.get('telefone') # Novo Campo
    posicao = request.form.get('posicao')
    
    df, caminho = carregar_df(nome_rota)
    nova = pd.DataFrame([{
        'Empresa': empresa, 'Endereço': endereco, 
        'Complemento': complemento, 'Telefone': telefone
    }])
    
    if posicao == 'inicio': df = pd.concat([nova, df], ignore_index=True)
    elif posicao == 'fim' or not posicao: df = pd.concat([df, nova], ignore_index=True)
    else:
        try:
            idx = int(posicao)
            df = pd.concat([df.iloc[:idx+1], nova, df.iloc[idx+1:]], ignore_index=True)
        except: df = pd.concat([df, nova], ignore_index=True)
            
    df.to_excel(caminho, index=False)
    flash('Adicionado!', 'success')
    return redirect(url_for('ver_coleta', nome_rota=nome_rota))

@app.route('/coleta/<nome_rota>/editar', methods=['POST'])
def editar(nome_rota):
    try:
        id_linha = int(request.form.get('id_linha'))
        df, caminho = carregar_df(nome_rota)
        if id_linha in df.index:
            df.at[id_linha, 'Empresa'] = request.form.get('empresa')
            df.at[id_linha, 'Endereço'] = request.form.get('endereco')
            df.at[id_linha, 'Complemento'] = request.form.get('complemento')
            df.at[id_linha, 'Telefone'] = request.form.get('telefone') # Novo Campo
            df.to_excel(caminho, index=False)
            flash('Atualizado!', 'info')
    except: pass
    return redirect(url_for('ver_coleta', nome_rota=nome_rota))

@app.route('/coleta/<nome_rota>/excluir/<int:id_linha>')
def excluir(nome_rota, id_linha):
    df, caminho = carregar_df(nome_rota)
    if id_linha in df.index:
        df = df.drop(id_linha)
        df.to_excel(caminho, index=False)
        flash('Excluído.', 'secondary')
    return redirect(url_for('ver_coleta', nome_rota=nome_rota))

@app.route('/coleta/<nome_rota>/reordenar/<int:id_linha>/<direcao>')
def reordenar(nome_rota, id_linha, direcao):
    df, caminho = carregar_df(nome_rota)
    idx_atual = id_linha
    idx_troca = id_linha - 1 if direcao == 'up' else id_linha + 1
    if idx_troca >= 0 and idx_troca < len(df):
        df.iloc[idx_atual], df.iloc[idx_troca] = df.iloc[idx_troca].copy(), df.iloc[idx_atual].copy()
        df.to_excel(caminho, index=False)
    return redirect(url_for('ver_coleta', nome_rota=nome_rota))

# --- NOVA ROTA: ARRASTAR E SOLTAR ---
@app.route('/coleta/<nome_rota>/reordenar_drag', methods=['POST'])
def reordenar_drag(nome_rota):
    try:
        dados = request.get_json()
        nova_ordem_ids = [int(x) for x in dados.get('ordem', [])]
        
        df, caminho = carregar_df(nome_rota)
        
        # Reorganiza o DataFrame com base na lista de índices recebida
        # .iloc[lista] cria um novo DF na ordem da lista
        if len(nova_ordem_ids) == len(df):
            df = df.iloc[nova_ordem_ids].reset_index(drop=True)
            df.to_excel(caminho, index=False)
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'msg': 'Tamanho da lista incorreto'}), 400
            
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

@app.route('/mover_coleta', methods=['POST'])
def mover_coleta():
    rota_origem = request.form.get('rota_origem')
    rota_destino = request.form.get('rota_destino')
    id_linha = int(request.form.get('id_linha'))
    
    if rota_origem == rota_destino: return redirect(url_for('ver_coleta', nome_rota=rota_origem))
    
    df_origem, path_origem = carregar_df(rota_origem)
    if id_linha in df_origem.index:
        linha_dados = df_origem.loc[[id_linha]]
        df_destino, path_destino = carregar_df(rota_destino)
        df_destino = pd.concat([df_destino, linha_dados], ignore_index=True)
        df_destino.to_excel(path_destino, index=False)
        df_origem = df_origem.drop(id_linha)
        df_origem.to_excel(path_origem, index=False)
        flash('Transferido com sucesso!', 'success')
        
    return redirect(url_for('ver_coleta', nome_rota=rota_origem))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')