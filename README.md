# Extrator de Dados do SEI

<div style="display: flex; align-items: center;">
    <img src="src/assets/Identidades%20visual/log_sei.png" alt="SEI" width="50" style="margin-right: 10px;">
    <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white" alt="Streamlit" width="150" style="margin-right: 10px;">
    <img src="https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=Selenium&logoColor=white" alt="Selenium" width="140">
</div>

# Descrição do projeto

Este projeto utiliza o Streamlit para criar um aplicativo web que realiza a raspagem de dados do Sistema Eletrônico de Informações (SEI) por meio de automações implementadas com o Selenium.

:dart: **Objetivo**: Buscar dados de vários processos de forma rápida e unificada, economizando tempo e evitando o trabalho manual.

### Principais Características
* **Automação Segura**: O aplicativo **não armazena informações de login, senha ou consultas realizadas pelos usuários**. O processo de autenticação ocorre diretamente no site oficial do SEI, garantindo a segurança e a privacidade dos dados.
* **Ausência de Cache em dados sensíveis**: A função de login não salva informações em cache, evitando qualquer retenção de credenciais após o uso.
* **Interatividade Simples**: O usuário insere os dados diretamente no aplicativo, que os registra nos campos apropriados do SEI automaticamente.
* **Exportação para Excel**: Os dados coletados podem ser baixados em um arquivo Excel ou CSV.
* **Implementação e Acesso**: Este aplicativo está hospedado na infraestrutura de nuvem do Streamlit, podendo ser acessado remotamente por meio do seguinte link: [extrator-sei-cge-al.streamlit.app](https://extrator-sei-cge-al.streamlit.app/)





