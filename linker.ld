FEATURES {
	STARTADDRESS:	default = $2001;
}
MEMORY {
	LOADADDR:	file = %O, start = %S - 2, size = 2, fill = yes;
	ZP:		file = "", define = yes, start = $0002, size = $00FE;
	# TODO: what is the exact "TOP" for RAM segment on C65?!
        RAM:		file = %O, start = %S, size = $C000 - %S, define = yes;
}
SEGMENTS {
	ZEROPAGE:	load = ZP, type = zp;
	LOADADDR:	load = LOADADDR;
	BASICSTUB:	load = RAM, define = yes;
	INIT:		load = RAM;
	CODE:		load = RAM;
	TEST:		load = RAM;
	BSS:		load = RAM, type = BSS, define = yes;
}
