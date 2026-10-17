> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase56 — minimized auditable record

**PROVEN:** normal file-backed writes use FAT copies, fixed-root sectors (FAT12/16), data clusters and, for FAT32, FSInfo. They do not require the identity cache, path, mount-ID padding, free-space cache or exact BPB trailing-sector count to calculate their physical target domains. Native mapper1AF1E uses base+stride×LBA in32 bits. Sources: [live-geometry-structure.md](<../phase49-existing-geometry-reader/live-geometry-structure.md>), [real-filesystem-geometry.md](<../phase47-filesystem-state-closure/real-filesystem-geometry.md>), [geometry-record.md](<../phase55-precleanup-geometry-snapshot/geometry-record.md>).

|Required canonical field |FS offset / source width |Stored encoding |Reachability role |

|---|---|---|---|

|fatbase |+2C /32 |13 bits |Lowest FAT-write LBA |

|fatsize |+24 /32 |13 bits |Extent of each FAT |

|database |+34 /32 |13 bits |Fixed-root end and data start |

|n_fatent |+20 /32 |13 bits |Upper valid data-cluster bound |

|csize |+0A /16 (native value from BPB byte) |3-bit log2, power-of-two check |Cluster-to-LBA multiplier |

|n_fats |+02 /8 |1 bit, value−1 |One or two FAT copies |

|FAT type |+00 /8 |1 bit: FAT12/FAT16 |FAT capacity check; excludes FSInfo writes |

**PROVEN:** these fields occupy57 bits, rounded to**8 bytes** with7 reserved zero bits. Encoding is lossless for the admitted scalar ranges. Four32-bit words use13 bits each, factors3+1 bits, type1 bit. FAT32 and any scalar>8191 are explicitly unsupported, never silently truncated. A general uncompressed seven-scalar FAT12/16 record is20 bytes (four32-bit words plus csize16,nfats8,type8); retaining volume base for FAT32 raises it to24 bytes, or23 with canonical8-bit csize. The last comparison is a scalar-width design calculation, not a claim FAT32 is fully qualified here.

**PROVEN conditional encoding domain:** native backing must be drive0/NOR with baseD4000 and stride/BPS4096. These are checked contract values, not an assumption that every per-unit BPB matches the reference. Host requires nonwrapping domains within the conservative32MiB partition bound. Then at most7980 logical sectors exist, and13 bits suffice for all admitted words. FAT32 cannot meet its native minimum cluster class within this bounded4096-byte-sector volume; reject it rather than carry unused FSInfo/root-cluster fields. Base/stride/type checks and lifecycle invalidation must be implemented for this omission to be safe. They are not yet a proved lifetime invariant of the new hook.

**PROVEN:** for FAT12/16 the native assignment is root=fatbase+n_fats×fatsize, and database=root+root-sectors. Capture verifies this relationship before omission. Host recomputes FATend, rejects overflow/inconsistency and bounds the whole fixed-root domain[FATend,database), so root-entry count need not be retained separately. Volume base/reserved sectors are not normal FAT12/16 write domains. Exact total sectors and padding have no role in the three retained domains. Native mounted-field provenance remains mandatory; this is not validation of arbitrary guessed RAM.

Host independently reconstructs:

`FAT=[fatbase,fatbase+n_fats*fatsize)`

`ROOT=[FATend,database)`

`DATA=[database,database+(n_fatent-2)*csize)`.

It checks FAT class/capacity and all arithmetic, then maps/expands these domains to physical erase boundaries. The admitted domain has sector-aligned4096-byte mapping, matching the reviewed erase alignment; both targets lie belowD4000. **PROVEN:**5 saved native-mount record round trips,7 rejection cases and16 factor cases pass. All required scalars survive exactly; unsafe/unsupported values fail closed. [compact.py](<../../../builds/phase56-geometry-snapshot-lifecycle/compact.py>), compact-tests.json (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/compact-tests.json`; not distributed).

**UNKNOWN:** a global information-theoretic minimum under every possible evidence representation. Two reachability bits alone are smaller but do not provide independent host verification. Eight bytes is the smallest implemented, tested canonical representation here, not a claimed impossibility theorem for7-byte enumerative encodings.

## Host versus device derivation

**STRONG INFERENCE — recommend A:** retain the8-byte raw canonical scalars; let the host calculate domains and target safety. OptionB's flags plus checksum cannot reconstruct omitted geometry, and checking a device-supplied checksum is not independent checking of a device-supplied conclusion. A sufficiently auditable B would have to retain equivalent source values and saves little.8 payload +4 control =12 bytes can theoretically reuse existing diagnostic-owned storage without the rejected52-byte extension. This is a proposed re-layout of live storage, not spare RAM.
