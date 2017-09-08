# hbp-cerebellum-models
Package of Human Brain Project (HBP) Cerebellum models.

## Description
This repository contains cerebellum models developed by the [cerebellum team](https://collab.humanbrainproject.eu/#/collab/375/nav/3408) led by [Prof. Egidio D’Angelo](http://www-5.unipv.it/dangelo/?page_id=295) at the [Human Brain Project](https://www.humanbrainproject.eu/en/).



## ~~Table of Contents~~

## Installation
Dependant packages (versions based on 31 August 2017):
- [NEURON](https://www.neuron.yale.edu/neuron/download) (tested on Release 7.4 (1370:16a7055d4a86) 2015-11-09)
- [Numpy](http://www.numpy.org/) (tested on 1.11.0)
- [NEO](https://github.com/NeuralEnsemble/python-neo) (tested on 0.5.1)
- [Elephant](https://pypi.python.org/pypi/elephant) (tested on 0.4.1)
- [Quantities](https://github.com/python-quantities/python-quantities) (tested on 0.12.1)
- [Matplotlib](https://matplotlib.org/users/installing.html) (tested on 1.5.1)

## Usage
1. To start using first:
```
git clone https://github.com/lungsi/hbp-cerebellum-models.git
cd hbp-cerebellum-models
```

2. To see the models import the `model_manager` module
```
from models import model_manager as mm
```

There models in the `hbp-cerebellum-models` pack is broken down to three **model_scale**: cells, microcircuit and network.

To see the names of the cellular models use the `model_manager.get_available_models` function
```
mm.get_available_models( model_scale="cells" )
```

3. Instantiate a model, say, the cellular model, *PC2015Masoli*
first import the `cells` module
```
from models import cells
```
Then instantiate the model
```
pc = cells.PC2015Masoli.PurkinjeCell()
```
*Note: PC2015Masoli is a Purkinje cell. For GrC2001DAngelo which is a Granular cell use the command: grc = cells.GrC2001DAngelo.GranularCell()*

4. Run the instantiated model
   - The default *voltage response*
     ```
     pc.produce_voltage_response()
     ```
     This is the same as
     ```
     pc.produce_voltage_response( cell_regions=['vm_soma', 'vm_NOR3'])
     ```
     NB: NOR3 stands for 3rd Node of Ranvier.

   - The default *spike response*
     ```
     pc.produce_spike_train()
     ```
     This is the same as
     ```
     pc.produce_spike_train( cell_locations=['vm_soma'], thresh=[0.0] )
     ```
     NB: Non default example `pc.produce_spike_train( cell_locations=['vm_soma', 'NOR3'], thresh=[0.0, -1.0] )`

## ~~Contribution~~

## ~~Credits~~

## License
BSD-3-Clause
Copyright 2017 Lungsi
See LICENSE.txt
