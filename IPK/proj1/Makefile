ipk: ipk-server.c ipk-client.c
	rm -f ipk-server ipk-client
	gcc -std=c99 -Wall -Wextra -pedantic -D_BSD_SOURCE -D_DEFAULT_SOURCE -o ipk-server ipk-server.c
	gcc -std=c99 -Wall -Wextra -pedantic -D_BSD_SOURCE -D_DEFAULT_SOURCE -o ipk-client ipk-client.c
