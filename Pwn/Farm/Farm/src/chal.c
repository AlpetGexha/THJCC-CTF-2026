#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

#define Farm_size 5

typedef struct {
  char crop_name[0x20];
  int health_status;
  char planted;
} farm_block;

void init(farm_block farm_map[5][5]) {
  setvbuf(stdout, 0, 2, 0);
  setvbuf(stdin, 0, 2, 0);
  for (int i = 0; i < 5; i++) {
    for (int j = 0; j < 5; j++) {
      farm_map[i][j].planted = ' ';
      farm_map[i][j].health_status = 0;
      strcpy(farm_map[i][j].crop_name, "\00");
    }
  }
}

void menu() {
  puts("(1) Plant");
  puts("(2) Harvesting");
  puts("(3) Sprinkle Water");
  puts("(4) Escape\n");
};

void show_farm_map(farm_block map[5][5]) {
  puts(".---.---.---.---.---.");
  printf("| %c | %c | %c | %c | %c |\n", map[0][0].planted, map[1][0].planted,
         map[2][0].planted, map[3][0].planted, map[4][0].planted);
  puts(":---+---+---+---+---:");
  printf("| %c | %c | %c | %c | %c |\n", map[0][1].planted, map[1][1].planted,
         map[2][1].planted, map[3][1].planted, map[4][1].planted);
  puts(":---+---+---+---+---:");
  printf("| %c | %c | %c | %c | %c |\n", map[0][2].planted, map[1][2].planted,
         map[2][2].planted, map[3][2].planted, map[4][2].planted);
  puts(":---+---+---+---+---:");
  printf("| %c | %c | %c | %c | %c |\n", map[0][3].planted, map[1][3].planted,
         map[2][3].planted, map[3][3].planted, map[4][3].planted);
  puts(":---+---+---+---+---:");
  printf("| %c | %c | %c | %c | %c |\n", map[0][4].planted, map[1][4].planted,
         map[2][4].planted, map[3][4].planted, map[4][4].planted);
  puts("'---'---'---'---'---'\n");
}

int escape_check(int row, int column, int border) {
  if (row > border || column > border) {
    puts("Never try to escape!");
    puts("Get back kid!");
    return 1;
  }

  return 0;
}

int main() {

  int farm_border = Farm_size - 1, row, column;
  uint32_t choice;
  farm_block farm_map[Farm_size][Farm_size];
  init(farm_map);

  puts("Welcome to the Farm where you can never escape!");
  puts("The only thing you can do here is farm until die!");
  puts("Never try to escape from my farm!\n");

  while (1) {
    show_farm_map(farm_map);
    menu();

    printf("Choice: ");
    scanf("%d", &choice);
    switch (choice) {
    case 1:
      printf("Row/Column: ");
      scanf("%d %d", &row, &column);
      getchar();
      if (escape_check(row, column, farm_border))
        continue;

      printf("Crop name: ");
      read(0, farm_map[row][column].crop_name, 0x20);
      farm_map[row][column].planted = '*';
      farm_map[row][column].health_status = 100;
      puts("Go work go work!");
      continue;
    case 2:
      printf("Row/Column: ");
      scanf("%d %d", &row, &column);
      getchar();
      if (escape_check(row, column, farm_border))
        continue;

      printf("Harvested %s", farm_map[row][column].crop_name);
      strcpy(farm_map[row][column].crop_name, "\00");
      farm_map[row][column].planted = ' ';
      farm_map[row][column].health_status = 0;
      puts("Keep working!");
      continue;
    case 3:
      printf("Row/Column: ");
      scanf("%d %d", &row, &column);
      getchar();
      if (escape_check(row, column, farm_border))
        continue;

      puts("The crop is now more healthy!\n");
      farm_map[row][column].health_status += 20;
      puts("Continue to work!");
      continue;
    case 4:
      puts("Nuh uh");
      return 0;
    }
  }
}
