# Happy Cat Jail

**Point: 494**

meow ?

nc chal.thjcc.org 9000

# Solution

The problem provides a little bit of source code.

```go
package main

import (
  "fmt"
  "unsafe"
)
```

Inside, it mentions unsafe, which looks quite dangerous. From the official Go website, you can see its introduction. It should be pretty obvious that this thing involves null pointers, right?

PoC:

```go
type catInterface struct {
  t uintptr
  v unsafe.Pointer
}

p := unsafe.Pointer(&target)

iface := (*catInterface)(p)

catStr := (*string)(iface.v)

fmt.Println(*catStr)
```

# Flag

`THJCC{iT'6m5E8Sm6Y_gOj!!!!!LwAnG}`
