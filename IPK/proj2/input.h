void dhcp_input(dhcp_t *dhcp){
  if(dhcp->opcode != DHCP_OFFER) return;
  ip = dhcp->yiaddr;
  pcap_breakloop(pcap_handle);
}

void udp_input(struct udphdr * udp_packet){
  if(ntohs(udp_packet->uh_sport) == DHCP_SERVER_PORT) dhcp_input((dhcp_t *)((char *)udp_packet + sizeof(struct udphdr)));
}

void ip_input(struct ip * ip_packet){
  if(ip_packet->ip_p == IPPROTO_UDP) udp_input((struct udphdr *)((char *)ip_packet + sizeof(struct ip)));
  server = ip_packet->ip_src.s_addr;
}

void ether_input(u_char *args, const struct pcap_pkthdr *header, const u_char *frame){
  (void) args;
  (void) header;
  struct ether_header *eframe = (struct ether_header *)frame;
  if(!memcmp(eframe->ether_dhost, mac, ETHER_ADDR_LEN) && htons(eframe->ether_type) == ETHERTYPE_IP) ip_input((struct ip *)(frame + sizeof(struct ether_header)));
}
