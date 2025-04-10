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


def main(fn : str):
    opc, opc_nop, opc_neg_neg, opc_neg_neg_nop = [[None,None]] * 256, [[None,None]] * 256, [[None,None]] * 256, [[None,None]] * 256
    with open(fn, "rt") as f:
        for l in f:
            l = l.strip()
            if l == "":
                continue
            l = tuple(map(str.strip, l.split(";")))
            if len(l) != 4:
                raise RuntimeError("Bad line")
            if l[0][0] != '$':
                continue
            ex, op, cy = int(l[0].lstrip("$"), 16), int(l[1].lstrip("$"), 16), int(l[3])
            if ex == 0:
                opc[op] = [cy, l[2]]
            elif ex == 2:
                opc_nop[op] = [cy, l[2]]
            elif ex == 3:
                opc_neg_neg[op] = [cy, l[2]]
            elif ex == 4:
                opc_neg_neg_nop[op] = [cy, l[2]]
            elif ex != 1:
                raise RuntimeError(f"Unknown 'EXT'")
    if opc[0xEA][0] != 1 or opc[0x42][0] != 1:
        raise RuntimeError("NEG and NOP should be one cycle (or missing from the result set?)!")
    # override "strange" results ... yeah, not an ideal solution ...
    opc[0x82][0] = 7        # STA  ($nn,SP),Y
    opc[0xE2][0] = 8        # LDA  ($nn,SP),Y
    print("#define TIMINGS_65GS_FAST\t{{{}}}\t// MEGA65 fast clock timings".format(",".join([str(a[0]) for a in opc])))
    for op in range(0x100):
        if opc[op][0] is None:
            raise RuntimeError(f"Missing test result for op ${op:02X}")
        if opc_nop[op][0]:
            print("#define MEGA_FOP_NOP_{:02X}_CYCLES {}\t// {} (NOP prefixed)         {} cycs total (+{})".format(
                op, opc_nop[op][0] - 1,         opc_nop[op][1],                 opc_nop[op][0], opc_nop[op][0] - 1 - opc[op][0]))
        if opc_neg_neg[op][0]:
            print("#define MEGA_FOP_NEG_NEG_{:02X}_CYCLES {}\t// {} (NEG NEG prefixed)     {} cycs total (+{})".format(
                op, opc_neg_neg[op][0] - 2,     opc_neg_neg[op][1],         opc_neg_neg[op][0], opc_neg_neg[op][0] - 2 - opc[op][0]))
        if opc_neg_neg_nop[op][0]:
            print("#define MEGA_FOP_NEG_NEG_NOP_{:02X}_CYCLES {}\t// {} (NEG NEG NOP prefixed) {} cycs total (+{})".format(
                op, opc_neg_neg_nop[op][0] - 3, opc_neg_neg_nop[op][1], opc_neg_neg_nop[op][0], opc_neg_neg_nop[op][0] - 3 - opc[op][0]))


if __name__ == "__main__":

    main("result/only-mega65.csv")
    sys.exit(0)
