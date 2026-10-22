# FitAgenda Pro 💪

Um sistema web completo de gestão de agendamentos e horários desenvolvido para Personal Trainers, construído com foco em segurança, facilidade de uso e design responsivo (Dark Mode).

### 🚀 Funcionalidades Principais (MVP)
* **Autenticação Segura:** Registo e Login de clientes com senhas encriptadas (Werkzeug Security).
* **Painel Admin Protegido:** Área restrita para gestão de horários, vitrine de vagas e controle de status de pagamentos.
* **Calendário Dinâmico:** Integração com FullCalendar.js para visualização da semana com etiquetas de cores (Livre, Pendente, Pago).
* **Fluxo de Reservas:** Sistema que evita choque de horários, retirando a vaga da vitrine assim que selecionada e gerando um checkout de pagamento.
* **Exportação de Relatórios:** Geração automática de relatórios financeiros em Excel utilizando Pandas.

### 🛠️ Tecnologias Utilizadas
* **Back-end:** Python, Flask
* **Banco de Dados:** SQLite
* **Front-end:** HTML5, Jinja2, Bootstrap 5, FullCalendar.js
* **Deploy/Hospedagem:** PythonAnywhere

### 🌐 Live Demo
O projeto está online e funcional. Pode testá-lo aqui: https://tf26.pythonanywhere.com/
*(Nota para Recrutadores: Para testar o painel administrativo, acesse `/login_admin` com a senha `TreinoPro2026`)*
