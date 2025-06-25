<div align="center">
  <img src="https://github.com/user-attachments/assets/beb49b33-82d2-4421-bcbe-0a604588fc0d" width="300" alt="SPARKS"/>
</div>

<h1 align="center">SPARKS</h1>
<h2 align="center">Multi-Agent Artificial Intelligence Model for End-to-End Scientific Discovery</h2>

A. Ghafarollahi, M.J. Buehler*

Massachusetts Institute of Technology

*mbuehler@MIT.EDU

Advances in artificial intelligence (AI) promise autonomous discovery, yet most systems still resurface knowledge latent in their training data. We present **Sparks, a multi-modal multi-agent AI model** that executes the entire discovery cycle that includes hypothesis generation, experiment design and iterative refinement to develop generalizable principles and a report without human intervention.

Applied to protein science, Sparks uncovered two previously unknown phenomena: (i) a length-dependent mechanical crossover whereby beta-sheet-biased peptides surpass alpha-helical ones in unfolding force beyond ~80 residues, establishing a new design principle for peptide mechanics; and (ii) a chain-length/secondary-structure stability map revealing unexpectedly robust beta-sheet-rich architectures and a ``frustration zone'' of high variance in mixed alpha/beta folds. 

These findings emerged from fully self-directed reasoning cycles that combined generative sequence design, high-accuracy structure prediction and physics-aware property models, with paired generation-and-reflection agents enforcing self-correction and reproducibility. The key result is that  Sparks can independently conduct rigorous scientific inquiry and identify previously unknown scientific principles.

## Model Overview

![Fig 1](https://github.com/user-attachments/assets/cfab1fe2-f8df-4d32-9c5a-dcd11b157d9a)

Figure 1. **Overview of Sparks, a multi-agent AI model for automated scientific discovery.** 

**Panel a**: Contemporary AI systems excel at statistical generalization within known domains, but rarely generate or validate hypotheses that extend beyond prior data, and cannot typically identify shared principles across distinct phenomena. This is because powerful models tend to memorize physics without discovering shared concepts. For scientific discovery, however, the elucidation of more general and shared foundational concepts (such as a scaling law, design principle, or crossover) is critical, in order to create significantly higher extrapolation capacity. **Panel b**: Sparks automates the end-to-end scientific process through four interconnected modules: 1) hypothesis generation, 2) testing, 3) refinement, and 4) documentation. The system begins with a user-defined query, which includes research goals, tools to test the hypothesis, and experimental constraints to guide the experimentation. It then formulates an innovative research idea with a testable hypothesis, followed by rigorous experimentation and refinement cycles. All findings are synthesized into a final document that captures the research objective, methodology, results, and directions for future work, in addition to a shared principle (such as in the examples presented here a scaling law or mechanistic rule). Each module is operated by specialized AI agents with clearly defined, synergistic roles.

### Installation

```
conda create -n Sparks python=3.10
conda activate Sparks

# Install PyPI requirements
pip install -r requirements.txt
```

### Launching Sparks
This repository provides code for running Sparks, a system for automated scientific discovery.

To launch Sparks, open and run the notebook in the main directory:

```
launch_Sparks.ipynb
```
This notebook takes the following inputs:

- ```query```: A user-defined research question or goal.

- ```tools```: Custom Python functions (defined by the user) that Sparks can call to test ideas.

- ```constraints```: Optional conditions (defined by the user) that should be respected when Sparks evaluates hypotheses.


### Defining Custom Tools
Sparks relies on user-defined tools to validate research ideas. Here's how to define and connect them:

1. **Define your tools** as Python functions in the file:
  ```
  functions.py
  ```

2. **Describe each tool** in the ```launch_Sparks.ipynb``` notebook, including:

- The tool's name

- A brief description of its purpose

- Its input parameters

- Its expected output

This description is how Sparks "understands" what each tool does.

**To adapt Sparks for your use case, just update ```functions.py``` with your tools and modify ```launch_Sparks.ipynb``` to include their descriptions.**

### Original paper

Please cite this work as:
```
@article{ghafarollahi2025sparksmultiagentartificialintelligence,
      title={Sparks, a Multi-Agent AI Model for Automated End-to-End Scientific Discovery}, 
      author={Alireza Ghafarollahi and Markus J. Buehler},
      year={2025},
      eprint={2504.19017},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2504.19017}, 
}
```
