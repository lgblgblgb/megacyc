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

* Make sure you use Linux/UNIX-like OS on your PC/whatever
* Make sure every utility (including Xemu) is available in your PATH mentioned at the beginning of the Makefile
* Make sure you have standard stuff (bash shell, GNU make, Python3, ...)

Utilities used:

* cl65: the "frontend" for CC65, you should have the full CC65 suite
* xemu-xmega65: it's Xemu
* mega65_etherload: etherload utility for MEGA65
* mega65_ftp: FTP-like utility for MEGA65 (can work over Ethernet too)
* c1541: disk image manipulation tool

If you have anything with different name (or not in your PATH), you need to modify the Makefile

### To test only Xemu:

* Make sure you have MEGA65 emulator of Xemu with the name mentioned in the Makefile
* Type `make xemutest`.
* If you see the directory listing in the emulator then (and only then!) exit from Xemu

Sample result can be found in this repository: public/only-xemu.txt (csv file is also available there)

### To test only MEGA65:

* Make sure you have a MEGA65 ;)
* Make sure it's turned on :)
* Make sure you have D81 file (it can/should be an empty but formatted D81) on your SD-card with the name (exactly!): OPCYCLES.D81
* Make sure it's connected to your Ethernet network
* Make sure network "remote control" is enabled (motherboard DIP switch)
* Make sure network "remote control" is activated (press SHIFT+POUND): you'll see flashing green/yellow power LED
* Type `make megatest`
* If you see the directory listing on your MEGA65 then (and only then!) press ENTER here (not on your MEGA65!)

Sample result can be found in this repository: public/only-mega65.txt (csv file is also available there)

### If you test both, you can have a nice comparison:

Either say `make parse` if you already ran both of `make xemutest` and `make megatest`, or type `make fulltest`
to test first both of them and then parsing/comparing the results automatically (it combines the functionality
of both tests).

Sample result can be found in this repository: public/comparison.txt (csv file is also available there)

### Is this test valid / precise enough at all?

To decide this question, with "MEGA65 testing" (or "both" / fulltest) there will be another result: Kibo had measurred some of the
opcodes before. I use these results (with his permission) to have a "ref" (refence) test which will also create a result file:

public/ref-mega65.txt (csv file is also available there)

This should have the very same result with my measurements, ie "OK" for all tests.

## Results so far ... and the problems

All opcodes are tested. The results so far are:

* [Xemu vs MEGA65 (after Xemu fixes)](public/comparison.tsv)
* [MEGA65-only results](public/only-mega65.tsv)
* [Xemu-only results](public/only-xemu.tsv)
* [My results vs Kibo's results](public/ref-mega65.tsv)

Please note, that I have several strange results and suspects. It seems (for me! I can be wrong!) the cycles needed to execute
a sequence of opcodes is not always the same as the sum of the cycles of those opcodes :( It seems there is some strange inter-opcode
state when one opcode modifies the execution time of an other. One extreme example is the SP relative addressing mode, I have results
like 40 and 50 cycles instead of the proposed 7-8. It seems however (according to the VHDL) that this addressing mode does a very
serious "wizardy" with various cache operations, so it's possible that the opcode really takes eg 7-8 cycles, but then there is a stall on the
next opcode, or whatever. I still don't fully understand these behaviours, to be honest. The SP-relative opcodes maybe just the extreme
case, but one cycle difference can be seen with other opcodes as well here and there.
