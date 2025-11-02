# Scripts organizados

Este diretório contém a versão organizada/essencial dos scripts usados para rodar a aplicação em desenvolvimento.

Files:
- `start.sh` - inicia o dashboard (ativa `.venv` se presente e executa `app.py`). Use este script para desenvolvimento local.

Observação sobre scripts originais
 - Os scripts de configuração/sistema que modificam `/etc` ou instalam serviços (p.ex. `configurar_suricata.sh`, `configurar_clamav.sh`) foram mantidos no diretório raíz do repositório sem alteração. Eles são úteis para a configuração inicial do sistema e não são necessários para executar o dashboard em um ambiente já preparado.
