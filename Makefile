# MEGA65 and Xemu opcode/cycle meassure/test tool.
#
# Copyright (C)2025 LGB (Gábor Lénárt) <lgblgblgb@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

CL65	= cl65
XEMU	= xemu-xmega65
M65ETHL	= mega65_etherload
M65FTP  = mega65_ftp
C1541	= c1541

SRC	= test.a65
PRG	= test
OBJ	= test.o
LST	= test.lst
MAP	= test.map
LINKCFG	= linker.ld
DEPENDS	= Makefile

XDISK	= result/XEMUDISK.D81
MDISK	= result/OPCYCLES.D81
XRESULT	= result/xemu.res
MRESULT = result/mega65.res

all: $(PRG)

$(PRG):	$(SRC) $(LINKCFG) $(DEPENDS)
	$(CL65) -C $(LINKCFG) -o $(PRG) --listing $(LST) --mapfile $(MAP) $(SRC)
	rm -f $(OBJ)

xemu:	$(PRG)
	echo "format opcycles,id d81 $(XDISK)" | $(C1541)
	$(XEMU) -fastboot -testing -9 $(XDISK) -prg $(PRG)

$(XDISK):
	$(MAKE) xemu

$(XRESULT): $(XDISK)
	echo "read result,s $(XRESULT)" | $(C1541) $(XDISK)

mega65:	$(PRG)
	rm -f $(MDISK)
	$(M65ETHL) -r $(PRG)

$(MDISK):
	rm -f "$(MDISK)"
	$(MAKE) mega65
	@echo
	@echo "*** MAKE SURE MEGA65 FINISHED THE TESTING (YOU'LL SEE THE DIRECTORY LISTING) ***"
	@echo "*** THEN - AND ONLY THEN - PRESS ENTER HERE (NOT ON YOUR MEGA65) ***"
	@read something
	$(M65FTP) -e -c "get `basename $(MDISK)` $(MDISK)" -c "exit"
	test -s "$(MDISK)" || exit 1

$(MRESULT): $(MDISK)
	echo "read result,s $(MRESULT)" | $(C1541) $(MDISK)

parse:
	utils/result_parser.py $(XRESULT) $(MRESULT) | tee result/comparison.txt
	sed -n 's/|/;/pg' result/comparison.txt > result/comparison.csv

refparse:
	utils/result_parser.py $(MRESULT) ref | tee result/ref-mega65.txt
	sed -n 's/|/;/pg' result/ref-mega65.txt > result/ref-mega65.csv

xemutest:
	rm -f $(XDISK) $(XRESULT)
	$(MAKE) $(XRESULT)
	utils/result_parser.py $(XRESULT) | tee result/only-xemu.txt
	sed -n 's/|/;/pg' result/only-xemu.txt > result/only-xemu.csv

megatest:
	rm -f $(MDISK) $(MRESULT)
	$(MAKE) $(MRESULT)
	utils/result_parser.py $(MRESULT) ref | tee result/ref-mega65.txt
	utils/result_parser.py $(MRESULT) | tee result/only-mega65.txt
	sed -n 's/|/;/pg' result/only-mega65.txt > result/only-mega65.csv
	sed -n 's/|/;/pg' result/ref-mega65.txt > result/ref-mega65.csv

fulltest:
	$(MAKE) xemutest
	$(MAKE) megatest
	$(MAKE) parse

publish:
	cp $(PRG) public/test.prg
	cp result/comparison.csv result/only-xemu.csv result/only-mega65.csv public/
	cp result/ref-mega65.csv public/

clean:
	rm -f $(PRG) $(LST) $(MAP) $(OBJ) $(XDISK) $(XRESULT) $(MDISK) $(MRESULT)
	rm -f result/comparison.txt result/only-xemu.txt result/only-mega65.txt
	rm -f result/comparison.csv result/only-xemu.csv result/only-mega65.csv
	rm -f result/ref-mega65.txt result/ref-mega65.csv

.PHONY: all xemu mega65 clean publish parse fulltest xemutest megatest refparse
