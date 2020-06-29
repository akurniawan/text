from itertools import combinations

import torch

from torchtext.experimental.utils import BucketByLengthBatchSampler

from ..common.torchtext_test_case import TorchtextTestCase


class TestSampler(TorchtextTestCase):
    def test_bucket_by_length_batch_sampler(self):
        dummy = [torch.tensor(range(1, torch.randint(2, 11, (1,))[0])) for num in range(15)]
        sampler = BucketByLengthBatchSampler(dummy, [5, 10], batch_size=5)

        # Ensure all indexes are available from the sampler
        indexes = [idx for row in sampler for idx in row]
        self.assertEquals(sorted(indexes), list(range(15)))

        # Since our bucket boundaries are 5 and 10, we can check if all of the
        # members have no difference more than 5
        def diff_among_members(arr):
            return abs(arr[0] - arr[1])

        for row in sampler:
            lengths = []
            for idx in row:
                lengths.append(dummy[idx].size(0))
            if len(lengths) > 1:
                max_diff = max(combinations(lengths, 2), key=diff_among_members)
                self.assertLess(abs(max_diff[0] - max_diff[1]), 5)

    def test_full_pipeline_bucket_sampler(self):
        from torch.utils.data import Dataset, DataLoader
        from torch.nn.utils.rnn import pad_sequence

        class MyDataset(Dataset):
            def __init__(self):
                self.data = []
                for num in range(150):
                    max_length = torch.randint(2, 11, (1,))[0]
                    self.data.append(torch.tensor(range(1, max_length)))

            def __getitem__(self, idx):
                return self.data[idx]

            def __len__(self):
                return len(self.data)

        def collate_fn(batch):
            return pad_sequence(batch, batch_first=True)

        dataset = MyDataset()
        batch_sampler = BucketByLengthBatchSampler(dataset, [3, 5, 10], 5)
        iterator = DataLoader(dataset, batch_sampler=batch_sampler, collate_fn=collate_fn)

        for x in iterator:
            print(x)
