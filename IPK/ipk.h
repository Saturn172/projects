#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <strings.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <arpa/inet.h>

#define MAX_SIZE 512000

char buf[MAX_SIZE];

int create_socket(){
  int socket_number;
  if((socket_number = socket(AF_INET, SOCK_STREAM, 0)) <= 0){
    perror("ERROR: socket");
    return 0;
  }
  return socket_number;
}
