import sqlite3

conexao = sqlite3.connect("agenda_personal.db")
cursor = conexao.cursor()

id_cliente_joao = 1

# 1. Busca se o João tem alguma reserva com pagamento 'Pendente'
cursor.execute("""
    SELECT id_agendamento, status_pagamento 
    FROM Agendamentos 
    WHERE id_cliente = ? AND status_pagamento = 'Pendente'
""", (id_cliente_joao,))

# Traz o resultado da busca
resultado = cursor.fetchone()

if resultado:
    id_do_agendamento = resultado[0]
    status_atual = resultado[1]
    
    print(f"Fatura encontrada (Reserva ID: {id_do_agendamento}) | Status atual: {status_atual}")
    print("Processando pagamento...")
    
    # 2. Atualiza o status financeiro da reserva para 'Pago' (Update)
    cursor.execute("""
        UPDATE Agendamentos 
        SET status_pagamento = 'Pago' 
        WHERE id_agendamento = ?
    """, (id_do_agendamento,))
    
    # Salva a alteração
    conexao.commit()
    print("✅ Pagamento confirmado! O recibo do aluno já está atualizado.")
    
else:
    print("❌ Nenhuma fatura 'Pendente' encontrada para este aluno.")

conexao.close()