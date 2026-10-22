import sqlite3

# 1. Cria o arquivo do banco de dados e estabelece a conexão
conexao = sqlite3.connect("agenda_personal.db")

# 2. Cria o 'cursor' (o mensageiro que leva os comandos SQL para o banco)
cursor = conexao.cursor()

print("Banco de dados criado e conectado com sucesso!")

# 3. Fecha a conexão para liberar recursos do sistema
conexao.close()
import sqlite3

conexao = sqlite3.connect("agenda_personal.db")
cursor = conexao.cursor()

# Comando obrigatório no SQLite para ele respeitar as "Chaves Estrangeiras" (vínculos entre tabelas)
cursor.execute("PRAGMA foreign_keys = ON;")

# Criação da tabela de Agenda
sql_criar_agenda = """
CREATE TABLE IF NOT EXISTS Agenda (
    id_agenda INTEGER PRIMARY KEY AUTOINCREMENT,
    data_horario DATETIME NOT NULL,
    status_horario TEXT DEFAULT 'Livre'
)
"""

# Criação da tabela de Agendamentos (O coração do app)
sql_criar_agendamentos = """
CREATE TABLE IF NOT EXISTS Agendamentos (
    id_agendamento INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER NOT NULL,
    id_agenda INTEGER NOT NULL,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    status_pagamento TEXT DEFAULT 'Pendente',
    FOREIGN KEY (id_cliente) REFERENCES Clientes (id_cliente),
    FOREIGN KEY (id_agenda) REFERENCES Agenda (id_agenda)
)
"""

# Executa as criações
cursor.execute(sql_criar_agenda)
cursor.execute(sql_criar_agendamentos)

# Salva as alterações
conexao.commit()

print("Tabelas 'Agenda' e 'Agendamentos' criadas com sucesso e prontas para uso!")

conexao.close()