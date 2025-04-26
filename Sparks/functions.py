#!/usr/bin/env python
# coding: utf-8

chroma_key = 'CHROMA KEY'

from MD_protein import *
import os
import os.path as osp
import torch
import subprocess
from subprocess import TimeoutExpired
import re
import numpy as np
from IPython.display import Markdown, display
import time
from Bio.PDB import PDBParser, DSSP
import json
import pandas as pd
import sys
from typing import Annotated
from typing import Union
from openai import OpenAI

client = OpenAI(organization ='')

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)


import base64

plot_discovery_prompt = '''Carefully review the following scientific query:

{query}

Then, examine the idea that was proposed to address this query:

{idea}

The idea was implemented, and the following plots were generated.

YOUR TASK:
-Your task is to carefully analyze the plot.
-Your goal is not only to analyze the plot but to explore it as a potential source of **scientific discovery**. 
-Go beyond merely interpreting what is depicted—look beneath the surface for surprising trends, hidden mechanisms, and novel insights. 
-Treat the plot as an experimental outcome from which new hypotheses or theoretical directions might emerge.

Specifically, aim to:
- Discover unexpected relationships or deviations.
- Identify emerging patterns not anticipated by the original idea.
- Propose new scientific questions, hypotheses, or mechanisms inspired by the plot.
- Consider alternate interpretations or edge cases the original idea did not anticipate.
- Reflect on how the results might challenge current understanding or open new research directions.

Respond in the following JSON format:

<plot_START>
<PLOT>
<plot_FINISH>

In <PLOT>, provide your response in the following structured format:

"description": "Describe what is visually shown in the plot, including key trends and variables.",
"hypothesis_shift": "Describe how the visual evidence might suggest a refinement or departure from the original hypothesis.",
"novel_patterns": "Identify any novel or surprising trends that were not part of the original expectation.",
"new_hypotheses": "Propose one or more new hypotheses that could be tested in follow-up studies.",
"mechanistic_speculation": "Speculate on possible mechanisms that could explain the new findings, even if tentative.",
"implications": "Discuss broader implications of these discoveries, including new directions for scientific inquiry.",
"caption": "Write a scientific figure caption. Start with a factual description of the plot, followed by interpretations and implications. Define all abbreviations on first use."
'''



def image_reasoning(input_image = 'image',
                    prompt='What is the image?',
                    model='o3', 
                    temperature=1,
                    reasoning_effort="high", 
                    system_message="You are a scientist.", 
                    msg_history=""):

    # Load and encode image
    with open(input_image, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    
    # Call GPT-4o with image and prompt
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
              "role": "developer",
              "content": [
                  {
                  "type": "text",
                  "text": f'{system_message}'
                  }
              ]
                },
                {
              "role": "assistant",
              "content": [
                  {
                  "type": "text",
                  "text": f'{msg_history}'
                  }
              ]
                },
            {
                "role": "user",
                "content": [
                    {"type": "image_url", 
                     "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"
                    }},
                    {"type": "text", 
                     "text": f'{prompt}'}
                ],
            }
        ],
    )
    
    # Print the response
    content = response.choices[0].message.content

    match = re.search(r'<plot_START>(.*?)<plot_FINISH>', content, re.DOTALL)
    if match:
        code_block = match.group(1).strip()
    else:
        print("Code block not found.")
    return code_block


code_dir = './'

try:
    os.mkdir(code_dir)
except:
    pass


from chroma import api
from chroma import Chroma, Protein, conditioners
from chroma.models import graph_classifier, procap
from chroma.utility.api import register_key
from chroma.utility.chroma import letter_to_point_cloud, plane_split_protein

api.register_key(chroma_key,)
chroma = Chroma()

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)

from typing import Annotated, Union
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import torch

import MDAnalysis as mda
from MDAnalysis.analysis.rms import RMSD
from MDAnalysis.analysis.rms import RMSF
import utils_ForceGPT

from transformers import AutoModelForCausalLM, AutoTokenizer

ForceGPT_model_name='lamm-mit/ProteinForceGPT'

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

tokenizer = AutoTokenizer.from_pretrained(ForceGPT_model_name, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

model_GPT = AutoModelForCausalLM.from_pretrained(
    ForceGPT_model_name, 
    trust_remote_code=True
).to(device)
model_GPT.config.use_cache = False

def calculate_energy_from_seq(sequence):
    prompt = f"CalculateEnergy<{sequence}>"
    print(prompt)
    task = utils_ForceGPT.extract_task(prompt, end_task_token='>') + ' '
    sample_output = utils_ForceGPT.generate_output_from_prompt(model_GPT, device, tokenizer, prompt=task, num_return_sequences=1, num_beams=1, temperature=0.01)
    for sample_output in sample_output:
        result=tokenizer.decode(sample_output, skip_special_tokens=True)  
        extract_data=utils_ForceGPT.extract_start_and_end(result, start_token='[', end_token=']')

    try:
        extract_data = float(extract_data)
        return extract_data
    except ValueError:
        print(f"Warning: Could not convert '{extract_data}' to float.")
        return None  # or any default/fallback value

def calculate_force_from_seq(sequence):
    prompt = f"CalculateForce<{sequence}>"
    print(prompt)
    task = utils_ForceGPT.extract_task(prompt, end_task_token='>') + ' '
    sample_output = utils_ForceGPT.generate_output_from_prompt(model_GPT, device, tokenizer, prompt=task, num_return_sequences=1, num_beams=1, temperature=0.01)
    for sample_output in sample_output:
        result=tokenizer.decode(sample_output, skip_special_tokens=True)  
        extract_data=utils_ForceGPT.extract_start_and_end(result, start_token='[', end_token=']')
    try:
        extract_data = float(extract_data)
        return extract_data
    except ValueError:
        print(f"Warning: Could not convert '{extract_data}' to float.")
        return None  # or any default/fallback value

def MD_protein(input_pdb: Annotated[str, 'protein PDB file name'], work_path: Annotated[str, 'name of the directory where simulation data will be stored. Use a descriptive name. Should differ for every protein.'])->str:
    pdb_name = simplify_and_remove_extension(input_pdb)
    input_pdb = f'{code_dir}{pdb_name}.pdb'
    assert os.path.exists(input_pdb), f"Error: {input_pdb} does not exist!"
    start_time = time.time()  # Record the start time

    #try:
    run_all(input_pdb=input_pdb,
            work_path=work_path, 
            eq_step=10000,
        #MD_1_step=75000, MD_2_step=75000, MD_3_step=100000,
        MD_1_step=5000, MD_2_step=5000, MD_3_step=100000,
        n_stage=10)

    #meanRMSD = mean_RMSD(work_path)
    maxRMSD = max_RMSD(work_path)
    data_rmsf = compute_RMSF(work_path)
    
    first_last_pdb_implicit_solvent(work_path)
    structure_first_frame, structure_first_frame_per_residue = analyze_protein_structure_V2(f'{work_path}/collect_results/first_frame.pdb')
    structure_last_frame, structure_last_frame_per_residue = analyze_protein_structure_V2(f'{work_path}/collect_results/last_frame.pdb')
    structure_rmsf_residue = {}
    for i in range(len(data_rmsf)-1):
        index, residue_name, residue_strcut = structure_last_frame_per_residue[i]
        residue_rmsf = data_rmsf[i][1]
        structure_rmsf_residue[f'residue# {index}'] = [f'AA: {residue_name}',f'SS: {residue_strcut}', f'RMSF: {residue_rmsf}'] 

    end_time = time.time()
    duration = end_time - start_time  # Calculate the duration
    print(f"The MD simulation took {duration} seconds.")
    #results = {"Mean RMSD (A)": f'{meanRMSD:.2f}', "secondary structure content of relaxed configuration %": structure_last_frame} 
    #return maxRMSD
    return maxRMSD, structure_last_frame
    #except:
    print('######################################')
    print(work_path)
    print('######################################')


def design_protein_from_length (length: Annotated[int, 'protein AA length'], caption='', steps=500, devices=device):
    chroma = Chroma()
    name = 'protein_sample'
    if caption != '':
        print (f'We use this caption to generate a protein: {caption}')
        procap_model = procap.load_model("named:public", device=devices,
                                        strict_unexpected=False,
                                        )
        conditioner = conditioners.ProCapConditioner(caption, -1, model=procap_model)
    else:
        conditioner=None

    protein = chroma.sample(chain_lengths=[length],steps=steps,
                           conditioner=conditioner, )
    fname = f'{code_dir}{name}.pdb' 
    protein.to(fname)
    sequence=protein.sequence()

    return sequence


def design_protein_from_CATH(length: Annotated[int, 'protein AA length'], 
                             cath: Annotated[str, '1 for alpha-helix, 2 for beta-sheet, 3 for mixed alpha-helix beta-sheet'], steps=500, device=device):
    print(f'We use this CATH to generate protein with length {length}: {cath}')
    name = 'protein_cath_sample'
    proclass_model = graph_classifier.load_model("named:public", device=device)
    conditioner = conditioners.ProClassConditioner("cath", cath, model=proclass_model)
    cath_conditioned_protein, _ = chroma.sample(samples=1, steps=steps,
    conditioner=conditioner, chain_lengths=[length], full_output=True,       
)
      
    fname = f'{code_dir}{name}.pdb'     
    protein = cath_conditioned_protein
    sequence=protein.sequence()
        #print(f'protein with name {fname} generated.')  
    #print(protein_seq)
    return sequence


def compute_RMSF(work_path):

    protein_pdb = work_path + '/TestProt_chain_0_after_psf.pdb'
    protein_dcd = work_path + '/1_Equilibrate_system/TestProt_chain_0_after_psf_AlongX_NPT.dcd'
    u = mda.Universe(protein_pdb, protein_dcd)
    
    # Select Cα atoms (commonly used for RMSF)
    calphas = u.select_atoms("protein and name CA")
    
    # Compute average positions
    avg_pos = np.mean(calphas.positions, axis=0)
    
    # Compute RMSF
    rmsf = np.sqrt(np.mean((calphas.positions - avg_pos) ** 2, axis=1))
    
    # Plot RMSF per residue
    residues = [res.resname for res in calphas.residues]
    
    data_rmsf = []
    
    for i in range(len(rmsf)):
        data_rmsf.append([residues[i], f'{rmsf[i]:.2f}'])    

    return data_rmsf


def analyze_protein_structure_V2(protein_struct: Annotated[str, 'protein pdb file']) -> str:

        pdb_name = simplify_and_remove_extension(protein_struct)
        protein_structure = f'{code_dir}{pdb_name}.pdb'
        if os.path.exists(protein_structure):
            protein_structure=protein_structure
        elif os.path.exists(protein_struct):
            protein_structure = protein_struct
        else:
            print('FILE NOT FOUND')

        #protein_structure, _ = check_pdb_name(protein_structure)
    
    #try:
            
            # Create a PDB parser
        #print ('Analyzing the secondary structure of this protein:', protein_structure )
            
        fix_pdb_file(protein_structure, protein_structure)
        add_missing_column(protein_structure)
        
        parser = PDBParser(QUIET=True)
        
        # Parse the PDB file
        structure = parser.get_structure('protein_structure', protein_structure)
        
        # Select the first model in the PDB file
        model = structure[0]
        
        # Run DSSP analysis
        dssp = DSSP(model, protein_structure, 'dssp', file_type='pdb')
        #print(dssp)
        
        # Initialize a dictionary for secondary structure counts
        secondary_structure_counts = {
            'H': 0,  # Alpha helix
            'B': 0,  # Isolated beta-bridge
            'E': 0,  # Extended strand
            'G': 0,  # 3-helix (3/10 helix)
            'I': 0,  # 5 helix (pi-helix)
            'T': 0,  # Hydrogen bonded turn
            'S': 0,  # Bend
            'P': 0,  # Poly-proline helices
            '-': 0   # None
        }
        
        # Count each secondary structure type
        per_residue_data = []
        for residue in dssp:
            per_residue_data.append([residue[0], residue[1], residue[2]])
            secondary_structure_counts[residue[2]] += 1
        
        # Calculate the total number of residues with assigned secondary structure
        total_residues = sum(secondary_structure_counts.values())
        
        #print ("The protein analyzed has ", total_residues, "residues.")
            
        # Calculate the percentage content for each secondary structure type
        secondary_structure_percentages = {ss: (count / total_residues * 100) for ss, count in secondary_structure_counts.items()}
    #except:
    #    pass
     
    # Return the results as a JSON string
        return secondary_structure_percentages, per_residue_data

def analyze_protein_structure(protein_struct: Annotated[str, 'protein pdb file']) -> str:

        pdb_name = simplify_and_remove_extension(protein_struct)
        protein_structure = f'{code_dir}{pdb_name}.pdb'
        if os.path.exists(protein_structure):
            protein_structure=protein_structure
        elif os.path.exists(protein_struct):
            protein_structure = protein_struct
        else:
            print('FILE NOT FOUND')

        #protein_structure, _ = check_pdb_name(protein_structure)
    
    #try:
            
            # Create a PDB parser
        #print ('Analyzing the secondary structure of this protein:', protein_structure )
            
        fix_pdb_file(protein_structure, protein_structure)
        add_missing_column(protein_structure)
        
        parser = PDBParser(QUIET=True)
        
        # Parse the PDB file
        structure = parser.get_structure('protein_structure', protein_structure)
        
        # Select the first model in the PDB file
        model = structure[0]
        
        # Run DSSP analysis
        dssp = DSSP(model, protein_structure, 'dssp', file_type='pdb')
        #print(dssp)

        
        
        # Initialize a dictionary for secondary structure counts
        secondary_structure_counts = {
            'H': 0,  # Alpha helix
            'B': 0,  # Isolated beta-bridge
            'E': 0,  # Extended strand
            'G': 0,  # 3-helix (3/10 helix)
            'I': 0,  # 5 helix (pi-helix)
            'T': 0,  # Hydrogen bonded turn
            'S': 0,  # Bend
            'P': 0,  # Poly-proline helices
            '-': 0   # None
        }
        
        # Count each secondary structure type
        per_residue_data = []
        for residue in dssp:
            per_residue_data.append({"index":residue[0], "AA":residue[1], "SS": residue[2]})
            secondary_structure_counts[residue[2]] += 1
        
        # Calculate the total number of residues with assigned secondary structure
        total_residues = sum(secondary_structure_counts.values())
        
        #print ("The protein analyzed has ", total_residues, "residues.")
            
        # Calculate the percentage content for each secondary structure type
        secondary_structure_percentages = {ss: (count / total_residues * 100) for ss, count in secondary_structure_counts.items()}
    #except:
    #    pass
     
    # Return the results as a JSON string
        results = {"secondary structure percentages": secondary_structure_percentages} 
        return secondary_structure_percentages


def add_missing_column(file_path ):
    # Read all lines from the file
    with open(file_path, 'r') as file:
        lines = file.readlines()
      
    header = False
    for line in lines:
        LINE = str(line).split(sep=' ')
        for item in LINE:
            if re.search('HEADER', item):
                header = True
    # Process lines
    modified_lines = []
    if not header:
        for line in lines:
            if line.startswith('ATOM'):
                columns = line.split()
                # Assuming the missing column is the atom type, which should be the 12th column
                if len(columns) < 13:
                    atom_type = columns[2][0]  # Extract atom type (3rd column in ATOM line)
                    # Add the atom type to the end of the line
                    modified_line = line.strip() + '    ' + atom_type + '\n'
                    modified_lines.append(modified_line)
                else:
                    modified_lines.append(line)
            else:
                modified_lines.append(line)

        # Write the modified lines back to the file
        with open(file_path, 'w') as file:
            file.writelines(modified_lines)

def simplify_and_remove_extension(filepath):
    # Get the base name of the file (i.e., with any directory path removed)
    base_name = os.path.basename(filepath)
    # Split the base name into the name and extension, and return just the name
    file_name_without_extension, _ = os.path.splitext(base_name)
    return file_name_without_extension

def fix_pdb_file(original_pdb_path, fixed_pdb_path):
    """
    Inserts a CRYST1 record into a PDB file if it is missing.

    Args:
    original_pdb_path (str): Path to the original PDB file.
    fixed_pdb_path (str): Path where the fixed PDB file will be saved.
    """
    with open(original_pdb_path, 'r') as file:
        lines = file.readlines()

    CRYST1 = False
    header = False
    for line in lines:
        LINE = str(line).split(sep=' ')
        for item in LINE:
            if re.search('CRYST1', item):
                CRYST1 = True
            if re.search('HEADER', item):
                header = True

    if (not CRYST1) and (not header):
        # Define a dummy CRYST1 record with a large unit cell
        # These numbers mean that the unit cell is a cube with 1000 Å edges.
        cryst1_record = "CRYST1 1000.000 1000.000 1000.000  90.00  90.00  90.00 P 1           1\n"
        lines.insert(0, cryst1_record)  # Insert the dummy CRYST1 record
        #lines.insert(0, 'header \n')

    with open(fixed_pdb_path, 'w') as file:
        file.writelines(lines)

def fold_protein (sequence: Annotated[str, 'protein sequence in fasta format. Only a sequence of amino acids.'], name: Annotated[str, 'proper name for the protein to be saved'], device='cpu') -> str:
    filename='temp.fasta'

    output=code_dir#'./'
    with open(filename, "w") as f:
        f.write(">%s\n%s\n" % (name, sequence))
    #omegafold='/home/bni/anaconda3/envs/protein_design/bin/omegafold'

    command = [
        "omegafold",
        filename,
        output,
        "--model", str(2),
        "--device", device
    ]
    # Run the command
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("OmegaFold Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error running OmegaFold:", e.stderr)

    fix_pdb_file(code_dir+name+'.pdb',code_dir+name+'.pdb')
    return name+'.pdb'

def first_last_pdb_implicit_solvent(work_path):

    input_pdb = f'./{work_path}/TestProt_chain_0_after_psf.pdb'
    input_psf = f'./{work_path}/TestProt_chain_0_after_psf.psf'
    input_dcd_file = f'./{work_path}/1_Equilibrate_system/TestProt_chain_0_after_psf_AlongX_NPT.dcd'

    tcl_script = f'''

    mol new {input_pdb} type pdb
    
    # Load the trajectory (DCD file)
    mol addfile {input_dcd_file} type dcd waitfor all
    
    # Get the number of frames in the trajectory
    set total_frames [molinfo top get numframes]

    # Calculating frame indices
    set first_quarter_frame [expr {{int(($total_frames - 1) / 4)}}]
    set halfway_frame [expr {{int(($total_frames - 1) / 2)}}]
    set last_quarter_frame [expr {{int(3 * ($total_frames - 1) / 4)}}]
    
    # Save the first frame
    animate write pdb ./{work_path}/collect_results/first_frame.pdb beg 0 end 0 waitfor all
    
    # Save the first quarter frame
    animate write pdb ./{work_path}/collect_results/first_quarter.pdb beg $first_quarter_frame end $first_quarter_frame waitfor all

    # Save the halfway frame
    animate write pdb ./{work_path}/collect_results/halfway.pdb beg $halfway_frame end $halfway_frame waitfor all
    
    # Save the last quarter frame
    animate write pdb ./{work_path}/collect_results/last_quarter.pdb beg $last_quarter_frame end $last_quarter_frame waitfor all

    puts "Total Frame: $total_frames" 
    # Save the last frame
    animate write pdb ./{work_path}/collect_results/last_frame.pdb beg [expr {{$total_frames - 1}}] end [expr {{$total_frames - 1}}] waitfor all
    exit
    '''
    with open('fig_script.tcl', 'w') as f:
        f.write(tcl_script)

    # Command to run VMD with the Tcl script
    command = f'vmd -dispdev text  -e fig_script.tcl'

    # Run the command
    completed_process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    stdout_text = completed_process.stdout.decode()
    stderr_text = completed_process.stderr.decode()