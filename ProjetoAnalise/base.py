import sqlite3

def criar_banco():
    # Cria a conexão com um arquivo de banco de dados local. 
    # Se o arquivo não existir, o Python cria na hora.
    conexao = sqlite3.connect('banco_qualidade.db')
    cursor = conexao.cursor()

    # 1. Tabela de Informações Gerais e Aprovações
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inspecao_cabecalho (
        id_inspecao INTEGER PRIMARY KEY AUTOINCREMENT,
        data_ensaio DATE NOT NULL,
        cor_preforma TEXT,
        lote_fabricacao TEXT NOT NULL,
        tipo_resina TEXT,
        sku_produto TEXT CHECK (sku_produto IN ('200mL', '1L', '2L', 'Outro')),
        fornecedor TEXT,
        tag_sopradora TEXT NOT NULL,
        gramatura REAL,
        executor TEXT NOT NULL,
        horario_finish TEXT,
        horario_resistencia_quimica TEXT,
        horario_resistencia_fisica TEXT,
        horario_pressao_interna TEXT,
        elaborado_por TEXT DEFAULT 'Weskley Rodrigues Monteiro',
        cargo_elaborador TEXT DEFAULT 'Assistente de Processos',
        data_elaboracao DATE DEFAULT '2026-07-02',
        revisado_por TEXT DEFAULT 'Rodrigues Pereira',
        cargo_revisor TEXT DEFAULT 'Assistente de Processos',
        data_revisao DATE DEFAULT '2026-08-17',
        aprovado_por TEXT DEFAULT 'Wanderson Rabelo',
        cargo_aprovador TEXT DEFAULT 'Coordenador de Qualidade',
        data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    # 2. Tabela com as Medições de Cada Molde
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS medicao_molde (
        id_medicao INTEGER PRIMARY KEY AUTOINCREMENT,
        id_inspecao INTEGER,
        numero_molde INTEGER NOT NULL,
        finish_status TEXT CHECK (finish_status IN ('C', 'NC')),
        resistencia_quimica_status TEXT CHECK (resistencia_quimica_status IN ('C', 'NC')),
        resistencia_fisica_status TEXT CHECK (resistencia_fisica_status IN ('C', 'NC')),
        pressao_estouro_bar REAL,
        pressao_status TEXT CHECK (pressao_status IN ('C', 'NC')),
        FOREIGN KEY(id_inspecao) REFERENCES inspecao_cabecalho(id_inspecao) ON DELETE CASCADE
    );
    ''')

    # Salva as alterações e fecha a conexão
    conexao.commit()
    conexao.close()
    print("Banco de dados 'banco_qualidade.db' criado com sucesso no padrão do formulário!")

# Executa a função
if __name__ == '__main__':
    criar_banco()