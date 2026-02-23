#include <stdio.h>
#include <stdint.h>
#include <unistd.h>  
#include <stdlib.h>   
#include <string.h>   

void init() {
    setvbuf(stdin,0,2,0);
    setvbuf(stdout,0,2,0);
    setvbuf(stderr,0,2,0);
}

void menu() {
    puts("1. login as admin.");
    puts("2. exit");
    printf("> ");
}

void login() {
    char username[0x100];
    uintptr_t password;
    uintptr_t admin_password = (uintptr_t)&system;

    printf("username: ");
    read(0, username, 0x100);
    printf("password: ");
    read(0, &password, 8);

    if (password == admin_password && strcmp(username, "admin") == 0) {
        puts("I should change my password..."); 
        system("/bin/sh");
    } else {
        printf("%s login failed!\n", username);
        return;
    }
}

int main() {
    init();
    int opt;
    while (1) {
        menu();
        scanf("%d", &opt);
        getchar();
        switch(opt) {
            case 1:
                login();
                break;
            case 2:
                puts("Bye!");
                exit(0);
            default:
                puts("Invalid option!");
        }
    }
}
