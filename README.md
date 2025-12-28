# 🚚 RotasLaPlaya - Sistema de Gerenciamento de Rotas de Coleta

Sistema web para gerenciamento de rotas de coleta desenvolvido com Flask.  Permite organizar, buscar e gerenciar informações de empresas e endereços em diferentes rotas de coleta.

## 📋 Funcionalidades

- **Gerenciamento de Rotas**: Criar, renomear e remover rotas de coleta
- **Cadastro de Empresas**: Adicionar, editar e excluir registros com informações de empresa, endereço, complemento e telefone
- **Busca Inteligente**: Sistema de busca com correspondência aproximada (fuzzy matching) usando a biblioteca thefuzz
- **Reordenação**:  Arrastar e soltar para reorganizar a ordem das coletas
- **Transferência**:  Mover empresas entre diferentes rotas
- **Persistência em Excel**: Dados salvos em planilhas Excel (.xlsx) para fácil exportação

## 🛠️ Tecnologias Utilizadas

- **Python 3.12**
- **Flask** - Framework web
- **Pandas** - Manipulação de dados
- **OpenPyXL** - Leitura e escrita de arquivos Excel
- **TheFuzz** - Busca por correspondência aproximada (fuzzy matching)
- **Gunicorn** - Servidor WSGI para produção
- **Jinja2** - Template engine

## 📦 Instalação

### Pré-requisitos
- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)

### Passos

1. Clone o repositório: 
```bash
git clone https://github.com/Fernandx7/RotasLaPlaya. git
cd RotasLaPlaya
```

2. Crie um ambiente virtual: 
```bash
python -m venv venv
```

3. Ative o ambiente virtual:
   - Windows:
   ```bash
   venv\Scripts\activate
   ```
   - Linux/Mac: 
   ```bash
   source venv/bin/activate
   ```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

## 🚀 Execução

### Modo de Desenvolvimento
```bash
python app.py
```
O servidor estará disponível em `http://localhost:5000`

### Modo de Produção
```bash
gunicorn app:app
```

## 📁 Estrutura do Projeto

```
RotasLaPlaya/
├── app.py              # Aplicação principal Flask
├── requirements. txt    # Dependências do projeto
├── rotas. json          # Configuração das rotas
├── deploy.sh           # Script de deploy
├── planilhas/          # Pasta com planilhas Excel das rotas
├── static/             # Arquivos estáticos (CSS, JS)
├── templates/          # Templates HTML (Jinja2)
└── venv/               # Ambiente virtual Python
```

## 📊 Rotas Disponíveis

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET | Página inicial com busca e lista de rotas |
| `/nova_rota` | POST | Criar uma nova rota |
| `/renomear_rota` | POST | Renomear uma rota existente |
| `/remover_rota/<rota_id>` | GET | Remover uma rota |
| `/coleta/<nome_rota>` | GET | Visualizar empresas de uma rota |
| `/coleta/<nome_rota>/adicionar` | POST | Adicionar empresa a uma rota |
| `/coleta/<nome_rota>/editar` | POST | Editar empresa |
| `/coleta/<nome_rota>/excluir/<id>` | GET | Excluir empresa |
| `/coleta/<nome_rota>/reordenar/<id>/<direcao>` | GET | Mover empresa para cima/baixo |
| `/coleta/<nome_rota>/reordenar_drag` | POST | Reordenar via drag and drop |
| `/mover_coleta` | POST | Transferir empresa entre rotas |

## ⚙️ Configuração

As rotas são configuradas no arquivo `rotas.json`. Exemplo de configuração:

```json
{
    "campo_grande": {
        "titulo": "Coleta Campo Grande",
        "arquivo": "coleta_campo_grande.xlsx"
    },
    "everton": {
        "titulo": "Coleta Everton",
        "arquivo":  "coleta_everton.xlsx"
    }
}
```

## 📝 Licença

Este projeto está sob licença livre para uso. 

## 👤 Autor

**Fernandx7** - [GitHub](https://github.com/Fernandx7)

---

⭐ Se este projeto foi útil, considere dar uma estrela! 
