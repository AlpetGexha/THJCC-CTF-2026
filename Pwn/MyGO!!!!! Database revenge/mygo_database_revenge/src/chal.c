#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int token;

void init() {
  setvbuf(stdout, 0, 2, 0);
  setvbuf(stdin, 0, 2, 0);
  srand(time(NULL));
  token = rand() % 500000000;
}

void print_database() {
  puts("+-------+-----------------+-----------------+");
  printf("| %-5s | %-33s |\n", "ID", "contents");
  puts("+-------+-----------------+-----------------+");
  printf("| %-5s | %-33s |\n", "0", "MyGO!!!!!");
  printf("| %-5s | %-33s |\n", "1", "Saki chan Saki chan!");
  printf("| %-5s | %-33s |\n", "2", "Tomorin is cute!");
  puts("+-------+-----------------+-----------------+");
}

int main() {
  char buf[32];
  int try = 0;
  init();

  while (1) {

    if (try >= 10) {
      puts("Bad hacker! denied.");
      return 1;
    }

    printf("MYGO Database Admin Token: ");
    fgets(buf, 32, stdin);

    if (atoi(buf) != token) {
      printf(buf);
      puts("is not correct token!");
      try++;
      continue;
    }
    break;
  }

  puts("Welcome to mygo database!");
  print_database();

  return 0;
}
