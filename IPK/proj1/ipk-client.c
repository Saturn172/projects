#include "ipk.h"

int main(int argc, char *argv[]){

  // default values
  char *server_hostname = "";
  int port_number = -1;

  // parsing arguments
  char opt;
  int style = 0; // number of l/n/f parameters

  do{
    opt = getopt(argc, argv, "h:p:fnl?");
    if(opt == 'h'){
      server_hostname = argv[optind - 1];
    } else if(opt == 'p'){
      port_number = atoi(argv[optind - 1]);
    } else if(opt == 'f'){
      msg[0] = 'f';
      msg[1] = ' ';
      for(unsigned int i = 0; i < strlen(argv[argc - 1]); i++){
        msg[i + 2] = argv[argc - 1][i];
      }
      style++;
      if(argc != 7){
        fprintf(stderr, "Missing parameter! Try -?.\n");
        exit(1);
      }
    } else if(opt == 'n'){
      msg[0] = 'n';
      msg[1] = ' ';
      for(unsigned int i = 0; i < strlen(argv[argc - 1]); i++){
        msg[i + 2] = argv[argc - 1][i];
      }
      style++;
      if(argc != 7){
        fprintf(stderr, "Missing parameter! Try -?.\n");
        exit(1);
      }
    } else if(opt == 'l'){
      msg[0] = 'l';
      if(argc == 7){
        // adding login if exists
        msg[1] = ' ';
        for(unsigned int i = 0; i < strlen(argv[argc - 1]); i++){
          msg[i + 2] = argv[argc - 1][i];
        }
      }
      style++;
    } else if(opt == '?'){
      printf("\
Returns information about users on server.\n\
\n\
Usage: ./ipk-client -h host -p port [-n|-f|-l] login\n\
\n\
-h name       host to call\n\
-p number     port number\n\
-n login      information mode\n\
-f login      home directory mode\n\
-l [login]    login list mode, if login entered, it is used as prefix\n");
      return 1;
    }
  } while(opt != -1);

  if(style != 1){
    fprintf(stderr, "Missing parameter or too many parameters! Try -?.\n");
    exit(1);
  }

  // no hostname
  if(!strcmp(server_hostname, "")){
    fprintf(stderr, "Enter a server name!\n");
    exit(1);
  }
  if(port_number == -1){
    fprintf(stderr, "Enter a port number!\n");
    exit(1);
  }

  int client_socket;

  // creating socket
  if(!(client_socket = create_socket())) return 1;

  // translating hostname
  struct hostent *server;
  if((server = gethostbyname(server_hostname)) == NULL){
    fprintf(stderr, "ERROR, no such host as %s\n", server_hostname);
    return 1;
  }

  // getting server address
  struct sockaddr_in server_address;
  bzero((char *) &server_address, sizeof(server_address));
  server_address.sin_family = AF_INET;
  bcopy((char *) server->h_addr_list[0], (char *) &server_address.sin_addr.s_addr, server->h_length);
  server_address.sin_port = htons(port_number);

  // connecting to server
  if(connect(client_socket, (const struct sockaddr *) &server_address, sizeof(server_address)) != 0){
    perror("ERROR: connect");
    exit(1);
  }

  // sending request
  ssize_t bytestx = send(client_socket, msg, strlen(msg), 0);
  if (bytestx < 0)  perror("ERROR: send");

  // timeot
  struct timeval timeout;
  timeout.tv_sec = 0;
  timeout.tv_usec = 500000;

  fd_set set;
  FD_ZERO(&set);
  FD_SET(client_socket, &set);

  // receiving message
  while(1){
    if(!select(client_socket + 1, &set, NULL, NULL, &timeout)) break;
    ssize_t bytesrx = recv(client_socket, buf, MAX_SIZE, 0);
    for(int i = 0; i < bytesrx; i++) printf("%c", buf[i]);
    if(bytesrx < 0){
      perror("ERROR: recv");
      exit(1);
    }
  }

  shutdown(client_socket, SHUT_RDWR);

  exit(0);
}
