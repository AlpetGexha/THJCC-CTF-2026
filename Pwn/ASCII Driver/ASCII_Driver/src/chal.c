#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void init() {
  setvbuf(stdout, 0, 2, 0);
  setvbuf(stdin, 0, 2, 0);
}

int win() {
  puts("You won!");
  puts("but nothing for u :)");
  return 0;
}

int staff_panel() {
  system("/bin/sh");
  return 0;
}

int main() {
  char ascii_character;
  char energy[0x90];

  init();
  printf("Pick your car by enter an ascii character:");
  ascii_character = getchar();
  getchar();

  if (ascii_character > '~') {
    puts("thats not an ascii character!");
    return 0;
  }

  puts("fill the energy!");
  fgets(energy, (unsigned char)ascii_character, stdin);

  if (strlen(energy) > 0x80)
    win();
  else
    puts("Nah I'd win");

  return 0;
}
