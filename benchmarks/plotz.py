#! /usr/bin/env python3

import json
import os
from pathlib import Path
import sys

HASH_NAMES = [
    ("blake3", "BLAKE3"),
    ("blake2b", "BLAKE2b"),
    ("blake2s", "BLAKE2s"),
    ("blake2bp", "BLAKE2bp"),
    ("blake2sp", "BLAKE2sp"),
    ("sha512", "OpenSSL SHA-512"),
    ("sha256", "OpenSSL SHA-256"),
    ("sha3-256", "OpenSSL SHA3-256"),
    ("kangarootwelve", "KangarooTwelve"),
]

SIZES = [
    (2**6, "64 B"),
    (2**7, "128 B"),
    (2**8, "256 B"),
    (2**9, "512 B"),
    (2**10, "1 KiB"),
    (2**11, "2 KiB"),
    (2**12, "4 KiB"),
    (2**13, "8 KiB"),
    (2**14, "16 KiB"),
    (2**15, "32 KiB"),
    (2**16, "64 KiB"),
    (2**17, "128 KiB"),
    (2**18, "256 KiB"),
    (2**19, "512 KiB"),
    (2**20, "1 MiB"),
    (2**21, "2 MiB"),
    (2**22, "4 MiB"),
    (2**23, "8 MiB"),
    (2**24, "16 MiB"),
]


def dense_sizes():
    sizes = []
    for (size, _) in SIZES[:-1]:
        sizes.append(size)
        sizes.append(size * 5 // 4)
        sizes.append(size * 6 // 4)
        sizes.append(size * 7 // 4)
    sizes.append(SIZES[-1][0])
    return sizes


def main():
    freq_mhz = None
    if "BENCH_FREQ_MHZ" in os.environ:
        freq_mhz = int(os.environ["BENCH_FREQ_MHZ"])
    target = Path(sys.argv[1])
    names = []
    throughputs = []
    sizes = []
    for hash_name, hash_name_pretty in HASH_NAMES:
        names.append(hash_name_pretty)
        hash_dir = target / "bench_group" / hash_name
        for size_i, size in enumerate(dense_sizes()):
            estimates_path = hash_dir / str(size) / "new/estimates.json"
            try:
                estimates = json.load(estimates_path.open())
            except FileNotFoundError:
                # Some benchmark runs use longer inputs than others, so we
                # ignore missing sizes here.
                continue
            slope = estimates["Slope"]
            point = slope["point_estimate"]
            # upper = slope["confidence_interval"]["upper_bound"]
            # lower = slope["confidence_interval"]["lower_bound"]
            seconds = point / 1e9
            bps_throughput = size / seconds
            gibps_throughput = bps_throughput / (2 ** 30)
            if freq_mhz is not None:
                cpb_throughput = freq_mhz * 1e6 / bps_throughput
            if len(sizes) == size_i:
                # sizes.append(size_pretty)
                sizes.append(size)
            if len(throughputs) == size_i:
                throughputs.append([])
            if freq_mhz is not None:
                throughputs[size_i].append(cpb_throughput)
            else:
                throughputs[size_i].append(gibps_throughput)

        print('% {}'.format(hash_name))
        print('\\addplot coordinates {')
        print('\n'.join([ '({}, {})'.format(x, y[HASH_NAMES.index((hash_name, hash_name_pretty))]) for x, y in zip(sizes, throughputs) ]))
        print('};')
        # break


if __name__ == "__main__":
    main()
