#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
//#include <netinet/in.h>
#include <netdb.h>

int main(){
  int client_socket;
  // creating socket
  if ((client_socket = socket(AF_INET, SOCK_DGRAM, 0)) <= 0){
    fprintf(stderr, "ERROR in socket");
    return EXIT_FAILURE;
  }
  printf("Socket number: %d\n", client_socket);
  return 0;
}
