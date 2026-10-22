import sqlite3

conexao = sqlite3.connect("agenda_personal.db")
cursor = conexao.cursor()

# O super SELECT usando JOIN para juntar as 3 tabelas
sql_painel_personal = """
SELECT 
    Clientes.nome_completo, 
    Clientes.telefone_whatsapp, 
    Agenda.data_horario, 
    Agendamentos.status_pagamento
FROM Agendamentos
INNER JOIN Clientes ON Agendamentos.id_cliente = Clientes.id_cliente
INNER JOIN Agenda ON Agendamentos.id_agenda = Agenda.id_agenda
"""

cursor.execute(sql_painel_personal)
meus_alunos = cursor.fetchall()

print("\n🏋️‍♂️ --- SUA AGENDA DE TREINOS CONFIRMADOS --- 🏋️‍♂️")
for treino in meus_alunos:
    nome = treino[0]
    telefone = treino[1]
    data_hora = treino[2]
    pagamento = treino[3]
    
    print(f"Aluno: {nome}")
    print(f"Data/Hora: {data_hora}")
    print(f"WhatsApp: {telefone} | Status Pagamento: {pagamento}")
    print("-" * 40)

conexao.close()