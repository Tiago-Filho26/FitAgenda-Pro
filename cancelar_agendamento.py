import sqlite3

conexao = sqlite3.connect("agenda_personal.db")
cursor = conexao.cursor()

# Vamos simular que o João (ID 1) pediu para cancelar o treino
id_cliente_joao = 1

# 1. Primeiro, precisamos descobrir QUAL horário o João tem agendado
cursor.execute("""
    SELECT id_agendamento, id_agenda 
    FROM Agendamentos 
    WHERE id_cliente = ?
""", (id_cliente_joao,))

# fetchone() traz apenas 1 resultado (o primeiro que encontrar)
resultado = cursor.fetchone()

if resultado:
    id_do_agendamento = resultado[0]
    id_do_horario = resultado[1]
    
    print(f"Reserva encontrada! Devolvendo o horário (ID {id_do_horario}) para a agenda...")
    
    # 2. Devolve o horário para a praça (Update)
    cursor.execute("""
        UPDATE Agenda 
        SET status_horario = 'Livre' 
        WHERE id_agenda = ?
    """, (id_do_horario,))
    
    # 3. Exclui definitivamente a reserva do sistema (Delete)
    cursor.execute("""
        DELETE FROM Agendamentos 
        WHERE id_agendamento = ?
    """, (id_do_agendamento,))
    
    # Salva as duas ações no banco simultaneamente
    conexao.commit()
    print("✅ Cancelamento concluído! O horário já está visível para outros alunos.")
    
else:
    print("❌ Nenhum agendamento encontrado para este aluno.")

conexao.close()