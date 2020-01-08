"""
Copyright 2019 Ryan Wick (rrwick@gmail.com)
https://github.com/rrwick/Trycycler

This file is part of Trycycler. Trycycler is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version. Trycycler is distributed
in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details. You should have received a copy of the GNU General Public License along with Trycycler.
If not, see <http://www.gnu.org/licenses/>.
"""

import random
import sys
import textwrap
import zlib

from .alignment import align_a_to_b
from .log import log, section_header, explanation
from .misc import reverse_complement
from . import settings


def get_starting_seq(seqs):
    section_header('Finding starting sequence')
    explanation('In this step, Trycycler finds a sequence to use as a starting point for each of '
                'the contigs. This can be a standard starting point (e.g. the dnaA gene) or if '
                'one is not found, then a randomly-chosen unique sequence will be used. The '
                'strands are also normalised in this step, so each contig has the starting '
                'sequence on the positive strand. Note that if the contigs are not circular, then '
                'the starting sequence will only be used for strand normalisation, not for contig '
                'rotation.')

    starting_seq = None  # TODO: look for known start sequences (dnaA/repA or user-provided) here.

    if starting_seq is None:
        starting_seq = get_random_starting_sequence(seqs)

    strand_fixed_seqs = normalise_strands(seqs, starting_seq)
    return starting_seq, strand_fixed_seqs


def rotate_to_starting_seq(seqs, starting_seq):
    section_header('Rotating contigs to starting sequence')
    explanation('For a circular contig, any point in the sequence is a valid starting position '
                'and it can thus be \'rotated\' by moving sequence from the contig start to the '
                'contig end. In this step, Trycycler rotates each contig such that it begins with '
                'the starting sequence, ensuring that all contigs begin and end together so they '
                'can be aligned to each other.')
    # TODO
    # TODO
    # TODO
    # TODO
    # TODO
    return seqs  # TEMP


def get_random_starting_sequence(seqs):
    potential_starting_seqs = get_random_starting_sequence_candidates(seqs)

    # Choose the first sequence which has a single solid alignment to each of the sequences.
    for starting_seq in potential_starting_seqs:
        num_alignments = []
        for seq in seqs.values():
            alignments = align_a_to_b(starting_seq, seq)
            alignments = [a for a in alignments if a.query_cov == 100.0
                          and a.percent_identity > settings.RANDOM_STARTING_SEQ_MIN_IDENTITY]
            num_alignments.append(len(alignments))

        if all(n == 1 for n in num_alignments):
            log('Using randomly-chosen unique starting sequence:')
            for line in textwrap.wrap(starting_seq, width=50):
                log('  ' + line)
            log()
            return starting_seq

    sys.exit('Error: unable to find a suitable starting sequence')


def get_random_starting_sequence_candidates(seqs):
    seq_names = list(seqs.keys())
    candidates = []
    for _ in range(settings.RANDOM_STARTING_SEQ_TRIAL_COUNT):
        seq = seqs[random.choice(seq_names)]
        start = random.randint(0, len(seq) - settings.RANDOM_STARTING_SEQ_LEN)
        end = start + settings.RANDOM_STARTING_SEQ_LEN
        potential_seq = seq[start:end]
        candidates.append(potential_seq)

    # Sort the candidates sequences from least-compressible (good) to most-compressible (bad) using
    # zlib compressed size as a metric.
    return sorted(candidates, reverse=True, key=lambda x: len(zlib.compress(x.encode())))


def normalise_strands(seqs, starting_seq):
    """
    This function returns a new dictionary of sequences where the starting sequence is on the
    positive strand for each.
    """
    log('Normalising strands:')
    strand_fixed_seqs = {}
    for seq_name, seq in seqs.items():
        log(f'  {seq_name}: ', end='')
        alignments = align_a_to_b(starting_seq, seq)
        assert len(alignments) == 1
        strand = alignments[0].strand
        if strand == '+':
            log('+ strand (using original sequence)')
            strand_fixed_seqs[seq_name] = seq
        else:
            assert strand == '-'
            log('- strand (using reverse complement sequence)')
            strand_fixed_seqs[seq_name] = reverse_complement(seq)
    log()
    return strand_fixed_seqs
