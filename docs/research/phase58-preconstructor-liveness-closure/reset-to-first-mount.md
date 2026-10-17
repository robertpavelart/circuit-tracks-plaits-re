> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase58 — ordered path and exact remaining frontier

|Stage |Exact authenticated control path |Evidence status |

|---|---|---|

|Boot reset/task prefix |Native reset→SVC/PendSV→Main02FDE→03A10→05D98→Storage→051C2 |PROVEN previously executed; genuine replay still stops before original81000 read completion |

|Boot post-read/metadata |02FE4→03B2A;02FFC→03B66;03002→03B9A→selected installer03C24 |PROVEN byte-derived order and selected installer model; not a joined complete reset run |

|Handoff |03D06 disables/clears NVIC lines, resets peripheral clock blocks, sets VTOR/CONTROL/MSP and branches through application vector |PROVEN body; do not infer that every possible pending system exception was modeled |

|Application entry |5C00C→1BC78→5C19C→5B990→5B590 |PROVEN authenticated reset/scatter chain |

|Static memory/ctors |Zero[20003D04,20006A54), initialized data[20000000,20003D02), handler5B958→iterator5B978→10 constructors |PROVEN source and new3-case native constructor replay |

|Postconstructor main |5B9AE→1D3C8→1DA08/watchdog/peripheral setup;1D3E4→1DC38;1D3E8→1B1A8 |PROVEN native continuation to1B266 clock wait |

|Later startup |1D3EC→1DCDE;1D3F0/3F6→1DD44;1D3FC→1DDD4;1D400→1DFEE;1D404→1E134;1D408→1D3A0;1D40E→1AAD8;1D414/41A→1E4B6;1D41E→1DE78 |PROVEN static Main initializer sequence; not reached in new execution |

|Task roots |Main1D4B0;UI1D680;Storage5767C;Content22ACC, created by1DDD4 |PROVEN functions/pointers; mount-time ready/priorities and all queued callbacks UNKNOWN |

|Main first explicit mount |1D4B4→1EC80(identity);1D4BC→1EEAA/peripheral;1D4C0→1F0A8→NOR1ADDC→19A92→197A0→1AE06;then SD and1D4C4 settings/content construction |PROVEN byte order plus prior isolated native mount cases; first full-boot epoch UNKNOWN |

Sources: [findings.md](<../phase38-nor81000/findings.md>), [update-noop-review.md](<../phase45-nor-mutation-closure/update-noop-review.md>), boot-08003d06.asm (local-only reference: `builds/phase58-preconstructor-liveness-closure/boot-08003d06.asm`; not distributed), [first-mount-provenance.md](<../phase57-first-mount-provenance/first-mount-provenance.md>), app-0801d3c8.asm (local-only reference: `builds/phase58-preconstructor-liveness-closure/app-0801d3c8.asm`; not distributed), app-0801ddd4.asm (local-only reference: `builds/phase58-preconstructor-liveness-closure/app-0801ddd4.asm`; not distributed), [mount-to-persistence-ordering.md](<../phase55-precleanup-geometry-snapshot/mount-to-persistence-ordering.md>).

**PROVEN new continuation:** native1D3C8 executes watchdog/setup and reaches**1B266→1B268→1B26A** waiting for the clock-ready predicate. A DBGMCU configuration shadow atE0042000 was mapped; no ready bits or I/O completions were fabricated. This is an ordinary missing peripheral model, not a device failure or a storage mutation. startup-frontier.json (local-only reference: `builds/phase58-preconstructor-liveness-closure/startup-frontier.json`; not distributed), app-0801b250.asm (local-only reference: `builds/phase58-preconstructor-liveness-closure/app-0801b250.asm`; not distributed).

All31 actually executed call events between constructor return and that frontier are listed individually below:

|Call site |Callee |

|---|---|

|0x801d3ca|0x801da08|

|0x801da0a|0x801eaf8|

|0x801da0e|0x801eb1e|

|0x801da12|0x801da8a|

|0x801da90|0x801afbc|

|0x801afd4|0x801b154|

|0x801afe0|0x801ba38|

|0x801da98|0x801b130|

|0x801daa0|0x8022228|

|0x801daa6|0x8022234|

|0x801daac|0x8022242|

|0x801dab2|0x8022230|

|0x801dab8|0x801b13e|

|0x801da16|0x801dac2|

|0x801dac8|0x8022228|

|0x801dace|0x8022234|

|0x801dad4|0x8022230|

|0x80222ec|0x802238c|

|0x80222fa|0x801bb6a|

|0x801da1a|0x801db4e|

|0x801db52|0x8022624|

|0x801db58|0x8022648|

|0x801d3e0|0x801b3b8|

|0x801d3e4|0x801dc38|

|0x801dc4e|0x801bb50|

|0x801dc54|0x8022658|

|0x8022670|0x801bbf8|

|0x8022682|0x801bb6a|

|0x801d3e8|0x801b1a8|

|0x801b1b2|0x801bc58|

|0x801b1ba|0x801bc58|

**UNKNOWN:** the requested complete list of every pre-snapshot function/callback/task cannot yet be asserted. The newly closed constructor list is complete for the admitted constructor invocation; the scheduler/deferred call graph after this frontier is not. Exact unresolved persistence-capable route remains pre-snapshot producers→22A5C enqueue→Content22ACC/22AE4→normal file work→197A0 slow mount or disk-write1A7AC→1AF1E. Its pre-snapshot normal producer predicates/queue state have not been closed. No earlier mounted epoch is invented from this capability.
