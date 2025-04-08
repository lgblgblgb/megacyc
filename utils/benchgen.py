#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# --------------------------------------------------------------------
# MEGA65 and Xemu opcode/cycle meassure/test tool.
#
# Copyright (C)2025 LGB (Gábor Lénárt) <lgblgblgb@gmail.com>
# --------------------------------------------------------------------
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
# ---------------------------------------------------------------------

import sys


OPCODES = (
    #x0    x1    x2    x3    x4    x5    x6    x7      x8    x9    xA    xB    xC    xD    xE    xF
    "BRK","ORA","CLE","SEE","TSB","ORA","ASL","RMB0", "PHP","ORA","ASL","TSY","TSB","ORA","ASL","BBR0", # 0x
    "BPL","ORA","ORA","BPL","TRB","ORA","ASL","RMB1", "CLC","ORA","INC","INZ","TRB","ORA","ASL","BBR1", # 1x
    "JSR","AND","JSR","JSR","BIT","AND","ROL","RMB2", "PLP","AND","ROL","TYS","BIT","AND","ROL","BBR2", # 2x
    "BMI","AND","AND","BMI","BIT","AND","ROL","RMB3", "SEC","AND","DEC","DEZ","BIT","AND","ROL","BBR3", # 3x
    "RTI","EOR","NEG","ASR","ASR","EOR","LSR","RMB4", "PHA","EOR","LSR","TAZ","JMP","EOR","LSR","BBR4", # 4x
    "BVC","EOR","EOR","BVC","ASR","EOR","LSR","RMB5", "CLI","EOR","PHY","TAB","MAP","EOR","LSR","BBR5", # 5x
    "RTS","ADC","RTS","BSR","STZ","ADC","ROR","RMB6", "PLA","ADC","ROR","TZA","JMP","ADC","ROR","BBR6", # 6x
    "BVS","ADC","ADC","BVS","STZ","ADC","ROR","RMB7", "SEI","ADC","PLY","TBA","JMP","ADC","ROR","BBR7", # 7x
    "BRA","STA","STA","BRA","STY","STA","STX","SMB0", "DEY","BIT","TXA","STY","STY","STA","STX","BBS0", # 8x
    "BCC","STA","STA","BCC","STY","STA","STX","SMB1", "TYA","STA","TXS","STX","STZ","STA","STZ","BBS1", # 9x
    "LDY","LDA","LDX","LDZ","LDY","LDA","LDX","SMB2", "TAY","LDA","TAX","LDZ","LDY","LDA","LDX","BBS2", # Ax
    "BCS","LDA","LDA","BCS","LDY","LDA","LDX","SMB3", "CLV","LDA","TSX","LDZ","LDY","LDA","LDX","BBS3", # Bx
    "CPY","CMP","CPZ","DEW","CPY","CMP","DEC","SMB4", "INY","CMP","DEX","ASW","CPY","CMP","DEC","BBS4", # Cx
    "BNE","CMP","CMP","BNE","CPZ","CMP","DEC","SMB5", "CLD","CMP","PHX","PHZ","CPZ","CMP","DEC","BBS5", # Dx
    "CPX","SBC","LDA","INW","CPX","SBC","INC","SMB6", "INX","SBC","NOP","ROW","CPX","SBC","INC","BBS6", # Ex
    "BEQ","SBC","SBC","BEQ","PHW","SBC","INC","SMB7", "SED","SBC","PLX","PLZ","PHW","SBC","INC","BBS7"  # Fx
)
OPCODE_ADMS = (
#   x0 x1 x2 x3 x4 x5 x6 x7 x8 x9 xA xB xC xD xE xF
     0,15, 0, 0, 3, 3, 3, 3, 0, 1,18, 0, 7, 7, 7, 4,    # 0x
    10,12,13,11, 3, 5, 5, 3, 0, 9, 0, 0, 7, 8, 8, 4,    # 1x
     7,15,16,17, 3, 3, 3, 3, 0, 1,18, 0, 7, 7, 7, 4,    # 2x
    10,12,13,11, 5, 5, 5, 3, 0, 9, 0, 0, 8, 8, 8, 4,    # 3x
     0,15, 0, 0, 3, 3, 3, 3, 0, 1,18, 0, 7, 7, 7, 4,    # 4x
    10,12,13,11, 5, 5, 5, 3, 0, 9, 0, 0, 0, 8, 8, 4,    # 5x
     0,15, 1,11, 3, 3, 3, 3, 0, 1,18, 0,16, 7, 7, 4,    # 6x
    10,12,13,11, 5, 5, 5, 3, 0, 9, 0, 0,17, 8, 8, 4,    # 7x
    10,15,14,11, 3, 3, 3, 3, 0, 1, 0, 8, 7, 7, 7, 4,    # 8x
    10,12,13,11, 5, 5, 6, 3, 0, 9, 0, 9, 7, 8, 8, 4,    # 9x
     1,15, 1, 1, 3, 3, 3, 3, 0, 1, 0, 7, 7, 7, 7, 4,    # Ax
    10,12,13,11, 5, 5, 6, 3, 0, 9, 0, 8, 8, 8, 9, 4,    # Bx
     1,15, 1, 3, 3, 3, 3, 3, 0, 1, 0, 7, 7, 7, 7, 4,    # Cx
    10,12,13,11, 3, 5, 5, 3, 0, 9, 0, 0, 7, 8, 8, 4,    # Dx
     1,15,14, 3, 3, 3, 3, 3, 0, 1, 0, 7, 7, 7, 7, 4,    # Ex
    10,12,13,11, 2, 5, 5, 3, 0, 9, 0, 0, 7, 8, 8, 4     # Fx
)
ADM_SYNS = (
    #0  1       2         3       4         5        6        7        8          9          10     11       12         13
    "", "#$nn", "#$nnnn", "$nn", "$nn,$rr", "$nn,X", "$nn,Y", "$nnnn", "$nnnn,X", "$nnnn,Y", "$rr", "$rrrr", "($nn),Y", "($nn),Z",
    #14           15         16          17          18
    "($nn,SP),Y", "($nn,X)", "($nnnn)", "($nnnn,X)", "A"
)
QOPCODES = (
    #x0     x1     x2     x3     x4     x5     x6     x7      x8     x9     xA     xB     xC     xD     xE     xF
    None,  None,  None,  None,  None, "ORQ", "ASLQ", None,   None,  None, "ASLQ", None,  None, "ORQ", "ASLQ", None, # 0x
    None,  None, "ORQ",  None,  None,  None, "ASLQ", None,   None,  None, "INQ",  None,  None,  None, "ASLQ", None, # 1x
    None,  None,  None,  None, "BITQ","ANDQ","ROLQ", None,   None,  None, "ROLQ", None, "BITQ","ANDQ","ROLQ", None, # 2x
    None,  None, "ANDQ", None,  None,  None, "ROLQ", None,   None,  None, "DEQ",  None,  None,  None, "ROLQ", None, # 3x
    None,  None, "NEGQ","ASRQ","ASRQ","EORQ","LSRQ", None,   None,  None, "LSRQ", None,  None, "EORQ","LSRQ", None, # 4x
    None,  None, "EORQ", None, "ASRQ", None, "LSRQ", None,   None,  None,  None,  None,  None,  None, "LSRQ", None, # 5x
    None,  None,  None,  None,  None, "ADCQ","RORQ", None,   None,  None, "RORQ", None,  None, "ADCQ","RORQ", None, # 6x
    None,  None, "ADCQ", None,  None,  None, "RORQ", None,   None,  None,  None,  None,  None,  None, "RORQ", None, # 7x
    None,  None,  None,  None,  None, "STQ",  None,  None,   None,  None,  None,  None,  None, "STQ",  None,  None, # 8x
    None,  None, "STQ",  None,  None,  None,  None,  None,   None,  None,  None,  None,  None,  None,  None,  None, # 9x
    None,  None,  None,  None,  None, "LDQ",  None,  None,   None,  None,  None,  None,  None, "LDQ",  None,  None, # Ax
    None,  None, "LDQ",  None,  None,  None,  None,  None,   None,  None,  None,  None,  None,  None,  None,  None, # Bx
    None,  None,  None,  None,  None, "CMPQ","DEQ",  None,   None,  None,  None,  None,  None, "CMPQ","DEQ",  None, # Cx
    None,  None, "CMPQ", None,  None,  None, "DEQ",  None,   None,  None,  None,  None,  None,  None, "DEQ",  None, # Dx
    None,  None,  None,  None,  None, "SBCQ","INQ",  None,   None,  None,  None,  None,  None, "SBCQ","INQ",  None, # Ex
    None,  None, "SBCQ", None,  None,  None, "INQ",  None,   None,  None,  None,  None,  None,  None, "INQ",  None  # Fx
)
NO_Z_WHEN_FLATQ = (
    0x12,   # ORQ  ($nn) / ORQ  [$nn]
    0x32,   # ANDQ ($nn) / ANDQ [$nn]
    0x52,   # EORQ ($nn) / EORQ [$nn]
    0x72,   # ADCQ ($nn) / ADCQ [$nn]
    0x92,   # STQ  ($nn) / STQ  [$nn]
    0xD2,   # CMPQ ($nn) / CMPQ [$nn]
    0xF2    # SBCQ ($nn) / SBCQ [$nn]
)


def main():
    imp, opc, first, target = {}, None, True, []
    with open("testbench.i65", "rt") as f:
        for l in f:
            l, o = l.strip().split(), l.rstrip()
            if first and o.startswith(";"):
                target.append(o)
            elif first:
                first = False
                if target:
                    target.extend(["", ""])
            if o == "":
                continue
            if len(l) > 2 and l[0] == "TESTING":
                opc = int(l[1].lstrip("$"), 16)
                continue
            if opc is not None:
                if opc not in imp:
                    imp[opc] = []
                imp[opc].append(o)
    res = {}
    for opc in range(0x100):
        opc16, asm, arg, qasm, flat = opc << 8, OPCODES[opc], ADM_SYNS[OPCODE_ADMS[opc]], QOPCODES[opc], OPCODE_ADMS[opc] == 13
        res[opc16] = f"|{asm} {arg}|"
        #if "$rr" in arg and opc not in (0x80, 0x83, 0x63):
        if "$rr" in arg and asm not in ("BRA", "BSR"):
            res[opc16 + 1] = f"{res[opc16]} (conditional branch taken)"
        if qasm:
            noz = ""
            if arg == "A":
                arg = "Q"
            elif flat and opc in NO_Z_WHEN_FLATQ:
                arg, noz = "($nn)", " (no Z!)"
            res[opc16 + 3] = f"|{qasm} {arg}| NEG_NEG_PREFIXED{noz}"
        if flat:
            res[opc16 + 2] = f"|{asm} [$nn],Z| NOP_PREFIXED"
            if qasm:
                res[opc16 + 4] = f"|{qasm} [$nn],Z| NOP_NEG_NEG_PREFIXED" if opc not in NO_Z_WHEN_FLATQ else f"|{qasm} [$nn]| NOP_NEG_NEG_PREFIXED (no Z!)"
    for opc in sorted(res):
        has_imp = opc in imp
        target.append("{}TESTING ${:04X}\t; {}".format("" if has_imp else ";", opc, res[opc].replace(" |", "|")))
        if has_imp:
            target.extend(imp[opc])
    print("\n".join(target))


if __name__ == "__main__":
    main()
    sys.exit(0)
