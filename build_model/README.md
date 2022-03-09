## Overview:

`compile_denovo.py`: Parse lists of de novo variants obtained from the literature, and in-house datasets. Details on each data source are provided in <placeholder link to manuscript>. Outputs list of all de novo and their source.

`compare_denovo.py`: Compare the mutational likelihoods of transitions, across different sources (germline, somatic tissue, somatic cancer) and sample de novo counts.

`filter_denovo.py`: Remove any de novo from outlier samples. Outputs list of de novo mutations used to calculate mutability. User specified arguments *-germline_max*, *-som_tissue_max*, *-som_cancer_max* to indicate the maximum sample de novo count used for filtering for each source. Defaults provided based on analyses.

`composite_likelihood_mito.py`: Code to apply the mitochondrial composite likelihood model. Outputs file with mutational likelihood scores for every single nucleotide variant in the mtDNA. User specified arguments *-context_size* to indicate how many nucleotides to include for sequence context, 3 for trinucleotide set as default, and *-denovo_list* the path to the list of de novo to use, the output of `filter_denovo.py` set as default.
