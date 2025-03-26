# MEGAcyc

Trying to measure cycle timing of MEGA65 CPU opcodes. Reasons of this project:

* It's not fully known/documented how much cycles needs an opcode to run specially on 40.5MHz fast clock
* Xemu has problems because of this (no exact info)
* So a tester should be written which can run on both of Xemu and real MEGA65
  (this is a factor here, as Xemu's other kind of timings are bad as well, so not every test ideas suit here)
* Provide a method which can auto-run tests on Xemu and MEGA65 and compare the result
* Also creating some "fancy" output maybe

MEGAcyc (C)2025 LGB Gábor Lénárt lgblgblgb@gmail.com - GNU/GPL v3 license (see file LICENSE)

Usual stuff: quick "try to do it" class of idea and implementation. Certainly it can be done much better ways.
However the mentioned factor also applies: it must be "Xemu friendly", as one of the goal to make it more
precise, but here is a chicken and egg problem: if the emulator is not precise enough we can't run precise
tests to measure the inaccuracy :) This is the reason for the test being "too much" ie running tests for
a full frame for example.

Currently, the tester writes out a file onto the mounted D81 with the result, which can be parsed with
a to-be-written python script. This is sub-optimal, serial connection between MEGA65 (via JTAG) would be
better, however I don't like that unrelaible connection too much. That's why this is a bit strange method:
I need a disk image mounted, a test program will write the result onto the disk, we transfer the disk
and extract the result. This is basically the same for MEGA65 and Xemu, just the "transfer method" is
different.

## Current awkward method of testing

Foreword: at this stage only some opcodes are tested, because the framework needs to be good first.

To test:

* Make sure you use Linux on your PC/whatever
* Make sure every utility (including Xemu) is available in your PATH mentioned at the beginning of the Makefile

### To test only Xemu (or both MEGA65 and Xemu):

* Make sure you have MEGA65 emulator of Xemu with the name mentioned in the Makefile
* Type `make xemutest`.
* If you see the directory, exit from Xemu

### To test only MEGA65 (or both of MEGA65 and Xemu):

* Make sure you have a MEGA65 ;)
* Make sure it's turned on :)
* Make sure it's connected to your Ethernet network
* Make sure network "remote control" is enabled (motherboard DIP switch)
* Make sure network "remote control" is activated (press SHIFT+POUND): you'll see flashing green/yellow power LED
* Type `make megatest`

### If you really test both, you can have a nice comparison:

Either say `make parse` if you already ran both of `make xemutest` and `make megatest`, or type `make fulltest`
to test first both of them and then parsing/comparing the results automatically.
