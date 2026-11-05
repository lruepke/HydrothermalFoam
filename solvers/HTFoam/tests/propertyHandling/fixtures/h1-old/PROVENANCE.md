# h1 old-solver numerical reference

Extracted without rerunning or modifying the preserved baseline of 2026-10-28.
This is a numerical regression fixture, not a scientific acceptance standard.

- Source: existing old HTFoam executable, OpenFOAM Foundation 10, arm64 macOS.
- EOS configuration: H2O-NaCl / IAPS84, X=0 kg/kg.
- Original executable build revisions are unknown; source checkout HEAD at capture
  does not establish binary provenance.
- Old executable SHA256: `79a704391f2703924c9b2595d9184f15372626bfe3dbbbd8e7a4c7d0a80e132a`.
- Current old archive SHA256 at capture: `4b95a1e8e8236c67ab267129124e6bfa3fa8f02cac87f7bae53b278b5aafa287`;
  this does not prove which archive was originally linked into that executable.
- Final time: 7884000000 s (250 years of 365 days), 9125 ten-day steps.
- Original fields were written with precision 6. Numeric extraction adds no precision.
- `cell-properties.txt`: internal p/T/U/rho/mu, 200 cells in original mesh order.
- `face-flux.txt`: internal phi only, 199 faces in original mesh order.
- `profile.xy`: unchanged original 1000-point x[m]/T[K]/p[Pa] sampled profile.
- Original initialization continued with physOK=0; that behavior is not endorsed.
- No binaries, mesh, logs, time directories, or full snapshots are included.

Default numeric regression tolerance is 5e-6 times the maximum reference magnitude
of each quantity (profile x tolerance 1e-12). This allows a margin over six-digit
output rounding and is not an EOS/physics validation tolerance. Optional same-host
full-baseline checks retain the stricter byte comparisons of the prior runner.

## Reference data SHA256

- Original p: `6a1a232d7b3e09c13f4d8c8c74f5799bd54342e953a41cd21a93d4199c74a0cc`.
- Original T: `41d4e23e939bf841c4f691e02029c10e27dac5a1eb44f3ab138584c885c98678`.
- Original U: `8ba8c3d8ddbaca172f2a422bfa18b1a45dff88235f34a74193930d91270d952e`.
- Original rho: `8699aa05c4c8dbee150d1c0480d100b790d467aa94a484ce0ca3bc1ed9272504`.
- Original mu: `e895e1a75439ebdd3e1d502ede58d8515597c69e640f8527736daaeca4501eba`.
- Original phi: `0706ff81a0794b3d27d9fcfd1f6fb43353c5a2ab584222b5372abab8b3d1625c`.

## Input SHA256 (review template)

Application naming differs from the old run and trailing whitespace is normalized
in the tracked input copy; numerical settings are unchanged.

- `.gitignore`: `54d275951d72257fcef90d0cc543d4234a9aed7a34841fa078424215d2a878f6`.
- `0/T`: `4836580efa61b3922b6e42310b948126c0f6176f0ec93b3565d219266494cbe5`.
- `0/h`: `643a8c87f11f0350892c3b6598e685b091af02b9e85bf7c9118fd1237eabae22`.
- `0/p`: `9e4c586ecd27e96012ec31a32f8f9e9d0aeefb73af913eb331da72dc9b7b1df8`.
- `0/permeability`: `675200f31048fb4c098ced17d562974eb47f7e1a73064f9657b6b1df3c4fae9f`.
- `clean.sh`: `31d81ee62c5b699334773665e556420332d3b7729e65fc090cc40be13d464568`.
- `constant/g`: `ea95e25259a3e7fa1bbc0bfb90efe069947ad30844957f6bb2bb2b7c9b73271a`.
- `constant/thermophysicalProperties`: `5d0fc5ca73ff99ec5844ee65ff37199946dab03c2c895c803183d510c11c308f`.
- `constant/transportProperties`: `d7c342b204dd37893ddd7494a42657a47e55be0033cb019eb917f0e9be9998f6`.
- `constant/xThermoProperties`: `dc1d53d8247f9189aa09440fb1ebdf8d92a2558ecf46325c3e8f8be70d06715d`.
- `run.sh`: `ad1cc13f5e3838f218d639ba01242b7a4274ff9b99f6b634afe11b5a59d8d69a`.
- `system/blockMeshDict`: `60bbe29a80826a8d43821c0d65f3c12e0136c3138533024b4a418ae5b73e6452`.
- `system/controlDict`: `79163e8bfe5aa1ba15705b67889d1a2700b28db0ef3df9c81b1ca703ec405c1d`.
- `system/fvSchemes`: `a65eccf9d82a3496e101aebf7703a2e81fcfe793ff5bc28356a8cc71c060b851`.
- `system/fvSolution`: `14dd60e9fef8784461b03d54f972ad228fba2a59f6198585370186841401a2ff`.
