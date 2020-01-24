import pyfaidx
import sys
sys.path.append("..")
import profile_internal_priming as prof_ip

def test_get_frac_plus_strand():
    """
          1   5    10   15   20   25
          ACTGACTGACTGAAATAAGAAACTGACTG
              ACTGACTG      (+)
        With range_size set to 10, we expect to extract seq "AAATAAGAAA"
        The correct fraction of As is therefore 8/10.
    """
    genome_file = "test_inputs/toy_genome.fa"
    genome = pyfaidx.Fasta(genome_file, sequence_always_upper=True,
                           one_based_attributes=False)
    frac = prof_ip.compute_frac_as_after_transcript("chrTest1", 12, '+', 10,
                                                    genome)

    assert frac == 8.0/10

def test_get_frac_minus_strand():
    """
          1   5    10   15   20   25
          ACTGACTGACTGAAATAAGAAACTGACTG
          TGACTGACTGACTTTATTCTTTGACTGAC
                    ACTTTATTCTTT  (-)                
        With range_size set to 8, we expect to extract seq "GTCAGTCA"
        The correct fraction of As is therefore 2/8.
    """
    genome_file = "test_inputs/toy_genome.fa"
    genome = pyfaidx.Fasta(genome_file, sequence_always_upper=True,
                           one_based_attributes=False)
    frac = prof_ip.compute_frac_as_after_transcript("chrTest1", 11, '-', 8,
                                                    genome)

    assert frac == 2.0/8
