#include "ipk.h"

int main(int argc, char *argv[]){

  int port_number = -1;

  // parsing arguments
  char opt;
  do{
    opt = getopt(argc, argv, "p:?");
   if(opt == 'p'){
      port_number = atoi(argv[optind - 1]);
    }
    if(opt == '?'){
      printf("\
Listens to requests of ipk-client.\n\
\n\
Usage: ./ipk-server -p port\n\
\n\
-p number     port number\n");
      exit(1);
    }
  }while(opt != -1);

  if(port_number == -1){
    fprintf(stderr, "Enter a port number!\n");
    exit(1);
  }

  // creating socket
  int welcome_socket;
  if(!(welcome_socket = create_socket())) exit(1);

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

  // listening
  if((listen(welcome_socket, 1)) < 0){
    perror("ERROR: listen");
    exit(1);
  }

  struct sockaddr client_address;
  socklen_t clientlen = sizeof(client_address);

  printf("Listening...\n\n");

  int comm_socket;

  // communication
  while(1){

    // accepting request
    while(1){
      comm_socket = accept(welcome_socket, (struct sockaddr*) &client_address, &clientlen);
      if(comm_socket < 0){
        perror("ERROR: accept");
        exit(1);
      }
      else if(comm_socket > 0) break;
    }

    // opening file
    FILE *users = fopen("/etc/passwd", "r");

    // clearing data from previous request
    int created = 0;
    memset(buf, 0, MAX_SIZE);
    memset(msg, 0, MAX_SIZE);

    // receiving request
    while(1){
      ssize_t bytesrx = recv(comm_socket, buf, MAX_SIZE, 0);
      if(bytesrx < 0){
        perror("ERROR: recv");
        exit(1);
      }
      else if(bytesrx == 0) break;

      // creating message (only once)
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

        // n or f parameter
        } else {
          int state = 0;
          int sector = 0;
          char c = '\0';
          unsigned int j = 2;
          while(c != EOF && i < MAX_SIZE){
            c = getc(users);
            switch(state){
              case 0:
                // checking login
                if(j < strlen(buf) && sector == 0){
                  // matches
                  if(buf[j] == c){
                    j++;
                  // wrong
                  } else {
                    j = 2;
                    state = 2;
                  }
                // next sector of line
                } else if(c == ':'){
                  sector++;
                  // n or f
                  if(buf[0] == 'n'){
                    if(sector == 4) state = 1;
                  } else {
                    if(sector == 5) state = 1;
                  }
                // not match
                } else {
                  if(sector == 0){
                    j = 2;
                    state = 2;
                  }
                }
                break;
              case 1:
                // end
                if(c == ':'){
                  j = 2;
                  state = 2;
                // collecting data
                } else {
                  msg[i] = c;
                  i++;
                }
                break;
              case 2:
                // skipping
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

      // sending message
      send(comm_socket, msg, strlen(msg), 0);
    }
  }

  shutdown(welcome_socket, SHUT_RDWR);
  exit(0);
}
