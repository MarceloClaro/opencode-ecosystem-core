rule cutadapt_paired:
    input:
        r1=lambda wildcards: SAMPLES[wildcards.sample]["r1"],
        r2=lambda wildcards: SAMPLES[wildcards.sample]["r2"],
    output:
        r1="trimmed/{sample}/{sample}_R1.fastq.gz",
        r2="trimmed/{sample}/{sample}_R2.fastq.gz",
        log="trimmed/{sample}/{sample}.cutadapt.log",
    params:
        a=lambda wildcards: config.get("adapter_r1", ""),
        A=lambda wildcards: config.get("adapter_r2", ""),
    conda:
        "../envs/fastq_qc.yaml"
    shell:
        "mkdir -p trimmed/{wildcards.sample:q} && "
        "{CUTADAPT:q} -a {params.a:q} -A {params.A:q} -o {output.r1:q} -p {output.r2:q} "
        "{input.r1:q} {input.r2:q} > {output.log:q}"


rule cutadapt_single:
    input:
        r1=lambda wildcards: SAMPLES[wildcards.sample]["r1"],
    output:
        r1="trimmed/{sample}/{sample}.fastq.gz",
        log="trimmed/{sample}/{sample}.cutadapt.log",
    params:
        a=lambda wildcards: config.get("adapter_r1", ""),
    conda:
        "../envs/fastq_qc.yaml"
    shell:
        "mkdir -p trimmed/{wildcards.sample:q} && "
        "{CUTADAPT:q} -a {params.a:q} -o {output.r1:q} {input.r1:q} > {output.log:q}"
