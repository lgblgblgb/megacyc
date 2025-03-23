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

all: $(PRG)

$(PRG): $(SRC) $(LINKCFG) $(DEPENDS)
	$(CL65) -C $(LINKCFG) -t none -o $(PRG) --listing $(LST) --mapfile $(MAP) $(SRC)
	rm -f $(OBJ)

xemu: $(PRG)
	$(XEMU) -fastboot -testing -prg $(PRG)

mega65: $(PRG)
	$(M65ETHL) -r test

clean:
	rm -f $(PRG) $(LST) $(MAP) $(OBJ)

.PHONY: all xemu mega65 clean
