#include <stdio.h>
#include <stdlib.h>

int main(){
  // creating socketa
  if ((client_socket = socket(AF_INET, SOCK_DGRAM, 0)) <= 0){
    perror("ERROR in socket");
    exit(EXIT_FAILURE);
  }
  return 0;
}
