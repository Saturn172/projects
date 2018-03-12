#include "ipk.h"

int main(int argc, char *argv[]){

  int port_number = -1;

  char opt;
  do{
    opt = getopt(argc, argv, "p:?");
   if(opt == 'p'){
      port_number = atoi(argv[optind - 1]);
    }
    if(opt == '?'){
      printf("Nápověda jak vostříž!\n");
      return 1;
    }
  }while(opt != -1);

  if(port_number == -1){
    fprintf(stderr, "Enter a port number!\n");
    exit(1);
  }

  int welcome_socket;
  if(!(welcome_socket = create_socket())) return 1;

  // setting server address
  struct sockaddr_in server_address;
  bzero((char *) &server_address, sizeof(server_address));
  server_address.sin_family = AF_INET;
  server_address.sin_addr.s_addr = htonl(INADDR_ANY);
  server_address.sin_port = htons((unsigned short)port_number);

  // binding
  if(bind(welcome_socket, (struct sockaddr *) &server_address, sizeof(server_address)) < 0){
    perror("ERROR: bind");
    exit(1);
  }

  //listening
  if((listen(welcome_socket, 1)) < 0){
    perror("ERROR: listen");
    exit(1);
  }

  struct sockaddr client_address;
  socklen_t clientlen = sizeof(client_address);

  printf("Listening...\n\n");

  int comm_socket;

  while(1){
    while(1){
      comm_socket = accept(welcome_socket, (struct sockaddr*) &client_address, &clientlen);
      if(comm_socket < 0){
        perror("ERROR: accept");
        exit(1);
      }
      else if(comm_socket > 0) break;
    }

    FILE *users = fopen("/etc/passwd", "r");
    char msg[MAX_SIZE];
    printf("Sending data.\n");

    // clear data from previous request
    int created = 0;
    memset(buf, 0, MAX_SIZE);
    memset(msg, 0, MAX_SIZE);

    while(1){
      ssize_t bytesrx = recv(comm_socket, buf, MAX_SIZE, 0);
      if(bytesrx < 0){
        perror("ERROR: recv");
        exit(1);
      }
      else if(bytesrx == 0) break;

      if(!created){
        int i = 0;

        // l parameter
        if(buf[0] == 'l'){
          int state = 0;
          char c = '\0';
          unsigned int j = 2;
          while(c != EOF && i < MAX_SIZE){
            c = getc(users);
            switch(state){
              case 0:
                // end of login
                if(c == ':'){
                  msg[i] = '\n';
                  i++;
                  state = 1;
                  break;
                // login in progress
                } else {
                  if(c != EOF){
                    // login entered
                    if(strlen(buf) > 1){
                      if(j < strlen(buf)){
                        if(buf[j] == c){
                          msg[i] = c;
                          i++;
                          j++;
                          break;
                        } else {
                          i -= (j - 2);
                          state = 1;
                          break;
                        }
                      }
                    }
                    // without login
                    msg[i] = c;
                    i++;
                  }
                  break;
                }
              // wrong login or after end of login
              case 1:
                if(c == '\n'){
                  j = 2;
                  state = 0;
                  break;
                } else {
                  break;
                }
            }
          }

        // n parameter
        } else if(buf[0] == 'n'){
          int state = 0;
          int sector = 0;
          char c = '\0';
          unsigned int j = 2;
          while(c != EOF && i < MAX_SIZE){
            c = getc(users);
            switch(state){
              case 0:
                if(j < strlen(buf) && sector == 0){
                  if(buf[j] == c){
                    j++;
                  } else {
                    state = 2;
                  }
                } else if(c == ':'){
                  sector++;
                  if(sector == 4) state = 1;
                } else {
                  if(sector == 0){
                    j = 2;
                    state = 2;
                  }
                }
                break;
              case 1:
                if(c == ':'){
                  sector++;
                  state = 2;
                } else {
                  msg[i] = c;
                  i++;
                }
                break;
              case 2:
                if(c == '\n') state = 0;
                break;
            }
          }
          msg[i] = '\n';
          i++;
        }
        msg[i] = '\0';
        created = 1;
      }

      send(comm_socket, msg, strlen(msg), 0);
    }
  }

  shutdown(welcome_socket, SHUT_RDWR);
  return 0;
}
