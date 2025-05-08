import subprocess
import pandas as pd
import os
import time
import json
import re
import numpy as np
from scipy.ndimage import uniform_filter1d
os.getcwd()
code_dir = './code_dir/'

def run_all(input_pdb:str, 
            work_path='1_working_dir',
            sep_chain=1,
            namdc='namd2_path',
            catdcd_commad='catdcd_path',
            eq_step=5000,
            MD_1_step=160000, MD_2_step=160000, MD_3_step=180000,
            n_stage=10,
            AA_lengh=100):
    # 1
    run_initialMD(input_pdb,             
               work_path=work_path,
               sep_chain=sep_chain,
               namdc=namdc,
               eq_step=eq_step,
               MD_1_step=MD_1_step, MD_2_step=MD_2_step, MD_3_step=MD_3_step)

    # 2
    merge_MD_results(work_path=work_path, namdc=namdc, n_stage=n_stage, catdcd_commad=catdcd_commad)
    # 3
    analyze_MD_results(work_path=work_path, namdc=namdc)
    

def mean_RMSD(work_path):
    df_path = work_path + '/collect_results/TestProt_chain_0_after_psf_AlongX_NPT_rmsd.dat'
    data = []
    with open(df_path) as file:
        lines = file.readlines()
    for line in lines:
        dat = line.split()
        data.append([float(dat[0]), float(dat[1])])

    d_2 = uniform_filter1d(np.array(data)[:, 0], size=20, mode='nearest')
    f_2 = uniform_filter1d(np.array(data)[:, 1], size=20, mode='nearest')
    
    meanRMSD = np.mean(np.sort(f_2))
    return meanRMSD

# %%
def max_RMSD(work_path):
    df_path = work_path + '/collect_results/TestProt_chain_0_after_psf_AlongX_NPT_rmsd.dat'
    data = []
    with open(df_path) as file:
        lines = file.readlines()
    for line in lines:
        dat = line.split()
        data.append([float(dat[0]), float(dat[1])])

    d_2 = uniform_filter1d(np.array(data)[:, 0], size=20, mode='nearest')
    f_2 = uniform_filter1d(np.array(data)[:, 1], size=20, mode='nearest')
    
    maxRMSD = np.max(np.sort(f_2))
    return maxRMSD

# %%
def protein_x_F(work_path,
                  AA_length):
    df_path = work_path + '/collect_results/data_smooth.csv'
    df = pd.read_csv(df_path)
    indices = np.linspace(0, len(np.array(df['F']))-1, AA_length, dtype=int)
    x_F = np.hstack((np.reshape(list(df['x'][indices]), (-1, 1)), np.reshape(list(df['F'][indices]), (-1, 1))))
    x_F_dict = {x_F[i][0]: x_F[i][1] for i in range(len(x_F))}
    return json.dumps(x_F_dict, indent=4)

def protein_F_max(work_path,
          AA_length):
    df_path = work_path + '/collect_results/data_smooth.csv'
    df = pd.read_csv(df_path)
    indices = np.linspace(0, len(np.array(df['F']))-1, AA_length, dtype=int)
    F_max = max(df['F'][indices])

    return json.dumps(F_max, indent=4)

def protein_energy(work_path,
          AA_length):
    df_path = work_path + '/collect_results/data_smooth.csv'
    df = pd.read_csv(df_path)
    indices = np.linspace(0, len(np.array(df['F']))-1, AA_length, dtype=int)
    energy = np.trapz(df['F'][indices], df['x'][indices])
    
    return json.dumps(energy, indent=4)

# %%
def run_initialMD(input_pdb, 
               work_path,
               sep_chain,
               namdc,
               eq_step, 
               MD_1_step, MD_2_step, MD_3_step):
    #try:
        # Create a temporary Tcl script to generate PSF using autopsf
        bash_script = f'''
        namdc={namdc}
        IF_Sepe_Chain={sep_chain}
        # water sphere without PBC
        IF_Prep_WS=1
        IF_Gene_psf=1
        n_stage=10
        IF_Run_Eq=1
        IF_Ana_eq=1
        IF_Run_SMD=1
        IF_Ana_smd=1
        IF_Make_Movie=0

        num_cpu=2
        
        # preparation
        code_path=0_codes
        work_path={work_path}
        resu_path=2_results_dir
        
        # under the work_path
        MD_eqi_path=1_Equilibrate_system/
        MD_smd_path=2_Loading/
        MD_pict=md_pict

        
        if [[ -d "./${{work_path}}" ]];
        then
        echo "Working path exists. May clean it up"
        # # for debug
        # echo "In DEBUG mode, EVERYTHING is from zero..."
        # rm -r ./${{work_path}}/*
        else
        echo "Creating the working path"
        mkdir ./${{work_path}}
        fi

        log_file=$PWD/run_monitor.log

        cd ${{work_path}}


        # make one-time log file
        echo "Beginning of a run..." > ${{log_file}}
        # copy the scripts
        cp ../${{code_path}}/path_lib.dat ./
        cp ../${{code_path}}/0_seperate_pdb_into_chains.tcl ./
        cp ../${{code_path}}/1_build_psf_for_protein_chain.tcl ./
        
        cp ../${{code_path}}/2_rotate_and_position_one_chain_ImplicitWater.tcl ./
        echo "tcl files copied..." > ${{log_file}}
        
        echo "*************************************************"
        
        # 1. seperate the chains and only take care of Chain A
        cp ../{input_pdb} ./RAW_PDB.pdb


        time_0=$SECONDS
        time_1=$SECONDS
        if [ $IF_Sepe_Chain -eq 1 ]
        then
            log_line="0. Create Raw Chain 0..."
            echo $log_line
        	echo $log_line >> ${{log_file}}
        
        	# should get TestProt_chain_0.pdb, check
            check_file=./TestProt_chain_0.pdb
            if [[ -f ${{check_file}} ]]; then
                log_line="Already done."
                echo $log_line
        	    echo $log_line >> ${{log_file}}
            else
                echo "seperating pdb"
                vmd -dispdev text -e ./0_seperate_pdb_into_chains.tcl
        	
                if [[ -f "./TestProt_chain_0.pdb" ]];
                then
                    log_line="Excuting: Done."
                else
                    log_line="Excuting: Error!!!!!!!!!!!!!!"
                fi
                echo $log_line
                echo $log_line >> ${{log_file}}
            fi
    
        fi
        time_2=$SECONDS
        echo "used time: $(($time_2-$time_1))" >>  ${{log_file}}
        
        echo "*************************************************"

        # 2. build the psf for Chain 0
        time_1=$SECONDS
        
        if [ $IF_Gene_psf -eq 1 ]
        then
            log_line="1. Create psf for chain A..."
            echo $log_line
        	echo $log_line >> ${{log_file}}
            # should get TestProt_chain_0_after_psf.pdb+psf, check
        
            check_file=./TestProt_chain_0_after_psf.psf
            if [[ -f ${{check_file}} ]]; then
                log_line="Already done."
                echo $log_line
        	    echo $log_line >> ${{log_file}}
            else
                vmd -dispdev text -e ./1_build_psf_for_protein_chain.tcl
        	
                if [[ -f ./TestProt_chain_0_after_psf.pdb && -f ./TestProt_chain_0_after_psf.psf ]];
                then
                    log_line="Excuting: Done."
                else
                    log_line="Excuting: Error!!!!!!!!!!!!!!"
                fi
                echo $log_line
                echo $log_line >> ${{log_file}}
        
            fi	
        
        fi
        time_2=$SECONDS
        echo "used time: $(($time_2-$time_1))" >>  ${{log_file}}

        echo "*************************************************"
        
        # 3. add water and prepare for eq
        time_1=$SECONDS
        if [ $IF_Prep_WS -eq 1 ]
        then
            log_line="2. Add into water sphere..."
            echo $log_line
        	echo $log_line >> ${{log_file}}
        
            # should get TestProt_chain_0_after_psf_AlongX_WS.pdf+psf+ref
            check_file_1=./TestProt_chain_0_after_psf_AlongX.ref
            check_file_2=./TestProt_chain_0_after_psf_AlongX.pdb
            # check_file_3=./TestProt_chain_0_after_psf_AlongX_WS.psf
            # if [[ -f $check_file_1 && -f $check_file_2 && -f $check_file_3 ]]; then
            if [[ -f $check_file_1 && -f $check_file_2 ]]; then
                log_line="Already done."
                echo $log_line
        	    echo $log_line >> ${{log_file}}
            else
                # ++++++++++++++++++++++++++++++++++++++++++++
                # # add a tcl source file to control SMD stages: n_stage
                #echo "set n_stage $n_stage" > ./SMD_step_set.tcl 
        
                vmd -dispdev text -e 2_rotate_and_position_one_chain_ImplicitWater.tcl
                # should get TestProt_chain_0_after_psf_AlongX_WB.ref, check
                if [[ -f "./TestProt_chain_0_after_psf_AlongX_WB.ref" ]];
                then
                    log_line="Excuting: Done."
                else
                    log_line="Excuting: Error!!!!!!!!!!!!!!"
                fi
                echo $log_line
                echo $log_line >> ${{log_file}}
            fi
        fi
        time_2=$SECONDS
        echo "used time: $(($time_2-$time_1))" >>  ${{log_file}}

        echo "*************************************************"

        # 4. performan eq: NPT with OX constrain
        mkdir -p $MD_eqi_path
        cd $MD_eqi_path
        # for continous operation
        ContiFile=./ContiInfo.dat
        
        # for real run
        # ================================================
        if [[ ! -e $ContiFile ]]; then
            touch $ContiFile
            echo "set MinStep     {eq_step}" >> $ContiFile
            echo "set NPTStep_S1 {MD_1_step}"  >> $ContiFile
            echo "set NPTStep_S2 {MD_2_step}"  >> $ContiFile
            echo "set NPTStep_S3 {MD_3_step}"  >> $ContiFile
        fi
        # ================================================
        
        # # for debug
        # # ================================================
        # if [[ ! -e $ContiFile ]]; then
        #     touch $ContiFile
        #     echo "set MinStep    10000" >> $ContiFile
        #     echo "set NPTStep_S1 4000"  >> $ContiFile
        #     echo "set NPTStep_S2 4000"  >> $ContiFile
        #     echo "set NPTStep_S3 4000"  >> $ContiFile
        # fi
        # # ================================================
        
        
        # for MD log files
        target_word="End of program"
        
        log_line="3. Minimization + NPT with OX constrain ..."
        echo $log_line
        echo $log_line >> ${{log_file}}
        
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        # S0
        time_1=$SECONDS
        if [ $IF_Run_Eq -eq 1 ]
        then
            log_line="4.1 Stage 1 of 4 ..."
            echo $log_line
            echo $log_line >> ${{log_file}}
        
            # 1. check wether it has been finished
            task_name=0_EneMin_NPT_withConstrain_S0
        
            task_log_file=${{task_name}}.log
            last_line=$( tail -n 1 $task_log_file )
            last_three_word=$( echo $last_line | rev | awk '{{NF=3}}1' |rev )
            # for debug
            echo $last_three_word
        
            if [[ "$last_three_word" == "$target_word" ]]; then
                log_line="Already done."
                echo $log_line
        	    echo $log_line >> ${{log_file}}
            else
                log_line="Excuting ..."
                echo $log_line
        	    echo $log_line >> ${{log_file}}
        
                # cp ../../${{code_path}}/0_EneMin_NPT_withConstrain.conf ./
                cp ../../${{code_path}}/${{task_name}}.conf ./
                # multi-cpu task
                ${{namdc}} +devices 0 ${{task_name}}.conf > $task_log_file
        
                # check
                # task_log_file=0_EneMin_NPT_withConstrain_S0.log
                last_line=$( tail -n 1 $task_log_file )
                last_three_word=$( echo $last_line | rev | awk '{{NF=3}}1' |rev )
        
                if [[ "$last_three_word" == "$target_word" ]]; then
                    log_line="Done"
                else
                    log_line="Error!!!!!!!!!!!!!!"
                fi
                echo $log_line
                echo $log_line >> ${{log_file}}
            fi
        
        fi
        time_2=$SECONDS
        echo "used time: $(($time_2-$time_1))" >>  ${{log_file}}

        echo "*************************************************"

        # S1
        time_1=$SECONDS
        if [ $IF_Run_Eq -eq 1 ]
        then
            log_line="4.1 Stage 2 of 4 ..."
            echo $log_line
            echo $log_line >> ${{log_file}}
        
            # 1. check wether it has been finished
            task_name=0_EneMin_NPT_withConstrain_S1
        
            task_log_file=${{task_name}}.log
            last_line=$( tail -n 1 $task_log_file )
            last_three_word=$( echo $last_line | rev | awk '{{NF=3}}1' |rev )
            # for debug
            echo $last_three_word
        
            if [[ "$last_three_word" == "$target_word" ]]; then
                log_line="Already done."
                echo $log_line
        	    echo $log_line >> ${{log_file}}
            else
                log_line="Excuting ..."
                echo $log_line
        	    echo $log_line >> ${{log_file}}
        
                # cp ../../${{code_path}}/0_EneMin_NPT_withConstrain.conf ./
                cp ../../${{code_path}}/${{task_name}}.conf ./
                # multi-cpu task
                ${{namdc}} +devices 0 ${{task_name}}.conf > $task_log_file
        
                # check
                # task_log_file=0_EneMin_NPT_withConstrain_S1.log
                last_line=$( tail -n 1 $task_log_file )
                last_three_word=$( echo $last_line | rev | awk '{{NF=3}}1' |rev )
        
                if [[ "$last_three_word" == "$target_word" ]]; then
                    log_line="Done"
                else
                    log_line="Error!!!!!!!!!!!!!!"
                fi
                echo $log_line
                echo $log_line >> ${{log_file}}
            fi
        
        fi
        time_2=$SECONDS
        echo "used time: $(($time_2-$time_1))" >>  ${{log_file}}

        echo "*************************************************"

        # S2
        time_1=$SECONDS
        if [ $IF_Run_Eq -eq 1 ]
        then
            log_line="4.3 Stage 3 of 4 ..."
            echo $log_line
            echo $log_line >> ${{log_file}}
        
            # 1. check wether it has been finished
            task_name=0_EneMin_NPT_withConstrain_S2

            task_log_file=${{task_name}}.log
            last_line=$( tail -n 1 $task_log_file )
            last_three_word_2=$( echo $last_line | rev | awk '{{NF=3}}1' |rev )
            
        
            # echo $last_three_word_2
            # echo $target_word
            
            # if [[ "$last_three_word_2" != "$target_word" ]] 
            # then
            #     echo match
            # fi 
        
            if [[ "$last_three_word_2" == "$target_word" ]]; then
                log_line="Already done."
                echo $log_line
        	    echo $log_line >> ${{log_file}}
            else
                log_line="Excuting ..."
                echo $log_line
        	    echo $log_line >> ${{log_file}}
        
                # cp ../../${{code_path}}/0_EneMin_NPT_withConstrain.conf ./
                cp ../../${{code_path}}/${{task_name}}.conf ./
                # multi-cpu task
                ${{namdc}} +devices 0 ${{task_name}}.conf > $task_log_file
        
                # check
                # task_log_file=0_EneMin_NPT_withConstrain_S2.log
                last_line=$( tail -n 1 $task_log_file )
                last_three_word=$( echo $last_line | rev | awk '{{NF=3}}1' |rev )
        
                if [[ $last_three_word=='End_of program' ]]; then
                    log_line="Done"
                else
                    log_line="Error!!!!!!!!!!!!!!"
                fi
                echo $log_line
                echo $log_line >> ${{log_file}}
            fi
           
        fi
        time_2=$SECONDS
        echo "used time: $(($time_2-$time_1))" >>  ${{log_file}}

        # S3
        time_1=$SECONDS
        if [ $IF_Run_Eq -eq 1 ]
        then
            log_line="4.4 Stage 4 of 4 ..."
            echo $log_line
            echo $log_line >> ${{log_file}}
        
            # 1. check wether it has been finished
            task_name=0_EneMin_NPT_withConstrain_S3
        
            task_log_file=${{task_name}}.log
            last_line=$( tail -n 1 $task_log_file )
            last_three_word_3=$( echo $last_line | rev | awk '{{NF=3}}1' |rev )
            
        
            # echo $last_three_word_2
            # echo $target_word
            
            # if [[ "$last_three_word_2" != "$target_word" ]] 
            # then
            #     echo match
            # fi 
        
            if [[ "$last_three_word_3" == "$target_word" ]]; then
                log_line="Already done."
                echo $log_line
        	    echo $log_line >> ${{log_file}}
            else
                log_line="Excuting ..."
                echo $log_line
        	    echo $log_line >> ${{log_file}}
        
                # cp ../../${{code_path}}/0_EneMin_NPT_withConstrain.conf ./
                cp ../../${{code_path}}/${{task_name}}.conf ./
                # multi-cpu task
                ${{namdc}} +devices 0 ${{task_name}}.conf > $task_log_file
        
                # check
                # task_log_file=0_EneMin_NPT_withConstrain_S2.log
                last_line=$( tail -n 1 $task_log_file )
                last_three_word=$( echo $last_line | rev | awk '{{NF=3}}1' |rev )
        
                if [[ $last_three_word=='End_of program' ]]; then
                    log_line="Done"
                else
                    log_line="Error!!!!!!!!!!!!!!"
                fi
                echo $log_line
                echo $log_line >> ${{log_file}}
            fi
           
        fi
        time_2=$SECONDS
        echo "used time: $(($time_2-$time_1))" >>  ${{log_file}}
        
        '''
        #writepsf {output_psf_file}s
        # Write Tcl script to a file
        with open('bash_script.sh', 'w') as f:
            f.write(bash_script)

        # Command to run VMD with the Tcl script
        command = f'bash ./bash_script.sh'

        # Run the command
        completed_process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        stdout_text = completed_process.stdout.decode()
        stderr_text = completed_process.stderr.decode()
   # except subprocess.CalledProcessError as e:
        #print(f"Error generating PSF file: {e}")

# %%
def merge_MD_results(work_path, namdc, n_stage, catdcd_commad):
    #try:
        # Create a temporary Tcl script to generate PSF using autopsf
        bash_script = f'''
        namdc={namdc}
        catdcd_commad={catdcd_commad}
        IF_Run_Eq=1
        code_path=0_codes
        MD_eqi_path=1_Equilibrate_system/
        work_path={work_path}
        n_stage={n_stage}
        log_file=$PWD/run_monitor.log
        
        cd ${{work_path}}
        cd $MD_eqi_path
    
        echo $PWD
        # Merge the results
        time_1=$SECONDS
        if [ $IF_Run_Eq -eq 1 ]
        then
            log_line="Merge the results and prepare the next step."
            echo $log_line
            echo $log_line >> ${{log_file}}
        
            out_dcd="./TestProt_chain_0_after_psf_AlongX_NPT.dcd"
            if [[ ! -e $out_dcd ]]; then
                # on dcd
                dcd_1=TestProt_chain_0_after_psf_AlongX_NPT_S1.dcd
                dcd_2=TestProt_chain_0_after_psf_AlongX_NPT_S2.dcd
                dcd_3=TestProt_chain_0_after_psf_AlongX_NPT_S3.dcd
        
                # dcd_out=TestProt_chain_0_after_psf_AlongX_WB_NPT.dcd
                ${{catdcd_commad}} -o ${{out_dcd}} ${{dcd_1}} ${{dcd_2}} ${{dcd_3}}
                # cp ../../${{code_path}}/3_1_merge_dcd.tcl ./
                # ${{namdc}} -dispdev text -e 3_1_merge_dcd.tcl

            fi
        
            # on log file
            out_log="./0_EneMin_NPT_withConstrain.log"
            if [[ ! -e $out_log ]]; then
                ene_log_1=0_EneMin_NPT_withConstrain_S1.log
                ene_log_2=0_EneMin_NPT_withConstrain_S2.log
                ene_log_3=0_EneMin_NPT_withConstrain_S3.log
        
                cat ${{ene_log_1}} ${{ene_log_2}} ${{ene_log_3}} > $out_log 
        
            fi
        
            # on the restart files
            rest_1=TestProt_chain_0_after_psf_AlongX_NPT.restart.coor
            rest_2=TestProt_chain_0_after_psf_AlongX_NPT.restart.vel
            rest_3=TestProt_chain_0_after_psf_AlongX_NPT.restart.xsc
            if [[ ! -e $rest_1 ]]; then
                cp TestProt_chain_0_after_psf_AlongX_NPT_S3.restart.coor ${{rest_1}}
            fi
            if [[ ! -e $rest_2 ]]; then
                cp TestProt_chain_0_after_psf_AlongX_NPT_S3.restart.vel  ${{rest_2}}
            fi
            if [[ ! -e $rest_3 ]]; then
                cp TestProt_chain_0_after_psf_AlongX_NPT_S3.restart.xsc  ${{rest_3}}
            fi
        
            log_line="Done."
            echo $log_line
            echo $log_line >> ${{log_file}}
        fi
        time_2=$SECONDS
        echo "used time: $(($time_2-$time_1))" >>  ${{log_file}}
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        cd ../
        echo $PWD
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        # +4.5. re-calibrate the distance between ends and set for SMD
        time_1=$SECONDS
        if [ $IF_Run_Eq -eq 1 ]
        then
            log_line="4.5 Analyze the last frame of Equ..."
            echo $log_line
            echo $log_line >> ${{log_file}}
        
            # deliver files
            cp ../${{code_path}}/2_5_plan_SMD_after_Eq.tcl ./
        
            check_file_1=./TestProt_chain_0_after_psf_AlongX_AfterEq.ref
            check_file_2=./TestProt_chain_0_after_psf_AlongX_AfterEq.pdb
            if [[ -f $check_file_1 && -f $check_file_2 ]]; then
                log_line="Already done."
                echo $log_line
        	    echo $log_line >> ${{log_file}}
            else
                # ++++++++++++++++++++++++++++++++++++++++++++++++++++
                # add a tcl source file to control SMD stages: n_stage
                echo "set n_stage $n_stage" > ./SMD_step_set.tcl 
        
                vmd -dispdev text -e 2_5_plan_SMD_after_Eq.tcl
                # should ./TestProt_chain_0_after_psf_AlongX_AfterEq.ref, check
                if [[ -f $check_file_1 && -f $check_file_2 ]];
                then
                    log_line="Excuting: Done."
                else
                    log_line="Excuting: Error!!!!!!!!!!!!!!"
                fi
                echo $log_line
                echo $log_line >> ${{log_file}}
        
        
            fi
        
        fi
        time_2=$SECONDS
        echo "used time: $(($time_2-$time_1))" >>  ${{log_file}}


        '''
        #writepsf {output_psf_file}s
        # Write Tcl script to a file
        with open('bash_script.sh', 'w') as f:
            f.write(bash_script)

        # Command to run VMD with the Tcl script
        command = f'bash ./bash_script.sh'

        # Run the command
        completed_process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        #stdout_text = completed_process.stdout.decode()
        #stderr_text = completed_process.stderr.decode()
        #print(stdout_text)

   # except subprocess.CalledProcessError as e:
        #print(f"Error generating PSF file: {e}")

# %%
def analyze_MD_results(work_path, namdc):

        bash_script = f'''
        echo $PWD
        code_path=0_codes
        work_path={work_path}
        resu_path=collect_results
        IF_Ana_eq=1
        
        # under the work_path
        MD_eqi_path=1_Equilibrate_system/
        MD_smd_path=2_Loading/
        MD_pict=md_pict
        IF_Run_SMD=1

        log_file=$PWD/run_monitor.log
        cd $work_path
        
        namdc={namdc}


        # 5. analyze the eq results
        # prepare to collect results:
        time_1=$SECONDS
        if [ $IF_Ana_eq -eq 1 ]
        then
            log_line="4. Analyze the eq results..."
            echo $log_line
            echo $log_line >> ${{log_file}}
        
            # deliver files
            cp ../${{code_path}}/3_analyze_eq.tcl ./
            cp ../${{code_path}}/fun_0_namdstats_adjusted.tcl ./
            cp ../${{code_path}}/plot_for_3.py ./
        
        	mkdir -p ./${{resu_path}}
        
            check_file=./${{resu_path}}/TOTAL.dat
            if [[ -f ${{check_file}} ]]; then
                log_line="Already done."
                echo $log_line
        	    echo $log_line >> ${{log_file}}
            else
                log_line="4. Excuting..."
                echo $log_line
                echo $log_line >> ${{log_file}}
        
                vmd -dispdev text -e 3_analyze_eq.tcl
                # covert datainto figures for check
                python3 plot_for_3.py
        
                if [[ -f ${{check_file}} ]]; then
                    log_line="Done"
                else
                    log_line="Error!!!!!!!!!!!!!!!!!!"
                fi
                echo $log_line
                echo $log_line >> ${{log_file}}
            fi
        
        fi
        time_2=$SECONDS
        echo "used time: $(($time_2-$time_1))" >>  ${{log_file}}

        '''
        #writepsf {output_psf_file}s
        # Write Tcl script to a file
        with open('bash_script.sh', 'w') as f:
            f.write(bash_script)

        # Command to run VMD with the Tcl script
        command = f'bash ./bash_script.sh'

        # Run the command
        completed_process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        

# %%
def run_SMD(work_path, namdc, n_stage):
    #try:
    # preparation
        
        # Create a temporary Tcl script to generate PSF using autopsf
        bash_script = f'''
        echo $PWD
        code_path=0_codes
        work_path={work_path}
        n_stage={n_stage}
        # under the work_path
        MD_eqi_path=1_Equilibrate_system/
        MD_smd_path=2_Loading/
        MD_pict=md_pict
        IF_Run_SMD=1

        log_file=$PWD/run_monitor.log
        cd $work_path
        
        namdc={namdc}
        

        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        # 6. SMD: 10 steps as an extreme case
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        log_line="5. NVT + SMD ..."
        echo $log_line
        echo $log_line >> ${{log_file}}
        
        mkdir -p $MD_smd_path
        cd $MD_smd_path
        
        target_word="End of program"
        
        # +++++++++++++++++++++++++++++++++++++++++++++++++++
        # change it into a with automatic N steps
        for (( i_SMD=1; i_SMD<=(($n_stage)); i_SMD++ ))
        do
            echo "test $i_SMD"
            time_1=$SECONDS
            if [ $IF_Run_SMD -eq 1 ]
            then
                log_line="5.$i_SMD Stage $i_SMD of $n_stage ..."
                echo $log_line
                echo $log_line >> ${{log_file}}
        
                # 1. check wether it has been finished
                task_name=1_Tension_AlongX_S${{i_SMD}}
                echo $task_name
        
                task_log_file=${{task_name}}.log
                last_line=$( tail -n 1 $task_log_file )
                last_three_word=$( echo $last_line | rev | awk '{{NF=3}}1' |rev )
                # for debug
                echo $last_three_word
        
                if [[ "$last_three_word" == "$target_word" ]]; then
                    log_line="Already done."
                    echo $log_line
                    echo $log_line >> ${{log_file}}
                else
                    log_line="Excuting ..."
                    echo $log_line
                    echo $log_line >> ${{log_file}}
        
                    if [ $i_SMD -eq 1 ]
                    then
                        echo ${{task_name}}
                        cp ../../${{code_path}}/${{task_name}}.conf ./
                    else
                        # create one on the spot
                        touch ${{task_name}}.conf 
                        # write a few lines that changes
                        echo "source ../box_dimension.dat" > ${{task_name}}.conf
                        echo "source ../box_dimension_after_eq.dat" >> ${{task_name}}.conf
                        echo "source ../path_lib.dat" >> ${{task_name}}.conf
                        echo "set PrevStep [expr \${{RunStep_sep}}*$((i_SMD-1))+0]" >> ${{task_name}}.conf
                        echo "set PrevName ./smdout_S$((i_SMD-1))" >> ${{task_name}}.conf
                        echo "set ThisName smdout_S$((i_SMD))" >> ${{task_name}}.conf
                        # copy the remaining common part
                        cat ../../${{code_path}}/1_Tension_AlongX_S_add_after1.conf >> ${{task_name}}.conf 
                    fi
                    # cp ../../${{code_path}}/${{task_name}}.conf ./
                    
                    # for debug
                    ${{namdc}} +devices 0 ${{task_name}}.conf > $task_log_file
        
                    # check
                    # task_log_file=0_EneMin_NPT_withConstrain_S1.log
                    last_line=$( tail -n 1 $task_log_file )
                    last_three_word=$( echo $last_line | rev | awk '{{NF=3}}1' |rev )
        
                    if [[ "$last_three_word" == "$target_word" ]]; then
                        log_line="Done"
                    else
                        log_line="Error!!!!!!!!!!!!!!"
                    fi
                    echo $log_line
                    echo $log_line >> ${{log_file}}
                fi
        
            fi
            time_2=$SECONDS
            echo "used time: $(($time_2-$time_1))" >>  ${{log_file}}
        
        done


        time_2=$SECONDS
        echo "used time: $(($time_2-$time_1))" >>  ${{log_file}}

        '''
        #writepsf {output_psf_file}s
        # Write Tcl script to a file
        with open('bash_script.sh', 'w') as f:
            f.write(bash_script)

        # Command to run VMD with the Tcl script
        command = f'bash ./bash_script.sh'

        # Run the command
        completed_process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        stdout_text = completed_process.stdout.decode()
        stderr_text = completed_process.stderr.decode()

# %%
def merge_SMD_results(work_path, namdc, catdcd_commad):

        bash_script = f'''
        namdc={namdc}
        catdcd_commad={catdcd_commad}
        IF_Run_Eq=1
        n_stage=10
        code_path=0_codes
        MD_eqi_path=1_Equilibrate_system/
        work_path={work_path}
        MD_smd_path=2_Loading/

        log_file=$PWD/run_monitor.log
        
        cd $work_path
        cd $MD_smd_path
        # Merge the results
        time_1=$SECONDS
        
        if [ $IF_Run_Eq -eq 1 ]
        then
            log_line="Merge the results and prepare the next step."
            echo $log_line
            echo $log_line >> ${{log_file}}
        
            out_dcd="./smdout.dcd"
            if [[ ! -e $out_dcd ]]; then
                # on dcd
                # +++++++++++++++++++++++++++++++++++++++++++++
                in_dcd_list=''
                for (( i_SMD=1; i_SMD<=(($n_stage)); i_SMD++ ))
                do
                    in_dcd_list="${{in_dcd_list}}smdout_S${{i_SMD}}.dcd "
                done
                # for debug
                echo $in_dcd_list
                # execute
                ${{catdcd_commad}} -o $out_dcd $in_dcd_list
        
            fi
        
            # on log file
            out_log="./0_Tension_AlongX_np.log"
            if [[ ! -e $out_log ]]; then
                # ++++++++++++++++++++++++++++++++++++++
                cat 1_Tension_AlongX_S1.log > $out_log 
                for (( i_SMD=2; i_SMD<=(($n_stage)); i_SMD++ ))
                do
                    cat 1_Tension_AlongX_S${{i_SMD}}.log >> $out_log 
                done
        
            fi
        
            log_line="Done."
            echo $log_line
            echo $log_line >> ${{log_file}}
        fi
        time_2=$SECONDS
        echo "used time: $(($time_2-$time_1))" >>  ${{log_file}}
        '''
        #writepsf {output_psf_file}s
        # Write Tcl script to a file
        with open('bash_script.sh', 'w') as f:
            f.write(bash_script)

        # Command to run VMD with the Tcl script
        command = f'bash ./bash_script.sh'

        # Run the command
        completed_process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        stdout_text = completed_process.stdout.decode()
        stderr_text = completed_process.stderr.decode()

# %%
def collect_SMD_results(work_path, namdc, catdcd_commad):

        bash_script = f'''
        namdc={namdc}
        catdcd_commad={catdcd_commad}
        IF_Run_Eq=1
        IF_Ana_smd=1
        IF_Make_Movie=1
        n_stage=10
        code_path=0_codes
        MD_eqi_path=1_Equilibrate_system/
        work_path={work_path}
        MD_smd_path=2_Loading/
        resu_path=collect_results
        MD_pict=md_pict
        log_file=$PWD/run_monitor.log
        
        cd $work_path

        # 7. Collect the results
        time_1=$SECONDS
        if [ $IF_Ana_smd -eq 1 ]
        then
        
            cp ../${{code_path}}/4_analyze_smd.tcl ./
            cp ../${{code_path}}/plot_for_6.py ./
        
            out_mp4="./${{resu_path}}/SMDHist_x_Fn.jpg"
            if [[ ! -e $out_mp4 ]]; then
            	vmd -dispdev text -e 4_analyze_smd.tcl
                # covert datainto figures for check
                python3 plot_for_6.py
            fi
        fi
        time_2=$SECONDS
        echo "used time: $(($time_2-$time_1))" >>  ${{log_file}}
        
        # 8. Make a Movie if needed
        time_1=$SECONDS
        if [ $IF_Make_Movie -eq 1 ]
        then
        
            cp ../${{code_path}}/5_make_movie.tcl  ./
        
        	log_line="7. Make movie of MD loading ...."
        	echo $log_line
            echo $log_line >> ${{log_file}}
        	
            mkdir -p $MD_pict
            # rm test_smd_x.mp4
        
            vmd -dispdev text -e 5_make_movie.tcl
        
            ffmpeg -r 60 -f image2 -i ./md_pict/%05d.tga -vcodec libx264 -crf 25  -pix_fmt yuv420p test_smd_x.mp4
        
            out_mp4="./test_smd_x.mp4"
            if [[ ! -e $out_mp4 ]]; then
                ffmpeg -framerate 30 -i ./md_pict/%05d.tga test_smd_x.mp4
            fi
        
        fi
        time_2=$SECONDS
        echo "used time: $(($time_2-$time_1))" >>  ${{log_file}}
        # 9. collect the results and clean up


        cd ../
        time_2=$SECONDS
        echo "used time: $(($time_2-$time_1))" >>  ${{log_file}}
        echo "Done."
        '''
        #writepsf {output_psf_file}s
        # Write Tcl script to a file
        with open('bash_script.sh', 'w') as f:
            f.write(bash_script)

        # Command to run VMD with the Tcl script
        command = f'bash ./bash_script.sh'

        # Run the command
        completed_process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        stdout_text = completed_process.stdout.decode()
        stderr_text = completed_process.stderr.decode()
        print(stdout_text)

# %%
