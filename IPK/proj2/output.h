void dhcp_output(dhcp_t *dhcp, u_int8_t *mac, int *len){
  *len += sizeof(dhcp_t);
  memset(dhcp, 0, sizeof(dhcp_t));

  dhcp->opcode = DHCP_BOOTREQUEST;
  dhcp->htype = DHCP_HTYPE_EHTHERNET;
  dhcp->hlen = 6;
  memcpy(dhcp->chaddr, mac, DHCP_CHADDR_LEN);
  dhcp->magic_cookie = htonl(DHCP_MAGIC_COOKIE);
}

void udp_output(struct udphdr *udp_header, int *len){
  if(*len & 1) *len += 1;
  *len += sizeof(struct udphdr);

  udp_header->uh_sport = htons(DHCP_CLIENT_PORT);
  udp_header->uh_dport = htons(DHCP_SERVER_PORT);
  udp_header->uh_ulen = htons(*len);
  udp_header->uh_sum = 0;
}

void ip_output(struct ip *ip_header, int *len){
  *len += sizeof(struct ip);

  ip_header->ip_hl = 5;
  ip_header->ip_v = IPVERSION;
  ip_header->ip_tos = 0x10;
  ip_header->ip_len = htons(*len);
  ip_header->ip_id = htons(0xffff);
  ip_header->ip_off = 0;
  ip_header->ip_ttl = 16;
  ip_header->ip_p = IPPROTO_UDP;
  ip_header->ip_sum = 0;
  ip_header->ip_src.s_addr = 0;
  ip_header->ip_dst.s_addr = 0xFFFFFFFF;
  ip_header->ip_sum = in_cksum((unsigned short *) ip_header, sizeof(struct ip));
}

void ether_output(u_char *frame, u_int8_t *mac, int len){
  struct ether_header *ether_frame = (struct ether_header *) frame;

  memcpy(ether_frame->ether_shost, mac, ETHER_ADDR_LEN);
  memset(ether_frame->ether_dhost, -1,  ETHER_ADDR_LEN);
  ether_frame->ether_type = htons(ETHERTYPE_IP);

  len = len + sizeof(struct ether_header);

  if(pcap_inject(pcap_handle, frame, len) <= 0) pcap_perror(pcap_handle, "ERROR:");
}
