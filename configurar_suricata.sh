#!/bin/bash
set -euo pipefail

CONFIG="/etc/suricata/suricata.yaml"
BACKUP="${CONFIG}.bak.$(date +%Y%m%d_%H%M%S)"
TMP="${CONFIG}.tmp.$(date +%s)"

echo "1/7 - Verificando arquivo: $CONFIG"
if [ ! -f "$CONFIG" ]; then
  echo "ERRO: $CONFIG não existe."
  exit 1
fi

echo "2/7 - Criando backup em: $BACKUP"
cp -a "$CONFIG" "$BACKUP"

echo "3/7 - Substituindo interface af-packet (eth0 -> wlp2s0) e garantindo parâmetros adicionais..."
# Substitui qualquer ocorrência de "interface: eth0" por "interface: wlp2s0"
# e, se existir a linha interface, insere as linhas de cluster/defrag logo após (se não houver).
awk -v iface_old="eth0" -v iface_new="wlp2s0" '
  BEGIN { inserted=0; }
  {
    print $0;
    if ($0 ~ "^[[:space:]]*interface:[[:space:]]*"+iface_old"[[:space:]]*$") {
      # substituir a linha já feita pela impressão acima — ajustar via stderr
    }
  }
' "$CONFIG" > "$TMP".awk && mv "$TMP".awk "$TMP"

# Substituição simples da interface (ajusta espaços)
sed -E "s/^[[:space:]]*interface:[[:space:]]*${iface_old}/${printf 'interface: %s' "$iface_new"}/" "$CONFIG" > "$TMP" 2>/dev/null || true

# If sed replacement didn't run because pattern spacing differs, do a more permissive replacement:
if ! grep -q -E "^[[:space:]]*interface:[[:space:]]*wlp2s0" "$TMP"; then
  # create a more permissive copy from the original replacing eth0 anywhere after 'interface:'
  sed -E "s/(^[[:space:]]*interface:[[:space:]]*)eth0/\\1wlp2s0/" "$CONFIG" > "$TMP"
fi

# Ensure cluster-id/cluster-type/defrag present immediately under the af-packet interface block
python3 - <<'PY'
import sys,ruamel.yaml,os
cfg="/etc/suricata/suricata.yaml"
tmp="/tmp/suricata_yaml_edit.$$"
from ruamel.yaml import YAML
yaml=YAML()
yaml.preserve_quotes=True
with open(cfg,'r') as f:
    data=yaml.load(f)
# if af-packet configured as list, iterate and fix
if 'af-packet' in data:
    changed=False
    ap=data['af-packet']
    if isinstance(ap,list):
        for entry in ap:
            # check if entry has interface key
            if isinstance(entry,dict):
                if 'interface' in entry:
                    if entry['interface']=='eth0':
                        entry['interface']='wlp2s0'; changed=True
                    # ensure cluster-id etc exist
                    if 'cluster-id' not in entry:
                        entry['cluster-id']=99; changed=True
                    if 'cluster-type' not in entry:
                        entry['cluster-type']='cluster_flow'; changed=True
                    if 'defrag' not in entry:
                        entry['defrag']='yes'; changed=True
    if changed:
        with open(tmp,'w') as f:
            yaml.dump(data,f)
        os.replace(tmp,cfg)
        print("AF-PACKET atualizado via YAML")
    else:
        print("AF-PACKET já estava consistente")
else:
    print("Nenhuma seção af-packet encontrada no YAML")
PY

# After Python modification, reload to tmp variable result
mv "$CONFIG" "$CONFIG".postedit || true
mv "$BACKUP" "$BACKUP".keeping || true
# restore original for subsequent steps
cp -a "$CONFIG".postedit "$CONFIG"

echo "4/7 - Garantindo seção eve-log (ativada e com filename absoluto e tipos relevantes)..."

python3 - <<'PY'
import sys,os
from ruamel.yaml import YAML
cfg="/etc/suricata/suricata.yaml"
yaml=YAML()
yaml.preserve_quotes=True
with open(cfg,'r') as f:
    data=yaml.load(f)
if 'outputs' not in data:
    data['outputs']=[]
# find eve-log in outputs
found=False
for out in data['outputs']:
    if isinstance(out,dict) and 'eve-log' in out:
        eve=out['eve-log']
        if eve is None:
            eve={}
            out['eve-log']=eve
        # set required values
        eve['enabled']=True
        eve['filetype']='regular'
        eve['filename']='/var/log/suricata/eve.json'
        # ensure types list contains entries
        types=eve.get('types',[])
        wanted=['alert','dns','http','tls']
        for w in wanted:
            if w not in types:
                types.append(w)
        eve['types']=types
        found=True
        break
if not found:
    # append new eve-log block
    eve_block={'eve-log': {'enabled': True, 'filetype': 'regular', 'filename': '/var/log/suricata/eve.json', 'types': ['alert','dns','http','tls']}}
    data['outputs'].append(eve_block)
# write back
with open(cfg,'w') as f:
    yaml.dump(data,f)
print("eve-log verificado/atualizado")
PY

echo "5/7 - Removendo socket antigo (se existir) e PID residual..."
sudo rm -f /var/run/suricata/suricata-command.socket /run/suricata.pid /var/run/suricata.pid || true

echo "6/7 - Reiniciando serviço Suricata..."
sudo systemctl daemon-reload || true
sudo systemctl restart suricata

echo "7/7 - Verificando status e existência do eve.json..."
sudo systemctl status suricata --no-pager
sleep 1
EVE="/var/log/suricata/eve.json"
if [ -f "$EVE" ]; then
  echo "OK: $EVE existe - tamanho: $(stat -c%s "$EVE") bytes"
else
  echo "AVISO: $EVE não encontrado. Verifique /etc/suricata/suricata.yaml manualmente."
  echo "Últimas linhas do journal para suricata:"
  sudo journalctl -u suricata -n 50 --no-pager
fi

echo "Script finalizado."
