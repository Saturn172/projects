// includes
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <pcap.h>
#include <errno.h>
#include <signal.h>
#include <time.h>
#include <ifaddrs.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <net/ethernet.h>
#include <net/if.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/udp.h>

// DHCP lengths
#define DHCP_CHADDR_LEN 16
#define DHCP_SNAME_LEN  64
#define DHCP_FILE_LEN   128

// DHCP opcodes
#define DHCP_BOOTREQUEST 1
#define DHCP_BOOTREPLY 2

// DHCP fields
#define DHCP_HTYPE_EHTHERNET 1

// DHCP options
#define DHCP_REQ_IP 50
#define DHCP_SERVER_ID 54
#define DHCP_MSG_TYPE 53
#define DHCP_OPT_END 255

// DHCP message types
#define DHCP_DISCOVER 1
#define DHCP_OFFER 2
#define DHCP_REQUEST 3
#define DHCP_ACK 4

// UDP ports for DHCP
#define DHCP_SERVER_PORT    67
#define DHCP_CLIENT_PORT    68

// magic cookie
#define DHCP_MAGIC_COOKIE   0x63825363

// timeout
#define TIMEOUT 5

// DHCP packet structure
typedef struct dhcp{
  u_int8_t    opcode;
  u_int8_t    htype;
  u_int8_t    hlen;
  u_int8_t    hops;
  u_int32_t   xid;
  u_int16_t   secs;
  u_int16_t   flags;
  u_int32_t       ciaddr;
  u_int32_t       yiaddr;
  u_int32_t       siaddr;
  u_int32_t       giaddr;
  u_int8_t    chaddr[DHCP_CHADDR_LEN];
  char        bp_sname[DHCP_SNAME_LEN];
  char        bp_file[DHCP_FILE_LEN];
  uint32_t    magic_cookie;
  u_int8_t    bp_options[0];
} dhcp_t;

// global variables
pcap_t *pcap_handle;
u_int32_t ip;
u_int32_t server;
u_int8_t mac[6];
int timed_out;

// get MAC address of device
int mac_address(char *dev_name, u_int8_t *mac){
  struct ifreq s;
  int fd = socket(PF_INET, SOCK_DGRAM, IPPROTO_IP);

  strcpy(s.ifr_name, dev_name);
  int res = ioctl(fd, SIOCGIFHWADDR, &s);
  close(fd);
  if(res != 0) return 1;

  memcpy((void *) mac, s.ifr_addr.sa_data, 6);
  return 0;
}

// return checksum for the given data
unsigned short in_cksum(unsigned short *addr, int len){
  register int sum = 0;
  u_short answer = 0;
  register u_short *w = addr;
  register int nleft = len;

  while(nleft > 1){
    sum += *w++;
    nleft -= 2;
  }

  if(nleft == 1){
    *(u_char *)(&answer) = *(u_char *) w;
    sum += answer;
  }

  sum = (sum >> 16) + (sum & 0xffff);
  sum += (sum >> 16);
  return ~sum;
}

// add DHCP option into packet
static int dhcp_option(u_int8_t *packet, u_int8_t code, u_int8_t *data, u_int8_t len){
  packet[0] = code;
  packet[1] = len;
  memcpy(&packet[2], data, len);
  return len + (sizeof(u_int8_t)*2);
}

// functions for packing and unpacking of DHCP packet
#include "output.h"
#include "input.h"
