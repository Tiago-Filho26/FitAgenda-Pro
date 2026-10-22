import sqlite3

# Conecta ao banco de dados
conexao = sqlite3.connect("agenda_personal.db")
cursor = conexao.cursor()

# 1. Simular a visão do aluno: Mostrar horários livres
print("--- Horários Disponíveis ---")
# Busca apenas os horários com status 'Livre'
cursor.execute("SELECT id_agenda, data_horario FROM Agenda WHERE status_horario = 'Livre'")
horarios_livres = cursor.fetchall()

# Exibe os horários na tela
for horario in horarios_livres:
    id_horario = horario[0]
    data_hora = horario[1]
    print(f"ID: {id_horario} | Data e Hora: {data_hora}")
print("----------------------------\n")

# 2. Simular a ação do aluno: O João (ID 1) escolhe o horário das 18h (que é o ID 1 da agenda)
id_cliente_joao = 1
id_horario_escolhido = 1

# 3. Regra de Negócio: O Python precisa verificar se o horário REALMENTE ainda está livre
cursor.execute("SELECT status_horario FROM Agenda WHERE id_agenda = ?", (id_horario_escolhido,))
resultado = cursor.fetchone()

# Se o resultado existir e o status for 'Livre', prosseguimos com o agendamento
if resultado and resultado[0] == 'Livre':
    print("Iniciando o agendamento...")
    
    # A. Cria a reserva na tabela de Agendamentos
    cursor.execute("""
        INSERT INTO Agendamentos (id_cliente, id_agenda) 
        VALUES (?, ?)
    """, (id_cliente_joao, id_horario_escolhido))
    
    # B. Atualiza a tabela Agenda, mudando o status para 'Reservado'
    cursor.execute("""
        UPDATE Agenda 
        SET status_horario = 'Reservado' 
        WHERE id_agenda = ?
    """, (id_horario_escolhido,))
    
    # Salva as duas ações no banco
    conexao.commit()
    print("✅ Agendamento realizado com sucesso!")
    
else:
    print("❌ Erro: Este horário já foi reservado ou não existe.")

conexao.close()