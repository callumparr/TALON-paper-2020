import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn' prevents output of some error message to stdout.
from optparse import OptionParser
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

def getOptions():
    parser = OptionParser()

    parser.add_option("--f", dest = "infile",
        help = "TALON read annot file", metavar = "FILE", type = str)
    parser.add_option("--ref", dest = "ref_sites",
        help = "TSV file of GENCODE starts and ends for each transcript", 
        metavar = "FILE", type = str)
    parser.add_option("--datasets", dest = "datasets", default = None,
        help = "Optional: comma-delim list of datasets to include", type = str)
    parser.add_option("--includeSpikes", dest = "spikes", action = "store_true",
                      default = False,
                      help = "Whether to include SIRV and ERCC reads. Default = False")
    parser.add_option("--xmax", dest = "xmax", type = int,
                      help = "Max x value for plots.", default = 5000)
    parser.add_option("--ymax", dest = "ymax", type = int,
                      help = "Max y value for plots.", default = 1000000)
    parser.add_option("--o", dest = "outprefix", help = "Prefix for outfile",
        metavar = "FILE", type = str)

    (options, args) = parser.parse_args()
    return options

def plot_histogram(data, xvar, label, xmax, ymax, fname):
    x = pd.Series(data[xvar], name=label)
    plt.xlim(-1*xmax,xmax)
    plt.ylim(0,ymax)
    ax = sns.distplot(x, kde = False, color = '#009E73',
                  bins = np.arange(min(x), max(x), 5))

    med = round(np.median(x), 1)

    style = dict(size=12, color='black')
    plt.axvline(med, linestyle = '--', color = 'lightgrey')

    ax.text(med + 50, ymax*7/8, "Median: " + str(med) + " bp", **style)
    ax.set(ylabel='Number of reads')

    plt.tight_layout()
    plt.savefig(fname, dpi = 600, bbox_inches='tight')
    plt.close()

# def plot_hires_bins(df, end_type, oprefix):
#     # diff_col = '{}_diff'.format(end_type)
#     diff_col = '{}_dist'.format(end_type.upper())
#     hires_bin_col = '{}_hires_bin'.format(end_type)
#     perc_col = 'perc_{}_hires'.format(end_type)

#     hires_total = len(df.loc[(df[diff_col] > -500)&(df[diff_col] <= 500)].index)
#     hires_bins = [i for i in range(-500,0,50)]
#     hires_bins += [-1, 0, 1]
#     hires_bins += [i for i in range(50,550,50)]

#     df[hires_bin_col] = pd.cut(df[diff_col], bins=hires_bins)
#     hires_df = df[[hires_bin_col, diff_col]].groupby(hires_bin_col).count()
#     hires_df.rename({diff_col: 'counts'}, axis=1, inplace=True)
#     hires_df.reset_index(inplace=True)
#     hires_df[perc_col] = (hires_df.counts/hires_total)*100
#     hires_df.counts.fillna(0, inplace=True)
#     hires_df[perc_col].fillna(0, inplace=True)

#     ax = sns.barplot(x=hires_bin_col, y=perc_col,
#             data=hires_df, color='#009E73', saturation=1)
#     ax.set(xlabel='Distance from annotated {} (bp)'.format(end_type.upper()))
#     ax.set(ylabel='Percentage of Known Reads within 500 bp')
#     ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
#     ax.set(ylim=(0,100))
#     fname = '{}_{}_dists_hires.png'.format(oprefix, end_type)
#     print('Saving plot {}'.format(fname))
#     plt.savefig(fname,
#         bbox_inches='tight')
#     plt.clf()

def plot_hires_bins(df, end_type, total_reads, oprefix):

    # get only the genes that are expressed above 10 TPM
    g_df = df[['gene_ID', 'annot_transcript_id']].groupby('gene_ID',
        as_index=False).count()
    g_df.rename({'annot_transcript_id': 'counts'}, axis=1, inplace=True)
    g_df['tpm'] = (g_df.counts/total_reads)*1000000
    g_df = g_df.loc[g_df.tpm >= 10]
    df = df.loc[df.gene_ID.isin(g_df.gene_ID.tolist())]

    calc_model_read_support(df, 50)

    # diff_col = '{}_diff'.format(end_type)
    diff_col = '{}_dist'.format(end_type.upper())
    hires_bin_col = '{}_hires_bin'.format(end_type)
    perc_col = 'perc_{}_hires'.format(end_type)

    hires_total = len(df.loc[(df[diff_col] > -500)&(df[diff_col] <= 500)].index)
    hires_bins = [i for i in range(-500,0,50)]
    hires_bins += [-1, 1]
    hires_bins += [i for i in range(50,550,50)]
    hires_bins = [df[diff_col].min()] + hires_bins
    hires_bins += [df[diff_col].max()]

    labels = ['({}, {}]'.format(i, j) for i,j in zip(hires_bins[:-1],hires_bins[1:])]
    labels[0] = '(min, -500]'
    labels[-1] = '(500, max]'

    bin_scores = [-1*min(abs(i),abs(j)) for i, j in zip(hires_bins[:-1],hires_bins[1:])] 
    bin_score_tuples = [(b,s) if b != '(-1, 1]' else (b,0) for b,s in zip(labels, bin_scores)]
    bin_score_dict = {i[0]:i[1] for i in bin_score_tuples}

    # {b: s if b != [-1, 1] else b: 0 for b,s in zip(labels, bin_scores)}

    df[hires_bin_col] = pd.cut(df[diff_col], bins=hires_bins, labels=labels)
    df['bin_score'] = df[hires_bin_col].map(bin_score_dict)


    hires_df = df[['annot_transcript_id',
                         'bin_score',
                         hires_bin_col,
                         diff_col]].groupby([hires_bin_col,
                         'bin_score',
                         'annot_transcript_id'],
                         as_index=False).count()
    hires_df.dropna(inplace=True)
    hires_df.rename({diff_col: 'counts'}, axis=1, inplace=True)

    # sort by bin score to prioritize keeping the highest-scoring 
    # bin when dropping duplicates on transcript id
    hires_df.sort_values(by='bin_score', ascending=False, inplace=True)

    # drop duplicate transcript ids and keep the first instance
    bop = hires_df.drop_duplicates(subset='annot_transcript_id',
        keep='first')

    beep = bop[[hires_bin_col, 'counts']].groupby(hires_bin_col,
        as_index=False).count()
    total = beep.counts.sum()
    beep['total_transcripts'] = total
    beep['perc_models'] = (beep.counts/beep.total_transcripts)*100


    ax = sns.barplot(x=hires_bin_col, y='perc_models',
            data=beep, color='#009E73', saturation=1)
    ax.set(xlabel='Distance from annotated {} (bp)'.format(end_type.upper()))
    ax.set(ylabel='Percentage of known transcript models with a read with {} in bin range'.format(end_type.upper()))
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
    ax.set(ylim=(0,50))
    fname = '{}_{}_dists_hires_10_TPM.png'.format(oprefix, end_type)
    print('Saving plot {}'.format(fname))
    plt.savefig(fname,
        bbox_inches='tight')
    plt.clf()

def calc_model_read_support(df, r):
    n_models = len(df.annot_transcript_id.unique())

    tss_models = df.loc[df.TSS_dist.abs() <= r,
        'annot_transcript_id'].to_frame()
    tss_models.drop_duplicates(inplace=True)
    tes_models = df.loc[df.TES_dist.abs() <= r,
        'annot_transcript_id'].to_frame()
    tes_models.drop_duplicates(inplace=True)


    both_models = tss_models.merge(tes_models, how='inner',
        on='annot_transcript_id')

    n_tss_models = len(tss_models.index)
    n_tes_models = len(tes_models.index)
    n_both_models = len(both_models.index)

    beep = 'Found {} models with at least one read within {} bp '+\
          'of the annotated TSS, which is {:.2f}% of known '+\
          'models'
    print(beep.format(n_tss_models, r, (n_tss_models/n_models)*100))

    beep = 'Found {} models with at least one read within {} bp '+\
          'of the annotated TES, which is {:.2f}% of known '+\
          'models'
    print(beep.format(n_tes_models, r, (n_tes_models/n_models)*100))

    beep = 'Found {} models with at least one read within {} bp '+\
          'of the annotated TSS and with at least one read within {} '+\
          'bp of the annotated TES, which is {:.2f}% of known '+\
          'models'
    print(beep.format(n_both_models, r, r, (n_both_models/n_models)*100))

def main():
    options = getOptions()
    infile = options.infile
    ref_sites = options.ref_sites

    data = pd.read_csv(infile, sep = '\t', header = 0)
    ref_sites = pd.read_csv(ref_sites, sep = '\t', header = 0)

    # Filter datasets (optional)
    if options.datasets != None:
        datasets = options.datasets.split(",")
        data = data[data['dataset'].isin(datasets)]

    # get the total number of reads from these datasets
    total_reads = len(data.index)

    # Remove chrM reads
    data = data.loc[data.chrom != "chrM"]

    # Remove spikes unless requested to keep
    if options.spikes == False:
         data = data[~data.chrom.str.contains("SIRV", na = False)] # Prevents float error from mixed datatypes from chr index
         data = data[~data.chrom.str.contains("ERCC", na = False)] # Prevents float error from mixed datatypes from chr index 

    # Limit to known transcripts
    data = data.loc[data.transcript_novelty == "Known"]   

    # Merge together reads with GENCODE start data
    data = data[["gene_ID", "annot_transcript_id", "strand", "read_start", "read_end"]]
    data = pd.merge(data, ref_sites, on = "annot_transcript_id", 
                    how = "left")

    # Compute TSS/TES distances
    # Negative distance is upstream, positive is downstream
    data['TSS_dist'] = data.read_start - data.TSS_pos
    data['TES_dist'] = data.read_end - data.TES_pos
    data.loc[data['strand']=='-', ['TSS_dist', 'TES_dist']] *= -1

    # # Plot
    # plot_histogram(data, "TSS_dist", "Distance from annotated TSS (bp)", 
    #                options.xmax, options.ymax, 
    #                options.outprefix + "_TSS_dist_known.png")
    # plot_histogram(data, "TES_dist", "Distance from annotated TES (bp)",
    #                options.xmax, options.ymax,
    #                options.outprefix + "_TES_dist_known.png")

    oprefix = options.outprefix
    plot_hires_bins(data, 'tss', total_reads, oprefix)
    plot_hires_bins(data, 'tes', total_reads, oprefix)

    # now we want to see 
    # 1. what percentage of known transcripts have a read that falls
    # within a certain bp of the annotated TSS
    # 2. what percentage of known transcripts have a read that falls
    # within a certain bp of the annotated TES
    # 3. what percentage of known transcripts have both? ( these can 
    # be from different reads )
    # calc_model_read_support(data, 50)

if __name__ == '__main__':
    main()
