## Isoforms detected
```
Rscript ../../../plotting_scripts/plot_novelty_categories_distinct_isoforms.R \
        --f ../SIRV_talon_abundance.tsv \
        --datasets SIRV_Rep1,SIRV_Rep2 \
        --ymax 350 \
        -o .
Rscript ../../../plotting_scripts/plot_novelty_categories_distinct_isoforms.R \
        --f ../SIRV_talon_abundance.tsv \
        --datasets SIRV_Rep1 \
        --ymax 350 \
        -o .
Rscript ../../../plotting_scripts/plot_novelty_categories_distinct_isoforms.R \
        --f ../SIRV_talon_abundance.tsv \
        --datasets SIRV_Rep2 \
        --ymax 350 \
        -o .
```

## Reads by category
```
# Plot number of reads by category (both reps together)
Rscript ../../../plotting_scripts/plot_novelty_category_read_counts.R \
    --f ../SIRV_talon_abundance.tsv \
    --ymax 10000 \
    --datasets SIRV_Rep1,SIRV_Rep2 \
    -o .

# Plot number of reads by category (Rep1)
Rscript ../../../plotting_scripts/plot_novelty_category_read_counts.R \
    --f ../SIRV_talon_abundance.tsv \
    --ymax 10000 \
    --datasets SIRV_Rep1 \
    -o .

# Plot number of reads by category (Rep2)
Rscript ../../../plotting_scripts/plot_novelty_category_read_counts.R \
    --f ../SIRV_talon_abundance.tsv \
    --ymax 10000 \
    --datasets SIRV_Rep2 \
    -o .
```

## Fraction As at end of transcript analysis
```
python ../../../plotting_scripts/plot_frac_As_by_read_annot_category.py \
    --f ../SIRV_talon_read_annot.tsv \
    --omitGenomic \
    --outprefix SIRV

```