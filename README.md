# SPARKS

<div align="center">
  <img src="https://github.com/user-attachments/assets/bdc0a774-85b8-4cbc-8d31-1ec5bf7542b2" width="300" alt="SPARKS"/>
</div>

## Multi-modal, multi-agent AI model capable of independently conducting research by formulating hypotheses, performing experiments, and adapting its strategy.
A. Ghafarollahi, M.J. Buehler*

Massachusetts Institute of Technology

*mbuehler@MIT.EDU

![Fig 1](https://github.com/user-attachments/assets/cfab1fe2-f8df-4d32-9c5a-dcd11b157d9a)

Figure 1. **Overview of Sparks, a multi-agent AI model for automated scientific discovery.** 

**Panel a**: Contemporary AI systems excel at statistical generalization within known domains, but rarely generate or validate hypotheses that extend beyond prior data, and cannot typically identify shared principles across distinct phenomena. This is because powerful models tend to memorize physics without discovering shared concepts. For scientific discovery, however, the elucidation of more general and shared foundational concepts (such as a scaling law, design principle, or crossover) is critical, in order to create significantly higher extrapolation capacity. **Panel b**: Sparks automates the end-to-end scientific process through four interconnected modules: 1) hypothesis generation, 2) testing, 3) refinement, and 4) documentation. The system begins with a user-defined query, which includes research goals, tools to test the hypothesis, and experimental constraints to guide the experimentation. It then formulates an innovative research idea with a testable hypothesis, followed by rigorous experimentation and refinement cycles. All findings are synthesized into a final document that captures the research objective, methodology, results, and directions for future work, in addition to a shared principle (such as in the examples presented here a scaling law or mechanistic rule). Each module is operated by specialized AI agents with clearly defined, synergistic roles.

### Codes
This repository contains code for .

The notebook files ```SciAgents_ScienceDiscovery_GraphReasoning_non-automated.ipynb``` and ```SciAgents_ScienceDiscovery_GraphReasoning_automated.ipynb``` in the Notebooks directory correspond to the non-automated and automated multi-agent frameworks, respectively, as explained in the accompanying paper.

The automated multi-agent model is implemented with [AG2](https://github.com/ag2ai/ag2?tab=readme-ov-file) (Formerly AutoGen), an open-source ecosystem for agent-based AI modeling. 
This project is also collected in [Build with AG2](https://github.com/ag2ai/build-with-ag2), you can checkout more projects built with AG2.

### Original paper

Please cite this work as:
```
```
