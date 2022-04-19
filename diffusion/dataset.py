import torch
import torchaudio
from torchaudio import transforms as T
import random
from glob import glob

from RAVE.rave.pqmf import PQMF

from .utils import MidSideEncoding, Mono, Stereo, RandomGain, PadCrop

class SampleDataset(torch.utils.data.Dataset):
  def __init__(self, paths, global_args):
    super().__init__()
    self.filenames = []

    self.channel_tf = torch.mean if global_args.mono else Stereo()

    self.transform = torch.nn.Sequential(
        Mono(),
        #MidSideEncoding(),
        RandomGain(0.5, 1.0),
        PadCrop(global_args.training_sample_size),
        PQMF(100, 128)
    )
    for path in paths:
      self.filenames += glob(f'{path}/**/*.wav', recursive=True)

  def __len__(self):
    return len(self.filenames)

  def __getitem__(self, idx):
    audio_filename = self.filenames[idx]
    try:
      audio, sr = torchaudio.load(audio_filename, normalize=True)
      if sr != 44100:
          resample_tf = T.Resample(sr, 44100)
          audio = resample_tf(audio)
      audio = audio.clamp(-1, 1)

      if self.transform is not None:
        audio = self.transform(audio)

      return audio
    except Exception as e:
     # print(f'Couldn\'t load file {audio_filename}: {e}')
      return self[random.randrange(len(self))]