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



def import_asm_comments(fn : str):

    process, res, ln, TV_BEGIN, TV_END = False, {}, 0, ("BEGIN", "TEST"), ("END", "TEST")
    with open(fn, "rt") as f:
        for ol in f:
            l, ln = ol.strip().split(), ln + 1
            if len(l) < 4 or l[0] != ";" or len(l[1]) < 2 or set(l[1]) != {"-"}:
                continue
            tv = tuple(map(str.upper, l[2:4]))
            if not process and tv == TV_BEGIN:
                process = True
            elif process and tv == TV_END:
                process = False
                break
            elif process:
                try:
                    opc = int(l[2].lstrip("$"), 16)
                except ValueError:
                    raise RuntimeError(f"Bad hex comment value in line {ln} of {fn} at \"{l[2]}\": {ol}")
                if opc in res:
                    raise RuntimeError(f"Opcode ${opc:02X} was already defined but reused in line {ln} of {fn}: {ol}")
                l[3] = f"{l[3]:5}"
                res[opc] = "".join(l[3:]).rstrip()
    if process:
        raise RuntimeError("No proper closer comment!")
    if len(res) == 0:
        raise RuntimeError("Empty result after parsing!")
    return res


def composer(opcodes : dict, res : dict):

    tests, N_A, REF, asm_align = sorted(res), "N/A", "REF", max(map(len, opcodes.values()))
    r = ["EXT", "OPC", ("{:"+str(asm_align)+ "}").format("ASM")] + tests
    if len(tests) == 2:
        r.append("COMPARISON")
    print(" | ".join(r))
    opcodes[-1] = "calibration"
    for ind in sorted(opcodes):
        opbyte, ext, asm = ind >> 8, ind & 0xFF, opcodes[ind]
        if REF in tests and ind not in res[REF]:
            continue
        r = [f"{res[t][ind]:3}" if ind in res[t] else N_A for t in tests]
        if set(r) == {N_A}:
            continue
        if len(tests) == 2:
            if N_A in r:
                diag = '-'
            else:
                diag = "OK" if len(set(r)) == 1 else "MISMATCH"
        else:
            diag = ""
        r = [f"${ext:02X}" if ind >= 0 else " - ", f"${opbyte:02X}" if ind >= 0 else " - ", f"{asm:{asm_align}}"] + r
        if diag:
            r.append(diag)
        print(" | ".join(r))


def add_reference(fn : str):

    res = {}
    with open(fn, "rt") as f:
        for l in f:
            l = tuple(map(str.strip, l.split(";")))
            if len(l) < 3 or l[0].startswith("#"):
                continue
            try:
                opc = int(l[0].lstrip("$"), 16)
            except ValueError:
                continue
            try:
                r = int(l[2])
            except ValueError:
                continue
            if opc in res:
                raise RuntimeError(f"Reference file has more lines for op ${opc:X}")
            res[opc] = r
    return res


def parse_result(fn : str):

    ID_STR = b'M65'
    print(f"--- PARSING: {fn} ---")
    with open(fn, "rb") as result:
        result = bytes(result.read())
    a = result.find(ID_STR)
    if a < 2 or a > 6:
        raise RuntimeError("Bad result, no valid M65 marker near the beginning of the file")
    l = result[a - 2] + (result[a - 1] << 8)
    print(f"\t(encoded length: {l})")
    result = result[a + len(ID_STR):]
    print(f"\t(stream length: {len(result)})")
    parsed = {-1: int(result[0])}
    print(f"\t(measure loop cycle count: {result[0]})")
    result = result[1:]
    while True:
        if len(result) < 1:
            raise RuntimeError("Unexpected end of the result stream (cyc)")
        cycles, result = int(result[0]), result[1:]
        if cycles == 0xFF:
            break
        if len(result) < 2:
            raise RuntimeError("Unexpected end of the result stream (id)")
        testid, result = result[0] + (result[1] << 8), result[2:]
        print(f"TEST ${testid:04X} result is {cycles}")
        parsed[testid] = cycles
    print(f"\t(remaining stream ({len(result)} bytes): {result})")
    return parsed


if __name__ == "__main__":

    if len(sys.argv) < 2:
        sys.stderr.write("Bad usage.\n")
        sys.exit(1)
    composer(opcodes = import_asm_comments("test.a65"), res = {
        fn.replace("\\", "/").split("/")[-1].split(".")[0].upper().replace("_", " "):
            add_reference("utils/reference_results.txt") if fn == "ref" else parse_result(fn)
        for fn in sys.argv[1:]
    })
    sys.exit(0)
