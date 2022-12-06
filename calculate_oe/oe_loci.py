import argparse
import datetime
from oe_functions import *
import os


def loci_oe(input_file: str, obs_value: str, fit_parameters: str, output_prefix: str, excluded_sites: List[int]):
	"""Calculate the observed:expected ratio and 90% confidence interval for genes and loci.

	:param input_file: annotated file with mutation likelihood scores and observed maximum heteroplasmy
	:param obs_value: the column header of observed value
	:param fit_parameters: the path to the file with the linear equation coefficients and intercepts to use
	:param output_prefix: string added to start of output file name
	:param excluded_sites: list of base positions to exclude from calculations
	"""
	file_genes = open('output_files/oe/%sgenes_obs_exp.txt' % output_prefix, "w")
	file_noncoding = open('output_files/oe/%snoncoding_obs_exp.txt' % output_prefix, "w")
	header = "locus	description	start	end	consequence	variant_count	observed	expected	obs:exp	lower_CI	upper_CI	pvalue"
	file_genes.write(header + '\n')
	file_noncoding.write(header + '\n')

	# extract loci to calculate obs:exp for
	mitomap_loci = {}
	for row in csv.DictReader(open('required_files/databases/mitomap_genome_loci.txt'), delimiter='\t'):
		if abs(int(row["Ending"]) - int(row["Starting"])) > 5:  # to skip very small loci
			mitomap_loci[(int(row["Starting"]), int(row["Ending"]))] = (row["Map_Locus"], row["Description"])
	
	# to handle variants in two genes
	per_gene = {}
	for row in csv.DictReader(open(
			'required_files/synthetic_vcf/NC_012920.1_synthetic_vep_splitvarstwogenes.vcf'), delimiter='\t'):
		per_gene[(row["POS"], row["REF"], row["ALT"], row["SYMBOL"])] = row["Consequence"]
	
	for loci in mitomap_loci:
		# initialize dictionary so all values are 0
		loci_sum = initialize_sum_dict(identifier_list=['synonymous', 'missense', 'stop_gain', 'SNV'])
		# for each locus, sum observed and likelihood for each variant class
		for row in csv.DictReader(open(input_file), delimiter='\t'):
			if int(row["POS"]) not in excluded_sites:
				mutation = row["REF"] + '>' + row["ALT"]
				region_to_use = 'ori' if (int(row["POS"]) in ori_region) else 'ref_exc_ori'
				name = ''
				# if the position is in the loci in loop, loci[0] is the start and loci[1] is the end coordinate
				if (loci[0] < loci[1]) and (loci[0] <= int(row["POS"]) <= loci[1]):
					if any(x in row["symbol"] for x in ["MT-A", "MT-C", "MT-N"]):  # protein gene
						if ("synonymous" in per_gene[
							(row["POS"], row["REF"], row["ALT"], mitomap_loci[loci][0])]) and not any(
								x in row["consequence"] for x in more_severe_than_syn):
							name = 'synonymous'
						elif ("missense" in per_gene[
							(row["POS"], row["REF"], row["ALT"], mitomap_loci[loci][0])]) and not any(
								x in row["consequence"] for x in more_severe_than_missense):
							name = 'missense'
						elif ("stop_gain" in per_gene[(row["POS"], row["REF"], row["ALT"], mitomap_loci[loci][0])]) and (
								'stop_gained&start_lost' not in row["consequence"]):
							name = 'stop_gain'
					elif not any(x in row["symbol"] for x in ["MT-A", "MT-C", "MT-N"]):  # RNA gene or non-coding
						name = 'SNV'
				# to handle loci spanning artificial break, this will only be non-coding loci
				elif (loci[0] > loci[1]) and ((int(row["POS"]) >= loci[0]) or (int(row["POS"]) <= loci[1])):
					name = 'SNV'
				if name != '':
					loci_sum = sum_obs_likelihood(
						mutation=mutation, identifier=name, region=region_to_use,
						observed=row[obs_value], likelihood=row["Likelihood"], dict=loci_sum)
		# now calculate expected
		for variant_type in ['synonymous', 'missense', 'stop_gain', 'SNV']:
			exp_max_het = calculate_exp(sum_dict=loci_sum, identifier=variant_type, fit_parameters=fit_parameters)
			if exp_max_het > 0:  # to skip those variant consequences not relevant to the locus
				obs_max_het = calculate_obs(identifier=variant_type, sum_dict=loci_sum)
				ratio_oe = obs_max_het / exp_max_het
				total_all = calculate_total(identifier=variant_type, sum_dict=loci_sum)
				(lower_CI, upper_CI) = calculate_CI(
					obs_max_het=obs_max_het, total=total_all, exp_max_het=exp_max_het)
				# set the observed as if it was the upper CI (upper_CI * exp_max_het) - to be conservative
				pvalue = calculate_pvalue(
					obs_max_het=(upper_CI * exp_max_het), total=total_all, exp_max_het=exp_max_het)
				
				print("Calculating values for", variant_type, "in", str(mitomap_loci[loci][0]))
				
				output = file_genes if ((variant_type != "SNV") or ("RNA" in mitomap_loci[loci][1])) else file_noncoding
				if (output == file_genes) or ((output == file_noncoding) and (round(exp_max_het) >= 10)):
					output.write(
						mitomap_loci[loci][0] + '\t' + mitomap_loci[loci][1] + '\t' + str(loci[0]) + '\t' + str(loci[1])
						+ '\t' + variant_type + '\t' + str(total_all) + '\t' + str(obs_max_het) + '\t' + str(exp_max_het)
						+ '\t' + str(ratio_oe) + '\t' + str(lower_CI) + '\t' + str(upper_CI) + '\t' + str(pvalue) + '\n')


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"-input", type=str, help="Annotated file with mutation likelihood scores and observed maximum heteroplasmy")
	parser.add_argument(
		"-obs", type=str, help="Population dataset from which observed maximum heteroplasmy is obtained")
	parser.add_argument(
		"-parameters", type=str, help="File with parameters from linear model to calculate expected")
	parser.add_argument(
		"-prefix", type=str, help="Output files prefix")
	parser.add_argument(
		"-exc_sites", type=int, nargs='+', help="List of base positions to exclude from calibration")
	args = parser.parse_args()
	
	# set defaults, for gnomAD
	if args.input is None:
		args.input = 'output_files/mutation_likelihoods/mito_mutation_likelihoods_annotated.txt'
	if args.obs is None:
		args.obs = "gnomad_max_hl"
	if args.parameters is None:
		args.parameters = 'output_files/calibration/linear_model_fits.txt'
	if args.prefix is None:
		args.prefix = ""
	if args.exc_sites is None:
		# exclude “artifact_prone_sites” in gnomAD positions - 301, 302, 310, 316, 3107, and 16182 (3107 already excluded)
		# variants at these sites were not called in gnomAD and therefore these positions removed from calculations
		args.exc_sites = [301, 302, 310, 316, 16182]
	
	for path in ['output_files/oe']:
		if not os.path.exists(path):
			os.makedirs(path)
			print("Creating required directories")
	
	print(datetime.datetime.now(), "Calculate the observed:expected ratio for each gene/locus")
	
	loci_oe(
		input_file=args.input, obs_value=args.obs, fit_parameters=args.parameters, output_prefix=args.prefix,
		excluded_sites=args.exc_sites)
	
	print(datetime.datetime.now(), "Script complete!" + '\n')
	