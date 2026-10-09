// Offline adapter for the audited MIT-licensed dsp56300-disasm library.
// Reads a file; never executes DSP instructions or accesses devices.
use std::{env, fs};
fn number(s: &str) -> u32 {
    u32::from_str_radix(s.trim_start_matches("0x"), 16).expect("hex address")
}
fn main() {
    let args: Vec<String> = env::args().collect();
    assert!(args.len() == 5, "usage: dsp_disasm FILE ORIGIN_HEX FROM_HEX TO_HEX");
    let data = fs::read(&args[1]).expect("read input");
    assert_eq!(data.len() % 3, 0, "not aligned to 24-bit words");
    let words: Vec<u32> = data.chunks_exact(3)
        .map(|b| ((b[0] as u32)<<16)|((b[1] as u32)<<8)|(b[2] as u32)).collect();
    let origin = number(&args[2]);
    let mut pc = number(&args[3]);
    let end = number(&args[4]);
    assert!(origin <= pc && pc <= end && end-origin <= words.len() as u32);
    while pc < end {
        let index = (pc-origin) as usize;
        let first = words[index];
        let next = words.get(index+1).copied().unwrap_or(0);
        let (text, len) = dsp56300_disasm::disassemble(pc, first, next);
        assert!(len >= 1 && len <= 2 && pc+len <= end, "truncated instruction");
        let raw = if len == 2 { format!("{first:06X} {next:06X}") } else { format!("{first:06X}") };
        println!("P:{pc:06X}  {raw:13}  {text}");
        pc += len;
    }
}
