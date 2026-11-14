# Acesso à Internet para VMs no EVE-NG hospedado no Google Cloud (GCP)

Guia técnico para habilitar acesso à internet em máquinas virtuais (como Ubuntu Server 22.04) executadas dentro de laboratórios do **EVE-NG** hospedados no **Google Cloud Platform (GCP)**.

---

## 1. Arquitetura e Motivo Técnico

No Google Cloud Platform, a placa de rede da instância (`nic0` / `pnet0`) aceita apenas tráfego originado do endereço IP interno atribuído à própria VM (ex.: `10.128.0.2`). Pacotes enviados diretamente por máquinas virtuais aninhadas dentro do EVE-NG (via `Cloud0`) são descartados pela VPC do GCP.

### Solução

Criar uma sub-rede privada isolada na bridge **`pnet1` (`Cloud1`)** do EVE-NG e configurar **IP Forwarding + NAT (Masquerade)** via `nftables`, mascarando o tráfego das VMs do laboratório com o IP da VM hospedeira do EVE-NG.

### Fluxo do Tráfego

```text
VM Ubuntu (192.168.100.10) ──▶ EVE-NG pnet1 (192.168.100.1) ──▶ NAT (nftables) ──▶ EVE-NG pnet0 (10.128.0.2) ──▶ NAT GCP (IP Público) ──▶ Internet
```

---

## 2. Configuração no Servidor EVE-NG (Host no GCP)

Acesse o servidor EVE-NG via **SSH** e configure a interface `pnet1` com IP estático e regras de NAT persistentes no boot.

### 2.1. Editar o arquivo de interfaces de rede

Abra o arquivo `/etc/network/interfaces`:

```bash
sudo nano /etc/network/interfaces
```

Localize o bloco referente à `pnet1` (em `# Cloud devices`), remova qualquer referência a `eth1` e deixe conforme abaixo:

```text
auto pnet1
iface pnet1 inet static
    address 192.168.100.1
    netmask 255.255.255.0
    bridge_ports none
    bridge_stp off
    post-up sysctl -w net.ipv4.ip_forward=1
    post-up nft add table ip nat ; nft 'add chain ip nat postrouting { type nat hook postrouting priority 100 ; }' ; nft add rule ip nat postrouting ip saddr 192.168.100.0/24 oifname "pnet0" masquerade
```

> **Nota:** As diretivas `post-up` garantem que o roteamento e o NAT sejam reaplicados automaticamente sempre que a VM do GCP for iniciada ou reiniciada.

### 2.2. Ativar a interface e aplicar as regras imediatamente

Execute os comandos abaixo para aplicar as alterações sem precisar reiniciar o servidor:

```bash
sudo ifdown pnet1 ; sudo ifup pnet1
sudo sysctl -w net.ipv4.ip_forward=1
sudo nft add table ip nat
sudo nft 'add chain ip nat postrouting { type nat hook postrouting priority 100 ; }'
sudo nft add rule ip nat postrouting ip saddr 192.168.100.0/24 oifname "pnet0" masquerade
```

---

## 3. Configuração da Topologia no EVE-NG (Interface Web)

1. Certifique-se de que o nó **Ubuntu** esteja desligado (_Stop_).
2. Clique com o botão direito na área de trabalho do laboratório e selecione **Network**.
3. No campo **Type**, escolha **`Cloud1`** (mapeada na `pnet1`) e clique em **Save**.
4. Conecte a interface de rede do Ubuntu (`e0`) à **`Cloud1`**.
5. Inicie o nó Ubuntu (_Start_).

---

## 4. Configuração de Rede no Ubuntu 22.04 (Guest)

Acesse o console do Ubuntu no laboratório e configure um endereço IP estático na faixa `192.168.100.0/24` com gateway apontando para a `pnet1` (`192.168.100.1`).

### 4.1. Identificar a placa de rede

```bash
ip a
```

_(Anote o nome da interface ativa, por exemplo: `ens3`)._

### 4.2. Configurar o Netplan

Abra o arquivo de configuração em `/etc/netplan/` (ex.: `00-installer-config.yaml`):

```bash
sudo nano /etc/netplan/00-installer-config.yaml
```

Substitua o conteúdo pelo modelo abaixo:

```yaml
network:
  version: 2
  ethernets:
    ens3:
      dhcp4: no
      addresses:
        - 192.168.100.10/24
      routes:
        - to: default
          via: 192.168.100.1
      nameservers:
        addresses:
          - 8.8.8.8
          - 1.1.1.1
```

### 4.3. Aplicar as configurações

```bash
sudo netplan try
sudo netplan apply
```

---

## 5. Validação e Troubleshooting

### Testes de Conectividade no Ubuntu (Guest)

```bash
ping -c 3 192.168.100.1   # Testa comunicação com o gateway (EVE-NG)
ping -c 3 8.8.8.8         # Testa saída para internet (NAT)
ping -c 3 google.com      # Testa resolução de nomes (DNS)
```

### Comandos Úteis de Diagnóstico no EVE-NG (Host)

- **Verificar se a VM está anexada na bridge `pnet1`:**

  ```bash
  brctl show pnet1
  ```

  _(Deve exibir uma interface `vunl...` ou `bun...` na coluna `interfaces`)._

- **Verificar se o IP Forwarding está ativo:**

  ```bash
  cat /proc/sys/net/ipv4/ip_forward
  ```

  _(O retorno esperado é `1`)._

- **Verificar regras de NAT ativas no `nftables`:**
  ```bash
  sudo nft list table ip nat
  ```
