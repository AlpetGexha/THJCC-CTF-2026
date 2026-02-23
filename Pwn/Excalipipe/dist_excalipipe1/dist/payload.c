void _start() {
    /* 
       Equivalent to:
       int fd = open("/flag.txt", O_RDONLY);
       char buf[128];
       int n = read(fd, buf, 128);
       write(1, "\nFLAG: ", 7);
       write(1, buf, n);
       write(1, "\n", 1);
       _exit(0);
    */
    __asm__(
        "mov $2, %rax\n"        // sys_open
        "lea flag_path(%rip), %rdi\n"
        "xor %rsi, %rsi\n"      // O_RDONLY
        "syscall\n"
        
        "mov %rax, %rdi\n"      // fd
        "xor %rax, %rax\n"      // sys_read
        "lea buffer(%rip), %rsi\n"
        "mov $128, %rdx\n"
        "syscall\n"
        
        "mov %rax, %r12\n"      // save nbytes read
        
        "mov $1, %rax\n"        // sys_write
        "mov $1, %rdi\n"        // stdout
        "lea prefix(%rip), %rsi\n"
        "mov $7, %rdx\n"
        "syscall\n"
        
        "mov $1, %rax\n"        // sys_write
        "mov $1, %rdi\n"        // stdout
        "lea buffer(%rip), %rsi\n"
        "mov %r12, %rdx\n"
        "syscall\n"
        
        "mov $1, %rax\n"        // sys_write
        "mov $1, %rdi\n"        // stdout
        "lea suffix(%rip), %rsi\n"
        "mov $1, %rdx\n"
        "syscall\n"
        
        "mov $60, %rax\n"       // sys_exit
        "xor %rdi, %rdi\n"
        "syscall\n"
        
        "flag_path: .string \"/flag.txt\"\n"
        "prefix: .string \"\\nFLAG: \"\n"
        "suffix: .string \"\\n\"\n"
        "buffer: .skip 128\n"
    );
}
