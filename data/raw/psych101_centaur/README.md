---
license: apache-2.0
language:
- en
tags:
- Psychology
pretty_name: Psych-101
size_categories:
- 100B<n<1T
---

### Dataset Summary

Psych-101 is a data set of natural language transcripts from human psychological experiments. 
It comprises trial-by-trial data from 160 psychological experiments and 60,092 participants, making 10,681,650 choices. 
Human choices are encapsuled in "<<" and ">>" tokens.

- **Paper:** [Centaur: a foundation model of human cognition](https://marcelbinz.github.io/imgs/Centaur__preprint_.pdf)
- **Point of Contact:** [Marcel Binz](mailto:marcel.binz@helmholtz-munich.de)

### Example Prompt

```
You will be presented with triplets of objects, which will be assigned to the keys D, P, and H.
In each trial, please indicate which object you think is the odd one out by pressing the corresponding key.
In other words, please choose the object that is the least similar to the other two.

D: piecrust, P: game, and H: bracelet. You press <<D>>.
D: tuning fork, P: rocket, and H: waffle iron. You press <<P>>.
D: grits, P: combination lock, and H: suitcase. You press <<D>>.
D: boulder, P: odometer, and H: salami. You press <<P>>.
D: spoon, P: diaper, and H: satellite dish. You press <<P>>.
[...]
```

### Languages

English.

### Usage

```
from datasets import load_dataset
data = load_dataset('marcelbinz/Psych-101')
```

### Data Fields


```
{
  "text": Natural language transcription of the experiment.
  "experiment": Identifier for the experiment.
  "participant": Identifier for the participant.
}
```

### Licensing Information

[Apache License 2.0](https://choosealicense.com/licenses/apache-2.0/)

### Citation Information

```
@misc{binz2024centaurfoundationmodelhuman,
      title={Centaur: a foundation model of human cognition}, 
      author={Marcel Binz and Elif Akata and Matthias Bethge and Franziska Brändle and Fred Callaway and Julian Coda-Forno and Peter Dayan and Can Demircan and Maria K. Eckstein and Noémi Éltető and Thomas L. Griffiths and Susanne Haridi and Akshay K. Jagadish and Li Ji-An and Alexander Kipnis and Sreejan Kumar and Tobias Ludwig and Marvin Mathony and Marcelo Mattar and Alireza Modirshanechi and Surabhi S. Nath and Joshua C. Peterson and Milena Rmus and Evan M. Russek and Tankred Saanum and Natalia Scharfenberg and Johannes A. Schubert and Luca M. Schulze Buschoff and Nishad Singhi and Xin Sui and Mirko Thalmann and Fabian Theis and Vuong Truong and Vishaal Udandarao and Konstantinos Voudouris and Robert Wilson and Kristin Witte and Shuchen Wu and Dirk Wulff and Huadong Xiong and Eric Schulz},
      year={2024},
      eprint={2410.20268},
      archivePrefix={arXiv},
      primaryClass={cs.LG},
      url={https://arxiv.org/abs/2410.20268}, 
}
```
