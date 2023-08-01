# Z(H)->bb(cc)+J/psi Analysis

## `singularity` for lpc
[run analysis in an interactive shell](https://github.com/ChuyuanLiu/heptools#singularity)

    git clone https://github.com/chuyuanliu/HqqJpsi.git
    cd HqqJpsi
    singularity shell                   `# run a shell within a container`\
    -B /cvmfs                           `# mount cvmfs`\
    -B ~/nobackup:/nobackup             `# mount nobackup dir`\
    -B .:/analysis                      `# mount analysis dir`\
    --pwd /analysis                     `# set initial working directory`\
    docker://chuyuanliu/heptools:latest `# use prebuilt docker image`

## `conda`
set up and activate conda environment

    conda env create -f local.yml
    conda activate hqqjpsi
    
    