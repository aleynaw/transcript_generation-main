import os, sys
import random
import time

from pathlib import Path
import glob, json

import pandas as pd
import numpy as np
from collections import defaultdict

from pprint import pprint

import matplotlib.pyplot as plt 
import seaborn as sns
import scipy
import ast

import nltk
from nltk import tokenize
nltk.download('punkt')

nltk.download('stopwords')
from nltk.corpus import stopwords


bar_col = {
    "DM-rambling": "blue",
    "DM-brief":"green",
    "SM-rambling": "yellow",
    "SM-brief":"red",
}

def get_melted_df(labeled_df, vars_to_keep:list, vars_to_melt, melted_name_col:str, melted_value_col:str):
    '''If the df has multiple columns "vars_to_melt", those column names will be shifted into a new column "melted_name_col" and their values will be shifted to a new column "melted_value_col".
    :param pandas dataframe labeled_df:
    :param list vars_to_keep:
    :param vars_to_melt: keys of the variables to melt together, values being the replacement for those variables
    :type vars_to_melt: list, dict
    :param str melted_name_col:
    :param str melted_value_col:

    labeled_df=labeled_df
    vars_to_keep=["dataset","bar_col"]
    vars_to_melt={"asst_avg_msg_len": "assistant", "user_avg_msg_len": "patient"}
    melted_name_col="speaker"
    melted_value_col="avg_msg_len"
    '''
    if type(vars_to_melt) == dict:
        vars_to_melt_list = [k for k in vars_to_melt.keys()]
        print(vars_to_melt_list)
        labeled_dfm = pd.melt(labeled_df, 
                            id_vars=vars_to_keep, 
                            value_vars=vars_to_melt_list, 
                            var_name=melted_name_col, 
                            value_name=melted_value_col) 
        #rename if available
        for var in vars_to_melt_list:
            labeled_dfm = labeled_dfm.replace(var, vars_to_melt[var])
    elif type(vars_to_melt) == list:
        labeled_dfm = pd.melt(labeled_df, 
                            id_vars=vars_to_keep, 
                            value_vars=vars_to_melt, 
                            var_name=melted_name_col, 
                            value_name=melted_value_col) 
    return labeled_dfm

def barplot_data(df, x_axis:str, y_axis:str, x_axis_label="", y_axis_label=""):
    g = sns.barplot(
        data=df, 
        x=x_axis, y=y_axis, hue=x_axis,
        errorbar="sd", alpha=.6
    )

    if x_axis_label=="":
            x_axis_label = x_axis
    if y_axis_label=="":
        y_axis_label = y_axis
    g.set(xlabel=x_axis_label, ylabel=y_axis_label)

    g = sns.swarmplot(x=x_axis, y=y_axis, hue=x_axis,palette="dark", alpha=.5, dodge=True,data=df)
    
    return g

def barplot_grouped_data(melted_df, x_axis:str, y_axis:str, x_axis_groupings:str, x_axis_label="", y_axis_label="", legend_label=""):
    '''Create a bar plot with error bars.

    x_axis="speaker"
    y_axis="avg_msg_len"
    x_axis_groupings="dataset"
    
    x_axis_label="Transcript Creation Method"
    y_axis_label="Avg Message Length (characters)"
    legend_label="Role"
    '''
    #make bar graph
    #optionally add palette="dark"
    g = sns.catplot(
        data=melted_df, kind="bar",
        x=x_axis, y=y_axis, hue=x_axis_groupings,
        errorbar="sd", 
        # color=bar_col, ##not working
        # palette="dark",
        palette = sns.color_palette("RdBu", n_colors=4),
        alpha=.6, height=6,
        legend=False
    )
    g.despine(left=True)

    if x_axis_label=="":
            x_axis_label = x_axis
    if y_axis_label=="":
        y_axis_label = y_axis
    g.set_axis_labels(x_axis_label, y_axis_label)

    #add individual points, must come after label attaching
    g = sns.swarmplot(x=x_axis, y=y_axis, hue=x_axis_groupings, palette="dark", alpha=.5, dodge=True,data=melted_df)

    #create legend
    if legend_label=="" and x_axis==x_axis_groupings:
        pass
    elif legend_label=="":
        legend_label = x_axis_groupings
        plt.legend(title=legend_label,loc='upper left',bbox_to_anchor=(1, 1))
        # g.legend.set_title(legend_label)
    else:
        plt.legend(title=legend_label,loc='upper left',bbox_to_anchor=(1, 1))
         
        # g.legend.set_title(legend_label)
    # plt.legend([],[], frameon=False)
    
    return g


def convert_pvalue_to_asterisks(pvalue, bf_correction):
    if pvalue <= 0.0001/bf_correction:
        return "****"
    elif pvalue <= 0.001/bf_correction:
        return "***"
    elif pvalue <= 0.01/bf_correction:
        return "**"
    elif pvalue <= 0.05/bf_correction:
        return "*"
    return "ns"

def get_role_comparison_pvalues(dfm, col, x_val="dataset", bf_correction = False):
    '''
    Parameters
    ----------
    dfm : pandas DataFrame 
        with columns "dataset" and "role" as either assistant/patient. values in the "x_val" column will be paired.
    col : str
        name of column in dfm that pvalue should be calculated from
    
    Output
    ------
    list
    '''
    x_values = dfm[x_val].unique()
    pvalues_list = []
    done = []
    for x in x_values:
        for x1 in x_values:
            if x != x1 and x1 not in done:
                asst_stat, asst_pvalue = scipy.stats.ttest_ind(
                    dfm[(dfm[x_val] == x) & (dfm["role"] == "assistant")][col],
                    dfm[(dfm[x_val] == x1) & (dfm["role"] == "assistant")][col]
                )
                user_stat, user_pvalue = scipy.stats.ttest_ind(
                    dfm[(dfm[x_val] == x) & (dfm["role"] == "patient")][col],
                    dfm[(dfm[x_val] == x1) & (dfm["role"] == "patient")][col]
                )
                pvalues_list.append(((x, x1), 
                                        {"assistant":(asst_pvalue), 
                                        "patient":(user_pvalue)}))
                
            done.append(x)
    if bf_correction:
        corr_val = len(done)
        pvalues_list = [((x, x1), 
                         {"assistant": (pvalue_dict["assistant"], 
                                        convert_pvalue_to_asterisks(pvalue_dict["assistant"], corr_val)),
                          "patient":  (pvalue_dict["patient"], 
                                       convert_pvalue_to_asterisks(pvalue_dict["patient"], corr_val))
                          }) for ((x, x1), pvalue_dict) in pvalues_list]
    else:
        pvalues_list = [((x, x1), 
                         {"assistant": (pvalue_dict["assistant"], 
                                        convert_pvalue_to_asterisks(pvalue_dict["assistant"], 1)),
                          "patient":  (pvalue_dict["patient"], 
                                       convert_pvalue_to_asterisks(pvalue_dict["patient"], 1))
                          }) for ((x, x1), pvalue_dict) in pvalues_list]
    return pvalues_list

def get_pvalues(dfm, col, x_val="dataset", bf_correction=False):
    '''
    Parameters
    ----------
    dfm : pandas DataFrame 
        with columns "dataset" and "speaker" as either assistant/patient. values in the "x_val" column will be paired.
    col : str
        name of column in dfm that pvalue should be calculated from
    x_val : str
        name of the column in dfm that is the x axis grouping
    bf_correction : bool
        whether or not bonferroni correction is applied
    '''
    x_values = dfm[x_val].unique()
    pvalues_list = []
    done = []
    for x in x_values:
        for x1 in x_values:
            if x != x1 and x1 not in done:
                stat, pvalue = scipy.stats.ttest_ind(
                    dfm[dfm[x_val] == x][col],
                    dfm[dfm[x_val] == x1][col]
                )
                pvalues_list.append(((x, x1), pvalue))
            done.append(x)

    #add asterisks for significance
    if bf_correction:
        corr_val = len(done)
        pvalues_list = [((x, x1), pvalue, convert_pvalue_to_asterisks(pvalue, corr_val)) for ((x, x1), pvalue) in pvalues_list]
    else:
        pvalues_list = [((x, x1), pvalue, convert_pvalue_to_asterisks(pvalue, 1)) for ((x, x1), pvalue) in pvalues_list]
    return pvalues_list

def assign_dataset_label(analysis_df):
    return pd.concat(
        [analysis_df[analysis_df["is_double_model"]==True][analysis_df["is_rambling_prompt"]==True].assign(dataset="DM-rambling", bar_col=bar_col["DM-rambling"]), 
        analysis_df[analysis_df["is_double_model"]==True][analysis_df["is_rambling_prompt"]==False].assign(dataset="DM-brief", bar_col=bar_col["DM-brief"]),
        analysis_df[analysis_df["is_double_model"]==False][analysis_df["is_rambling_prompt"]==True].assign(dataset="SM-rambling", bar_col=bar_col["SM-rambling"]),
        analysis_df[analysis_df["is_double_model"]==False][analysis_df["is_rambling_prompt"]==False].assign(dataset="SM-brief", bar_col=bar_col["SM-brief"])])

def assign_dataset_label_gentype(analysis_df):
    return pd.concat(
        [analysis_df[analysis_df["is_double_model"]==True].assign(gentype="DM", bar_col=bar_col["DM-rambling"]), 
        analysis_df[analysis_df["is_double_model"]==False].assign(gentype="SM", bar_col=bar_col["SM-rambling"])])