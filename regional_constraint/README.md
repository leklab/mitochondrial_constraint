## Overview:

`regional_constraint.py`: Identify regional constraint in mitochondrial genes, either in the 'real alignment', or in 'shuffles' which are used to calculate false discovery rates (FDR). Outputs a list of all regions that are more significantly constrained than the locus (*all_significant_kmers.txt*), as well as a list of non-overlapping regions that remain after application of a greedy algorithm (*regional_constraint_intervals.txt*). User specified argument *-input*;  the output of `annotate_mutations.py` set as default; *-n_shuffles*; set as default of  0 (i.e. 'real alignment'), *-loci_type*; set by user for either protein genes, RNA or non-coding loci, or both, *-out_dir*; name out output directory set by user, *-sig_threshold*; set by user. All other arguments set as defaults for gnomAD (*-obs*, *-parameters*, *-exc_sites*, *-loci_input*, *-noncoding_input*). 

`apply_FDR_filter.py`: Uses the output from the shuffles to calculate the FDR for each regional constraint interval identified in the 'real alignment'. The list of shuffles to iterate over, as well as the FDR threshold to apply, can be modified by a user by editing parameters passed into the function call for `apply_FDR_filter`. The *all_significant_kmers.txt* and *regional_constraint_intervals.txt* outputs from `regional_cosntraint.py` for both the real and shuffled alignments are required as input; these can also be set by editing the parameters for `apply_FDR_filter` in the script. A custom script was used to combine output files from shuffles run separately into a single file (i.e. each *regional_constraint_intervals.txt* output combined to create *all_shuffles_nonoverlapping.txt*, and each *all_significant_kmers.txt* combined to create *all_sig_shuffles.txt*). Outputs *final_regional_constraint_intervals.txt*, a list of high confidence intervals of regional constraint.

`annotate_regional_constraint.py`: Uses the output of `apply_FDR_filter.py` to annotate every possible SNV with their regional constraint status (i.e. within or not) and minimum distance from regional constraint in 3D structures.


These scripts use multiprocessing module to maximise use of available CPU.