rule fastqc_trimmed_paired:
    input:
        r1="trimmed/{sample}/{sample}_R1.fastq.gz",
        r2="trimmed/{sample}/{sample}_R2.fastq.gz",
    output:
        directory("fastqc/trimmed/paired/{sample}")
    threads: THREADS
    conda:
        "../envs/fastq_qc.yaml"
    shell:
        "mkdir -p {output:q} && {FASTQC:q} -t {threads} -o {output:q} {input.r1:q} {input.r2:q}"


rule fastqc_trimmed_single:
    input:
        r1="trimmed/{sample}/{sample}.fastq.gz",
    output:
        directory("fastqc/trimmed/single/{sample}")
    threads: THREADS
    conda:
        "../envs/fastq_qc.yaml"
    shell:
        "mkdir -p {output:q} && {FASTQC:q} -t {threads} -o {output:q} {input.r1:q}"


rule multiqc_trimmed:
    input:
        expand("fastqc/trimmed/paired/{sample}", sample=PAIRED),
        expand("fastqc/trimmed/single/{sample}", sample=SINGLE)
    output:
        "multiqc/trimmed/multiqc_report.html"
    conda:
        "../envs/fastq_qc.yaml"
    shell:
        "mkdir -p multiqc/trimmed && "
        "{MULTIQC:q} --force --cl-config 'no_version_check: true' --no-megaqc-upload "
        "fastqc/trimmed trimmed -o multiqc/trimmed"
