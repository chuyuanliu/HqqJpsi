from heptools.cms import AAA, LPC
from heptools.dataset import Dataset, File
from heptools.system.eos import EOS, PathLike


def to_filelist(dataset: Dataset, output: PathLike):
    output = EOS(output)
    for (_, dataset, year, era, tier), filelist in dataset:
        path = (output / tier).mkdir(True)
        with open(path / f'{dataset}{year}{era}.txt', 'w') as f:
            for file in filelist.files:
                f.write(f'{EOS(file.path, AAA.EOS_LPC)}\n')

if __name__ == '__main__':
    File.priority = LPC.priority
    to_filelist(Dataset.load('../../datasets/data_PicoAOD.json'), '../../fileLists')
