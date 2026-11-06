# SPDX-License-Identifier: MIT
# Copyright (c) 2026 liuliu
# Read-only installed firmware audit; no APK modification or device writes.
# Locked to the observed layout; unsupported builds fail instead of guessing.
import zipfile,struct,hashlib,pathlib,json,sys
import dexparser
from dexparser.disassembler import opcode
import argparse
parser=argparse.ArgumentParser(description='Read-only audit of Samsung OEM menu visibility; never modifies an APK or phone.')
parser.add_argument('--apk',type=pathlib.Path,required=True)
parser.add_argument('--output',type=pathlib.Path,required=True)
args=parser.parse_args()
path=args.apk
expected_apk_hash='2ac6a07687b627a04615d9d2eb3e9c461b334ce5c81f426adcbbed817c0f5bcd'
apk_hash=hashlib.sha256(path.read_bytes()).hexdigest()
if apk_hash != expected_apk_hash:
    parser.exit(2, 'Unsupported APK build; no visibility verdict generated.\n')
with zipfile.ZipFile(path) as z:blob=z.read('classes.dex')
d=dexparser.Dexparser(fileobj=blob);strings=[x.decode(errors='replace') for x in d.get_strings()];types=d.get_typeids();methods=d.get_methods();fields=d.get_fieldids()
class_name='Lcom/android/settings/development/OemUnlockPreferenceController;'
cls=next(c for c in d.get_classdef_data() if strings[types[c['class_idx']]]==class_name)
cd=d.get_class_data(cls['class_data_off']);method=next(m for m in cd['direct_methods']+cd['virtual_methods'] if strings[methods[m['diff']]['name_idx']]=='isAvailable')
off=method['code_off'];size=struct.unpack_from('<I',blob,off+12)[0];words=list(struct.unpack_from('<'+'H'*size,blob,off+16))
i=0;instructions=[]
while i<len(words):
 word=words[i];op=word&255;name=opcode.get(op,'unknown');a=word>>8;length=1;operands=''
 if op in [0x1a,0x22]:
  length=2;idx=words[i+1];ref=strings[idx] if op==0x1a else strings[types[idx]];operands='v%d, %s'%(a,ref)
 elif op in [0x6e,0x6f,0x70,0x71,0x72]:
  length=3;m=methods[words[i+1]];count=(word>>12)&15;regs=words[i+2];vals=[(regs>>(4*j))&15 for j in range(min(count,4))];
  if count==5:vals.append((word>>8)&15)
  operands='{'+','.join('v%d'%v for v in vals)+'}, '+strings[types[m['class_idx']]]+'->'+strings[m['name_idx']]
 elif op==0x54:
  length=2;f=fields[words[i+1]];operands='v%d, v%d, %s->%s'%(a&15,a>>4,strings[types[f['class_idx']]],strings[f['name_idx']])
 elif op in [0x38,0x39]:
  length=2;delta=struct.unpack('<h',struct.pack('<H',words[i+1]))[0];operands='v%d, @%d'%(a,i+delta)
 elif op==0x28:
  delta=struct.unpack('<b',bytes([a]))[0];operands='@%d'%(i+delta)
 elif op==0x12:
  val=a>>4;val=val-16 if val&8 else val;operands='v%d, %d'%(a&15,val)
 elif op in [0x0a,0x0c,0x0f,0x11]:operands='v%d'%a
 else:raise SystemExit('Unsupported opcode at '+str(i)+': '+str(op))
 instructions.append({'code_unit':i,'opcode':name,'operands':operands,'raw':[hex(x) for x in words[i:i+length]]});i+=length
for ins in instructions:print('%02d %-22s %s'%(ins['code_unit'],ins['opcode'],ins['operands']))
# This prototype intentionally refuses an unexpected firmware control-flow layout.
assert instructions[-1]['opcode']=='return' and instructions[-1]['operands']=='v1'
assert any(i['code_unit']==49 and i['opcode']=='const/4' and i['operands']=='v1, 0' for i in instructions)
assert any(i['code_unit']==62 and i['opcode']=='if-nez' and i['operands']=='v0, @81' for i in instructions)
report={'apk_sha256':apk_hash,'class':class_name,'method':'isAvailable','dex':'classes.dex','method_code_offset':off,'instruction_code_units':size,'audit':'read-only static decoding; not runtime execution','finding':'When ro.boot.other.locked equals 1, the visibility predicate returns false.','runtime_property':'Not collected by this offline tool; obtain separately from live ADB.','instructions':instructions}
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
