# MEGAcyc

Trying to measure cycle timing of MEGA65 CPU opcodes. Reasons of this project:

* It's not fully known/documented how much cycles needs an opcode to run specially on 40.5MHz fast clock
* Xemu has problems because of this (no exact info)
* So a tester should be written which can run on both of Xemu and real MEGA65
  (this is a factor here, as Xemu's other kind of timings are bad as well, so not every test ideas suit here)
* Provide a method which can auto-run tests on Xemu and MEGA65 and compare the result
* Also creating some "fancy" output maybe

MEGAcyc (C)2025 LGB Gábor Lénárt lgblgblgb@gmail.com
GNU/GPL license see file LICENSE

Usual stuff: quick "try to do it" class of idea and implementation. Certainly it can be done much better ways.
However the mentioned factor also applies: it must be "Xemu friendly", as one of the goal to make it more
precise, but here is a chicken and egg problem: if the emulator is not precise enough we can't run precise
tests to measure the inaccuracy :) This is the reason for the test being "too much" ie running tests for
a full frame for example.
