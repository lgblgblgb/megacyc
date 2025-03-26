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
SRC	= test.a65
PRG	= test
OBJ	= test.o
LST	= test.lst
MAP	= test.map
LINKCFG	= linker.ld
XEMU	= xemu-xmega65
M65ETHL	= mega65_etherload
M65FTP  = mega65_ftp
DEPENDS	= Makefile

C1541	= c1541

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
	$(M65FTP) -e -c "get `basename $(MDISK)` $(MDISK)" -c "exit"
	test -s "$(MDISK)" || exit 1

$(MRESULT): $(MDISK)
	echo "read result,s $(MRESULT)" | $(C1541) $(MDISK)

parse:
	utils/result_parser.py $(XRESULT) $(MRESULT) | tee result/comparison.txt

xemutest:
	rm -f $(XDISK) $(XRESULT)
	$(MAKE) $(XRESULT)
	utils/result_parser.py $(XRESULT) | tee result/only-xemu.txt

megatest:
	rm -f $(MDISK) $(MRESULT)
	$(MAKE) $(MRESULT)
	utils/result_parser.py $(MRESULT) | tee result/only-mega65.txt

fulltest:
	rm -f $(XDISK) $(XRESULT) $(MDISK) $(MRESULT)
	$(MAKE) xemu
	$(MAKE) $(XRESULT)
	$(MAKE) mega65
	$(MAKE) $(MRESULT)
	$(MAKE) parse

publish:
	cp $(PRG) public/test.prg
	cp result/comparison.txt result/only-xemu.txt result/only-mega65.txt public/

clean:
	rm -f $(PRG) $(LST) $(MAP) $(OBJ) $(XDISK) $(XRESULT) $(MDISK) $(MRESULT) result/comparison.txt result/only-xemu.txt result/only-mega65.txt

.PHONY: all xemu mega65 clean publish parse fulltest xemutest megatest
