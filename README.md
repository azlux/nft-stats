# nft-stats
Get the nftables counters easier to read

It kind of hard to read the output of `nft list ruleset` so there is a small program parcising the output to make counter et stats easier to read.

I make the ouput look like `iptables -nvL`

## Usage

```
nft-stats
```

## TODO
- Color
- Counter when nft named counters into the config

## Install
### With APT (recommended)
    echo "deb [signed-by=/usr/share/keyrings/azlux-archive-keyring.gpg] http://packages.azlux.fr/debian/ bullseye main" | sudo tee /etc/apt/sources.list.d/azlux.list
    sudo wget -O /usr/share/keyrings/azlux-archive-keyring.gpg  https://azlux.fr/repo.gpg
    sudo apt update
    sudo apt install nft-stats

### Manually
You can just clone the project, it's a one-script (`nft-stats.py`) project. But you will have not auto-update.

## Example
### Without nft-stats
command : `nft list ruleset`
<details>
  <summary>Click to expand!</summary>

```
root@AZLUX-PC:~# nft list ruleset
table ip filter {
        set router {
                type ipv4_addr
                comment "Azlux routers"
                elements = { xxxx/32,xxxx/28,xxxx/32 }
        }
        set ip_source_users {
                type ipv4_addr
                flags interval
                elements = { xxxx,xxxx,xxxx,xxxx }
        }
        chain OUTPUT {
                type filter hook output priority filter; policy accept;
                oif "eth0" ip daddr @router tcp dport 179 counter packets 8345 bytes 410788 accept
                oif "eth0" tcp dport 179 counter packets 0 bytes 0 drop
        }

        chain INPUT {
                type filter hook input priority filter; policy accept;
                ct state established accept
                iif "lo" accept
                iif "eth0" ip saddr @ip_source_users tcp dport { 22, 80, 443 } counter packets 2361 bytes 141660 accept
                counter packets 8742 bytes 454622 drop
        }
}
table ip6 filter {
        set ip6_source_users {
                type ipv6_addr
                flags interval
                elements = { xx:xx:xx:xx::xx,
                             xx:xx:xx:xx::xx }
        }

        chain INPUT {
                type filter hook input priority filter; policy accept;
                ct state established accept
                iif "lo" accept
                icmpv6 type { destination-unreachable, packet-too-big, time-exceeded, parameter-problem, mld-listener-query, mld-listener-report, mld-listener-done, nd-router-solicit, nd-router-advert, nd-neighbor-solicit, nd-neighbor-advert, ind-neighbor-solicit, ind-neighbor-advert, mld2-listener-report } accept comment "Accept ICMPv6"
                iif "eth0" ip6 saddr @ip6_source_users tcp dport { 22, 80, 443 } counter packets 0 bytes 0 accept
                counter packets 4 bytes 321 drop
        }
}
table inet filter {
        chain FORWARD {
                type filter hook forward priority filter; policy drop;
                counter packets 0 bytes 0 drop
        }
}

```
</details>

### With nft-stats
command : `nft-stats`
<details>
  <summary>Click to expand!</summary>

```
root@AZLUX-PC:~# nft-stats

OUTPUT IP (policy ACCEPT)
pkts       bytes      action
8240       396.13K    ACCEPT  oif "eth0" ip daddr @router tcp dport 179
0          0          DROP    oif "eth0" tcp dport 179

INPUT IP (policy ACCEPT)
pkts       bytes      action
-          -          ACCEPT  oif "eth0" tcp dport 179
-          -          ACCEPT  oif "eth0" tcp dport 179
2310       135.35K    ACCEPT  iif "eth0" ip saddr @ip_source_users tcp dport  22, 80, 443
8659       439.32K    DROP    

INPUT IP6 (policy ACCEPT)
pkts       bytes      action
-          -          ACCEPT  ct state established accept
-          -          ACCEPT  iif "lo" accept
-          -          ACCEPT  icmpv6 type  destination-unreachable, packet-too-big, time-exceeded, parameter-problem, mld-listener-query, mld-listener-report, mld-listener-done, nd-router-solicit, nd-router-advert, nd-neighbor-solicit, nd-neighbor-advert, ind-neighbor-solicit, ind-neighbor-advert, mld2-listener-report  accept comment "Accept ICMPv6"
0          0          ACCEPT  iif "eth0" ip6 saddr @ip6_source_users tcp dport  22, 80, 443
4          321        DROP    

FORWARD INET (policy DROP)
pkts       bytes      action
0          0          DROP    
```
</details>
