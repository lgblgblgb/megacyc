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



def import_asm_data(fn : str):

    res, ln, MAC_NAME = {}, 0, "TESTING"
    with open(fn, "rt") as f:
        for ol in f:
            l, ln = ol.strip().split(), ln + 1
            # TESTING $0000   ; |LDA #nn| random comment
            if len(l) < 4 or l[0] != MAC_NAME or not l[1].startswith("$") or l[2] != ";" or not l[3].startswith("|"):
                if len(l) > 0 and l[0] == MAC_NAME:
                    raise RuntimeError(f"Bad comment line, found '{MAC_NAME}' marker but other format error found in line {ln} of file {fn}: {ol}")
                continue
            try:
                opc = int(l[1].lstrip("$"), 16)
            except ValueError:
                raise RuntimeError(f"Bad hex value in line {ln} of file {fn} at \"{l[1]}\": {ol}")
            if (opc & 0xFF) >= 0x80:
                continue
            if opc in res:
                raise RuntimeError(f"Opcode ${opc:02X} was already defined but reused in line {ln} of file {fn}: {ol}")
            l = " ".join(l[3:])[1:].split("|")[0].strip().split()
            l[0] = f"{l[0]:5}"
            res[opc] = "".join(l).rstrip()
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
    refs = set(res[REF]) if REF in tests else set()
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
                if refs:
                    refs.remove(ind)
                diag = "OK" if len(set(r)) == 1 else "MISMATCH"
        else:
            diag = ""
        r = [f"${ext:02X}" if ind >= 0 else " - ", f"${opbyte:02X}" if ind >= 0 else " - ", f"{asm:{asm_align}}"] + r
        if diag:
            r.append(diag)
        print(" | ".join(r))
    if refs:
        print("Missing measurements for these references: {}".format(" ".join(map("${:04X}".format, sorted(refs)))))


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
    parsed, tail_cost, pre_cost  = {}, 0, 0
    while True:
        if len(result) < 4:
            raise RuntimeError("Unexpected end of the result stream")
        testid, loopcnt, result = result[0] + (result[1] << 8), result[2] + (result[3] << 8), result[4:]
        if testid == 0xFFFF and loopcnt == 0xFFFF:
            break
        cyc_float = 810000.0 / loopcnt - tail_cost - pre_cost
        cyc = round(cyc_float)
        print(f"TEST ${testid:04X} result is {cyc} ({cyc_float} - {loopcnt})")
        if cyc < 1:
            raise RuntimeError(f"Impossible cycle count got: {cyc}")
        if tail_cost == 0:
            tail_cost = cyc
            print(f"\t(measure loop cycle count: {tail_cost})")
            if tail_cost < 16:
                raise RuntimeError(f"Impossible tail_cost: {tail_cost}")
        else:
            if (testid & 0xFF) >= 0x80:
                if pre_cost:
                    raise RuntimeError(f"More than one correction entires in a row at testid ${testid:04X}")
                pre_cost = cyc
            else:
                pre_cost = 0
                if testid in parsed:
                    raise RuntimeError(f"More than one result for testid ${testid:04X}")
                parsed[testid] = cyc
    print(f"\t(remaining stream ({len(result)} bytes): {result})")
    parsed[-1] = tail_cost
    return parsed


if __name__ == "__main__":

    if len(sys.argv) < 2:
        sys.stderr.write("Bad usage.\n")
        sys.exit(1)
    composer(opcodes = import_asm_data("testbench.i65"), res = {
        fn.replace("\\", "/").split("/")[-1].split(".")[0].upper().replace("_", " "):
            add_reference("utils/reference_results.txt") if fn == "ref" else parse_result(fn)
        for fn in sys.argv[1:]
    })
    sys.exit(0)
