/*
    Copyright © 2025 Cognizant.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    nat.c
    Author:         Bryce Young <bryce.young@cognizant.com>
    Description:    NAT/PAT BPF program for packet PRE/POST routing
*/

#include <linux/bpf.h>
#include <bpf/bpf_endian.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

#include <linux/if_ether.h>
#include <linux/in.h>
#include <linux/ip.h>
#include <linux/pkt_cls.h>
#include <linux/tcp.h>
#include <linux/types.h>

struct nat_key {
    __u32 ip;      
    __u16 port;    
    __u8 proto;
    __u8 padding;
};

struct nat_ct_key {
    __u32 src_ip;
    __u16 src_port;
    __u32 dst_ip;
    __u16 dst_port;
};

struct nat_value {
    __u32 ip;
    __u16 port;
    __u16 padding;
};

// From include/uapi/linux/in.h:
// IPPROTO_IP = 0;  -- Used as a wildcard for all protocols
// IPPROTO_ICMP = 1;
// IPPROTO_TCP = 6;
// IPPROTO_UDP = 17;

// Prerouting rules
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 256);
    __type(key, struct nat_key);
    __type(value, struct nat_value);
    __uint(pinning, LIBBPF_PIN_BY_NAME);
} nat_prerouting SEC(".maps");

// Postrouting rules
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 256);
    __type(key, struct nat_key);
    __type(value, struct nat_value);
    __uint(pinning, LIBBPF_PIN_BY_NAME);
} nat_postrouting SEC(".maps");

// NAT connection tracking
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 1024);
    __type(key, struct nat_ct_key);
    __type(value, struct nat_value);
    __uint(pinning, LIBBPF_PIN_BY_NAME);
} nat_connection_tracking SEC(".maps");


// Extract the ethheader from the packet
static __always_inline struct ethhdr* get_eth_header(void* data, void* data_end) {
    struct ethhdr *eth = data;
    if ((void *)(eth + 1) > data_end)
        return NULL;

    return eth;
}

// Extract the ipheader from the packet
static __always_inline struct iphdr* get_ip_header(void* data, void* data_end, struct ethhdr *eth) {
    if (eth->h_proto != bpf_htons(ETH_P_IP))
        return NULL;

    struct iphdr *ip = data + sizeof(*eth);
    if ((void *)(ip + 1) > data_end)
        return NULL;

    return ip;
}

// Extract the tcp header from the packet
static __always_inline struct tcphdr* get_tcp_header(void* data, void* data_end, __u32 tcp_offset) {
    if (data + tcp_offset > data_end)
        return NULL;

    struct tcphdr *tcp = data + tcp_offset;

    if ((void *)tcp + sizeof(*tcp) > data_end)
        return NULL;

    return tcp;
}

static __always_inline int print_ip(const char* label, __u32 ip, __u16 port) {
    __u8 octet1 = (ip >> 24) & 0xFF;
    __u8 octet2 = (ip >> 16) & 0xFF;
    __u8 octet3 = (ip >> 8) & 0xFF;
    __u8 octet4 = ip & 0xFF;

    if(octet1 == 192 && octet2 == 168 && octet3 == 0) {
        bpf_printk("%s: 192.168.0.%u:%u", label, octet4, port);
    } else {
        bpf_printk("%s", label);
        bpf_printk("%u.%u", octet1, octet2);
        bpf_printk("%u.%u", octet3, octet4);
        bpf_printk(":%u", port);
    }

    return 1;
}

static __always_inline struct nat_value* lookup_nat(__u32 ip, __u16 port, __u8 proto) {
    struct nat_value* value = NULL;
    struct nat_key key;

    __builtin_memset(&key, 0, sizeof(key));

    // Check if there is a rule for the IP
    key.ip = ip;
    key.port = 0;
    key.proto = 0;
    value = bpf_map_lookup_elem(&nat_prerouting, &key);

        // Check if there is a rule for the protocol
    if(!value) {
        key.ip = 0;
        key.proto = proto;
        value = bpf_map_lookup_elem(&nat_prerouting, &key);
    }

    // Check if there is a rule for IP + protocol
    if(!value) {
        key.ip = ip;
        value = bpf_map_lookup_elem(&nat_prerouting, &key);
    }

    // Check for a port-specific rule (TCP and UDP only)
    if (!value && (0 != port)) {           
        key.ip = 0;
        key.port = port;
        key.proto = 0;
        value = bpf_map_lookup_elem(&nat_prerouting, &key);

        // Check if there is a rule for the port + protocol
        if(!value) {
            key.proto = proto;
            value = bpf_map_lookup_elem(&nat_prerouting, &key);
        }

        // Check if there is a rule for the IP + port + protocol
        if(!value) {
            key.ip = ip;
            value = bpf_map_lookup_elem(&nat_prerouting, &key);
        }
    }

    return value;
}

static __always_inline int track_connection(__u32 src_ip, __u16 src_port, __u32 dst_ip, __u16 dst_port, __u32 nat_ip, __u16 nat_port) {
    struct nat_ct_key rdnat_key;
    struct nat_ct_key snat_key;
    struct nat_ct_key rsnat_key;
    struct nat_value rdnat_value;
    struct nat_value snat_value;
    struct nat_value rsnat_value;

    __builtin_memset(&rdnat_key, 0, sizeof(rdnat_key));
    __builtin_memset(&snat_key, 0, sizeof(snat_key));
    __builtin_memset(&rsnat_key, 0, sizeof(rsnat_key));
    __builtin_memset(&rdnat_value, 0, sizeof(rdnat_value));
    __builtin_memset(&snat_value, 0, sizeof(snat_value));
    __builtin_memset(&rsnat_value, 0, sizeof(rsnat_value));

    rdnat_key.src_ip  = nat_ip;      // 192.168.0.180
    rdnat_key.src_port = nat_port;   // 9090
    rdnat_key.dst_ip = dst_ip;       // 192.168.0.181
    rdnat_key.dst_port = dst_port;   // 1234

    snat_key.src_ip = src_ip;       // 192.168.0.180
    snat_key.src_port = src_port;   // 41728
    snat_key.dst_ip = nat_ip;       // 192.168.0.180
    snat_key.dst_port = nat_port;   // 9090

    rsnat_key.src_ip = nat_ip;       // 192.168.0.180
    rsnat_key.src_port = nat_port;   // 9090
    rsnat_key.dst_ip = src_ip;       // 192.168.0.180
    rsnat_key.dst_port = src_port;   // 41728

    rdnat_value.ip = src_ip;         // 192.168.0.180
    rdnat_value.port = src_port;     // 41728

    snat_value.ip = dst_ip;         // 192.168.0.181
    snat_value.port = dst_port;     // 1234

    bpf_printk("Tracking connection");
    print_ip("Src", src_ip, src_port);
    print_ip("Dst", dst_ip, dst_port);
    print_ip("NAT", nat_ip, nat_port);
    bpf_map_update_elem(&nat_connection_tracking, &rdnat_key, &rdnat_value, BPF_ANY);
    bpf_map_update_elem(&nat_connection_tracking, &snat_key, &snat_value, BPF_ANY);
    bpf_map_update_elem(&nat_connection_tracking, &rsnat_key, &snat_value, BPF_ANY);   

    return 1;
}



SEC("action/ingress")
int prerouting(struct __sk_buff *ctx) {
    struct ethhdr* eth;
    struct iphdr* ip;
    struct tcphdr* tcp;
    //struct nat_key key;
    struct nat_ct_key ct_key;
    struct nat_value* value = NULL;
    void* data;
    void* data_end;

    __u32 src_ip = 0;
    __u16 src_port = 0;
    __u32 dst_ip = 0;
    __u16 dst_port = 0;
    __u32 dnat_ip = 0;    
    __u16 dnat_port = 0;
    
    // Initialise memory for keys
    //__builtin_memset(&key, 0, sizeof(key));
    __builtin_memset(&ct_key, 0, sizeof(ct_key));

    // Extract ethernet and ip headers
    data = (void *)(long)ctx->data;
    data_end = (void *)(long)ctx->data_end;

    eth = get_eth_header(data, data_end);
    if(!eth)
        return TC_ACT_OK;

    ip = get_ip_header(data, data_end, eth);
    if (!ip)
        return TC_ACT_OK;

    src_ip = bpf_ntohl(ip->saddr);
    dst_ip = bpf_ntohl(ip->daddr);

    tcp = get_tcp_header(data, data_end, sizeof(struct ethhdr) + sizeof(struct iphdr));

    if ((ip->protocol == IPPROTO_TCP || ip->protocol == IPPROTO_UDP)) {   
        if (!tcp)
            return TC_ACT_OK;

        src_port = bpf_ntohs(tcp->source);
        dst_port = bpf_ntohs(tcp->dest);
    }

    ct_key.src_ip = src_ip;
    ct_key.dst_ip = dst_ip;
    ct_key.src_port = src_port;
    ct_key.dst_port = dst_port;

    value = bpf_map_lookup_elem(&nat_connection_tracking, &ct_key);

    // If there isn't an existing connection, check for a NAT rule
    if (!value) {
        value = lookup_nat(dst_ip, dst_port, ip->protocol);

        // If a NAT rule is found, update the connection tracking
        if(value) {
            (void)track_connection(src_ip, src_port, dst_ip, dst_port, value->ip, value->port);
        }
    }

    // If an active connection or NAT rule is found, update the destination IP/Port in the packet
    if (value) {
        int do_fib = 0;
        int ifindex = ctx->ifindex;

        bpf_printk("PREROUTING");
        bpf_printk("Packet Info:");
        print_ip("Src", src_ip, src_port);
        print_ip("Dst", dst_ip, dst_port);
        print_ip("DNAT", value->ip, value->port);
        

        // Convert the IP and Port to network byte order
        dnat_ip = bpf_htonl(value->ip);
        dnat_port = bpf_htons(value->port);
        
        if (0 != dnat_ip) {
            bpf_printk("Do DNAT");

            // Update the IP header
            bpf_skb_store_bytes(ctx, sizeof(struct ethhdr) + offsetof(struct iphdr, daddr), &dnat_ip, sizeof(__u32), 0);
            bpf_l3_csum_replace(ctx, sizeof(struct ethhdr) + offsetof(struct iphdr, check), bpf_htonl(dst_ip), dnat_ip, sizeof(__u32));
            do_fib = 1;
        }

        if(tcp && dnat_port != 0) {
            bpf_printk("Do DPAT");

            // Update the TCP header
            bpf_skb_store_bytes(ctx, sizeof(struct ethhdr) + sizeof(struct iphdr) + offsetof(struct tcphdr, dest), &dnat_port, sizeof(__u16), 0);
            bpf_l4_csum_replace(ctx, sizeof(struct ethhdr) + sizeof(struct iphdr) + offsetof(struct tcphdr, check), bpf_htons(dst_port), dnat_port, sizeof(__u16));
        }

        if(do_fib) {
            bpf_printk("Do FIB");

            // Perform FIB lookup
            struct bpf_fib_lookup fib;
            __builtin_memset(&fib, 0, sizeof(fib));

            fib.family = 2; // AF_INET
            fib.ifindex = ctx->ifindex;
            fib.ipv4_src = bpf_htonl(src_ip);
            fib.ipv4_dst = dnat_ip;


            if (BPF_FIB_LKUP_RET_SUCCESS == bpf_fib_lookup(ctx, &fib, sizeof(fib), 0)) {
                ifindex = fib.ifindex;

                // Apply new MAC addresses for forwarding
                bpf_skb_store_bytes(ctx, offsetof(struct ethhdr, h_source), fib.smac, 6, 0);
                bpf_skb_store_bytes(ctx, offsetof(struct ethhdr, h_dest), fib.dmac, 6, 0);
            } else {
                // Drop packet if no route found
                return TC_ACT_SHOT;
            }
        }

        bpf_printk("Redirecting\n");
        return bpf_redirect(ifindex, BPF_FIB_LKUP_RET_SUCCESS);
    }

    return TC_ACT_OK;
}


SEC("action/egress")
int postrouting(struct __sk_buff *ctx) {
    struct ethhdr* eth;
    struct iphdr* ip;
    struct tcphdr* tcp;
    struct nat_ct_key ct_key;
    struct nat_value* value = NULL;
    void* data;
    void* data_end;
    
    __u32 src_ip = 0;
    __u16 src_port = 0;
    __u32 dst_ip = 0;   
    __u16 dst_port = 0;
    __u32 snat_ip = 0;
    __u16 snat_port = 0;

    // Initialise memory for key
    __builtin_memset(&ct_key, 0, sizeof(ct_key));

    // Extract ethernet and ip headers
    data = (void *)(long)ctx->data;
    data_end = (void *)(long)ctx->data_end;

    eth = get_eth_header(data, data_end);
    if(!eth)
        return TC_ACT_OK;

    ip = get_ip_header(data, data_end, eth);
    if (!ip)
        return TC_ACT_OK;

    tcp = get_tcp_header(data, data_end, sizeof(struct ethhdr) + sizeof(struct iphdr));

    // Check if the connection is tracked and requires SNAT
    src_ip = bpf_ntohl(ip->saddr);
    dst_ip = bpf_ntohl(ip->daddr);

    if ((ip->protocol == IPPROTO_TCP || ip->protocol == IPPROTO_UDP)) {   
        if (!tcp)
            return TC_ACT_OK;

        src_port = bpf_ntohs(tcp->source);
        dst_port = bpf_ntohs(tcp->dest);
    }

    ct_key.src_ip = src_ip;
    ct_key.dst_ip = dst_ip;
    ct_key.src_port = src_port;
    ct_key.dst_port = dst_port;
    
    value = bpf_map_lookup_elem(&nat_connection_tracking, &ct_key);

    // If an active connection or SNAT rule is found, update the source IP/Port in the packet
    if (value) {
        int do_fib = 0;
        int ifindex = ctx->ifindex;

        bpf_printk("POSTROUTING");
        bpf_printk("Packet Info:");
        print_ip("Src", src_ip, src_port);
        print_ip("Dst", dst_ip, dst_port);
        print_ip("SNAT", value->ip, value->port);

        // Convert the IP and Port to network byte order
        snat_ip = bpf_htonl(value->ip);
        snat_port = bpf_htons(value->port);
        
        if (0 != snat_ip) {
            bpf_printk("Do SNAT");

            // Update the IP header
            bpf_skb_store_bytes(ctx, sizeof(struct ethhdr) + offsetof(struct iphdr, saddr), &snat_ip, sizeof(__u32), 0);
            bpf_l3_csum_replace(ctx, sizeof(struct ethhdr) + offsetof(struct iphdr, check), bpf_htonl(src_ip), snat_ip, sizeof(__u32));
            do_fib = 1;
        }
        
        if(tcp && 0 != snat_port) {
            bpf_printk("Do SPAT");

            // Update the TCP header
            bpf_skb_store_bytes(ctx, sizeof(struct ethhdr) + sizeof(struct iphdr) + offsetof(struct tcphdr, source), &snat_port, sizeof(__u16), 0);
            bpf_l4_csum_replace(ctx, sizeof(struct ethhdr) + sizeof(struct iphdr) + offsetof(struct tcphdr, check), bpf_htons(src_port), snat_port, sizeof(__u16));
        }

        if (do_fib) {
            // Perform FIB lookup
            struct bpf_fib_lookup fib;
            __builtin_memset(&fib, 0, sizeof(fib));

            fib.family = 2; // AF_INET
            fib.ifindex = ctx->ifindex;
            fib.ipv4_src = snat_ip;
            fib.ipv4_dst = bpf_htonl(dst_ip);

            if (BPF_FIB_LKUP_RET_SUCCESS == bpf_fib_lookup(ctx, &fib, sizeof(fib), BPF_FIB_LOOKUP_DIRECT)) {
                ifindex = fib.ifindex;

                // Apply new MAC addresses for forwarding
                bpf_skb_store_bytes(ctx, offsetof(struct ethhdr, h_source), fib.smac, 6, 0);
                bpf_skb_store_bytes(ctx, offsetof(struct ethhdr, h_dest), fib.dmac, 6, 0);
            } else {
                // Drop packet if no route found
                return TC_ACT_SHOT;
            }
        }

        bpf_printk("Redirecting\n");
        bpf_redirect(ifindex, BPF_FIB_LKUP_RET_SUCCESS);
    }

    return TC_ACT_OK;
}


// Enable GPL license if you need bpf_printk
char __license[] SEC("license") = "GPL";  
//char __license[] SEC("license") = "Apache-2.0";