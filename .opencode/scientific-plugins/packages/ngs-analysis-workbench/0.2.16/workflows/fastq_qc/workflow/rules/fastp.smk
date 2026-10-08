rule fastp_paired:
    input:
        r1=lambda wildcards: SAMPLES[wildcards.sample]["r1"],
        r2=lambda wildcards: SAMPLES[wildcards.sample]["r2"],
    output:
        r1="trimmed/{sample}/{sample}_R1.fastq.gz",
        r2="trimmed/{sample}/{sample}_R2.fastq.gz",
        html="trimmed/{sample}/{sample}.fastp.html",
        json="trimmed/{sample}/{sample}.fastp.json",
    threads: THREADS
    conda:
        "../envs/fastq_qc.yaml"
    shell:
        "mkdir -p trimmed/{wildcards.sample:q} && "
        "{FASTP:q} -i {input.r1:q} -I {input.r2:q} -o {output.r1:q} -O {output.r2:q} "
        "--html {output.html:q} --json {output.json:q} --thread {threads}"


rule fastp_single:
    input:
        r1=lambda wildcards: SAMPLES[wildcards.sample]["r1"],
    output:
        r1="trimmed/{sample}/{sample}.fastq.gz",
        html="trimmed/{sample}/{sample}.fastp.html",
        json="trimmed/{sample}/{sample}.fastp.json",
    threads: THREADS
    conda:
        "../envs/fastq_qc.yaml"
    shell:
        "mkdir -p trimmed/{wildcards.sample:q} && "
        "{FASTP:q} -i {input.r1:q} -o {output.r1:q} --html {output.html:q} "
        "--json {output.json:q} --thread {threads}"
