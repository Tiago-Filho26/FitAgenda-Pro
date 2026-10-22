import sqlite3

conexao = sqlite3.connect("agenda_personal.db")
cursor = conexao.cursor()

# 1. Inserindo o primeiro Cliente (Aluno)
sql_inserir_cliente = """
INSERT INTO Clientes (nome_completo, telefone_whatsapp, email, senha_hash)
VALUES ('João Silva (Teste)', '11999999999', 'joao@email.com', 'senha_criptografada_123')
"""

# 2. Inserindo 3 horários livres na sua Agenda de uma só vez
# O formato padrão de data/hora no banco é Ano-Mês-Dia Hora:Minuto:Segundo
sql_inserir_horarios = """
INSERT INTO Agenda (data_horario)
VALUES 
    ('2026-10-20 18:00:00'),
    ('2026-10-20 19:00:00'),
    ('2026-10-21 07:00:00')
"""

# Executa os comandos
cursor.execute(sql_inserir_cliente)
cursor.execute(sql_inserir_horarios)

# Salva no banco de dados
conexao.commit()

print("Dados de teste inseridos com sucesso!")

conexao.close()