from flask import Flask, request, session, redirect, send_file, render_template
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import pandas as pd
import io
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from datetime import timedelta
import os

app = Flask(__name__)
# Chave de segurança forte para a nuvem
app.secret_key = "a8f!9GzP$2xK#vL7mQ@wE1yR*cT4bN" 
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60) 

# Configuração do Caminho Absoluto para o Banco de Dados (Evita Erro 500)
PASTA_PROJETO = os.path.dirname(os.path.abspath(__file__))
CAMINHO_BANCO = os.path.join(PASTA_PROJETO, "agenda_personal.db")

SENHA_ADMIN_HASH = generate_password_hash("Husky26BF")

CABECALHO = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FitAgenda Pro</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <style>
        body { background-color: #121214; color: #e1e1e6; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .card-custom { background-color: #202024; border: 1px solid #323238; border-radius: 12px; }
        .btn-purple { background-color: #8257e5; color: white; border: none; transition: 0.2s; }
        .btn-purple:hover { background-color: #6833c5; color: white; }
        .list-group-item { background-color: #121214; border-color: #323238; color: #e1e1e6; }
        strong, h2, h3, h4, h5 { color: #ffffff !important; }
        .text-purple { color: #8257e5; }
    </style>
</head>
<body class="d-flex align-items-center justify-content-center min-vh-100 py-4">
<div class="container" style="max-width: 600px;">
<div class="card card-custom shadow-lg p-4">
"""
RODAPE = "</div></div></body></html>"

@app.after_request
def add_security_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route("/")
def pagina_inicial():
    return render_template('index.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    mensagem_erro = ""
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]
        
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()
        cursor.execute("SELECT id_cliente, nome_completo, senha_hash FROM Clientes WHERE email = ?", (email,))
        aluno = cursor.fetchone()
        conexao.close()
        
        if aluno and (aluno[2] == senha or check_password_hash(aluno[2], senha)):
            session.permanent = True
            session['id_cliente'] = aluno[0]
            session['nome_cliente'] = aluno[1]
            return redirect("/")
        else:
            mensagem_erro = "<div class='alert alert-danger p-2 text-center border-0 small'>❌ E-mail ou senha incorretos!</div>"
            
    return render_template('login.html', mensagem_erro=mensagem_erro)


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    mensagem = ""
    if request.method == "POST":
        nome = request.form["nome"]
        whatsapp = request.form["whatsapp"]
        email = request.form["email"]
        senha = request.form["senha"]
        senha_criptografada = generate_password_hash(senha)
        
        conexao = sqlite3.connect(CAMINHO_BANCO)
        cursor = conexao.cursor()
        try:
            cursor.execute("INSERT INTO Clientes (nome_completo, telefone_whatsapp, email, senha_hash) VALUES (?, ?, ?, ?)", 
                           (nome, whatsapp, email, senha_criptografada))
            conexao.commit()
            mensagem = "<div class='alert alert-success p-2 text-center border-0 small'>✅ Conta criada! Faça login.</div>"
        except sqlite3.IntegrityError:
            mensagem = "<div class='alert alert-danger p-2 text-center border-0 small'>❌ Este e-mail já está cadastrado.</div>"
        finally:
            conexao.close()

    return render_template('cadastro.html', mensagem=mensagem)


@app.route("/login_admin", methods=["GET", "POST"])
def login_admin():
    mensagem_erro = ""
    if request.method == "POST":
        senha_digitada = request.form["senha_admin"]
        
        if check_password_hash(SENHA_ADMIN_HASH, senha_digitada):
            session.permanent = True
            session['admin_logado'] = True
            return redirect("/admin")
        else:
            mensagem_erro = "<div class='alert alert-danger p-2 text-center border-0 small'>❌ Senha incorreta! Acesso negado.</div>"
            
    return render_template('login_admin.html', mensagem_erro=mensagem_erro)


@app.route("/admin", methods=["GET", "POST"])
def painel_admin():
    if not session.get('admin_logado'):
        return redirect("/login_admin")

    mensagem = ""
    conexao = sqlite3.connect(CAMINHO_BANCO)
    cursor = conexao.cursor()

    if request.method == "POST":
        if "data_horario" in request.form:
            novo = request.form["data_horario"].replace("T", " ") + ":00"
            cursor.execute("INSERT INTO Agenda (data_horario) VALUES (?)", (novo,))
            conexao.commit()
            mensagem = "<div class='alert alert-success p-2 text-center border-0 small'>✅ Horário adicionado!</div>"
        elif "id_agendamento_pago" in request.form:
            cursor.execute("UPDATE Agendamentos SET status_pagamento = 'Pago' WHERE id_agendamento = ?", (request.form["id_agendamento_pago"],))
            conexao.commit()
            mensagem = "<div class='alert alert-success p-2 text-center border-0 small'>✅ Pagamento confirmado!</div>"
        elif "id_agendamento_cancelar" in request.form:
            id_ag = request.form["id_agendamento_cancelar"]
            cursor.execute("SELECT id_agenda FROM Agendamentos WHERE id_agendamento = ?", (id_ag,))
            res = cursor.fetchone()
            if res:
                cursor.execute("DELETE FROM Agendamentos WHERE id_agendamento = ?", (id_ag,))
                cursor.execute("UPDATE Agenda SET status_horario = 'Livre' WHERE id_agenda = ?", (res[0],))
                conexao.commit()
                mensagem = "<div class='alert alert-danger p-2 text-center border-0 small'>🗑️ Treino cancelado! Horário voltou para a vitrine.</div>"
        elif "id_agenda_apagar" in request.form:
            id_ag = request.form["id_agenda_apagar"]
            cursor.execute("DELETE FROM Agenda WHERE id_agenda = ?", (id_ag,))
            conexao.commit()
            mensagem = "<div class='alert alert-danger p-2 text-center border-0 small'>🗑️ Horário apagado do sistema!</div>"

    cursor.execute("SELECT id_agenda, data_horario FROM Agenda WHERE status_horario = 'Livre' ORDER BY data_horario")
    horarios_livres_raw = cursor.fetchall()
    
    html_livres = ""
    eventos_para_calendario = []
    
    for h in horarios_livres_raw:
        html_livres += f"<li class='list-group-item d-flex justify-content-between align-items-center py-2'>{h[1]} <form method='POST' class='m-0 p-0'><input type='hidden' name='id_agenda_apagar' value='{h[0]}'><button type='submit' class='btn btn-sm btn-outline-danger' onclick=\"return confirm('Apagar este horário da agenda?')\"><i class='bi bi-trash'></i></button></form></li>"
        eventos_para_calendario.append({
            "title": "LIVRE",
            "start": h[1].replace(" ", "T"),
            "color": "#8257e5"
        })

    cursor.execute("""
    SELECT Agendamentos.id_agendamento, Clientes.nome_completo, Agenda.data_horario, Agendamentos.status_pagamento
    FROM Agendamentos INNER JOIN Clientes ON Agendamentos.id_cliente = Clientes.id_cliente
    INNER JOIN Agenda ON Agendamentos.id_agenda = Agenda.id_agenda ORDER BY Agenda.data_horario
    """)
    alunos_raw = cursor.fetchall()
    html_alunos = ""
    
    for aluno in alunos_raw:
        status_html = f"<span class='text-danger fw-bold'>Pendente</span><form method='POST' class='d-inline m-0 p-0 ms-2'><input type='hidden' name='id_agendamento_pago' value='{aluno[0]}'><button type='submit' class='btn btn-sm btn-success'>Pago</button></form>" if aluno[3] == 'Pendente' else "<span class='text-success fw-bold'>Pago</span>"
        botao_cancelar = f"<form method='POST' class='d-inline m-0 p-0 ms-2'><input type='hidden' name='id_agendamento_cancelar' value='{aluno[0]}'><button type='submit' class='btn btn-sm btn-outline-danger' onclick=\"return confirm('Cancelar este agendamento de {aluno[1]}?')\"><i class='bi bi-x-circle'></i></button></form>"
        html_alunos += f"<li class='list-group-item d-flex justify-content-between align-items-center py-3'><div><strong>{aluno[1]}</strong><br><small class='text-secondary'>{aluno[2]}</small></div><div>{status_html}{botao_cancelar}</div></li>"
        
        cor_calendario = "#198754" if aluno[3] == "Pago" else "#dc3545"
        eventos_para_calendario.append({
            "title": f"{aluno[1].split(' ')[0]} ({aluno[3]})",
            "start": aluno[2].replace(" ", "T"),
            "color": cor_calendario
        })

    conexao.close()

    return render_template('admin.html', mensagem=mensagem, html_alunos=html_alunos, html_livres=html_livres, eventos_calendario=eventos_para_calendario)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/horarios")
def vitrine_horarios():
    if 'id_cliente' not in session: return redirect("/login")
    conexao = sqlite3.connect(CAMINHO_BANCO)
    cursor = conexao.cursor()
    cursor.execute("SELECT id_agenda, data_horario FROM Agenda WHERE status_horario = 'Livre' ORDER BY data_horario")
    horarios = cursor.fetchall()
    conexao.close()
    
    html_lista = ""
    if not horarios:
        html_lista = "<p class='text-center text-muted py-3'>Nenhum horário livre de momento.</p>"
    else:
        for h in horarios:
            html_lista += f"<li class='list-group-item d-flex justify-content-between align-items-center py-3'><strong>{h[1]}</strong><a href='/agendar/{h[0]}' class='btn btn-sm btn-purple fw-bold px-3'>Reservar</a></li>"
        
    return CABECALHO + f"""
        <h3 class="mb-4 text-center text-white"><i class="bi bi-calendar-week text-purple"></i> Agenda de Treinos</h3>
        <ul class='list-group mb-4 shadow-sm rounded'>{html_lista}</ul>
        <a href='/' class='btn btn-outline-light w-100'><i class="bi bi-arrow-left"></i> Voltar ao Início</a>
    """ + RODAPE


@app.route("/agendar/<int:id_horario>")
def fazer_reserva(id_horario):
    if 'id_cliente' not in session: return redirect("/login")
    conexao = sqlite3.connect(CAMINHO_BANCO)
    cursor = conexao.cursor()
    cursor.execute("SELECT status_horario FROM Agenda WHERE id_agenda = ?", (id_horario,))
    resultado = cursor.fetchone()
    
    if resultado and resultado[0] == 'Livre':
        cursor.execute("INSERT INTO Agendamentos (id_cliente, id_agenda) VALUES (?, ?)", (session['id_cliente'], id_horario))
        id_agendamento_criado = cursor.lastrowid
        cursor.execute("UPDATE Agenda SET status_horario = 'Reservado' WHERE id_agenda = ?", (id_horario,))
        conexao.commit()
        conexao.close()
        return redirect(f"/pagamento/{id_agendamento_criado}")
    else:
        conexao.close()
        return CABECALHO + "<div class='text-center p-4'><h2 class='text-danger mb-3'><i class='bi bi-x-circle'></i> Ops!</h2><p class='text-light'>Este horário já não está disponível.</p><a href='/horarios' class='btn btn-outline-light mt-3'>Tentar outro</a></div>" + RODAPE


@app.route("/pagamento/<int:id_agendamento>", methods=["GET", "POST"])
def checkout_simulado(id_agendamento):
    if 'id_cliente' not in session: return redirect("/login")
    conexao = sqlite3.connect(CAMINHO_BANCO)
    cursor = conexao.cursor()
    
    if request.method == "POST":
        cursor.execute("UPDATE Agendamentos SET status_pagamento = 'Pago' WHERE id_agendamento = ?", (id_agendamento,))
        conexao.commit()
        conexao.close()
        return redirect("/meus_treinos")
        
    cursor.execute("""
        SELECT Agenda.data_horario FROM Agendamentos 
        INNER JOIN Agenda ON Agendamentos.id_agenda = Agenda.id_agenda 
        WHERE Agendamentos.id_agendamento = ? AND Agendamentos.id_cliente = ?
    """, (id_agendamento, session['id_cliente']))
    detalhes = cursor.fetchone()
    conexao.close()
    
    if not detalhes: return redirect("/meus_treinos")
    
    return CABECALHO + f"""
        <h3 class="mb-4 text-center text-white"><i class="bi bi-credit-card text-purple"></i> Checkout Seguro</h3>
        <div class="p-4 rounded-3 mb-4 text-center" style="background-color: #121214; border: 1px solid #323238;">
            <h5 class="text-white mb-3">Treino com Personal</h5>
            <p class="text-secondary mb-3"><i class="bi bi-calendar-event"></i> {detalhes[0]}</p>
            <div class="border-top border-secondary pt-3 mt-2 d-flex justify-content-between align-items-center">
                <span class="text-secondary">Total:</span>
                <h2 class="text-success fw-bold m-0">R$ 80,00</h2>
            </div>
        </div>
        <form method="POST">
            <button type="submit" class="btn btn-success btn-lg w-100 fw-bold mb-3 py-2"><i class="bi bi-phone"></i> Pagar com PIX</button>
            <button type="submit" class="btn btn-purple btn-lg w-100 fw-bold py-2"><i class="bi bi-credit-card"></i> Pagar com Cartão</button>
        </form>
        <a href="/meus_treinos" class="btn btn-outline-secondary text-light w-100 mt-4 border-secondary">Pagar depois</a>
    """ + RODAPE


@app.route("/meus_treinos")
def meus_treinos():
    if 'id_cliente' not in session: return redirect("/login")
    conexao = sqlite3.connect(CAMINHO_BANCO)
    cursor = conexao.cursor()
    cursor.execute("""
    SELECT Agendamentos.id_agendamento, Agenda.data_horario, Agendamentos.status_pagamento
    FROM Agendamentos INNER JOIN Agenda ON Agendamentos.id_agenda = Agenda.id_agenda
    WHERE Agendamentos.id_cliente = ? ORDER BY Agenda.data_horario
    """, (session['id_cliente'],))
    agendamentos = cursor.fetchall()
    conexao.close()
    
    html_lista = ""
    if not agendamentos:
        html_lista = "<p class='text-center text-secondary py-3'>Você ainda não tem treinos agendados.</p>"
    else:
        for ag in agendamentos:
            id_ag, data, status = ag[0], ag[1], ag[2]
            cor_status = "text-success" if status == "Pago" else "text-danger"
            botao_pagar = "" if status == "Pago" else f"<a href='/pagamento/{id_ag}' class='btn btn-sm btn-purple me-2'>Pagar</a>"
                
            html_lista += f"""
            <li class='list-group-item d-flex justify-content-between align-items-center flex-wrap py-3'>
                <div><strong class="fs-5">{data}</strong><br><small class='{cor_status} fw-bold'>Status: {status}</small></div>
                <div class="mt-2 mt-sm-0">
                    {botao_pagar}
                    <a href='/cancelar/{id_ag}' class='btn btn-sm btn-outline-danger' onclick="return confirm('Tem certeza que deseja cancelar o treino?')"><i class="bi bi-trash3"></i> Cancelar</a>
                </div>
            </li>
            """
            
    return CABECALHO + f"""
        <h3 class="mb-4 text-center text-white"><i class="bi bi-bag-check text-purple"></i> Meus Treinos</h3>
        <ul class='list-group mb-4 shadow-sm rounded'>{html_lista}</ul>
        <a href='/' class='btn btn-outline-light w-100'><i class="bi bi-arrow-left"></i> Voltar ao Início</a>
    """ + RODAPE


@app.route("/cancelar/<int:id_agendamento>")
def cancelar_reserva(id_agendamento):
    if 'id_cliente' not in session: return redirect("/login")
    conexao = sqlite3.connect(CAMINHO_BANCO)
    cursor = conexao.cursor()
    cursor.execute("SELECT id_agenda FROM Agendamentos WHERE id_agendamento = ? AND id_cliente = ?", (id_agendamento, session['id_cliente']))
    resultado = cursor.fetchone()
    if resultado:
        cursor.execute("DELETE FROM Agendamentos WHERE id_agendamento = ?", (id_agendamento,))
        cursor.execute("UPDATE Agenda SET status_horario = 'Livre' WHERE id_agenda = ?", (resultado[0],))
        conexao.commit()
    conexao.close()
    return redirect("/meus_treinos")


@app.route("/exportar_excel")
def exportar():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    df = pd.read_sql_query("""SELECT Clientes.nome_completo AS "Nome", Clientes.telefone_whatsapp AS "WhatsApp", Agenda.data_horario AS "Data/Hora", Agendamentos.status_pagamento AS "Pagamento" FROM Agendamentos INNER JOIN Clientes ON Agendamentos.id_cliente = Clientes.id_cliente INNER JOIN Agenda ON Agendamentos.id_agenda = Agenda.id_agenda ORDER BY Agenda.data_horario""", conexao)
    conexao.close()
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Relatório')
        planilha = writer.sheets['Relatório']
        fundo = PatternFill(start_color="8257e5", end_color="8257e5", fill_type="solid")
        fonte = Font(bold=True, color="FFFFFF")
        centro = Alignment(horizontal="center")
        for celula in planilha[1]:
            celula.font, celula.fill, celula.alignment = fonte, fundo, centro
        for coluna in planilha.columns:
            try: planilha.column_dimensions[coluna[0].column_letter].width = max([len(str(c.value)) for c in coluna]) + 5
            except: pass
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="Relatorio_Faturamento.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    app.run(debug=False)